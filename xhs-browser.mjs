import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import { mkdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

const HOME = 'https://www.xiaohongshu.com/explore';
export class AccountError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}

// These functions run inside the official page and read rendered page content.
export function readAccount() {
  const visible = node => !!node && node.getClientRects().length > 0;
  const user = window.__INITIAL_STATE__?.user;
  const ownLink = [...document.querySelectorAll('.channel-list-content a, .user a, .user.side-bar-component a')]
    .find(node => /\/user\/profile\//.test(node.getAttribute('href') || '') && visible(node));
  const loggedIn = user?.loggedIn === true || !!ownLink;
  const info = user?.userInfo || {};
  return {
    loggedIn,
    accountId: loggedIn ? String(info.userId || info.user_id || info._id || ownLink?.getAttribute('href')?.split('/profile/')[1]?.split('?')[0] || '') : '',
    name: loggedIn ? (info.nickname || info.nickName || info.nick_name || ownLink?.innerText?.trim() || '我的小红书账号') : '',
    verification: [...document.querySelectorAll('iframe[src*="captcha"], .captcha-container, .verify-container, [role="dialog"][class*="verify"]')].some(visible) || /IP存在风险|安全限制|访问受限/.test(document.body?.innerText || ''),
    loginVisible: [...document.querySelectorAll('.login-container, .login-modal, .login-box')].some(visible)
  };
}

// Read only the official login panel. Never expose QR identifiers or cookies.
export function readLoginPanel() {
  const visible = node => !!node && node.getClientRects().length > 0;
  const body = document.body?.innerText || '';
  const restricted = /IP存在风险|安全限制|访问受限/.test(body);
  const panels = [...document.querySelectorAll('.login-container, .login-modal, .login-box, .login, [class*="login-container"], [class*="login-modal"], [class*="login-panel"]')].filter(visible);
  const panel = panels.find(n => /扫码|二维码/.test(n.innerText)) || panels[0];
  const text = panel?.innerText || '';
  return {
    restricted,
    message: restricted ? body.split('\n').filter(Boolean).slice(0,3).join(' · ').slice(0,240) : '',
    expired: /二维码.*(失效|过期)|(失效|过期).*二维码|点击刷新|重新获取二维码/.test(text),
    scanned: /扫描成功|扫码成功|已扫码|已扫描|手机.*确认|请.*确认登录/.test(text),
    visible: !!panel
  };
}

// Locate a loaded QR inside the official login panel, excluding avatars and icons.
export function readLoginQr() {
  const panels = document.querySelectorAll('.login-container, .login-modal, .login-box, [class*="login-panel"]');
  for (const panel of panels) {
    if (!panel.getClientRects().length) continue;
    for (const node of panel.querySelectorAll('img, canvas')) {
      const box = node.getBoundingClientRect();
      if (!node.getClientRects().length || box.width < 80 || box.height < 80 || Math.abs(box.width - box.height) > 8) continue;
      if (!/qr|code/i.test(node.className + ' ' + node.parentElement?.className) && node.tagName !== 'CANVAS') continue;
      if (node.tagName === 'IMG' && (!node.complete || !node.naturalWidth)) continue;
      let fingerprint = node.currentSrc || node.getAttribute('src') || '';
      let image = '';
      try {
        if (node.tagName === 'CANVAS') image = fingerprint = node.toDataURL('image/png');
        else {
          const canvas = document.createElement('canvas');
          canvas.width = node.naturalWidth; canvas.height = node.naturalHeight;
          canvas.getContext('2d').drawImage(node, 0, 0);
          image = canvas.toDataURL('image/png');
        }
      } catch { /* Cross-origin images use a native page capture instead. */ }
      return { image, fingerprint, source: node.tagName === 'IMG' ? node.currentSrc || node.src : '' };
    }
  }
  return null;
}

export function readRecommendations() {
  const safeUrl = (value, image = false) => {
    try {
      const url = new URL(value, location.origin);
      if (url.protocol !== 'https:') return '';
      if (image ? /\.(xhscdn\.com|xiaohongshu\.com)$/.test(url.hostname) : url.hostname === 'www.xiaohongshu.com') return url.href;
    } catch {}
    return '';
  };
  return [...document.querySelectorAll('.note-item')].slice(0, 60).map(node => {
    const link = node.querySelector('a.cover, a.title, a[href*="/explore/"]');
    const image = node.querySelector('.cover img');
    return {
      id: node.dataset.noteId || link?.pathname?.split('/').pop() || '',
      title: node.querySelector('.title')?.textContent?.trim() || '查看笔记',
      author: node.querySelector('.author .name, .author-wrapper .name')?.textContent?.trim() || '',
      cover: image ? safeUrl(image.currentSrc || image.getAttribute('src'), true) : '',
      url: link ? safeUrl(link.href) : '',
      likes: node.querySelector('.like-wrapper .count')?.textContent?.trim() || '',
      type: node.querySelector('.play-icon') ? '视频' : '图文'
    };
  }).filter(note => note.id && note.url);
}

export function readMessagePanel(kind) {
  const visible = node => !!node && node.getClientRects().length > 0;
  const selectors = kind === 'private'
    ? ['.conversation-list', '.chat-list', '[class*="conversation-list"]', '[class*="conversationList"]', '[class*="chat-list"]', '[class*="chatList"]', '.chat-container', '[class*="message-panel"]', '[class*="chat-panel"]', '[class*="im-container"]']
    : ['.notification-container', '.notification-list', '[class*="notification-list"]', '[class*="notification-panel"]', '[class*="notification-content"]', '[class*="interaction-list"]'];
  let panel;
  for (const selector of selectors) {
    panel = [...document.querySelectorAll(selector)].find(node => visible(node) && node.innerText?.trim());
    if (panel) break;
  }
  if (!panel) return { readable: false, text: '', items: [] };
  const candidates = [...panel.querySelectorAll('.interaction-item, .notification-item, .conversation-item, .chat-item, [class*="conversation-item"], [class*="chat-item"], [class*="interaction-item"]')].filter(visible);
  return {
    readable: true, text: panel.innerText.trim().slice(0, 16000),
    items: candidates.slice(0, 50).map((node, index) => ({ id: String(index), text: node.innerText.trim().slice(0, 1600) })).filter(item => item.text)
  };
}

export class XhsBrowser {
  constructor({ profileDir = resolve('.local/xiaohongshu-profile'), headless = true, browserType = chromium } = {}) {
    this.profileDir = profileDir; this.headless = headless; this.browserType = browserType;
    this.context = null; this.page = null; this.busy = false; this.area = '';
    this.account = { loggedIn: false, name: '', verification: false }; this.error = '';
    this.login = { status: 'idle', image: '', message: '' };
    this.loginStartedAt = 0; this.loginBusy = false; this.qrFingerprint = '';
  }
  async exclusive(action) {
    if (this.busy) throw new AccountError('正在处理上一项操作，请稍后重试。', 409);
    this.busy = true;
    try { this.error = ''; return await action(); }
    catch (error) {
      if (error instanceof AccountError) throw error;
      this.error = '小红书暂时未响应，请在当前页面重试。';
      throw new AccountError(this.error, 502);
    } finally { this.busy = false; }
  }
  async status() {
    if (this.page && !this.page.isClosed() && !this.busy) {
      if (this.page.url().startsWith('https://www.xiaohongshu.com/')) {
        try {
          this.account = await this.page.evaluate(readAccount);
          if (!this.account.loggedIn) await this.updateLogin();
        } catch {}
      } else this.account = { loggedIn: false, name: '', verification: false };
    }
    return {
      status: !this.context ? 'disconnected' : this.account.loggedIn ? 'connected' : this.account.verification || this.login.status === 'restricted' ? 'verification_required' : 'awaiting_login',
      name: this.account.name, accountId: this.account.accountId || '', busy: this.busy, profileSaved: existsSync(this.profileDir), error: this.error,
      login: this.account.loggedIn ? { status: 'connected', image: '', message: '登录成功' } : this.login
    };
  }
  async updateLogin() {
    if (this.loginBusy || !this.page || this.page.isClosed() || this.account.loggedIn) return;
    this.loginBusy = true;
    const page = this.page;
    try {
      if (!page.url().startsWith('https://www.xiaohongshu.com/')) return;
      const panel = await page.evaluate(readLoginPanel);
      if (panel.restricted || this.account.verification) {
        this.login = { status: 'restricted', image: '', message: panel.message || '小红书要求额外验证，当前无法获取登录二维码。请稍后重试。' };
        return;
      }
      if (panel.expired) { this.login = { status: 'expired', image: '', message: '二维码已过期，请刷新后重新扫码。' }; return; }
      if (panel.scanned) { this.login = { status: 'scanned', image: '', message: '已扫码，请在手机小红书上确认登录。' }; return; }
      const qr = page.locator('.login-container .qrcode-img, .login-container .qr-code img, .login-container .qrcode img, .login-container .qrcode canvas, .login-container canvas, .login-container img[class*="qr"], .login-container img[class*="code"], .login-modal canvas, .login-modal img[class*="qr"], .login-box canvas, .login-box img[class*="qr"], [class*="login"] [class*="qrcode"] img, [class*="login"] [class*="qr-code"] img, [class*="login"] [class*="qrcode"] canvas').filter({ visible: true }).first();
      if (await qr.count()) {
        const fingerprint = await qr.evaluate(node => node.tagName === 'CANVAS' ? node.toDataURL() : node.currentSrc || node.getAttribute('src') || '');
        const box = await qr.boundingBox();
        const loaded = await qr.evaluate(node => node.tagName === 'CANVAS' || (node.complete && node.naturalWidth > 0));
        if (loaded && fingerprint && box?.width >= 80 && box?.height >= 80) {
          if (fingerprint !== this.qrFingerprint || !this.login.image) {
            const buffer = await qr.screenshot({ type: 'png', timeout: 2500 });
            if (page !== this.page) return;
            this.qrFingerprint = fingerprint;
            this.login = { status: 'ready', image: 'data:image/png;base64,' + buffer.toString('base64'), message: '打开手机小红书，扫描二维码登录。' };
          }
          return;
        }
      }
      if (!panel.visible) {
        const button = page.getByText('登录', { exact: true }).first();
        if (await button.isVisible().catch(() => false)) await button.click({ timeout: 1500 });
        else {
          const notification = page.locator('.channel-list-content a').filter({ hasText: /^通知$/ }).first();
          // Only click once the site's own app is hydrated; earlier clicks do nothing.
          const hydrated = await page.evaluate(() => !!document.querySelector('#app')?.__vue_app__ || document.readyState === 'complete');
          if (hydrated && await notification.isVisible().catch(() => false)) await notification.click({ timeout: 1500 });
        }
      }
      if (Date.now() - this.loginStartedAt > 150000) this.login = { status: 'error', image: '', message: '官网暂未提供登录二维码，请点击刷新二维码重试。' };
      else this.login = { status: 'loading', image: '', message: '正在加载小红书官方登录二维码，请稍候…' };
    } finally { this.loginBusy = false; }
  }
  async connect(refresh = false) {
    return this.exclusive(async () => {
      this.loginStartedAt = Date.now();
      if (!this.context) {
        await mkdir(this.profileDir, { recursive: true });
        try {
          this.context = await this.browserType.launchPersistentContext(this.profileDir, {
            channel: process.env.XHS_BROWSER_CHANNEL || 'msedge', headless: this.headless,
            viewport: { width: 1280, height: 850 }, locale: 'zh-CN'
          });
        } catch {
          throw new AccountError('无法启动浏览器。请安装 Microsoft Edge，或设置 XHS_BROWSER_CHANNEL=chrome 后重启服务。', 503);
        }
        const context = this.context;
        context.on('close', () => {
          if (this.context === context) {
            this.context = null; this.page = null; this.account = { loggedIn: false, name: '', verification: false };
          }
        });
        this.page = context.pages()[0] || await context.newPage();
        await this.page.goto(HOME, { waitUntil: 'commit', timeout: 25000 });
      }
      if (!this.page || this.page.isClosed()) {
        this.page = await this.context.newPage();
        await this.page.goto(HOME, { waitUntil: 'commit', timeout: 25000 });
      }
      if (!this.page.url().startsWith('https://www.xiaohongshu.com/')) await this.page.goto(HOME, { waitUntil: 'commit', timeout: 25000 });
      if (refresh) await this.page.reload({ waitUntil: 'commit', timeout: 25000 });
      this.login = { status: 'loading', image: '', message: '正在加载小红书官方登录二维码，请稍候…' }; this.qrFingerprint = '';
      this.account = await this.page.evaluate(readAccount);
      if (!this.account.loggedIn) await this.updateLogin();
      return { ...(await this.status()), busy: false };
    });
  }
  async requireLogin() {
    if (!this.page || this.page.isClosed() || !this.context) throw new AccountError('请先在账号页扫码登录小红书。', 401);
    if (!this.page.url().startsWith('https://www.xiaohongshu.com/')) throw new AccountError('请在连接的浏览器中返回小红书官网后重试。', 401);
    this.account = await this.page.evaluate(readAccount);
    if (this.account.verification) throw new AccountError('小红书当前要求额外验证，请查看账号页的登录状态。', 401);
    if (!this.account.loggedIn) throw new AccountError('还未检测到账号登录，请在账号页扫码并在手机确认。', 401);
  }
  async recommendations(more = false) {
    return this.exclusive(async () => {
      await this.requireLogin();
      if (!more || this.area !== 'recommendations' || !new URL(this.page.url()).pathname.startsWith('/explore')) {
        await this.page.goto(HOME, { waitUntil: 'commit', timeout: 25000 });
      } else {
        await this.page.evaluate(() => window.scrollBy(0, Math.max(800, innerHeight * 1.5)));
        await this.page.waitForTimeout(1100);
      }
      await this.page.locator('.note-item').first().waitFor({ timeout: 18000 });
      await this.page.waitForFunction(() => window.__INITIAL_STATE__?.user?.loggedIn === true || !!document.querySelector('.channel-list-content a[href*="/user/profile/"]'), null, { timeout: 10000 }).catch(() => {});
      await this.requireLogin();
      this.area = 'recommendations';
      return { items: await this.page.evaluate(readRecommendations), updatedAt: new Date().toISOString() };
    });
  }
  async messages(kind = 'notifications', openOnly = false) {
    return this.exclusive(async () => {
      await this.requireLogin();
      const label = kind === 'private' ? '消息' : '通知';
      const entry = this.page.locator('.channel-list-content a').filter({ hasText: new RegExp('^' + label + '$') }).first();
      const target = await entry.count() ? entry : this.page.getByText(label, { exact: true }).first();
      if (!await target.isVisible().catch(() => false)) throw new AccountError('未找到官网消息入口，请在官方窗口中手动打开消息后重试。', 422);
      if (!(await this.page.evaluate(readMessagePanel, kind)).readable) {
        await target.click({ timeout: 6000 });
        await this.page.waitForTimeout(900);
      }
      await this.requireLogin();
      this.area = kind;
      if (openOnly) await this.page.bringToFront();
      let panel = await this.page.evaluate(readMessagePanel, kind);
      if (!panel.readable) { await this.page.waitForTimeout(1200); panel = await this.page.evaluate(readMessagePanel, kind); }
      return { ...panel, kind, updatedAt: new Date().toISOString() };
    });
  }
  async disconnect() {
    return this.exclusive(async () => {
      if (this.context) await this.context.close();
      this.context = null; this.page = null; this.account = { loggedIn: false, name: '', verification: false };
      await rm(this.profileDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
      this.login = { status: 'idle', image: '', message: '' }; this.qrFingerprint = '';
      return { status: 'disconnected', name: '', busy: false, profileSaved: false, error: '', login: this.login };
    });
  }
  async close() { if (this.context) await this.context.close(); }
}
