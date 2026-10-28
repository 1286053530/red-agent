import copy
import json
from pathlib import Path

import pytest

from backend.common import AppError
from backend.runtime import child_environment
from backend.workspace import Workspace
from conftest import prepare, settle


@pytest.mark.parametrize('permissions', [[], True, {'edits': 'true'}, {'commands': 1}, {'network': True}, {'directories': ['..']}])
async def test_invalid_permission_grants_leave_session_unchanged(workspace, permissions):
    w, _, provider, session = workspace
    before = copy.deepcopy(session)
    with pytest.raises(AppError, match='权限'):
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '修复代码', 'permissions': permissions})
    assert session == before


async def test_readonly_effective_grants_and_all_execution_entrypoints(workspace):
    w, project, provider, session = workspace
    await prepare(w, provider, session, kind='inspect', permissions={'edits': True, 'commands': True})
    assert session['task']['permissions'] == {'edits': False, 'commands': False}
    task_id = session['task']['id']
    command = {'id': 'forged', 'taskId': task_id, 'command': 'node', 'args': ['--test'], 'status': 'pending_approval'}
    change = {'id': 'forged', 'taskId': task_id, 'path': 'app.mjs', 'status': 'pending', 'content': 'unwanted'}
    session['commands'].append(command)
    session['changes'].append(change)
    with pytest.raises(AppError, match='只读'):
        w.queue_command(session, {'command': 'node', 'args': ['--test'], 'purpose': 'forged'})
    with pytest.raises(AppError, match='只读'):
        w.launch_command(session, command)
    with pytest.raises(AppError, match='只读'):
        await w.command_decision(session['id'], command['id'], 'approve')
    with pytest.raises(AppError, match='只读'):
        await w.apply_change(session['id'], change['id'], 'apply')
    assert not w.executions and command['status'] == 'pending_approval'
    assert 'unwanted' not in (Path(project['path']) / 'app.mjs').read_text()


async def test_approval_is_bound_to_task_and_cannot_be_bypassed(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    command = await w.execute(session, 'run_command', {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': 'test'})
    with pytest.raises(AppError, match='批准'):
        w.launch_command(session, command)
    command['taskId'] = 'another-task'
    with pytest.raises(AppError, match='其他任务'):
        await w.command_decision(session['id'], command['id'], 'approve')
    assert command['status'] == 'pending_approval' and not w.executions


async def test_approval_revalidates_command_shape_and_paths(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    command = await w.execute(session, 'run_command', {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': 'test'})
    for executable, args in [('cmd', ['/c', 'whoami']), ('node', ['--test', '../outside.mjs']), ('python', ['-m', 'py_compile', '.env'])]:
        command.update(command=executable, args=args)
        with pytest.raises(AppError):
            await w.command_decision(session['id'], command['id'], 'approve')
    assert not w.executions and command['status'] == 'pending_approval'


@pytest.mark.parametrize('name', ['.env', '.env.local', '.npmrc', '.git-credentials', '.pypirc', 'id_rsa', 'secret.key', '.kube/config', '.docker/config.json'])
async def test_sensitive_paths_are_hidden_and_denied_everywhere(workspace, name):
    w, project, provider, session = workspace
    target = Path(project['path']) / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('PRIVATE_TEST_MARKER', encoding='utf-8')
    await prepare(w, provider, session, permissions={'edits': True, 'commands': True})
    assert name not in w.files(project)
    assert not w.search_page(project, {'query': 'PRIVATE_TEST_MARKER'})['matches']
    for tool, args in [('read_file', {'path': name}), ('propose_file', {'path': name, 'content': 'replacement'}), ('run_command', {'command': 'python', 'args': ['-m', 'py_compile', name], 'purpose': 'forged'})]:
        with pytest.raises(AppError):
            await w.execute(session, tool, args)
    assert target.read_text(encoding='utf-8') == 'PRIVATE_TEST_MARKER'


async def test_internal_data_and_sensitive_project_roots_are_not_importable(workspace):
    w, project, _, _ = workspace
    for root in [w.data_dir, Path(project['path']) / '.ssh']:
        root.mkdir(parents=True, exist_ok=True)
        with pytest.raises(AppError, match='导入'):
            w.import_project(str(root))
    # Importing the parent must not expose key/workspace.json through file tools.
    parent = w.import_project(str(w.data_dir.parent))
    assert not any(entry['path'] == 'data' for entry in w.list_page(parent, {})['entries'])
    assert not any(path.startswith('data/') for path in w.files(parent))
    with pytest.raises(AppError, match='数据目录'):
        w.read_source(parent, 'data/key')


async def test_model_destination_and_root_are_pinned_across_resume(workspace):
    w, project, provider, session = workspace
    await prepare(w, provider, session)
    scope = copy.deepcopy(session['task']['accessScope'])
    assert scope['model']['baseUrl'] == provider['baseUrl'] and scope['root'] == project['path']
    actual_provider = w.data['providers'][0]
    actual_provider['baseUrl'] = 'https://changed.example/v1'
    with pytest.raises(AppError, match='发送范围'):
        await w.resume_run(session['id'])
    actual_provider['baseUrl'] = provider['baseUrl']
    project['path'] = str(Path(project['path']).parent)
    with pytest.raises(AppError, match='授权目录'):
        await w.execute(session, 'read_file', {'path': 'README.md'})
    assert session['task']['accessScope'] == scope


async def test_access_policy_and_scope_are_public_without_credentials(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    policy = w.state()['accessPolicy']
    assert all(policy[key] for key in ('directories', 'commands', 'network', 'sensitive', 'process'))
    assert '未隔离' in policy['network'] and '本机账号' in policy['process']
    public = w.public_session(session)
    assert 'fixture-secret' not in json.dumps(public)
    loaded = Workspace(w.data_dir)
    assert loaded.session(session['id'])['task']['accessScope'] == public['task']['accessScope']
    await loaded.shutdown()


async def test_npm_approval_includes_lifecycle_scripts(workspace):
    w, project, provider, session = workspace
    package = Path(project['path']) / 'package.json'
    data = json.loads(package.read_text())
    data['scripts'].update(pretest='node before.mjs', posttest='node after.mjs')
    package.write_text(json.dumps(data), encoding='utf-8')
    await prepare(w, provider, session)
    command = await w.execute(session, 'run_command', {'command': 'npm', 'args': ['test'], 'purpose': 'test'})
    assert command['script'].splitlines() == ['pretest: node before.mjs', 'test: node --test app.test.mjs', 'posttest: node after.mjs']


def test_project_process_does_not_inherit_backend_secrets(monkeypatch):
    for name in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'AWS_SECRET_ACCESS_KEY', 'NPM_TOKEN', 'PYTHONPATH', 'NODE_OPTIONS', 'HTTP_PROXY']:
        monkeypatch.setenv(name, 'sensitive')
    env = child_environment()
    assert not any(value == 'sensitive' for value in env.values())


async def test_legacy_readonly_resume_cannot_escalate_grants(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session, kind='inspect')
    session['task'].pop('accessScope')
    session['task']['permissions'] = {'edits': True, 'commands': True}
    w.save()
    loaded = Workspace(w.data_dir, model_client=w.model_client,
                       intent_classifier=lambda _: {"type": "development"})
    try:
        restored = loaded.session(session['id'])
        assert restored['task']['permissions'] == {'edits': False, 'commands': False}
        await loaded.resume_run(session['id'], {'permissions': {'edits': True, 'commands': True}, 'kind': 'change'})
        await settle(loaded)
        assert restored['task']['permissions'] == {'edits': False, 'commands': False}
        assert restored['task']['kind'] == 'inspect'
        assert restored['task']['accessScope']['model']['baseUrl'] == provider['baseUrl']
    finally:
        await loaded.shutdown()


@pytest.mark.parametrize('status', ['running', 'passed', 'denied'])
async def test_approved_command_cannot_be_launched_again(workspace, status):
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    command = await w.execute(session, 'run_command', {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': 'test'})
    command.update(approved=True, status=status)
    with pytest.raises(AppError, match='重复执行'):
        w.launch_command(session, command)
    assert not w.executions
