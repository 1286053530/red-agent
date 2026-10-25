import { app, session, BrowserWindow, webContents } from 'electron';
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const {DesktopXhs,officialUrl}=await import(process.argv.includes('--packaged')
  ? pathToFileURL(resolve(process.env.SHUJIN_TEST_APP_DIR||'release/win-unpacked','resources/app.asar/desktop/xhs.mjs')).href
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
    let network=0,heartbeats=0,pageLoads=0;
    await profile.protocol.handle('https',request=>{
      assert.equal(new URL(request.url).hostname,'www.xiaohongshu.com');
      network++;
      if(new URL(request.url).pathname==='/heartbeat'){heartbeats++;return new Response('fixture');}
      pageLoads++;
      return new Response('<html><head><title>Isolated official page</title></head><body>Manual fixture<a id="official" href="https://www.xiaohongshu.com/notification" target="_blank">Messages</a><a id="outside" href="https://evil.example/" target="_blank">Outside</a><script>setInterval(()=>fetch("https://www.xiaohongshu.com/heartbeat"),150);</script></body></html>',{headers:{'Content-Type':'text/html; charset=utf-8'}});
    });
    const win=new BrowserWindow({show:false,webPreferences:{sandbox:true,contextIsolation:true,nodeIntegration:false}});
    const xhs=new DesktopXhs(win,{partition});
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
    assert.equal(network,0);
    assert.equal(typeof xhs.openInBrowser,'undefined');
    assert.equal(officialUrl('https://www.xiaohongshu.com/explore'),true);
    assert.equal(officialUrl('https://www.xiaohongshu.com.evil.example/'),false);
    await assert.rejects(()=>xhs.open('https://evil.example'),error=>error.status===400);
    assert.throws(()=>xhs.setBounds({x:NaN,y:0,width:100,height:100}),error=>error.status===400);
    xhs.setBounds({x:180,y:120,width:460,height:320});
    await xhs.open();assert.ok(xhs.view);
    assert.deepEqual(xhs.view.getBounds(),{x:180,y:120,width:460,height:320});
    xhs.setBounds({x:190,y:130,width:420,height:300});
    assert.deepEqual(xhs.view.getBounds(),{x:190,y:130,width:420,height:300});
    const contents=xhs.view.webContents;
    assert.deepEqual(await contents.executeJavaScript('({node:typeof require,bridge:typeof window.shujinDesktop})'),{node:'undefined',bridge:'undefined'});
    for(let i=0;i<40&&heartbeats===0;i++)await new Promise(resolve=>setTimeout(resolve,100));
    assert.ok(network>0);assert.ok(heartbeats>0);
    const windowCount=BrowserWindow.getAllWindows().length;
    const contentsCount=webContents.getAllWebContents().length;
    const navigated=new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(Error('Embedded popup navigation timed out')),5000);
      contents.once('did-finish-load',()=>{clearTimeout(timer);resolve();});
    });
    await contents.executeJavaScript('document.querySelector("#official").click()');
    await navigated;
    assert.equal(contents.getURL(),'https://www.xiaohongshu.com/notification');
    assert.equal(xhs.view.webContents,contents);
    await contents.executeJavaScript('document.querySelector("#outside").click()');
    await new Promise(resolve=>setTimeout(resolve,200));
    assert.equal(contents.getURL(),'https://www.xiaohongshu.com/notification');
    assert.match(xhs.error,/站外/);
    assert.equal(BrowserWindow.getAllWindows().length,windowCount);
    assert.equal(webContents.getAllWebContents().length,contentsCount);
    await contents.executeJavaScript('document.body.style.height="3000px";window.scrollTo(0,480);window.fixtureDraft="keep this draft"');
    const retainedState=await contents.executeJavaScript('({scroll:scrollY,draft:fixtureDraft})');
    assert.ok(retainedState.scroll>=400,'fixture must actually scroll before the retention check');
    const beforeHideLoads=pageLoads;
    const originalView=xhs.view;
    xhs.hide();assert.equal(xhs.visible,false);assert.equal(contents.isDestroyed(),false);
    win.emit('minimize');win.emit('restore');assert.equal(xhs.visible,false,'restoring Agent must not reveal the hidden website');
    await new Promise(resolve=>setTimeout(resolve,250));
    xhs.show();assert.equal(xhs.view,originalView);assert.equal(xhs.visible,true);
    assert.equal(contents.getURL(),'https://www.xiaohongshu.com/notification');
    assert.deepEqual(await contents.executeJavaScript('({scroll:scrollY,draft:fixtureDraft})'),retainedState);
    assert.equal(pageLoads,beforeHideLoads,'switching views must not reload the page');
    await xhs.close();
    await new Promise(resolve=>setTimeout(resolve,100));
    assert.equal(contents.isDestroyed(),true);assert.equal(xhs.view,null);
    const afterClose=network;
    await new Promise(resolve=>setTimeout(resolve,500));
    assert.equal(network,afterClose,'closing must stop the fixture page timers');
    await assert.rejects(()=>profile.fetch(HOME),'closed partition must reject even non-page network requests');
    assert.equal(network,afterClose);
    await xhs.open();const beforeMinimize=xhs.view;win.emit('minimize');
    await new Promise(resolve=>setTimeout(resolve,100));
    assert.equal(xhs.view,beforeMinimize);assert.equal(xhs.visible,false);
    win.emit('restore');assert.equal(xhs.view,beforeMinimize);assert.equal(xhs.visible,true);
    if(verify){await xhs.disconnect();assert.equal((await profile.cookies.get({url:HOME})).length,0);}
    else await profile.cookies.flushStore();
    await xhs.close();
    win.destroy();
    await mkdir(folder,{recursive:true});
    await writeFile(resolve(folder,verify?'persistence.json':'session.json'),JSON.stringify({passed:true,manualOnly:true,idleRequests:0,automaticOpens:0,fixtureRequests:network,closedRequests:0,officialLinksReuseView:true,retainedOnSwitch:true,scrollPreserved:retainedState.scroll,extraWindows:0,embeddedPageDestroyed:true,currentSessionCleared:verify},null,2));
    console.log('MANUAL_ACCESS_PASS '+(verify?'persistence-and-cleanup':'idle-and-explicit-open'));
    app.exit(0);
  }catch(error){console.error(error.stack);app.exit(1);}
});
