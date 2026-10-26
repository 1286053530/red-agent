import { session, WebContentsView } from 'electron';

const HOME = 'https://www.xiaohongshu.com/explore';
const PAGE_ZOOM = 0.8;
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
  constructor(win, { partition = 'persist:xiaozhu-manual-v1' } = {}) {
    this.win = win;
    this.partition = partition;
    this.view = null;
    this.visible = false;
    this.requestedVisible = false;
    this.error = '';
    this.clearing = false;
    this.bounds = null;
    this.zoomFactor = PAGE_ZOOM;
    const profile = session.fromPartition(partition);
    // An explicitly opened page may keep its normal connections while retained.
    // Closing it still blocks all subsequent partition traffic, including workers.
    profile.webRequest.onBeforeRequest((details,callback)=>callback({cancel:!this.view}));
    profile.setPermissionRequestHandler((_contents,_permission,callback)=>callback(false));
    profile.setPermissionCheckHandler(()=>false);
    profile.on('will-download',event=>event.preventDefault());
    win?.on('resize',()=>this.resize());
    win?.on('minimize',()=>this.suspend());
    win?.on('hide',()=>this.suspend());
    win?.on('restore',()=>{if(this.requestedVisible)this.show();});
    win?.on('show',()=>{if(this.requestedVisible)this.show();});
  }
  resize() {
    if(!this.view || !this.bounds || !this.win || this.win.isDestroyed())return;
    const [width,height]=this.win.getContentSize();
    const x=Math.min(Math.max(0,this.bounds.x),Math.max(0,width-1));
    const y=Math.min(Math.max(0,this.bounds.y),Math.max(0,height-1));
    this.view.setBounds({x,y,width:Math.max(1,Math.min(this.bounds.width,width-x)),height:Math.max(1,Math.min(this.bounds.height,height-y))});
  }
  setBounds(bounds) {
    if(!bounds || !['x','y','width','height'].every(key=>Number.isFinite(bounds[key])) || bounds.width<1 || bounds.height<1)
      throw new AccountError('官网显示区域无效。',400);
    this.bounds=Object.fromEntries(['x','y','width','height'].map(key=>[key,Math.round(bounds[key])]));
    this.resize();
    return {updated:true};
  }
  setZoomFactor(factor) {
    if(!Number.isFinite(factor)||factor<0.5||factor>PAGE_ZOOM)throw new AccountError('页面缩放应在 50% 至 80% 之间。',400);
    if(!this.view||this.view.webContents.isDestroyed())throw new AccountError('请先打开官网。',409);
    this.zoomFactor=Math.round(factor*100)/100;
    this.view.webContents.setZoomFactor(this.zoomFactor);
    this.notify();return {zoomFactor:this.zoomFactor};
  }
  notify() {
    if(this.win&&!this.win.isDestroyed())this.win.webContents.send('xhs:view',{visible:this.visible,retained:!!this.view&&!this.view.webContents.isDestroyed(),error:this.error,url:this.view?.webContents.getURL()||HOME,zoomFactor:this.zoomFactor});
  }
  show() {
    if(!this.view||this.view.webContents.isDestroyed())return {opened:false,retained:false};
    this.requestedVisible=true;
    this.visible=!this.win.isMinimized();
    this.view.setVisible(this.visible);
    this.resize();this.notify();
    return {opened:true,retained:true,mode:'manual_embedded'};
  }
  hide() {
    this.requestedVisible=false;this.visible=false;
    if(this.view&&!this.view.webContents.isDestroyed())this.view.setVisible(false);
    this.notify();return {retained:!!this.view};
  }
  suspend() {
    const requested=this.requestedVisible;
    this.hide();this.requestedVisible=requested;
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
    if(!this.bounds)throw new AccountError('请先指定官网的内嵌显示区域。',400);
    if(this.view&&!this.view.webContents.isDestroyed())return this.show();
    const view=new WebContentsView({webPreferences:{partition:this.partition,nodeIntegration:false,contextIsolation:true,sandbox:true}});
    this.view=view;this.visible=true;this.requestedVisible=true;this.error='';
    const wc=view.webContents;
    wc.setZoomFactor(this.zoomFactor);
    wc.on('did-finish-load',()=>wc.setZoomFactor(this.zoomFactor));
    wc.setWindowOpenHandler(({url})=>{
      if(!this.visible)return {action:'deny'};
      if(!officialUrl(url)){this.error='已阻止站外链接，仅支持在内嵌页访问小红书官网。';this.notify();return {action:'deny'};}
      // Reuse the existing isolated page, including links with target="_blank".
      setImmediate(()=>{
        if(this.view!==view||wc.isDestroyed())return;
        this.error='';this.notify();
        void wc.loadURL(url).catch(()=>{
          if(this.view!==view||wc.isDestroyed())return;
          this.error='链接未能加载，请在内嵌官网中手动重试。';this.notify();
        });
      });
      return {action:'deny'};
    });
    const restrict=(event,target)=>{if(!officialUrl(target)){event.preventDefault();this.error='已阻止站外跳转，仅支持在内嵌页访问小红书官网。';this.notify();}};
    wc.on('will-navigate',restrict);wc.on('will-redirect',restrict);
    wc.on('did-navigate',()=>this.notify());
    this.win.contentView.addChildView(view);this.resize();this.notify();
    try {await wc.loadURL(HOME);}
    catch(error){
      if(this.view!==view)return {opened:false,closed:true};
      this.error='官网未能加载。请返回工作台后手动重试；不会自动重试。';
      this.notify();throw new AccountError(this.error,502);
    }
    return {opened:true,mode:'manual_embedded'};
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
    this.view=null;this.visible=false;this.requestedVisible=false;this.error='';
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
