import copy

import httpx
import pytest

from backend.common import AppError
from backend.workspace import Workspace


async def test_archive_retains_history_across_restart_and_requires_restore(workspace):
    w, _, provider, session = workspace
    session["messages"] = [{"role": "user", "content": "保留这份对话"}]
    session["history"] = copy.deepcopy(session["messages"])
    w.archive_session(session["id"], True)
    timestamp = session["archivedAt"]
    assert timestamp and w.state()["sessions"][0]["archivedAt"] == timestamp
    with pytest.raises(AppError, match="恢复"):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "修复"})
    with pytest.raises(AppError, match="恢复"):
        await w.resume_run(session["id"])
    restored = Workspace(w.data_dir, model_client=w.model_client)
    try:
        archived = restored.session(session["id"])
        assert archived["archivedAt"] == timestamp
        assert archived["messages"] == session["messages"]
        assert archived["history"] == session["history"]
        result = restored.archive_session(session["id"], False)
        assert result["archivedAt"] is None and result["messages"] == session["messages"]
    finally:
        await restored.shutdown()


async def test_archive_rejects_active_work_without_losing_state(workspace):
    w, _, _, session = workspace
    for status, changes, commands in [
        ("running", [], []),
        ("review", [{"status": "pending"}], []),
        ("waiting", [], [{"status": "pending_approval"}]),
        ("stopped", [], [{"status": "running"}]),
    ]:
        session.update(status=status, changes=changes, commands=commands)
        before = copy.deepcopy(session)
        with pytest.raises(AppError, match="审核"):
            w.archive_session(session["id"], True)
        assert session == before
    session.update(status="idle", changes=[], commands=[])


async def test_archive_restore_api_supports_legacy_sessions(live_server, workspace):
    w, _, _, session = workspace
    _, origin = live_server
    assert "archivedAt" not in session
    async with httpx.AsyncClient(base_url=origin, trust_env=False) as client:
        path = "/api/dev/sessions/" + session["id"]
        archived = await client.post(path + "/archive", json={})
        assert archived.status_code == 200 and archived.json()["archivedAt"]
        state = (await client.get("/api/dev/state")).json()
        assert state["sessions"][0]["archivedAt"]
        restored = await client.post(path + "/restore", json={})
        assert restored.status_code == 200 and restored.json()["archivedAt"] is None
        assert (await client.post("/api/dev/sessions/missing/archive", json={})).status_code == 404
