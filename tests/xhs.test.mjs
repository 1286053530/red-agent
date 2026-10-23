import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';
import { XhsBrowser, readAccount, readRecommendations, readMessagePanel, readLoginPanel } from '../xhs-browser.mjs';
import { server } from '../server.mjs';

const fixture = `<!doctype html><html><head><meta charset="UTF-8"></head><body>
<div class="channel-list-content"><a href="/explore">发现</a><a href="#" onclick="document.querySelector('.notification-container').hidden=false;return false">通知</a><a href="#" onclick="document.querySelector('.conversation-list').hidden=false;return false">消息</a></div>
<section class="note-item" data-note-id="real-note"><a class="cover" href="/explore/real-note?xsec_token=test"><img src="https://sns-webpic-qc.xhscdn.com/test.webp"></a><a class="title" href="/explore/real-note">测试笔记 &amp; 标题</a><div class="author-wrapper"><a class="author"><span class="name">测试作者</span></a><span class="like-wrapper"><span class="count">1.2万</span></span></div></section>
<section class="note-item" data-note-id="unsafe"><a class="cover" href="javascript:alert(1)"></a><a class="title">不应读取的链接</a></section>
<div class="notification-container" hidden><div class="interaction-item">用户甲\n赞了你的笔记\n10分钟前</div></div>
<div class="conversation-list" hidden><div class="conversation-item">同事乙\n周末一起喝咖啡吗？</div></div>
<script>window.__INITIAL_STATE__={user:{loggedIn:localStorage.getItem('testLogin')==='1',userInfo:{nickname:'测试账号'}}};</script>
</body></html>`;

test('browser session: login gate, actual DOM extraction, messages, persistence, clearing', async t => {
  const temp = await mkdtemp(join(tmpdir(),'guanshu-xhs-test-'));
  const browserType = {
    async launchPersistentContext(profile, options) {
      const context = await chromium.launchPersistentContext(profile, options);
      await context.route('**/*', async route => {
        if (route.request().isNavigationRequest()) await route.fulfill({ contentType:'text/html; charset=utf-8',body:fixture });
        else await route.abort();
      });
      return context;
    }
  };
  const session = new XhsBrowser({ profileDir:join(temp,'profile'),headless:true,browserType });
  t.after(async()=>{await session.close();await rm(temp,{recursive:true,force:true,maxRetries:3,retryDelay:100});});
  assert.equal((await session.status()).status,'disconnected');
  await assert.rejects(()=>session.recommendations(),error=>error.status===401);
  assert.equal((await session.connect()).status,'awaiting_login');
  await assert.rejects(()=>session.messages(),error=>error.status===401);
  await session.page.evaluate(()=>{localStorage.setItem('testLogin','1');window.__INITIAL_STATE__.user.loggedIn=true;});
  assert.equal((await session.status()).status,'connected');
  const feed=await session.recommendations();
  assert.equal(feed.items.length,1);
  assert.equal(feed.items[0].title,'测试笔记 & 标题');
  assert.equal(feed.items[0].author,'测试作者');
  assert.equal(feed.items[0].likes,'1.2万');
  assert.match(feed.items[0].url,/xsec_token=test/);
  const notifications=await session.messages();
  assert.equal(notifications.readable,true);
  assert.match(notifications.items[0].text,/赞了你的笔记/);
  const messages=await session.messages('private');
  assert.equal(messages.readable,true);
  assert.match(messages.items[0].text,/咖啡/);
  await session.close();
  assert.equal((await session.status()).status,'disconnected');
  assert.equal((await session.status()).profileSaved,true);
  assert.equal((await session.connect()).status,'connected');
  const cleared=await session.disconnect();
  assert.equal(cleared.status,'disconnected');
  assert.equal(cleared.profileSaved,false);
});

test('rendered page: hidden account and unrelated feed do not imply login or messages',async t=>{
  const browser=await chromium.launch({channel:process.env.XHS_BROWSER_CHANNEL||'msedge',headless:true});
  t.after(()=>browser.close());
  const page=await browser.newPage();
  await page.setContent('<div class="channel-list-content"><a href="/user/profile/hidden" style="display:none">我</a></div><div class="note-item">这是推荐流，不是消息</div>');
  assert.equal((await page.evaluate(readAccount)).loggedIn,false);
  assert.equal((await page.evaluate(readMessagePanel,'private')).readable,false);
  assert.equal((await page.evaluate(readMessagePanel,'notifications')).readable,false);
  assert.equal((await page.evaluate(readRecommendations)).length,0);
});

test('inline QR login: hidden browser, QR capture, expiry, refresh, confirmation and restrictions',async t=>{
  const temp=await mkdtemp(join(tmpdir(),'guanshu-qr-test-'));
  const browserType={async launchPersistentContext(profile,options){
    assert.equal(options.headless,true,'login must not open a visible browser');
    const context=await chromium.launchPersistentContext(profile,options);
    await context.route('**/*',route=>route.fulfill({contentType:'text/html; charset=utf-8',body:`<!doctype html><meta charset="utf-8"><div class="login-container"><h2>扫码登录</h2><div class="qrcode"><canvas width="160" height="160"></canvas></div><p id="qrState">打开小红书扫一扫</p></div><script>window.__INITIAL_STATE__={user:{loggedIn:false,userInfo:{nickname:'二维码测试账号'}}};const c=document.querySelector('canvas').getContext('2d');c.fillStyle='white';c.fillRect(0,0,160,160);c.fillStyle='black';c.fillRect(12,12,35,35);</script>`}));
    return context;
  }};
  const session=new XhsBrowser({profileDir:join(temp,'profile'),browserType});
  t.after(async()=>{await session.close();await rm(temp,{recursive:true,force:true,maxRetries:3,retryDelay:100});});
  await session.connect();
  let result=await session.status();
  assert.equal(result.login.status,'ready');
  assert.match(result.login.image,/^data:image\/png;base64,/);
  assert.equal(result.status,'awaiting_login');
  await session.page.locator('#qrState').evaluate(n=>n.textContent='二维码已过期，点击刷新');
  result=await session.status();
  assert.equal(result.login.status,'expired');
  assert.equal(result.login.image,'');
  await session.connect(true);
  assert.equal((await session.status()).login.status,'ready');
  await session.page.locator('#qrState').evaluate(n=>n.textContent='扫码成功，请在手机确认登录');
  result=await session.status();
  assert.equal(result.login.status,'scanned');
  assert.equal(result.status,'awaiting_login','scanning alone must not imply login');
  assert.equal(result.login.image,'');
  await session.page.evaluate(()=>window.__INITIAL_STATE__.user.loggedIn=true);
  result=await session.status();
  assert.equal(result.status,'connected');
  assert.equal(result.login.status,'connected');
  assert.equal(result.login.image,'');
  await session.page.evaluate(()=>{window.__INITIAL_STATE__.user.loggedIn=false;document.body.innerHTML='<h2>安全限制</h2><p>IP存在风险，请切换可靠网络环境后重试</p><p>300012</p>';});
  result=await session.status();
  assert.equal(result.status,'verification_required');
  assert.equal(result.login.status,'restricted');
  assert.match(result.login.message,/IP存在风险/);
  assert.equal(result.login.image,'');
  await session.page.setContent('<div class="verify-icon">普通图标，不是验证</div>');
  assert.equal((await session.page.evaluate(readAccount)).verification,false);
  assert.equal((await session.page.evaluate(readLoginPanel)).restricted,false);
});

test('local API: denies unauthenticated reads, foreign origins and private files',async t=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  t.after(()=>new Promise(resolve=>server.close(resolve)));
  const port=server.address().port;
  const request=(path,method='GET',extra={})=>new Promise((resolve,reject)=>{
    const req=http.request({host:'127.0.0.1',port,path,method,headers:{host:'localhost:3000',...extra}},response=>{
      let body='';response.on('data',chunk=>body+=chunk);response.on('end',()=>resolve({status:response.statusCode,body}));
    });req.on('error',reject);req.end();
  });
  assert.equal((await request('/api/xhs/status')).status,200);
  assert.equal((await request('/api/xhs/recommendations','POST')).status,401);
  assert.equal((await request('/api/xhs/messages','POST')).status,401);
  assert.equal((await request('/api/xhs/connect')).status,405);
  assert.equal((await request('/api/xhs/connect','POST',{origin:'https://other.example'})).status,403);
  assert.equal((await request('/api/xhs/status','GET',{'sec-fetch-site':'cross-site'})).status,403);
  assert.equal((await request('/api/xhs/status','GET',{host:'evil.example:3000'})).status,403);
  for(const path of ['/.local/xiaohongshu-profile/Default/Cookies','/server.mjs','/package.json','/node_modules/playwright/package.json']) assert.equal((await request(path)).status,404);
  assert.equal((await request('/account.js')).status,200);
});

test('workspace UI: connection, recommendations, message tabs, errors and clearing',async t=>{
  const browser=await chromium.launch({channel:process.env.XHS_BROWSER_CHANNEL||'msedge',headless:true});
  t.after(()=>browser.close());
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.addInitScript(()=>{window.shujinDesktop={onOfficial:()=>()=>{},openOfficial:async()=>{},closeOfficial:async()=>{}};});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  let status='disconnected', failFeed=false, refreshes=0;
  const qrImage='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aL1sAAAAASUVORK5CYII=';
  await page.route('http://workbench.test/**',async route=>{
    const url=new URL(route.request().url());
    if(url.pathname.startsWith('/api/xhs/')) {
      let data={},code=200;
      if(url.pathname.endsWith('/connect'))status='awaiting_login';
      if(url.pathname.endsWith('/login/refresh')) {status='awaiting_login';refreshes++;}
      if(url.pathname.endsWith('/disconnect'))status='disconnected';
      if(url.pathname.endsWith('/status')||url.pathname.endsWith('/connect')||url.pathname.endsWith('/disconnect')||url.pathname.endsWith('/login/refresh')) data={status,name:status==='connected'?'测试账号':'',profileSaved:status!=='disconnected',busy:false,error:'',login:{status:status==='awaiting_login'?'ready':'idle',image:status==='awaiting_login'?qrImage:''}};
      if(url.pathname.endsWith('/recommendations')) {
        if(failFeed){code=502;data={error:'官网暂时无法读取，请稍后重试。'};}
        else data={items:[{id:'one',title:'真实页面标题 <img src=x onerror=alert(1)>',author:'测试作者',cover:'',url:'https://www.xiaohongshu.com/explore/one',likes:'123',type:'图文'}],updatedAt:new Date().toISOString()};
      }
      if(url.pathname.endsWith('/messages'))data={readable:true,items:[{text:url.searchParams.get('kind')==='private'?'同事乙：一起喝咖啡吗？':'用户甲赞了你的笔记'}],updatedAt:new Date().toISOString()};
      await route.fulfill({status:code,contentType:'application/json',body:JSON.stringify(data)});return;
    }
    const path=url.pathname==='/'?'index.html':url.pathname.slice(1);
    try {
      const body=await readFile(new URL('../'+path,import.meta.url));
      await route.fulfill({body,contentType:path.endsWith('.css')?'text/css':path.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'});
    }catch{await route.fulfill({status:404,body:'Not found'});}
  });
  await page.goto('http://workbench.test/#account');
  await page.locator('#accountView [data-connect-xhs]').first().click();
  await page.getByText('在此页面扫码登录',{exact:true}).waitFor();
  assert.equal(await page.locator('#loginQrImage').isVisible(),true,'desktop displays the returned QR');
  assert.equal(await page.locator('#loginQrImage').getAttribute('src'),qrImage);
  await page.locator('#refreshQrButton').click();
  await page.waitForFunction(()=>!document.querySelector('#refreshQrButton').disabled);
  assert.equal(refreshes,1,'desktop refresh calls the refresh endpoint');
  assert.equal(await page.locator('#openOfficialLoginButton').isVisible(),true);
  status='connected';
  await page.locator('#checkConnectionButton').click();
  await page.getByText('测试账号',{exact:true}).first().waitFor();
  await page.getByRole('button',{name:'我的推荐',exact:true}).click();
  await page.locator('.personal-note').waitFor();
  assert.match(await page.locator('.personal-note-title').innerText(),/<img src=x/);
  assert.equal(await page.locator('.personal-note-title img').count(),0);
  assert.equal(await page.locator('.personal-note-title').getAttribute('href'),'https://www.xiaohongshu.com/explore/one');
  failFeed=true;
  await page.locator('#syncRecommendations').click();
  await page.getByText('官网暂时无法读取，请稍后重试。',{exact:true}).waitFor();
  assert.equal(await page.locator('.personal-note').count(),1);
  await page.getByRole('button',{name:'消息中心',exact:true}).click();
  await page.getByText('用户甲赞了你的笔记',{exact:true}).waitFor();
  await page.getByRole('tab',{name:'私信会话'}).click();
  await page.getByText('同事乙：一起喝咖啡吗？',{exact:true}).waitFor();
  assert.equal(await page.getByRole('tab',{name:'私信会话'}).getAttribute('aria-selected'),'true');
  await page.getByRole('button',{name:'小红书账号',exact:true}).click();
  await page.locator('#clearConnectionButton').click();
  await page.getByText('准备连接你的账号',{exact:true}).waitFor();
  await page.getByRole('button',{name:'消息中心',exact:true}).click();
  assert.equal(await page.locator('.personal-message').count(),0);
  await page.getByRole('button',{name:'我的推荐',exact:true}).click();
  assert.equal(await page.locator('.personal-note').count(),0);
  await page.setViewportSize({width:390,height:844});
  for(const view of ['account','recommendations','messages']) {
    await page.evaluate(view=>window.showView(view),view);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,view+' must not overflow');
  }
  assert.deepEqual(errors,[]);
});
