import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { join } from 'node:path';

export function startPythonBackend({ root, resources, packaged = false, dataDir, native, onExit = () => {} }) {
  const executable = packaged ? join(resources, 'backend', 'shujin-backend.exe')
    : process.env.SHUJIN_PYTHON || (existsSync(join(root, '.venv', 'Scripts', 'python.exe')) ? join(root, '.venv', 'Scripts', 'python.exe')
      : existsSync(join(root, '.venv', 'bin', 'python')) ? join(root, '.venv', 'bin', 'python') : 'python');
  const assets = packaged ? join(resources, 'frontend') : root;
  const args = [...(packaged ? [] : ['-m', 'backend']), '--desktop', '--port', '0', '--data-dir', dataDir, '--assets', assets];
  const env = { ...process.env, PYTHONUTF8: '1', SHUJIN_NODE_EXEC: process.execPath, SHUJIN_NODE_IS_ELECTRON: process.versions.electron ? '1' : '0' };
  delete env.ELECTRON_RUN_AS_NODE;
  const child = spawn(executable, args, { cwd: packaged ? resources : root, env, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'] });
  let ready = false, closed = false, stopping = false, diagnostics = '';
  child.stderr.setEncoding('utf8');
  child.stderr.on('data', chunk => { diagnostics = (diagnostics + chunk).slice(-8000); });
  // No user/model request can select an arbitrary native method.
  const allowed = new Set(['pick-folder', 'xhs:disconnect']);
  const lines = createInterface({ input: child.stdout });
  const exited = new Promise(resolve => child.once('close', (code, signal) => { closed = true; lines.close(); resolve({ code, signal }); if (!stopping) onExit(code, diagnostics); }));
  const startup = new Promise((resolve, reject) => {
    const timer = setTimeout(() => { reject(new Error('Python 后端启动超时。' + diagnostics)); void stop(); }, 120000);
    child.once('error', error => { clearTimeout(timer); reject(new Error('无法启动 Python 后端：' + error.message)); });
    child.once('close', code => { clearTimeout(timer); if (!ready) reject(new Error('Python 后端启动失败（' + code + '）：' + diagnostics)); });
    lines.on('line', async line => {
      let message;
      try { message = JSON.parse(line); } catch { return; }
      if (message.type === 'ready' && !ready) {
        const url = new URL(message.origin);
        if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !/^[a-f0-9]{64}$/.test(message.token)) {
          clearTimeout(timer); reject(new Error('Python 后端返回了无效启动信息。')); void stop(); return;
        }
        ready = true; clearTimeout(timer); resolve({ ...message, stop, child }); return;
      }
      if (message.type !== 'native' || typeof message.id !== 'string' || stopping) return;
      let reply;
      try {
        if (!allowed.has(message.method)) throw new Error('不支持的客户端操作。');
        reply = { id: message.id, result: await native(message.method, message.params || {}) };
      } catch (error) { reply = { id: message.id, error: error.message, status: error.status || 500 }; }
      if (!closed && !child.stdin.destroyed) child.stdin.write(JSON.stringify(reply) + '\n');
    });
  });
  async function stop() {
    if (stopping) return exited;
    stopping = true;
    if (!closed && !child.stdin.destroyed) child.stdin.end(JSON.stringify({ type: 'shutdown' }) + '\n');
    const timeout = setTimeout(() => { if (!closed) child.kill(); }, 10000);
    timeout.unref();
    const result = await exited;
    clearTimeout(timeout);
    return result;
  }
  return startup;
}
