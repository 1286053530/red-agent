import { app, session, BrowserWindow } from 'electron';
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const {DesktopXhs,officialUrl}=await import(process.argv.includes('--packaged')
  ? pathToFileURL(resolve('release/win-unpacked/resources/app.asar/desktop/xhs.mjs')).href
  : new URL('../desktop/xhs.mjs',import.meta.url).href);

const folder=resolve('.local/manual-access-check');
app.setPath('userData',resolve(folder,'profile'));
const verify=process.argv.includes('--verify-persistence');
const HOME='https://www.xiaohongshu.com/explore';
app.on('window-all-closed',()=>{});
app.whenReady().then(async()=>{
  try {
    const partition='persist:manual-access-fixture';
    const profile=session.fromPartition(partition);
    let network=0,heartbeats=0;
    await profile.protocol.handle('https',request=>{
      assert.equal(new URL(request.url).hostname,'www.xiaohongshu.com');
      network++;
      if(new URL(request.url).pathname==='/heartbeat'){heartbeats++;return new Response('fixture');}
      return new Response('<html><head><title>Isolated official page</title></head><body>Manual fixture<script>setInterval(()=>fetch("https://www.xiaohongshu.com/heartbeat"),150);</script></body></html>',{headers:{'Content-Type':'text/html; charset=utf-8'}});
    });
    const opened=[];
    const win=new BrowserWindow({show:false,webPreferences:{sandbox:true,contextIsolation:true,nodeIntegration:false}});
    const xhs=new DesktopXhs(win,{partition,openExternal:async url=>opened.push(url)});
    if(!verify){
      await profile.clearStorageData();
      await profile.cookies.set({url:HOME,name:'fixture_auth',value:'1',expirationDate:Math.floor(Date.now()/1000)+3600});
    }
    assert.equal((await profile.cookies.get({url:HOME})).length,1);
    for(let i=0;i<5;i++)assert.equal((await xhs.status()).status,'automation_disabled');
    for(const action of [()=>xhs.connect(),()=>xhs.connect(true),()=>xhs.recommendations(),()=>xhs.messages('private')]){
      await assert.rejects(action,error=>error.status===410);
    }
    assert.equal(xhs.view,null);
    assert.equal(typeof xhs.restore,'undefined');
    assert.equal(network,0);assert.deepEqual(opened,[]);
    assert.equal(officialUrl('https://www.xiaohongshu.com/explore'),true);
    assert.equal(officialUrl('https://www.xiaohongshu.com.evil.example/'),false);
    await assert.rejects(()=>xhs.open('https://evil.example'),error=>error.status===400);
    await xhs.open();assert.deepEqual(opened,[]);assert.ok(xhs.view);
    const contents=xhs.view.webContents;
    assert.deepEqual(await contents.executeJavaScript('({node:typeof require,bridge:typeof window.shujinDesktop})'),{node:'undefined',bridge:'undefined'});
    for(let i=0;i<40&&heartbeats===0;i++)await new Promise(resolve=>setTimeout(resolve,100));
    assert.ok(network>0);assert.ok(heartbeats>0);
    await xhs.close();
    await new Promise(resolve=>setTimeout(resolve,100));
    assert.equal(contents.isDestroyed(),true);assert.equal(xhs.view,null);
    const afterClose=network;
    await new Promise(resolve=>setTimeout(resolve,500));
    assert.equal(network,afterClose,'closing must stop the fixture page timers');
    await assert.rejects(()=>profile.fetch(HOME),'closed partition must reject even non-page network requests');
    assert.equal(network,afterClose);
    await xhs.open();win.emit('minimize');
    await new Promise(resolve=>setTimeout(resolve,100));
    assert.equal(xhs.view,null);win.emit('restore');assert.equal(xhs.view,null);
    await xhs.openInBrowser();assert.deepEqual(opened,[HOME]);
    if(verify){await xhs.disconnect();assert.equal((await profile.cookies.get({url:HOME})).length,0);}
    else await profile.cookies.flushStore();
    await xhs.close();
    win.destroy();
    await mkdir(folder,{recursive:true});
    await writeFile(resolve(folder,verify?'persistence.json':'session.json'),JSON.stringify({passed:true,manualOnly:true,idleRequests:0,automaticOpens:0,fixtureRequests:network,closedRequests:0,explicitExternalOpenCount:opened.length,embeddedPageDestroyed:true,currentSessionCleared:verify},null,2));
    console.log('MANUAL_ACCESS_PASS '+(verify?'persistence-and-cleanup':'idle-and-explicit-open'));
    app.exit(0);
  }catch(error){console.error(error.stack);app.exit(1);}
});
