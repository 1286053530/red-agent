import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomBytes } from 'node:crypto';
import { createWorkbench } from '../server.mjs';
import { DevWorkspace } from '../dev-agent.mjs';
import { DesktopXhs } from './xhs.mjs';

const here=dirname(fileURLToPath(import.meta.url));
app.setName('筱竹书瑾');
if(!app.isPackaged && process.env.SHUJIN_DESKTOP_SMOKE==='1') app.setPath('userData',join(here,'../.local/desktop-check/profile'));
let win, workbench, xhs, origin, quitting=false;
if(!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance',()=>{if(win){if(win.isMinimized())win.restore();win.show();win.focus();}});
  app.whenReady().then(async()=>{
    win=new BrowserWindow({width:1440,height:960,minWidth:960,minHeight:680,title:'筱竹书瑾',icon:join(here,'icon.png'),backgroundColor:'#f5f6f8',show:false,
      webPreferences:{preload:join(here,'preload.cjs'),partition:'shujin-local',nodeIntegration:false,contextIsolation:true,sandbox:true}});
    win.removeMenu();
    xhs=new DesktopXhs(win);
    const dev=new DevWorkspace({dataDir:join(app.getPath('userData'),'developer')});
    dev.pickFolder=async()=>{const result=await dialog.showOpenDialog(win,{title:'导入本地项目',properties:['openDirectory']});return {path:result.canceled?'':result.filePaths[0]};};
    const desktopToken=randomBytes(32).toString('hex');
    workbench=createWorkbench({xhs,dev,allowedPort:0,desktopToken});
    await new Promise((resolve,reject)=>{workbench.server.once('error',reject);workbench.server.listen(0,'127.0.0.1',resolve);});
    origin='http://127.0.0.1:'+workbench.server.address().port;
    await win.webContents.session.cookies.set({url:origin,name:'shujin_session',value:desktopToken,httpOnly:true,sameSite:'strict'});
    const trusted=event=>{
      if(event.sender!==win.webContents || event.senderFrame!==win.webContents.mainFrame || new URL(event.senderFrame.url).origin!==origin) throw Error('此页面不允许调用客户端接口。');
    };
    ipcMain.handle('xhs:open',async(event,url)=>{trusted(event);return xhs.open(url||'https://www.xiaohongshu.com/explore');});
    ipcMain.handle('xhs:hide',event=>{trusted(event);xhs.hide();return true;});
    ipcMain.handle('xhs:refresh',async event=>{trusted(event);return xhs.connect(true);});
    win.webContents.setWindowOpenHandler(({url})=>{if(url.startsWith('https://www.xiaohongshu.com/'))void xhs.open(url).catch(()=>{});return {action:'deny'};});
    win.webContents.on('will-navigate',(event,url)=>{if(new URL(url).origin!==origin)event.preventDefault();});
    win.on('close',event=>{if(!quitting){event.preventDefault();app.quit();}});
    const launchSmoke=!app.isPackaged && process.env.SHUJIN_DESKTOP_SMOKE==='1';
    let launched=false;
    const finishLoad=async()=>{
      if(launched || !win || win.isDestroyed())return;
      launched=true;
      win.show();
      if(!launchSmoke)void xhs.restore().catch(()=>{});
      // Optional developer-only smoke harness. Never included in release files.
      if(launchSmoke){const {runSmoke}=await import('../tests/desktop-smoke.mjs');await runSmoke({app,win,xhs,workbench,origin});}
    };
    win.webContents.once('dom-ready',()=>void finishLoad().catch(error=>{dialog.showErrorBox('客户端验证失败',error.message);app.exit(1);}));
    void win.loadURL(origin+'/#account').catch(error=>{if(!launched){dialog.showErrorBox('客户端启动失败',error.message);app.exit(1);}});
  }).catch(error=>{dialog.showErrorBox('客户端启动失败',error.message);app.exit(1);});
  app.on('before-quit',event=>{
    if(quitting)return;
    event.preventDefault();quitting=true;
    Promise.resolve(workbench?.close()).finally(()=>app.quit());
  });
  app.on('window-all-closed',()=>app.quit());
}
