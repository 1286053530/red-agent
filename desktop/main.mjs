import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { startPythonBackend } from './python-backend.mjs';
import { DesktopXhs } from './xhs.mjs';

const here=dirname(fileURLToPath(import.meta.url));
app.setName('筱竹书瑾');
const explicitDataDir=app.commandLine.getSwitchValue('user-data-dir');
if(explicitDataDir)app.setPath('userData',resolve(explicitDataDir));
const smokeTest=app.commandLine.hasSwitch('shujin-smoke-test')&&!!explicitDataDir;
let win, workbench, xhs, origin, quitting=false;
if(!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance',()=>{if(win){if(win.isMinimized())win.restore();win.show();win.focus();}});
  app.whenReady().then(async()=>{
    win=new BrowserWindow({width:1440,height:960,minWidth:960,minHeight:680,title:'筱竹书瑾',icon:join(here,'icon.png'),backgroundColor:'#f5f6f8',show:false,
      webPreferences:{preload:join(here,'preload.cjs'),partition:'shujin-local',nodeIntegration:false,contextIsolation:true,sandbox:true}});
    win.removeMenu();
    xhs=new DesktopXhs(win);
    workbench=await startPythonBackend({root:join(here,'..'),resources:process.resourcesPath,packaged:app.isPackaged,dataDir:app.getPath('userData'),
      native:async(method,params)=>{
        if(method==='pick-folder'){const result=await dialog.showOpenDialog(win,{title:'导入本地项目',properties:['openDirectory']});return {path:result.canceled?'':result.filePaths[0]};}
        if(method==='xhs:disconnect')return xhs.disconnect();
        throw Error('不支持的客户端操作。');
      },onExit:(code,detail)=>{if(!quitting){dialog.showErrorBox('Python 后端已退出','请重新启动客户端。\n'+detail);app.quit();}}});
    origin=workbench.origin;
    await win.webContents.session.cookies.set({url:origin,name:'shujin_session',value:workbench.token,httpOnly:true,sameSite:'strict'});
    const trusted=event=>{
      if(event.sender!==win.webContents || event.senderFrame!==win.webContents.mainFrame || new URL(event.senderFrame.url).origin!==origin) throw Error('此页面不允许调用客户端接口。');
    };
    ipcMain.handle('xhs:open',async(event,bounds)=>{trusted(event);xhs.setBounds(bounds);return xhs.open();});
    ipcMain.handle('xhs:bounds',async(event,bounds)=>{trusted(event);return xhs.setBounds(bounds);});
    ipcMain.handle('xhs:zoom',async(event,factor)=>{trusted(event);return xhs.setZoomFactor(factor);});
    ipcMain.handle('xhs:hide',async event=>{trusted(event);return xhs.hide();});
    ipcMain.handle('xhs:resume',async(event,bounds)=>{trusted(event);xhs.setBounds(bounds);return xhs.show();});
    ipcMain.handle('xhs:close',async event=>{trusted(event);return xhs.close();});
    win.webContents.on('did-start-loading',()=>void xhs.close());
    win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
    win.webContents.on('will-navigate',(event,url)=>{if(new URL(url).origin!==origin)event.preventDefault();});
    win.on('close',event=>{if(!quitting){event.preventDefault();app.quit();}});
    let launched=false;
    const finishLoad=async()=>{
      if(launched || !win || win.isDestroyed())return;
      launched=true;
      if(!smokeTest)win.show();
    };
    win.webContents.once('dom-ready',()=>void finishLoad().catch(error=>{dialog.showErrorBox('客户端验证失败',error.message);app.exit(1);}));
    void win.loadURL(origin+'/#developer').catch(error=>{if(!launched){dialog.showErrorBox('客户端启动失败',error.message);app.exit(1);}});
  }).catch(error=>{dialog.showErrorBox('客户端启动失败',error.message);app.exit(1);});
  app.on('before-quit',event=>{
    if(quitting)return;
    event.preventDefault();quitting=true;
    Promise.resolve(workbench?.stop()).then(()=>xhs?.close()).finally(()=>app.quit());
  });
  app.on('window-all-closed',()=>app.quit());
}
