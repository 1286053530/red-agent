import { session, shell, WebContentsView } from 'electron';

const HOME = 'https://www.xiaohongshu.com/explore';
const DISABLED = '自动化访问已停用，请在官方页面中手动操作。';
class AccountError extends Error { constructor(message,status=410){super(message);this.status=status;} }

export function officialUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && url.hostname === 'www.xiaohongshu.com' && !url.username && !url.password && !url.port;
  } catch { return false; }
}

// A manual browser surface only: no DOM access, login checks or content tools.
export class DesktopXhs {
  constructor(win, { partition = 'persist:xiaozhu-manual-v1', openExternal = url => shell.openExternal(url) } = {}) {
    this.win = win;
    this.partition = partition;
    this.openExternal = openExternal;
    this.view = null;
    this.visible = false;
    this.error = '';
    this.clearing = false;
    const profile = session.fromPartition(partition);
    // Deny background traffic, including any worker left by a previously open page.
    profile.webRequest.onBeforeRequest((details,callback)=>callback({cancel:!this.view || !this.visible || this.win?.isMinimized()===true}));
    profile.setPermissionRequestHandler((_contents,_permission,callback)=>callback(false));
    profile.setPermissionCheckHandler(()=>false);
    profile.on('will-download',event=>event.preventDefault());
    win?.on('resize',()=>this.resize());
    win?.on('minimize',()=>void this.close());
    win?.on('hide',()=>void this.close());
  }
  resize() {
    if(!this.view || !this.win || this.win.isDestroyed())return;
    const [width,height]=this.win.getContentSize();
    this.view.setBounds({x:0,y:104,width:Math.max(1,width),height:Math.max(1,height-104)});
  }
  notify() {
    if(this.win&&!this.win.isDestroyed())this.win.webContents.send('xhs:view',{visible:this.visible,error:this.error,url:this.view?.webContents.getURL()||HOME});
  }
  async status() {
    return { status:'automation_disabled', automationEnabled:false, manualOnly:true, name:'', accountId:'', busy:false,
      profileSaved:false, error:'', mode:'manual_embedded', login:{status:'disabled',image:'',message:DISABLED} };
  }
  async open(url = HOME) {
    if (url !== HOME) throw new AccountError('仅支持手动打开小红书官网首页。',400);
    if(this.closing)await this.closing;
    if(this.clearing)throw new AccountError('正在清理本软件登录数据，请稍后再打开。',409);
    if(!this.win||this.win.isDestroyed())throw new AccountError('工作台窗口不可用。',409);
    if(this.view&&!this.view.webContents.isDestroyed())return {opened:true,mode:'manual_embedded'};
    const view=new WebContentsView({webPreferences:{partition:this.partition,nodeIntegration:false,contextIsolation:true,sandbox:true}});
    this.view=view;this.visible=true;this.error='';
    const wc=view.webContents;
    wc.setWindowOpenHandler(()=>{this.error='此链接需要新窗口，请按需使用系统浏览器。';this.notify();return {action:'deny'};});
    const restrict=(event,target)=>{if(!officialUrl(target)){event.preventDefault();this.error='此页面需要站外跳转，请按需使用系统浏览器。';this.notify();}};
    wc.on('will-navigate',restrict);wc.on('will-redirect',restrict);
    wc.on('did-navigate',()=>this.notify());
    this.win.contentView.addChildView(view);this.resize();this.notify();
    try {await wc.loadURL(HOME);}
    catch(error){
      if(this.view!==view)return {opened:false,closed:true};
      this.error='官网未能加载。请返回工作台，或手动使用系统浏览器；不会自动重试。';
      this.notify();throw new AccountError(this.error,502);
    }
    return {opened:true,mode:'manual_embedded'};
  }
  async openInBrowser() {
    await this.close();
    await this.openExternal(HOME);
    return {opened:true,mode:'external'};
  }
  async connect() { throw new AccountError(DISABLED); }
  async recommendations() { throw new AccountError(DISABLED); }
  async messages() { throw new AccountError(DISABLED); }
  async disconnect() {
    this.clearing=true;
    try {
      await this.close();
      // Explicit local cleanup of this app's current and legacy partitions only.
      for(const partition of new Set([this.partition,'persist:xiaozhu-xhs'])){
        const profile=session.fromPartition(partition);
        await profile.clearStorageData();await profile.clearCache();
      }
      return this.status();
    }finally{this.clearing=false;}
  }
  async close() {
    const view=this.view;
    if(!view){if(this.closing)await this.closing;return;}
    this.view=null;this.visible=false;this.error='';
    if(view&&!view.webContents.isDestroyed()){
      view.webContents.stop();
      if(this.win&&!this.win.isDestroyed())this.win.contentView.removeChildView(view);
      view.webContents.close({waitForBeforeUnload:false});
    }
    this.notify();
    const closing=session.fromPartition(this.partition).closeAllConnections();
    this.closing=closing;
    try {await closing;}finally{if(this.closing===closing)this.closing=null;}
  }
}
