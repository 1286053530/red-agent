import { app } from 'electron';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

app.whenReady().then(async () => {
  const cwd = await mkdtemp(join(tmpdir(), 'shujin-electron-agent-'));
  try {
    const source = process.argv.includes('--packaged') ? pathToFileURL(resolve('release/win-unpacked/resources/app.asar/agent-runtime.mjs')) : new URL('../agent-runtime.mjs', import.meta.url);
    const { runProcess } = await import(source.href);
    await writeFile(join(cwd, 'real.test.mjs'), "import {test} from 'node:test';import assert from 'node:assert/strict';test('real behavior',()=>assert.equal(2+3,5));\n");
    const result = await runProcess({command:'node',args:['--test','real.test.mjs'],cwd});
    assert.equal(result.status, 'passed', JSON.stringify(result));
    assert.equal(result.passedTests, 1, JSON.stringify(result));
    await writeFile(join(cwd,'empty.test.mjs'),'// empty\n');
    const empty = await runProcess({command:'node',args:['--test','empty.test.mjs'],cwd});
    assert.equal(empty.passedTests,0,JSON.stringify(empty));
    console.log('Desktop Agent runtime: real behavioral check and empty-suite evidence passed' + (process.argv.includes('--packaged')?' (packaged ASAR)':''));
  } catch(error) { console.error(error); process.exitCode=1; }
  finally {await rm(cwd,{recursive:true,force:true}); app.exit(process.exitCode || 0);}
});
