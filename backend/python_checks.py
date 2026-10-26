"""Python command policy and project interpreter selection (not an OS sandbox)."""
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import sys

from .common import AppError


def _path(value, selectors=False):
    path = value.split("::", 1)[0] if selectors else value
    if path == ".":
        return path
    if (not path or Path(path).is_absolute() or PureWindowsPath(path).drive
            or re.search(r'[\x00-\x1f:*?"<>|]', path)
            or any(p in {"", ".", ".."} for p in path.replace("\\", "/").split("/"))):
        raise AppError("Python 检查请使用项目内的相对路径，不接受外部路径或通配路径。")
    return path


def python_check(args):
    """Return the check kind and path arguments; reject interpreter/module escapes."""
    paths = []
    if len(args) >= 2 and args[:2] == ["-m", "pytest"]:
        rest, index = args[2:], 0
        flags = {"-q", "-qq", "-v", "-vv", "-s", "-x", "--exitfirst", "--disable-warnings",
                 "--strict-markers", "--strict-config", "--collect-only", "--co"}
        while index < len(rest):
            arg = rest[index]
            if arg in {"-k", "-m"}:
                index += 1
                if index >= len(rest) or not rest[index].strip():
                    raise AppError("pytest 筛选参数缺少表达式。")
            elif arg in {"-c", "--ignore"}:
                index += 1
                if index >= len(rest):
                    raise AppError("pytest 参数缺少项目内路径。")
                paths.append(_path(rest[index]))
            elif arg in flags or re.fullmatch(r"--(?:tb=(?:auto|long|short|line|native|no)|maxfail=[1-9][0-9]*)", arg):
                pass
            elif arg.startswith("-"):
                raise AppError("不支持此 pytest 参数；可用相对测试路径、-q/-v/-x、-k/-m、-c、--ignore、--tb、--maxfail。")
            else:
                paths.append(_path(arg, selectors=True))
            index += 1
        return "pytest", paths
    if len(args) >= 3 and args[:3] == ["-m", "unittest", "discover"]:
        rest, index = args[3:], 0
        while index < len(rest):
            arg = rest[index]
            if arg in {"-s", "-t", "-p"}:
                index += 1
                if index >= len(rest):
                    raise AppError("unittest discover 参数缺少值。")
                if arg == "-p":
                    if not re.fullmatch(r"[\w.*?\[\]-]+\.py", rest[index]):
                        raise AppError("unittest 测试模式须为 Python 文件名模式。")
                else:
                    paths.append(_path(rest[index]))
            elif arg not in {"-v", "-q", "-f", "-b"}:
                raise AppError("仅支持 unittest discover 及 -s/-t/-p/-v/-q/-f/-b 参数。")
            index += 1
        return "unittest", paths
    if len(args) >= 3 and args[:2] == ["-m", "py_compile"]:
        if all(arg.endswith(".py") and not arg.startswith("-") for arg in args[2:]):
            return "syntax", [_path(arg) for arg in args[2:]]
        return _invalid()
    if args and not args[0].startswith("-") and args[0].endswith(".py"):
        return "script", [_path(args[0])]
    return _invalid()


def _invalid():
    raise AppError("仅支持 python -m pytest、python -m unittest discover、python -m py_compile 文件或 python 项目脚本.py [参数]。")


def python_environment(cwd):
    root = Path(cwd)
    for name in (".venv", "venv"):
        folder = root / name
        if folder.exists():
            candidate = folder / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            if not candidate.is_file():
                raise AppError(f"项目 {name} 缺少 Python 解释器，请修复虚拟环境；不会回退到其他环境。")
            # Do not resolve POSIX venv symlinks: their path selects the environment.
            return {"executable": str(candidate.absolute()), "source": name}
    configured = os.environ.get("SHUJIN_PROJECT_PYTHON")
    if configured:
        if not Path(configured).is_absolute() or not Path(configured).is_file():
            raise AppError("SHUJIN_PROJECT_PYTHON 须为已安装 Python 解释器的绝对路径。")
        return {"executable": configured, "source": "SHUJIN_PROJECT_PYTHON"}
    if not getattr(sys, "frozen", False):
        return {"executable": sys.executable, "source": "backend-python"}
    for name in ("python", "python3") if os.name == "nt" else ("python3", "python"):
        executable = shutil.which(name)
        if executable and Path(executable).resolve() != Path(sys.executable).resolve():
            return {"executable": executable, "source": "PATH"}
    raise AppError("没有找到项目 Python。请准备 .venv/venv、安装本机 Python，或设置 SHUJIN_PROJECT_PYTHON；应用内置后端不能代替项目解释器。")


def is_behavior_check(command, args):
    return (command == "node" and args[:1] == ["--test"]
            or command == "npm" and args in [["test"], ["run", "test"]]
            or command == "python" and python_check(args)[0] in {"pytest", "unittest"})
