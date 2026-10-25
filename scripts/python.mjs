import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = dirname(dirname(fileURLToPath(import.meta.url)));
const python = process.env.SHUJIN_PYTHON || (existsSync(join(root,'.venv','Scripts','python.exe')) ? join(root,'.venv','Scripts','python.exe') : existsSync(join(root,'.venv','bin','python')) ? join(root,'.venv','bin','python') : 'python');
const commands = {
  serve: ['-m','backend'],
  test: ['-m','pytest'],
  build: ['-m','PyInstaller','--noconfirm','--clean','--onedir','--name','shujin-backend','--paths','.',
    '--distpath','dist/python','--workpath','build/python','--specpath','build',
    '--exclude-module','playwright','--collect-submodules','uvicorn',
    '--add-data',join(root,'backend/tools.json')+ ';backend',
    '--add-data',join(root,'backend/BASE.md')+ ';backend',
    '--add-data',join(root,'backend/skills')+';backend/skills',
    '--add-data',join(root,'backend/agent-test-reporter.mjs')+';backend','scripts/backend_entry.py']
};
const args=commands[process.argv[2]];
if(!args)throw new Error('Expected serve, test or build');
const child=spawn(python,[...args,...process.argv.slice(3)],{cwd:root,env:{...process.env,PYTHONUTF8:'1'},stdio:'inherit',windowsHide:true});
child.on('error',error=>{console.error('Python 启动失败：'+error.message);process.exitCode=1;});
child.on('exit',code=>{process.exitCode=code??1;});
