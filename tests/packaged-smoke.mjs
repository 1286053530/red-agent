import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
const folder=resolve('.local/packaged-check');
await mkdir(folder,{recursive:true});
let browser;
try {
  browser=await chromium.connectOverCDP('http://127.0.0.1:9227');
  const context=browser.contexts()[0];
  const page=context.pages().find(p=>/^http:\/\/127.0.0.1:/.test(p.url()));
  assert.ok(page,'packaged workbench opens');
  await page.waitForFunction(()=>!!window.shujinDesktop);
  const report={title:await page.title(),bridge:await page.evaluate(()=>({version:window.shujinDesktop.version,node:typeof require}))};
  assert.match(report.title,/筱竹书瑾/);assert.equal(report.bridge.node,'undefined');
  report.origin=new URL(page.url()).origin;
  report.noAuth=await fetch(report.origin+'/api/dev/state').then(r=>r.status);
  assert.equal(report.noAuth,403);
  await page.evaluate(()=>showView('developer'));
  await page.waitForSelector('#devImportButton');
  report.developer=await page.evaluate(async()=>({visible:!document.querySelector('#developerView').classList.contains('hidden'),response:await fetch('/api/dev/state').then(r=>r.status)}));
  assert.equal(report.developer.visible,true);assert.equal(report.developer.response,200);
  await page.screenshot({path:resolve(folder,'developer.png')});
  await page.evaluate(()=>showView('account'));
  await page.waitForFunction(async()=>!(await fetch('/api/xhs/status').then(r=>r.json())).busy,{},{timeout:45000});
  report.connect=await page.evaluate(()=>fetch('/api/xhs/connect',{method:'POST'}).then(r=>r.json()));
  assert.equal(report.connect.error,'');
  await page.waitForFunction(async()=>{
    const s=await fetch('/api/xhs/status').then(r=>r.json());
    return s.login?.status==='ready';
  },{},{timeout:45000});
  await page.locator('#checkConnectionButton').click();
  await page.locator('#loginQrImage:not(.hidden)').waitFor();
  report.card=await page.locator('#loginQrImage').evaluate(n=>({loaded:n.complete&&n.naturalWidth>0,source:n.src.startsWith('data:image/png;base64,')}));
  assert.deepEqual(report.card,{loaded:true,source:true});
  await page.screenshot({path:resolve(folder,'inline-qr.png')});
  await page.locator('#refreshQrButton').click();
  await page.waitForFunction(()=>!document.querySelector('#refreshQrButton').disabled);
  await page.locator('#loginQrImage:not(.hidden)').waitFor({timeout:45000});
  await page.locator('#openOfficialLoginButton').click();
  let official;
  for(let i=0;i<30;i++){
    official=context.pages().find(p=>p.url().startsWith('https://www.xiaohongshu.com/'));
    if(official&&await official.locator('.login-container img,.login-modal img').count())break;
    await new Promise(r=>setTimeout(r,500));
  }
  assert.ok(official,'official page stays in the same application');
  report.official=await official.evaluate(()=>({title:document.title,url:location.href,restricted:/300012|IP存在风险/.test(document.body.innerText),qrImages:[...document.querySelectorAll('.login-container img,.login-modal img')].filter(n=>n.getClientRects().length&&n.complete&&n.naturalWidth>80).length,node:typeof require,bridge:typeof window.shujinDesktop}));
  assert.equal(report.official.restricted,false);assert.ok(report.official.qrImages>0);
  assert.equal(report.official.node,'undefined');assert.equal(report.official.bridge,'undefined');
  await official.screenshot({path:resolve(folder,'official.png')});
  report.overlay=await page.locator('.official-overlay').evaluate(n=>({visible:!n.classList.contains('hidden'),title:n.querySelector('strong').textContent}));
  assert.equal(report.overlay.visible,true);
  await page.evaluate(()=>window.shujinDesktop.closeOfficial());
  await page.screenshot({path:resolve(folder,'workbench.png')});
  await writeFile(resolve(folder,'report.json'),JSON.stringify({...report,passed:true},null,2));
  console.log(JSON.stringify({...report,passed:true},null,2));
  await browser.close();
} catch(error) {if(browser)await browser.close().catch(()=>{});console.error(error);process.exitCode=1;}
