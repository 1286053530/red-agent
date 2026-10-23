import { app, BrowserWindow, session } from 'electron';
import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import { writeFile } from 'node:fs/promises';
import { mkdirSync } from 'node:fs';
import { DesktopXhs } from '../desktop/xhs.mjs';

const folder=resolve('.local/desktop-fixture');
mkdirSync(folder,{recursive:true});
app.setPath('userData',resolve(folder,'profile'));
const verify=process.argv.includes('--verify-persistence');
const HOME='https://www.xiaohongshu.com/explore';
const fixture=`<!doctype html><html><body><div id="app"><div class="channel-list-content"><button id="notification">通知</button><button id="private">消息</button></div><article class="note-item" data-note-id="fixture"><a class="cover" href="/explore/fixture"></a><span class="title">测试推荐笔记</span><span class="author"><span class="name">测试作者</span></span></article></div><script>const loggedIn=document.cookie.includes('fixture_auth=1');window.__INITIAL_STATE__={user:{loggedIn,userInfo:{nickname:'桌面测试账号',userId:'fixture'}}};if(loggedIn)document.querySelector('.channel-list-content').insertAdjacentHTML('beforeend','<a href="/user/profile/fixture">桌面测试账号</a>');else document.body.insertAdjacentHTML('beforeend','<div class="login-container">扫码登录</div>');for(const [id,container,item,text] of [['notification','notification-container','notification-item','测试互动通知'],['private','conversation-list','conversation-item','测试私信会话']])document.getElementById(id).onclick=()=>{document.querySelectorAll('.panel').forEach(n=>n.remove());document.body.insertAdjacentHTML('beforeend','<div class="panel '+container+'"><div class="'+item+'">'+text+'</div></div>')};</script></body></html>`;
let win,xhs;
app.whenReady().then(async()=>{
try {
  win=new BrowserWindow({show:false,webPreferences:{sandbox:true,nodeIntegration:false,contextIsolation:true}});
  const partition='persist:isolated-desktop-test';
  const profile=session.fromPartition(partition);
  await profile.protocol.handle('https',request=>new Response(new URL(request.url).hostname==='www.xiaohongshu.com'?fixture:'',{headers:{'Content-Type':'text/html; charset=utf-8'}}));
  xhs=new DesktopXhs(win,{partition});
  if(verify) {
    assert.equal((await xhs.status()).profileSaved,true);
    await xhs.restore();
    assert.equal((await xhs.status()).status,'connected','login restored after a full process restart');
    assert.equal(xhs.visible,false,'restoring session keeps workbench visible');
    const restoring=xhs.restore();
    const connecting=xhs.connect();
    await restoring;
    assert.equal((await connecting).status,'connected','opening login waits for startup restoration');
    await xhs.disconnect();
    assert.equal((await xhs.status()).status,'disconnected');
    assert.equal((await profile.cookies.get({url:HOME})).length,0);
    assert.equal((await xhs.status()).profileSaved,false);
  } else {
    await profile.clearStorageData();
    assert.equal((await xhs.connect()).status,'awaiting_login');
    assert.equal(xhs.visible,false,'inline login keeps the account card visible');
    await xhs.evaluate(()=>{
      const panel=document.querySelector('.login-container');
      panel.innerHTML='<h2>扫码登录</h2><div class="qrcode"><canvas width="160" height="160"></canvas></div><p id="qrState">打开小红书扫一扫</p>';
      const c=panel.querySelector('canvas').getContext('2d');
      c.fillStyle='white';c.fillRect(0,0,160,160);c.fillStyle='black';c.fillRect(12,12,35,35);
    });
    const qr=await xhs.status();
    assert.equal(qr.login.status,'ready');
    assert.match(qr.login.image,/^data:image\/png;base64,/,'desktop returns the official QR image to the card');
    assert.equal(xhs.visible,false,'capturing the QR does not open the official overlay');
    await xhs.evaluate(()=>document.querySelector('#qrState').textContent='二维码已过期，点击刷新');
    assert.equal((await xhs.status()).login.image,'');
    assert.equal((await xhs.status()).login.status,'expired');
    await xhs.evaluate(()=>document.querySelector('#qrState').textContent='扫码成功，请在手机确认登录');
    assert.equal((await xhs.status()).login.status,'scanned');
    assert.equal((await xhs.status()).login.image,'');
    await xhs.evaluate(()=>document.body.insertAdjacentHTML('beforeend','<div class="verify-container">请完成验证</div>'));
    assert.equal((await xhs.status()).login.status,'restricted');
    assert.equal((await xhs.status()).login.image,'');
    await xhs.connect(true);
    assert.equal((await xhs.status()).login.status,'loading','refresh clears stale QR and reloads the official page');
    await assert.rejects(xhs.recommendations(),/扫码登录/);
    const remote=await xhs.evaluate(()=>({node:typeof require,bridge:typeof window.shujinDesktop}));
    assert.deepEqual(remote,{node:'undefined',bridge:'undefined'});
    await profile.cookies.set({url:HOME,name:'fixture_auth',value:'1',expirationDate:Math.floor(Date.now()/1000)+3600});
    await xhs.navigate(HOME);
    assert.equal((await xhs.status()).status,'connected');
    assert.equal((await xhs.status()).login.image,'');
    assert.equal((await xhs.recommendations()).items[0].title,'测试推荐笔记');
    assert.match((await xhs.messages('notifications')).items[0].text,/互动通知/);
    assert.match((await xhs.messages('private')).items[0].text,/私信会话/);
    xhs.busy=true;
    await assert.rejects(xhs.connect(),/上一项操作/);
    xhs.busy=false;
    await assert.rejects(xhs.navigate('https://example.com'),/仅支持/);
  }
  await xhs.close();
  await writeFile(resolve(folder,verify?'persistence.json':'session.json'),JSON.stringify({passed:true,phase:verify?'process restart, restore and clear':'login, recommendations, notifications, private messages, isolation and concurrency'},null,2));
  console.log('DESKTOP_SESSION_PASS '+(verify?'persistence':'session'));
  win.destroy();app.quit();
} catch(error) {
  console.error(error.stack);
  if(xhs)await xhs.close().catch(()=>{});
  if(win&&!win.isDestroyed())win.destroy();
  app.exit(1);
}
});
