import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
export async function runSmoke({app,win,xhs,workbench,origin}) {
  const folder=resolve('.local/desktop-check');
  await mkdir(folder,{recursive:true});
  const errors=[];
  win.webContents.on('console-message',event=>{if(event.level==='error')errors.push(event.message);});
  const report={origin,version:app.getVersion(),title:win.getTitle()};
  try {
    console.log('DESKTOP_SMOKE_START');
    report.noAuth=await fetch(origin+'/api/dev/projects').then(r=>r.status);
    report.bridge=await win.webContents.executeJavaScript('({available:!!window.shujinDesktop,node:typeof require})');
    // Trigger the real UI/API path, not a synthetic login-success flag.
    report.connect=await win.webContents.executeJavaScript("fetch('/api/xhs/connect',{method:'POST'}).then(r=>r.json())");
    console.log('DESKTOP_SMOKE_CONNECTED');
    await pause(18000);
    report.status=await xhs.status();
    console.log('DESKTOP_SMOKE_QR '+report.status.login?.status);
    if(report.status.login?.status!=='ready') throw new Error('官方二维码未返回账号卡片：'+report.status.login?.status);
    await win.webContents.executeJavaScript("document.querySelector('#checkConnectionButton').click()");
    await pause(1000);
    report.card=await win.webContents.executeJavaScript("({state:document.querySelector('#qrLoginCard').dataset.state,visible:!document.querySelector('#loginQrImage').classList.contains('hidden'),loaded:document.querySelector('#loginQrImage').naturalWidth>0})");
    if(!report.card.visible || !report.card.loaded) throw new Error('账号卡片未显示二维码');
    console.log('DESKTOP_SMOKE_CARD '+JSON.stringify(report.card));
    report.page=await xhs.evaluate(()=>{
      const text=document.body?.innerText||'';
      return {url:location.href,title:document.title,restricted:/IP存在风险|300012/.test(text),hasLogin:/扫码|登录/.test(text),
        qrImages:[...document.querySelectorAll('.login-container img,.login-modal img')].filter(n=>n.getClientRects().length&&n.complete&&n.naturalWidth>80).length};
    });
    xhs.show(); await pause(500);
    await writeFile(resolve(folder,'official.png'),(await xhs.view.webContents.capturePage()).toPNG());
    xhs.hide(); await pause(800);
    await writeFile(resolve(folder,'workbench.png'),(await win.capturePage()).toPNG());
    await win.webContents.executeJavaScript("showView('developer')");
    await pause(800);
    report.developer=await win.webContents.executeJavaScript("({visible:!document.querySelector('#developerView').classList.contains('hidden'),environment:document.querySelector('.environment-tag').textContent.trim()})");
    await writeFile(resolve(folder,'developer.png'),(await win.capturePage()).toPNG());
    report.errors=errors;
  } catch(error) { report.failure=error.stack; }
  const summarize=(key,value)=>key==='image'&&typeof value==='string'&&value.startsWith('data:image/')?'[PNG image, '+value.length+' characters]':value;
  await writeFile(resolve(folder,'report.json'),JSON.stringify(report,summarize,2));
  console.log('DESKTOP_SMOKE '+JSON.stringify(report,summarize));
  app.quit();
}
