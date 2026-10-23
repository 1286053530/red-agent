import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { delimiter, dirname, join } from 'node:path';

export const CHECK_SCRIPTS = ['test', 'build', 'lint', 'typecheck', 'check'];
export function validateCommand(command, args = []) {
  if (!Array.isArray(args) || args.length > 30 || args.some(a => typeof a !== 'string' || a.length > 500 || /[\x00-\x1f]/.test(a))) throw Error('命令参数格式无效。');
  if (command === 'node' && ['--test', '--check'].includes(args[0]) && (args[0] !== '--check' || args.length === 2) && args.slice(1).every(a => !a.startsWith('-'))) return;
  if (command === 'npm' && ((args.length === 1 && args[0] === 'test') || (args.length === 2 && args[0] === 'run' && CHECK_SCRIPTS.includes(args[1])))) return;
  throw Error('当前仅支持 node --test / --check，以及 npm 的 test、build、lint、typecheck、check 脚本。安装依赖、删除、发布和任意 shell 命令不在自动执行范围。');
}

// No shell interpolation. This is a command policy, not an OS sandbox: project checks execute trusted project code.
export function runProcess({ command, args, cwd, signal, timeoutMs = 60000, onOutput = () => {}, onStart = () => {} }) {
  validateCommand(command, args);
  timeoutMs = Math.min(120000, Math.max(100, Number(timeoutMs) || 60000));
  const env = {};
  const allowed = /^(?:PATH|PATHEXT|SYSTEMROOT|WINDIR|COMSPEC|TEMP|TMP|HOME|USERPROFILE|APPDATA|LOCALAPPDATA|PROGRAMFILES|PROGRAMFILES\(X86\)|LANG|LC_ALL)$/i;
  for (const [key, value] of Object.entries(process.env)) if (allowed.test(key)) env[key] = value;
  env.CI = '1'; env.NO_COLOR = '1';
  env.PATH = dirname(process.execPath) + delimiter + (env.Path || env.PATH || '');
  if (process.versions.electron) env.ELECTRON_RUN_AS_NODE = '1';
  let runtimeArgs = args;
  if (command === 'node' && args[0] === '--test') runtimeArgs = ['--test', '--test-reporter=' + new URL('./agent-test-reporter.mjs', import.meta.url).href, ...args.slice(1)];
  if (command === 'npm') {
    const paths=[dirname(process.execPath),...(process.env.Path || process.env.PATH || '').split(delimiter)];
    const cli=paths.map(path=>join(path,'node_modules/npm/bin/npm-cli.js')).find(path=>existsSync(path));
    if(!cli)throw Error('没有找到本机 npm。可用内置 node --test 验证，或安装 Node.js 后运行 npm 检查。');
    runtimeArgs=[cli,...args];
  }
  return new Promise(resolve => {
    const start = Date.now();
    let output = '', bytes = 0, reason = '', spawnError = '', finished = false, timer, killer;
    const child = spawn(process.execPath, runtimeArgs, { cwd, env, windowsHide: true, shell: false, detached: process.platform !== 'win32', stdio: ['ignore', 'pipe', 'pipe'] });
    const terminate = why => {
      if (finished || reason) return;
      reason = why;
      if (process.platform === 'win32' && child.pid) {
        const kill = spawn('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
        kill.on('error', () => child.kill());
        kill.on('exit', code => { if (code) child.kill(); });
      } else if (child.pid) { try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill('SIGKILL'); } }
      killer = setTimeout(() => child.kill('SIGKILL'), 2000); killer.unref();
    };
    const append = chunk => {
      bytes += Buffer.byteLength(chunk);
      const text = chunk;
      output = (output + text).slice(-24000);
      onOutput({ text: text.slice(-24000), output, bytes, truncated: bytes > 24000 });
      if (bytes > 2 * 1024 * 1024) terminate('output_limit');
    };
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data', append); child.stderr.on('data', append);
    child.once('spawn', () => onStart(child.pid));
    child.once('error', error => { spawnError = error.message; });
    const abort = () => terminate('interrupted');
    signal?.addEventListener('abort', abort, { once: true });
    if (signal?.aborted) abort();
    timer = setTimeout(() => terminate('timed_out'), timeoutMs);
    child.once('close', (exitCode, exitSignal) => {
      finished = true; clearTimeout(timer); clearTimeout(killer); signal?.removeEventListener('abort', abort);
      const evidence = output.match(/SHUJIN_TEST_EVIDENCE (\{[^\n]+\})/g)?.at(-1);
      let passedTests = null;
      try { const value = evidence && JSON.parse(evidence.slice('SHUJIN_TEST_EVIDENCE '.length)).passed; if (Number.isSafeInteger(value) && value >= 0) passedTests = value; } catch { /* Untrusted output must never crash the process supervisor. */ }
      resolve({ status: reason || (spawnError ? 'spawn_error' : exitCode === 0 ? 'passed' : 'failed'), exitCode, signal: exitSignal, error: spawnError, output, passedTests, bytes, truncated: bytes > 24000, durationMs: Date.now() - start, finishedAt: new Date().toISOString() });
    });
  });
}

// Keep complete protocol turns; a persisted factual checkpoint survives pruning.
export function boundedHistory(history, max = 42000) {
  const groups = [];
  for (const message of history) {
    if (message.role !== 'tool' || !groups.length) groups.push([]);
    groups.at(-1).push(message);
  }
  const kept = []; let size = 0;
  for (const group of groups.reverse()) {
    const length = JSON.stringify(group).length;
    if (size + length > max) break;
    kept.unshift(...group); size += length;
  }
  // User goals and facts are sent separately, so dropping an oversized turn is safe.
  return kept;
}
