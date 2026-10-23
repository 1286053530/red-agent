import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DevWorkspace, callModel } from '../dev-agent.mjs';

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), 'guanshu-dev-'));
  const project = join(root, 'project');
  const data = join(root, 'data');
  await mkdir(project, { recursive: true });
  await writeFile(join(project, 'app.js'), 'export const answer = 1;\n');
  return { root, project, data };
}

test('developer workspace isolates project files and never exposes provider secrets', async t => {
  const f = await fixture();
  t.after(() => rm(f.root, { recursive: true, force: true }));
  const workspace = new DevWorkspace({ dataDir: f.data, fetcher: async () => ({ ok: true, json: async () => ({ choices: [{ message: { role: 'assistant', content: 'OK' } }] }) }) });
  await workspace.ready;
  const project = await workspace.importProject(f.project);
  const provider = await workspace.saveProvider({ name: '本地测试', protocol: 'compatible', baseUrl: 'https://example.com/v1', model: 'test-model', apiKey: 'secret-key' });
  assert.equal(provider.hasKey, true);
  assert.equal(JSON.stringify(await workspace.state()).includes('secret-key'), false);
  const files = await workspace.files(project);
  assert.deepEqual(files, ['app.js']);
  await assert.rejects(() => workspace.readSource(project, '../outside.txt'), /不在可访问的源码范围/);
});

test('provider encryption survives reload and protected files are excluded', async t => {
  const f = await fixture(); t.after(() => rm(f.root, { recursive: true, force: true }));
  const workspace = new DevWorkspace({ dataDir: f.data }); await workspace.ready;
  const project = await workspace.importProject(f.project);
  await writeFile(join(f.project, '.env'), 'SECRET=private');
  await mkdir(join(f.project, '.GIT')); await writeFile(join(f.project, '.GIT', 'config'), 'private');
  const provider = await workspace.saveProvider({ name: 'Example', protocol: 'compatible', baseUrl: 'https://example.com/v1', model: 'test', apiKey: 'encrypted-secret' });
  assert.equal((await readFile(join(f.data, 'workspace.json'), 'utf8')).includes('encrypted-secret'), false);
  const reloaded = new DevWorkspace({ dataDir: f.data }); await reloaded.ready;
  await reloaded.saveProvider({ ...provider, name: 'Renamed', apiKey: '' });
  assert.equal(reloaded.decrypt(reloaded.data.providers[0].secret), 'encrypted-secret');
  assert.deepEqual(await reloaded.files(project), ['app.js']);
  for (const path of ['.env', '.GIT/config', 'nested/../app.js', 'secret.key']) await assert.rejects(() => reloaded.readSource(project, path));
});

test('model tool loop reads, proposes and applies only after review', async t => {
  const f = await fixture(); t.after(() => rm(f.root, { recursive: true, force: true }));
  let calls = 0;
  const toolCall = (name, args) => ({ id: 'call_' + calls, type: 'function', function: { name, arguments: JSON.stringify(args) } });
  const workspace = new DevWorkspace({ dataDir: f.data, fetcher: async (url, request) => {
    const body = JSON.parse(request.body); calls++;
    assert.equal(request.headers.Authorization, 'Bearer test-key');
    assert.equal(body.model, 'test-model');
    const message = calls === 1 ? { tool_calls: [toolCall('read_file', { path: 'app.js' })] } : calls === 2 ? { tool_calls: [toolCall('propose_file', { path: 'app.js', content: 'export const answer = 2;\n', reason: '更新值' })] } : { content: '已提出修改，请审核。' };
    return { ok: true, json: async () => ({ choices: [{ message }] }) };
  } });
  await workspace.ready; const project = await workspace.importProject(f.project);
  const provider = await workspace.saveProvider({ name: 'Test', protocol: 'compatible', baseUrl: 'https://example.com/v1', model: 'test-model', apiKey: 'test-key' });
  const session = await workspace.createSession({ projectId: project.id });
  await workspace.startRun(session.id, { providerId: provider.id, message: '更新示例值' });
  await Promise.all([...workspace.runTasks]);
  assert.equal(calls, 2); assert.equal(workspace.session(session.id).status, 'review');
  assert.equal(await readFile(join(f.project, 'app.js'), 'utf8'), 'export const answer = 1;\n');
  const change = workspace.session(session.id).changes[0];
  assert.equal(workspace.publicSession(workspace.session(session.id)).changes[0].original, 'export const answer = 1;\n');
  await workspace.applyChange(session.id, change.id, 'apply');
  await Promise.all([...workspace.runTasks]);
  assert.notEqual(workspace.session(session.id).status, 'completed');
  assert.equal(await readFile(join(f.project, 'app.js'), 'utf8'), 'export const answer = 2;\n');
});

test('Anthropic adapter preserves tool calls and results', async () => {
  const result = await callModel({ protocol: 'anthropic', baseUrl: 'https://example.com/v1', model: 'test', apiKey: 'test' }, [
    { role: 'system', content: 'system' }, { role: 'user', content: 'inspect' },
    { role: 'assistant', content: '', tool_calls: [{ id: 'one', function: { name: 'list_files', arguments: '{}' } }] },
    { role: 'tool', tool_call_id: 'one', content: '{"files":[]}' }
  ], { fetcher: async (url, request) => {
    assert.equal(url, 'https://example.com/v1/messages');
    const body = JSON.parse(request.body);
    assert.equal(body.messages[1].content[0].type, 'tool_use');
    assert.equal(body.messages[2].content[0].tool_use_id, 'one');
    assert.equal(body.system, 'system');
    return { ok: true, json: async () => ({ content: [{ type: 'text', text: '完成' }] }) };
  } });
  assert.equal(result.content, '完成');
});

test('running project rejects another task and shutdown stops the model request', async t => {
  const f = await fixture(); t.after(() => rm(f.root, { recursive: true, force: true }));
  const workspace = new DevWorkspace({ dataDir: f.data, fetcher: async (_, { signal }) => new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new Error('aborted'));
    signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true });
  }) });
  await workspace.ready; const project = await workspace.importProject(f.project);
  const provider = await workspace.saveProvider({ name: 'Test', protocol: 'compatible', baseUrl: 'https://example.com/v1', model: 'test' });
  const first = await workspace.createSession({ projectId: project.id }), second = await workspace.createSession({ projectId: project.id });
  await workspace.startRun(first.id, { providerId: provider.id, message: 'test' });
  await assert.rejects(() => workspace.startRun(second.id, { providerId: provider.id, message: 'test' }), /正在执行/);
  await workspace.shutdown(); assert.equal(workspace.session(first.id).status, 'stopped');
  assert.equal(workspace.runs.size, 0);
});

test('developer changes stay pending until review and detect concurrent edits', async t => {
  const f = await fixture();
  t.after(() => rm(f.root, { recursive: true, force: true }));
  const workspace = new DevWorkspace({ dataDir: f.data });
  await workspace.ready;
  const project = await workspace.importProject(f.project);
  const session = await workspace.createSession({ projectId: project.id });
  await workspace.executeTool(workspace.session(session.id), {function:{name:'read_file',arguments:JSON.stringify({path:'app.js'})}});
  const proposal = await workspace.executeTool(workspace.session(session.id), { function: { name: 'propose_file', arguments: JSON.stringify({ path: 'app.js', content: 'export const answer = 2;\n', reason: '修正示例值' }) } }, new AbortController().signal);
  assert.equal(proposal.status, 'pending_review');
  assert.equal((await readFile(join(f.project, 'app.js'), 'utf8')).includes('2'), false);
  await writeFile(join(f.project, 'app.js'), 'export const answer = 3;\n');
  await assert.rejects(() => workspace.applyChange(session.id, workspace.session(session.id).changes[0].id, 'apply'), /文件已在其他地方修改/);
  const result = await workspace.applyChange(session.id, workspace.session(session.id).changes[0].id, 'discard');
  assert.equal(result.changes[0].status, 'discarded');
});
