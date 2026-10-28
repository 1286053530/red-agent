"""SSH transport for explicitly configured project remotes."""
import base64
import hashlib
from pathlib import PurePosixPath
import re
import socket
import stat
import time

import paramiko

from .common import AppError


FINGERPRINT = re.compile(r"^SHA256:[A-Za-z0-9+/]{43}$")
HOST = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")
USERNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")


def validate_remote(data, previous=None):
    if not isinstance(data, dict):
        raise AppError("SSH 配置格式无效。")
    host, username = data.get("host"), data.get("username")
    port, fingerprint = data.get("port", 22), data.get("hostKey")
    password = data.get("password", "")
    if not isinstance(host, str) or not HOST.fullmatch(host) or ".." in host or host.endswith("."):
        raise AppError("SSH 主机名或 IPv4 地址无效。")
    if type(port) is not int or not 1 <= port <= 65535 or not isinstance(username, str) or not USERNAME.fullmatch(username):
        raise AppError("SSH 端口或用户名无效。")
    if not isinstance(fingerprint, str) or not FINGERPRINT.fullmatch(fingerprint):
        raise AppError("请先核对并填写 SSH 主机公钥 SHA-256 指纹。")
    if not isinstance(password, str) or len(password) > 4096 or "\x00" in password:
        raise AppError("SSH 密码格式无效。")
    if not password and not previous:
        raise AppError("请填写 SSH 密码。")
    return {"host": host.lower(), "port": port, "username": username, "hostKey": fingerprint, "password": password}


def validate_remote_path(path):
    if (not isinstance(path, str) or len(path) > 2048 or not path.startswith("/")
            or any(part in {"", ".", ".."} for part in path[1:].split("/"))
            or any(ord(char) < 32 for char in path)):
        raise AppError("远程路径须为不含 .、.. 的绝对 POSIX 路径。")
    return path


def key_fingerprint(key):
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode("ascii").rstrip("=")


def _transport(host, port, fingerprint=None, password=None, username=None):
    transport, sock = None, None
    try:
        sock = socket.create_connection((host, port), timeout=10)
        transport = paramiko.Transport(sock)
        transport.start_client(timeout=15)
        actual = key_fingerprint(transport.get_remote_server_key())
        if fingerprint is not None and actual != fingerprint:
            raise AppError("SSH 主机公钥指纹与已授权配置不符，已在发送密码前中止。", 403)
        if password is not None:
            transport.auth_password(username, password, fallback=False)
            if not transport.is_authenticated():
                raise AppError("SSH 认证失败。", 403)
        return transport, actual
    except Exception as exc:
        if transport:
            transport.close()
        elif sock:
            sock.close()
        if isinstance(exc, AppError):
            raise
        if isinstance(exc, paramiko.AuthenticationException):
            raise AppError("SSH 密码认证失败。", 403) from exc
        if isinstance(exc, (OSError, EOFError, paramiko.SSHException)):
            raise AppError("SSH 连接失败；请检查主机、端口、网络和服务状态。") from exc
        raise


def probe_remote(host, port):
    validate_remote({"host": host, "port": port, "username": "probe", "hostKey": "SHA256:" + "A" * 43, "password": "probe"})
    transport, fingerprint = _transport(host, port)
    try:
        return {"host": host, "port": port, "hostKey": fingerprint, "algorithm": transport.get_remote_server_key().get_name()}
    finally:
        transport.close()


def run_remote(profile, password, command, stop=None, timeout_ms=120000):
    if not isinstance(command, str) or not command.strip() or len(command) > 12000 or "\x00" in command:
        raise AppError("远程命令须为不超过 12000 字符的非空文本。")
    if type(timeout_ms) is not int or not 1000 <= timeout_ms <= 300000:
        raise AppError("远程命令超时须为 1 至 300 秒。")
    if stop and stop.is_set():
        return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0}
    transport, _ = _transport(profile["host"], profile["port"], profile["hostKey"], password, profile["username"])
    try:
        if stop and stop.is_set():
            return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0}
        channel = transport.open_session(timeout=15)
        if stop and stop.is_set():
            return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0}
        channel.exec_command(command)
        deadline = time.monotonic() + timeout_ms / 1000
        output, byte_count, status = bytearray(), 0, ""
        while True:
            for ready, receive in ((channel.recv_ready, channel.recv), (channel.recv_stderr_ready, channel.recv_stderr)):
                if ready():
                    chunk = receive(8192)
                    byte_count += len(chunk)
                    output.extend(chunk)
                    del output[:-24000]
            if byte_count > 2 * 1024 * 1024:
                status = "output_limit"
                break
            if stop and stop.is_set():
                status = "interrupted"
                break
            if time.monotonic() >= deadline:
                status = "timed_out"
                break
            if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                break
            time.sleep(0.05)
        exit_code = channel.recv_exit_status() if not status else None
        channel.close()
        return {"status": status or ("passed" if exit_code == 0 else "failed"), "exitCode": exit_code,
                "output": output.decode("utf-8", "replace").replace(password, "[REDACTED]"),
                "bytes": byte_count, "truncated": byte_count > 24000}
    except (OSError, EOFError, paramiko.SSHException) as exc:
        raise AppError("SSH 命令执行失败；请检查远端服务与连接状态。") from exc
    finally:
        transport.close()


def upload_remote(profile, password, sources, remote_path, stop=None):
    validate_remote_path(remote_path)
    if not sources or len(sources) > 2000:
        raise AppError("一次最多上传 2000 个文件。")
    for _, relative in sources:
        if not isinstance(relative, str) or (relative and (relative.startswith("/")
                or any(part in {"", ".", ".."} for part in relative.split("/"))
                or any(ord(char) < 32 for char in relative))):
            raise AppError("上传文件的相对路径无效。")
    total_bytes = sum(path.stat().st_size for path, _ in sources)
    if total_bytes > 1024 * 1024 * 1024:
        raise AppError("一次上传总量不能超过 1 GB。")
    if stop and stop.is_set():
        return {"status": "interrupted", "files": 0, "bytes": 0}
    transport, _ = _transport(profile["host"], profile["port"], profile["hostKey"], password, profile["username"])
    sftp = None
    try:
        if stop and stop.is_set():
            return {"status": "interrupted", "files": 0, "bytes": 0}
        sftp = paramiko.SFTPClient.from_transport(transport)
        if stop and stop.is_set():
            return {"status": "interrupted", "files": 0, "bytes": 0}
        created, transferred, written = set(), 0, 0

        def ensure_directory(directory):
            if directory == "/" or directory in created:
                return
            ensure_directory(str(PurePosixPath(directory).parent))
            try:
                if not stat.S_ISDIR(sftp.stat(directory).st_mode):
                    raise AppError("远程目标路径不是目录。")
            except FileNotFoundError:
                sftp.mkdir(directory)
            created.add(directory)

        for local, relative in sources:
            if stop and stop.is_set():
                return {"status": "interrupted", "files": transferred, "bytes": written}
            target = str(PurePosixPath(remote_path) / relative) if relative else remote_path
            ensure_directory(str(PurePosixPath(target).parent))
            try:
                sftp.stat(target)
            except FileNotFoundError:
                pass
            else:
                raise AppError("远程目标已存在；请先备份并使用新的暂存路径。")
            temporary = target + ".shujin-uploading"
            owned = False
            try:
                remote_file = sftp.open(temporary, "wx")
                owned = True
                with remote_file, local.open("rb") as source:
                    while chunk := source.read(65536):
                        if stop and stop.is_set():
                            raise InterruptedError("任务已停止。")
                        written += len(chunk)
                        if written > 1024 * 1024 * 1024:
                            raise AppError("上传文件已超过 1 GB 上限。")
                        remote_file.write(chunk)
                    remote_file.flush()
                if stop and stop.is_set():
                    raise InterruptedError("任务已停止。")
                # Standard SFTP rename rejects an existing destination. Do not use posix_rename.
                try:
                    sftp.stat(target)
                except FileNotFoundError:
                    pass
                else:
                    raise AppError("远程目标已存在；请先备份并使用新的暂存路径。")
                sftp.rename(temporary, target)
                owned = False
            except InterruptedError:
                return {"status": "interrupted", "files": transferred, "bytes": written}
            finally:
                if owned:
                    try:
                        sftp.remove(temporary)
                    except OSError:
                        pass
            transferred += 1
        return {"status": "passed", "files": transferred, "bytes": written, "remotePath": remote_path}
    except (OSError, EOFError, paramiko.SSHException) as exc:
        raise AppError("SFTP 上传失败；请检查远端路径、权限和连接状态。") from exc
    finally:
        if sftp:
            sftp.close()
        transport.close()
