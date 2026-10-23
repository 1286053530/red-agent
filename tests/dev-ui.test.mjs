import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { chromium } from 'playwright';
import { DevWorkspace } from '../dev-agent.mjs';

test('developer UI imports projects, configures models, runs tools and reviews changes', async t => {
  const root = await mkdtemp(join(tmpdir(), 'dev-ui-')), projectPath = join(root, 'demo-app');
  await mkdir(projectPath); await writeFile(join(projectPath, 'app.js'), 'const value = 1;\n');
  await writeFile(join(projectPath, 'app.test.mjs'), "import {test} from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';test('updated value',()=>assert.match(readFileSync(new URL('./app.js',import.meta.url),'utf8'),/value = 2/));\n");
  const steps=[
    ['read_file',{path:'app.js'}],
    ['update_plan',{summary:'更新示例值',criteria:'示例值测试通过',next_action:'修改源码并测试'}],
    ['propose_file',{path:'app.js',content:'const value = 2;\n',reason:'更新值'}],
    ['run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'验证示例值与原测试'}],
    ['review_diff',{}],
    ['finish_task',{summary:'已更新示例值',evidence:'真实 Node 测试通过，退出码 0，最终变更已复核。'}]
  ];let round = 0;
  const workspace = new DevWorkspace({ dataDir: join(root, 'data'), fetcher: async () => {
    const [name,args]=steps[round++];
    const message={tool_calls:[{id:'ui-'+round,type:'function',function:{name,arguments:JSON.stringify(args)}}]};
    return { ok: true, json: async () => ({ choices: [{ message }] }) };
  } });
  await workspace.ready; workspace.pickFolder = async () => ({ path: projectPath });
  const server = createServer(async (request, response) => {
    const url = new URL(request.url, 'http://localhost');
    try {
      if (url.pathname.startsWith('/api/')) {
        const data = url.pathname.startsWith('/api/dev/') ? await workspace.handle(request, url.pathname, url) : { status: 'disconnected' };
        response.writeHead(200, { 'Content-Type': 'application/json' }); response.end(JSON.stringify(data)); return;
      }
      const file = url.pathname === '/' ? 'index.html' : url.pathname.slice(1);
      const body = await readFile(new URL('../' + file, import.meta.url));
      response.writeHead(200, { 'Content-Type': file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'text/html; charset=utf-8' }); response.end(body);
    } catch (error) { response.writeHead(error.status || 500, { 'Content-Type': 'application/json' }); response.end(JSON.stringify({ error: error.message })); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: process.env.XHS_BROWSER_CHANNEL || 'msedge', headless: true });
  t.after(async () => { await browser.close(); await workspace.shutdown(); await new Promise(resolve => server.close(resolve)); await rm(root, { recursive: true, force: true }); });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } }), errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/#account`, { waitUntil: 'domcontentloaded' });
  await page.locator('.breadcrumb-link').click(); await page.locator('#devImportButton').click();
  await page.locator('#devProjectSelect option', { hasText: 'demo-app' }).waitFor({ state: 'attached' });
  await page.locator('#devSettingsButton').click();
  await page.locator('#devProviderName').fill('测试厂商'); await page.locator('#devProviderUrl').fill('https://example.com/v1');
  await page.locator('#devProviderModel').fill('test-model'); await page.locator('#devProviderKey').fill('test-key');
  await page.locator('#devProviderSave').click(); await page.locator('[data-edit-provider]').waitFor();
  await page.locator('[data-edit-provider]').click(); await page.locator('#devAddProvider').click();
  assert.equal(await page.locator('#devProviderId').inputValue(), '');
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#devSendButton').isEnabled(), true);
  await page.locator('[data-file-path="app.js"]').click();
  await page.waitForFunction(() => document.querySelector('#devFilePreview').innerText.includes('value = 1'));
  assert.match(await page.locator('#devFilePreview').innerText(), /value = 1/);
  await page.locator('#devPrompt').fill('更新示例值'); await page.locator('#devSendButton').click();
  await page.locator('[data-change-action="apply"]').waitFor();
  assert.equal(await readFile(join(projectPath, 'app.js'), 'utf8'), 'const value = 1;\n');
  await page.locator('.dev-change-card summary').click(); assert.match(await page.locator('.dev-change-card').innerText(), /修改前/);
  await page.locator('[data-change-action="apply"]').click(); await page.waitForFunction(() => !document.querySelector('[data-change-action=apply]'));
  await page.locator('[data-command-action=approve]').waitFor();
  assert.equal(workspace.data.sessions[0].status,'waiting');
  assert.equal(workspace.data.sessions[0].commands[0].startedAt,undefined);
  await page.locator('[data-command-action=approve]').click();
  await page.locator('#devExecution').getByText('已验证完成',{exact:true}).waitFor();
  assert.equal(await page.locator('[data-change-action=revert]').count(), 1);
  await page.locator('#devExportLogs').click();
  assert.equal(await readFile(join(projectPath, 'app.js'), 'utf8'), 'const value = 2;\n');
  await page.reload(); await page.getByText('已更新示例值', { exact: true }).first().waitFor();
  assert.equal(await page.locator('#devProjectSelect').inputValue(), workspace.data.projects[0].id);
  await mkdir('test-results',{recursive:true});
  await page.screenshot({path:'test-results/developer-loop-desktop.png',fullPage:true});
  for (const width of [1440, 1024, 768, 390]) {
    await page.setViewportSize({ width, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'overflow at ' + width);
  }
  await page.screenshot({path:'test-results/developer-loop-mobile.png',fullPage:true});
  await page.locator('#devSettingsButton').click();
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  assert.deepEqual(errors, []);
});
