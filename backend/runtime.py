"""Supervised checks. A command allowlist is not an operating-system sandbox."""
import asyncio
import codecs
import json
import os
from pathlib import Path
import re
import shutil
import signal
import tempfile
import threading
import time

from .common import AppError, now
from .python_checks import python_check, python_environment

CHECK_SCRIPTS = {"test", "build", "lint", "typecheck", "check"}
REPORTER = Path(__file__).with_name("agent-test-reporter.mjs")
PYTHON_RUNNER = Path(__file__).with_name("agent-python-runner.py")
SSH_TARGET = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}@[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")


def ssh_parts(args):
    if not isinstance(args, list):
        raise AppError("SSH 参数须为目标和远程命令。")
    if len(args) not in {2, 4} or any(not isinstance(arg, str) for arg in args):
        raise AppError("SSH 仅支持 [-p 端口] 用户@主机 远程命令。")
    if len(args) == 2:
        port, target, remote_command = 22, *args
    elif len(args) == 4 and args[0] == "-p" and args[1].isdigit():
        port, target, remote_command = int(args[1]), args[2], args[3]
    else:
        raise AppError("SSH 仅支持 [-p 端口] 用户@主机 远程命令。")
    host = target.partition("@")[2]
    if (not 1 <= port <= 65535 or not SSH_TARGET.fullmatch(target)
            or ".." in host or host.endswith(".") or not remote_command.strip()
            or len(remote_command) > 12000 or re.search(r"[\x00-\x1f]", remote_command)):
        raise AppError("SSH 目标、端口或远程命令无效。")
    return port, target, remote_command


def validate_command(command, args):
    if command == "ssh":
        ssh_parts(args)
        return
    if not isinstance(args, list) or len(args) > 30 or any(
        not isinstance(a, str) or len(a) > 500 or re.search(r"[\x00-\x1f]", a) for a in args
    ):
        raise AppError("命令参数格式无效。")
    if command == "node" and args and args[0] in {"--test", "--check"}:
        if (args[0] != "--check" or len(args) == 2) and all(not a.startswith("-") for a in args[1:]):
            return
    if command == "npm" and (args == ["test"] or len(args) == 2 and args[0] == "run" and args[1] in CHECK_SCRIPTS):
        return
    if command == "python":
        python_check(args)
        return
    raise AppError("仅支持受控的 Node/npm/Python 项目检查和 SSH 远程命令；不支持 shell 或依赖安装。")


def bounded_history(history, max_chars=42000):
    groups = []
    for message in history:
        if message.get("role") != "tool" or not groups:
            groups.append([])
        groups[-1].append(message)
    kept, size = [], 0
    for group in reversed(groups):
        length = len(json.dumps(group, ensure_ascii=False))
        if size + length > max_chars:
            # A new tool result must reach the next model request at least once.
            # Batched calls can exceed the target even though each page is bounded.
            # Keep that complete latest turn; the provider can reject an oversized
            # request explicitly, instead of silently claiming its source was read.
            if not kept:
                kept = group
            break
        kept[0:0] = group
        size += length
    # Images are small references here, not Base64. Keep their original user
    # messages when older text/tool turns are compacted so visual evidence is
    # still available on later rounds and after a restart.
    discarded = history[:len(history) - len(kept)]
    return [message for message in discarded if message.get("images")] + kept


def child_environment():
    allowed = {
        "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "HOME",
        "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "LANG", "LC_ALL",
    }
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    env.update(CI="1", NO_COLOR="1")
    # PyInstaller modifies DLL lookup paths; never leak its own bundled libraries to project processes.
    if "LD_LIBRARY_PATH_ORIG" in os.environ:
        env["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH_ORIG"]
    return env


def node_executable():
    executable = os.environ.get("SHUJIN_NODE_EXEC") or shutil.which("node")
    if not executable:
        raise AppError("没有找到 Node.js。请安装 Node.js 22+ 后运行项目检查。")
    return executable


def command_argv(command, args, env, cwd=None, report=None):
    if command == "ssh":
        executable = shutil.which("ssh")
        if not executable:
            raise AppError("运行环境未找到 OpenSSH 客户端。")
        port, target, remote_command = ssh_parts(args)
        if os.environ.get("SSH_AUTH_SOCK"):
            env["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
        return [executable, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=10", "-p", str(port), target, remote_command]
    if command == "python":
        environment = python_environment(cwd)
        executable = environment["executable"]
        env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        if report:
            # Never validate stale, same-size/same-second bytecode from a prior run.
            # Keep project caches untouched and remove our private cache on exit.
            env["PYTHONPYCACHEPREFIX"] = str(Path(report).parent / "pycache")
            env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PATH"] = str(Path(executable).parent) + os.pathsep + env.get("PATH", "")
        if environment["source"] in {".venv", "venv"}:
            env["VIRTUAL_ENV"] = str(Path(cwd) / environment["source"])
        kind, _ = python_check(args)
        if kind in {"pytest", "unittest"}:
            return [executable, str(PYTHON_RUNNER), str(report), kind, *args[2:]]
        return [executable, *args]
    node = node_executable()
    if os.environ.get("SHUJIN_NODE_IS_ELECTRON") == "1":
        env["ELECTRON_RUN_AS_NODE"] = "1"
    if command == "node":
        if args[0] == "--test":
            return [node, "--test", "--test-reporter=" + REPORTER.as_uri(), *args[1:]]
        return [node, *args]
    locations = [Path(shutil.which("node") or node).parent]
    locations.extend(Path(p) for p in os.get_exec_path())
    for location in locations:
        cli = location / "node_modules/npm/bin/npm-cli.js"
        if cli.is_file():
            return [node, str(cli), *args]
    raise AppError("没有找到本机 npm。可使用 node --test，或安装 Node.js / npm。")


async def kill_tree(process):
    if process.returncode is not None:
        return
    if os.name == "nt":
        killer = await asyncio.create_subprocess_exec(
            "taskkill.exe", "/PID", str(process.pid), "/T", "/F",
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
            creationflags=0x08000000,
        )
        await killer.wait()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.returncode is None:
        try:
            process.kill()
        except ProcessLookupError:
            pass


async def run_process(command, args, cwd, stop=None, timeout_ms=60000, on_output=None, ssh_password=None):
    validate_command(command, args)
    started = time.monotonic()
    timeout_ms = min(120000, max(100, int(timeout_ms)))
    if ssh_password is not None:
        if command != "ssh" or not isinstance(ssh_password, str) or not ssh_password or len(ssh_password) > 4096:
            raise AppError("SSH 密码参数无效。")
        from .ssh_runtime import run_password_ssh
        password_stop = threading.Event()
        worker = asyncio.create_task(asyncio.to_thread(run_password_ssh, *ssh_parts(args), ssh_password, password_stop, timeout_ms))
        interrupted = asyncio.create_task((stop or asyncio.Event()).wait())
        try:
            done, _ = await asyncio.wait([worker, interrupted], timeout=timeout_ms / 1000, return_when=asyncio.FIRST_COMPLETED)
            if worker in done:
                result = await worker
            else:
                password_stop.set()
                worker.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
                result = {"status": "interrupted" if interrupted in done else "timed_out", "exitCode": None,
                          "output": "", "bytes": 0}
        except asyncio.CancelledError:
            password_stop.set()
            worker.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
            raise
        finally:
            interrupted.cancel()
            await asyncio.gather(interrupted, return_exceptions=True)
        return {**result, "passedTests": None, "signal": None, "error": result.get("error", ""),
                "truncated": result.get("bytes", 0) > 24000,
                "durationMs": round((time.monotonic() - started) * 1000), "finishedAt": now()}
    env = child_environment()
    output, byte_count, passed_tests = "", 0, None
    status, error, process = "", "", None
    reason = asyncio.Event()
    evidence_dir = tempfile.TemporaryDirectory(prefix="shujin-check-") if command == "python" else None
    report = Path(evidence_dir.name) / "evidence.json" if evidence_dir else None

    async def consume(stream):
        nonlocal output, byte_count, status
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        while True:
            chunk = await stream.read(8192)
            if not chunk:
                output = (output + decoder.decode(b"", final=True))[-24000:]
                break
            byte_count += len(chunk)
            output = (output + decoder.decode(chunk))[-24000:]
            if on_output:
                on_output({"output": output, "bytes": byte_count, "truncated": byte_count > 24000})
            if byte_count > 2 * 1024 * 1024 and not reason.is_set():
                status = "output_limit"
                reason.set()

    if stop and stop.is_set():
        if evidence_dir:
            evidence_dir.cleanup()
        return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0,
                "passedTests": None, "truncated": False, "error": "执行前任务已停止。", "finishedAt": now(), "durationMs": 0}
    try:
        argv = command_argv(command, args, env, cwd, report)
        kwargs = {"creationflags": 0x08000000} if os.name == "nt" else {"start_new_session": True}
        process = await asyncio.create_subprocess_exec(
            *argv, cwd=str(cwd), env=env, stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs,
        )
        readers = [asyncio.create_task(consume(process.stdout)), asyncio.create_task(consume(process.stderr))]
        closed = asyncio.create_task(process.wait())
        interrupted = asyncio.create_task((stop or asyncio.Event()).wait())
        exceeded = asyncio.create_task(reason.wait())
        waiters = [closed, interrupted, exceeded]
        try:
            done, _ = await asyncio.wait(waiters, timeout=timeout_ms / 1000, return_when=asyncio.FIRST_COMPLETED)
            if closed not in done:
                status = status or ("interrupted" if interrupted in done else "timed_out")
                await kill_tree(process)
            await closed
            await asyncio.gather(*readers)
        except asyncio.CancelledError:
            await kill_tree(process)
            await asyncio.gather(closed, *readers, return_exceptions=True)
            raise
        finally:
            for waiter in waiters:
                if not waiter.done():
                    waiter.cancel()
            await asyncio.gather(*waiters, return_exceptions=True)
        status = status or ("passed" if process.returncode == 0 else "failed")
        evidence = re.findall(r"SHUJIN_TEST_EVIDENCE (\{[^\n]+\})", output) if command != "python" else []
        if evidence:
            try:
                value = json.loads(evidence[-1]).get("passed")
                if type(value) is int and value >= 0:
                    passed_tests = value
            except ValueError:
                pass
        if report and report.is_file():
            try:
                value = json.loads(report.read_text(encoding="utf-8")).get("passed")
                if type(value) is int and value >= 0:
                    passed_tests = value
            except (ValueError, OSError, AttributeError):
                pass
    except (OSError, AppError) as exc:
        status, error = "spawn_error", str(exc)
    finally:
        if evidence_dir:
            evidence_dir.cleanup()
    return {"status": status, "exitCode": process.returncode if process else None, "signal": None,
            "error": error, "output": output, "passedTests": passed_tests, "bytes": byte_count,
            "truncated": byte_count > 24000, "durationMs": round((time.monotonic() - started) * 1000), "finishedAt": now()}
