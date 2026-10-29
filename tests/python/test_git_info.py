from pathlib import Path

from backend.git_info import current_branch
from backend.workspace import Workspace
from conftest import prepare


def test_current_branch_returns_none_for_non_git_directory(tmp_path):
    assert current_branch(tmp_path) is None


async def test_import_and_task_capture_current_git_branch(workspace, monkeypatch):
    w, project, provider, session = workspace
    monkeypatch.setattr("backend.workspace.current_branch", lambda path: "release/2026-10")
    project = w.import_project(str(Path(project["path"])))
    assert project["gitBranch"] == "release/2026-10"
    state = w.state()
    assert state["projects"][0]["gitBranch"] == "release/2026-10"
    monkeypatch.setattr("backend.workspace.current_branch", lambda path: "feature/latest")
    await prepare(w, provider, session, permissions={"commands": False})
    await w.execute(session, "update_plan", {"summary": "分支", "criteria": "记录当前分支", "next_action": "读取"})
    assert session["task"]["accessScope"]["gitBranch"] == "feature/latest"
