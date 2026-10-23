import { WebContentsView, session, nativeImage } from 'electron';
import { AccountError, readAccount, readLoginPanel, readLoginQr, readRecommendations, readMessagePanel } from '../xhs-browser.mjs';
const HOME = 'https://www.xiaohongshu.com/explore';
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
export function officialUrl(value) {
  try { const u = new URL(value); return u.protocol === 'https:' && u.hostname === 'www.xiaohongshu.com'; } catch { return false; }
}

// A normal, visible, persistent official page. No headless/automation flags or cookie import.
export class DesktopXhs {
  constructor(win, { partition = 'persist:xiaozhu-xhs' } = {}) {
    this.win = win; this.partition = partition; this.view = null; this.visible = false; this.busy = false; this.error = ''; this.loaded = false;
    this.account = {}; this.login = {status:'idle', image:'', message:''}; this.loginStartedAt=0; this.qrFingerprint='';
    win.on('resize', () => this.resize());
  }
  ensure() {
    if (this.view && !this.view.webContents.isDestroyed()) return;
    this.view = new WebContentsView({webPreferences:{partition:this.partition, nodeIntegration:false, contextIsolation:true, sandbox:true, backgroundThrottling:false}});
    this.win.contentView.addChildView(this.view);
    this.view.setVisible(false);
    this.view.webContents.setWindowOpenHandler(({url}) => { if(officialUrl(url)) void this.navigate(url).catch(()=>{}); return {action:'deny'}; });
    this.view.webContents.on('will-navigate', (event, url) => { if(!officialUrl(url)) event.preventDefault(); });
    this.view.webContents.on('will-redirect', (event, url) => { if(!officialUrl(url)) event.preventDefault(); });
    this.view.webContents.on('did-fail-load', (_e, code, description, _url, mainFrame) => {
      if(mainFrame && code !== -3) { this.error = '官网加载失败：' + description; this.notify(); }
    });
    this.view.webContents.on('did-navigate', () => { this.account={}; this.notify(); });
    this.view.webContents.on('dom-ready', () => { this.loaded=officialUrl(this.view.webContents.getURL()); if(this.loaded)this.error=''; this.notify(); });
    this.view.webContents.on('did-navigate-in-page', () => this.notify());
    this.view.webContents.session.setPermissionRequestHandler((_wc, _permission, callback) => callback(false));
    this.resize();
  }
  resize() {
    if(!this.view || this.win.isDestroyed()) return;
    const [width,height] = this.win.getContentSize();
    this.view.setBounds({x:16,y:108,width:Math.max(1,width-32),height:Math.max(1,height-124)});
  }
  notify() {
    if(!this.win.isDestroyed()) this.win.webContents.send('xhs:view', {visible:this.visible, url:this.view?.webContents.getURL() || HOME, error:this.error});
  }
  show() { this.ensure(); this.visible=true; this.resize(); this.notify(); this.view.setVisible(true); }
  hide() { this.visible=false; this.view?.setVisible(false); this.notify(); }
  async evaluate(fn, arg) {
    if(!this.view || !officialUrl(this.view.webContents.getURL())) throw new AccountError('请先在客户端打开小红书官网。',401);
    return this.view.webContents.mainFrame.executeJavaScript('(' + fn.toString() + ')(' + JSON.stringify(arg ?? null) + ')');
  }
  async exclusive(action) {
    if(this.busy)throw new AccountError('正在处理上一项操作，请稍后重试。',409);
    this.busy=true;
    try{return await action();}finally{this.busy=false;}
  }
  restore() {
    if(this.restoring)return this.restoring;
    this.restoring=this.exclusive(async()=>{
    if((await session.fromPartition(this.partition).cookies.get({url:HOME})).length) {
      await this.navigate(HOME);await this.status(true);
    }
    }).finally(()=>{this.restoring=null;});
    return this.restoring;
  }
  async navigate(url = HOME) {
    if(!officialUrl(url)) throw new AccountError('仅支持打开小红书官方页面。');
    this.ensure(); this.error='';
    this.account={}; this.qrFingerprint=''; this.loginStartedAt=Date.now(); this.login={status:'loading',image:'',message:''};
    const wc=this.view.webContents;
    let timer,ready;
    const documentReady=new Promise((resolve,reject)=>{
      ready=()=>resolve();wc.once('dom-ready',ready);
      timer=setTimeout(()=>reject(new Error('加载超时')),30000);
    });
    try {
      // The login document can work while unrelated resources are still loading.
      await Promise.race([wc.loadURL(url),documentReady]); this.loaded=true; this.error='';
    } catch {
      const usable=await this.evaluate(()=>!!document.querySelector('#app')&&!location.href.startsWith('chrome-error:')).catch(()=>false);
      if(usable){this.loaded=true;this.error='';return;}
      this.error='小红书官网未能加载，请在客户端内点击刷新重试。'; throw new AccountError(this.error,502);
    } finally {clearTimeout(timer);wc.removeListener('dom-ready',ready);this.notify();}
  }
  async open(url = HOME) { await this.restoring; return this.exclusive(async()=>{this.show(); if(!this.loaded || this.view.webContents.getURL() !== url) await this.navigate(url); return {...await this.status(true),busy:false};}); }
  async status(force = false) {
    if(this.view && officialUrl(this.view.webContents.getURL()) && (!this.busy || force)) {
      try {
        this.account = await this.evaluate(readAccount);
        const panel = await this.evaluate(readLoginPanel);
        const state=this.account.loggedIn?'connected':panel.restricted||this.account.verification?'restricted':panel.expired?'expired':panel.scanned?'scanned':'loading';
        if(state!=='loading') this.login={status:state,image:'',message:panel.message || (state==='restricted'?'请打开官方页面完成验证。':'')};
        else {
          const qr=await this.evaluate(readLoginQr);
          if(qr) {
            if(!qr.fingerprint || qr.fingerprint!==this.qrFingerprint || !this.login.image) {
              let image=qr.image;
              if(!image) {
                const source=new URL(qr.source);
                if(source.protocol!=='https:' || !/(^|\.)(xiaohongshu\.com|xhscdn\.com)$/.test(source.hostname)) throw new Error('Unsupported QR source');
                const response=await this.view.webContents.session.fetch(source.href,{signal:AbortSignal.timeout(8000)});
                if(!response.ok) throw new Error('QR image unavailable');
                const decoded=nativeImage.createFromBuffer(Buffer.from(await response.arrayBuffer()));
                if(decoded.isEmpty()) throw new Error('QR image is empty');
                image=decoded.toDataURL();
              }
              this.login={status:'ready',image,message:'打开手机小红书，扫描二维码登录。'};
              this.qrFingerprint=qr.fingerprint;
            }
          } else this.login={status:Date.now()-this.loginStartedAt>45000?'error':'loading',image:'',message:'官网暂未提供二维码，可刷新重试或打开官方页面查看。'};
        }
      } catch {
        this.account={};
        this.login={status:Date.now()-this.loginStartedAt>45000?'error':'loading',image:'',message:'二维码暂未加载完成，请刷新重试或打开官网查看。'};
      }
    }
    return {status:!this.view?'disconnected':this.account.loggedIn?'connected':this.account.verification||this.login.status==='restricted'?'verification_required':'awaiting_login',
      name:this.account.name||'', accountId:this.account.accountId||'', busy:this.busy, profileSaved:!!this.view || (await session.fromPartition(this.partition).cookies.get({url:HOME})).length>0, error:this.error, mode:'desktop', login:this.login};
  }
  async connect(refresh = false) {
    await this.restoring;
    return this.exclusive(async()=>{
    this.ensure();
    if(!this.loaded || refresh) await this.navigate(HOME);
    // Login is initiated through the site's own button and UI.
    await this.evaluate(() => {
      const visible = n => n.getClientRects().length;
      if([...document.querySelectorAll('.login-container,.login-modal,.login-box')].some(visible)) return;
      const button = [...document.querySelectorAll('button,.login-btn')].find(n=>visible(n)&&n.innerText.trim()==='登录');
      button?.click();
    }).catch(()=>{});
    return {...await this.status(true),busy:false};
    });
  }
  async requireLogin() {
    const state=await this.status(true);
    if(state.status!=='connected') { this.show(); throw new AccountError('请在客户端内的官方页面扫码登录或完成验证后重试。',401); }
  }
  async recommendations(more = false) {
    return this.exclusive(async()=>{
    await this.requireLogin();
    if(!new URL(this.view.webContents.getURL()).pathname.startsWith('/explore')) await this.navigate(HOME);
    else if(more) { await this.evaluate(()=>window.scrollBy(0,Math.max(800,innerHeight*1.5))); await pause(1000); }
    for(let i=0;i<15;i++) {
      await this.requireLogin();
      const items=await this.evaluate(readRecommendations);
      if(items.length) return {items,updatedAt:new Date().toISOString()};
      await pause(500);
    }
    return {items:[],updatedAt:new Date().toISOString()};
    });
  }
  async messages(kind='notifications', openOnly=false) {
    return this.exclusive(async()=>{
    await this.requireLogin();
    if(openOnly) this.show();
    if(!(await this.evaluate(readMessagePanel,kind)).readable) {
      const clicked=await this.evaluate(kind=>{
        const label=kind==='private'?'消息':'通知';
        const visible=n=>n.getClientRects().length;
        const target=[...document.querySelectorAll('.channel-list-content a, .side-bar-component, button')].find(n=>visible(n)&&n.innerText.trim()===label);
        if(target) {target.click();return true;} return false;
      },kind);
      if(!clicked) { this.show(); return {readable:false,items:[],text:'请在客户端内使用官网的消息入口。',kind,updatedAt:new Date().toISOString()}; }
      await pause(1200);
    }
    await this.requireLogin();
    return {...await this.evaluate(readMessagePanel,kind),kind,updatedAt:new Date().toISOString()};
    });
  }
  async disconnect() {
    return this.exclusive(async()=>{
    await this.close();
    const profile=session.fromPartition(this.partition);
    await profile.clearStorageData(); await profile.clearCache();
    this.account={}; this.loaded=false; this.login={status:'idle',image:'',message:''}; this.error='';
    return {...await this.status(),profileSaved:false,busy:false};
    });
  }
  async close() {
    this.hide();
    if(this.view) { this.win.contentView.removeChildView(this.view); this.view.webContents.close(); this.view=null; }
    await session.fromPartition(this.partition).cookies.flushStore();
  }
}
