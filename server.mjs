import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { AccountError, XhsBrowser } from './xhs-browser.mjs';
import { DevError, DevWorkspace } from './dev-agent.mjs';

const root = fileURLToPath(new URL('.', import.meta.url));
const port = Number(process.env.PORT || 3000);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8' };
const publicFiles = new Set(['/index.html', '/styles.css', '/desktop.css', '/account.css', '/app.js', '/account.js', '/developer.js', '/developer.css', '/desktop-client.js', '/desktop-client.css']);
function json(response, status, data) {
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  response.end(JSON.stringify(data));
}

export function createWorkbench({ xhs = new XhsBrowser({profileDir:resolve(root,'.local/xiaohongshu-profile')}), dev = new DevWorkspace({dataDir:resolve(root,'.local/developer')}), allowedPort = port, desktopToken = '' } = {}) {
  const server = createServer(async (request, response) => {
    try {
      const activePort = allowedPort || server.address()?.port;
      const origins = ['http://localhost:' + activePort, 'http://127.0.0.1:' + activePort, 'http://[::1]:' + activePort];
      const host = request.headers.host;
      if (!origins.includes('http://' + host)) return json(response, 403, { error: '仅支持本机访问。' });
      const url = new URL(request.url, 'http://' + host);
      if (desktopToken && !(request.headers.cookie || '').split(';').some(part => part.trim() === 'shujin_session=' + desktopToken)) return json(response, 403, { error: '此服务仅允许桌面客户端访问。' });
      const pathname = decodeURIComponent(url.pathname);
      if (pathname.startsWith('/api/')) {
        if ((request.headers.origin && !origins.includes(request.headers.origin)) || request.headers['sec-fetch-site'] === 'cross-site') return json(response, 403, { error: '不允许其他站点访问本机账号。' });
        if (pathname.startsWith('/api/dev/')) return json(response, 200, await dev.handle(request, pathname, url));
        if (pathname === '/api/xhs/status' && request.method === 'GET') return json(response, 200, await xhs.status());
        const actions = {
          '/api/xhs/connect': () => xhs.connect(),
          '/api/xhs/login/refresh': () => xhs.connect(true),
          '/api/xhs/recommendations': () => xhs.recommendations(url.searchParams.get('more') === '1'),
          '/api/xhs/messages': () => xhs.messages(url.searchParams.get('kind') === 'private' ? 'private' : 'notifications', url.searchParams.get('open') === '1'),
          '/api/xhs/disconnect': () => xhs.disconnect()
        };
        if (!Object.hasOwn(actions, pathname)) return json(response, 404, { error: '接口不存在。' });
        if (request.method !== 'POST') return json(response, 405, { error: '请使用 POST 请求。' });
        return json(response, 200, await actions[pathname]());
      }
      if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405).end(); return; }
      const file = pathname === '/' ? '/index.html' : pathname;
      if (!publicFiles.has(file)) { response.writeHead(404).end('Not found'); return; }
      const body = await readFile(resolve(root, '.' + file));
      response.writeHead(200, { 'Content-Type': types[extname(file)], 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy':'no-referrer' }).end(request.method === 'HEAD' ? undefined : body);
    } catch (error) {
      json(response, error instanceof AccountError || error instanceof DevError ? error.status : 500, { error: error instanceof AccountError || error instanceof DevError ? error.message : '服务暂时不可用，请重试。' });
    }
  });
  return {server, xhs, dev, close:async () => { await dev.shutdown(); await xhs.close(); if(server.listening) await new Promise(resolve => server.close(resolve)); }};
}
const workbench = process.versions.electron ? null : createWorkbench();
export const server = workbench?.server;
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  server.listen(port, 'localhost', () => console.log('筱竹书瑾 running at http://localhost:' + port));
  const shutdown = async () => { await workbench.close(); process.exit(0); };
  process.on('SIGINT', shutdown); process.on('SIGTERM', shutdown);
}
