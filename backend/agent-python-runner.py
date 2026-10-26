"""Run with the project's Python, never with the frozen application's executable.

Evidence is written separately from untrusted/truncated stdout. This runner is
bundled application data and deliberately has no backend or third-party imports
until the requested test framework is selected.
"""
import json
from pathlib import Path
import sys


def main():
    report, kind, *args = sys.argv[1:]
    passed = 0
    if kind == "pytest":
        try:
            import pytest
        except ImportError:
            print("项目 Python 环境缺少 pytest，请先为该环境安装项目测试依赖；Agent 不自动安装依赖。", file=sys.stderr)
            return 2

        class Evidence:
            def pytest_runtest_logreport(self, report):
                nonlocal passed
                if report.when == "call" and report.passed and not hasattr(report, "wasxfail"):
                    passed += 1

        sys.path.insert(0, str(Path.cwd()))
        code = int(pytest.main(args, plugins=[Evidence()]))
    else:
        import unittest

        class Evidence(unittest.TextTestResult):
            def addSuccess(self, test):
                nonlocal passed
                passed += 1
                super().addSuccess(test)

        sys.path.insert(0, str(Path.cwd()))
        class Runner(unittest.TextTestRunner):
            resultclass = Evidence

        program = unittest.main(module=None, argv=["unittest", *args], testRunner=Runner, exit=False)
        code = 0 if program.result.wasSuccessful() else 1
    Path(report).write_text(json.dumps({"passed": passed}), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
