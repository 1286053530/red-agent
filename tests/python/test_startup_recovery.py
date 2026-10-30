"""Restore historical command evidence without depending on every project file being readable."""
from pathlib import Path

import pytest

from backend.common import AppError
from backend.workspace import Workspace


def saved_command_evidence(w, project, session):
    fingerprint = w.fingerprint(project)
    session['task'] = {'id': 'restore-fixture', 'kind': 'change', 'checkpoint': {'evidence': [
        {'commandId': 'check-one', 'valid': True}, {'commandId': 'check-two', 'valid': True}
    ]}}
    session['commands'] = [{'id': command_id, 'status': 'passed', 'fingerprint': fingerprint}
                           for command_id in ('check-one', 'check-two')]
    w.save()
    return fingerprint


async def test_office_lock_file_never_read_during_restore_listing_search_or_fingerprint(workspace, monkeypatch):
    w, project, _, session = workspace
    fingerprint = saved_command_evidence(w, project, session)
    root = Path(project['path'])
    lock = root / 'docs' / '~$方案.xlsx'
    lock.parent.mkdir()
    lock.write_bytes(b'office lock')
    original_open = Path.open

    def locked_open(target, *args, **kwargs):
        if target == lock:
            raise PermissionError('Office denies sharing')
        return original_open(target, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', locked_open)
    restored = Workspace(w.data_dir)
    try:
        assert restored.fingerprint(project) == fingerprint
        assert not restored.list_page(project, {'path': 'docs'})['entries']
        assert not restored.search_page(project, {'query': 'office lock'})['skipped']
        with pytest.raises(AppError, match='源码范围'):
            restored.safe_path(project, 'docs/~$方案.xlsx')
        assert all(item['valid'] for item in restored.session(session['id'])['task']['checkpoint']['evidence'])
    finally:
        await restored.shutdown()


@pytest.mark.parametrize('error_type', [PermissionError, FileNotFoundError])
async def test_unreadable_project_file_invalidates_evidence_but_preserves_workspace(workspace, monkeypatch, error_type):
    w, project, _, session = workspace
    saved_command_evidence(w, project, session)
    blocked = Path(project['path']) / 'app.mjs'
    original_open = Path.open

    def blocked_open(target, *args, **kwargs):
        if target == blocked:
            raise error_type('project file unavailable')
        return original_open(target, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, 'open', blocked_open)
        restored = Workspace(w.data_dir)
        try:
            evidence = restored.session(session['id'])['task']['checkpoint']['evidence']
            assert all(not item['valid'] and item['validationError'] for item in evidence)
            assert restored.session(session['id'])['commands'] == session['commands']
            # Active verification must still fail rather than silently hash only readable files.
            with pytest.raises(error_type):
                restored.fingerprint(project)
        finally:
            await restored.shutdown()
    recovered = Workspace(w.data_dir)
    try:
        evidence = recovered.session(session['id'])['task']['checkpoint']['evidence']
        assert all(item['valid'] and 'validationError' not in item for item in evidence)
    finally:
        await recovered.shutdown()


@pytest.mark.parametrize('error_type', [PermissionError, AppError])
async def test_project_scan_failure_checked_once_and_keeps_other_sessions(workspace, monkeypatch, error_type):
    w, project, _, session = workspace
    saved_command_evidence(w, project, session)
    another = w.create_session({'projectId': project['id']})
    calls = []

    def unavailable(self, current):
        calls.append(current['id'])
        raise error_type('directory unavailable')

    monkeypatch.setattr(Workspace, 'fingerprint', unavailable)
    restored = Workspace(w.data_dir)
    try:
        assert calls == [project['id']]
        assert restored.session(another['id'])['status'] == 'idle'
        assert all(not item['valid'] for item in restored.session(session['id'])['task']['checkpoint']['evidence'])
    finally:
        await restored.shutdown()
