"""One-shot password SSH using the running account's known_hosts file."""
from pathlib import Path
import time

import paramiko


def known_hosts_path():
    path = Path.home() / ".ssh" / "known_hosts"
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    return path


def run_password_ssh(port, target, remote_command, password, stop, timeout_ms):
    started = time.monotonic()
    if stop and stop.is_set():
        return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0}
    username, host = target.split("@", 1)
    client = paramiko.SSHClient()
    output, byte_count, status, exit_code = bytearray(), 0, "", None
    try:
        client.load_host_keys(str(known_hosts_path()))
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_timeout = min(10, max(0.1, timeout_ms / 1000))
        client.connect(host, port=port, username=username, password=password,
                       allow_agent=False, look_for_keys=False, timeout=connect_timeout,
                       auth_timeout=connect_timeout, banner_timeout=connect_timeout)
        if stop and stop.is_set():
            status = "interrupted"
        else:
            channel = client.get_transport().open_session(timeout=10)
            try:
                if stop and stop.is_set():
                    status = "interrupted"
                else:
                    channel.exec_command(remote_command)
                    deadline = started + timeout_ms / 1000
                    while True:
                        for ready, receive in ((channel.recv_ready, channel.recv),
                                               (channel.recv_stderr_ready, channel.recv_stderr)):
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
                            exit_code = channel.recv_exit_status()
                            break
                        time.sleep(0.05)
            finally:
                channel.close()
        status = status or ("passed" if exit_code == 0 else "failed")
        error = ""
    except paramiko.BadHostKeyException:
        status, error = "failed", "SSH 主机密钥已变化，连接已拒绝。"
    except paramiko.AuthenticationException:
        status, error = "failed", "SSH 密码认证失败。"
    except (OSError, EOFError, paramiko.SSHException):
        status, error = "failed", "SSH 连接或远程执行失败。"
    finally:
        client.close()
    return {"status": status, "exitCode": exit_code, "output": output.decode("utf-8", "replace").replace(password, "[REDACTED]"),
            "bytes": byte_count, "error": error}
