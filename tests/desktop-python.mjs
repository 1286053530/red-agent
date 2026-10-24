import { app, BrowserWindow, session } from 'electron';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { startPythonBackend } from '../desktop/python-backend.mjs';
import { DesktopXhs } from '../desktop/xhs.mjs';

const packaged = process.argv.includes('--packaged');
app.on('window-all-closed',()=>{});
let backend, win, xhs, folder;
app.whenReady().then(async () => {
  try {
    folder = await mkdtemp(join(tmpdir(),'shujin-python-desktop-'));
    app.setPath('userData',join(folder,'profile'));
    win = new BrowserWindow({show:false,webPreferences:{sandbox:true,nodeIntegration:false,contextIsolation:true}});
    const partition='persist:python-desktop-fixture';
    const profile=session.fromPartition(partition);
    const fixture='<html><body><div id="app"><div class="login-container">扫码登录<div class="qrcode"><canvas width="160" height="160"></canvas></div></div></div><script>window.__INITIAL_STATE__={user:{loggedIn:false}};const c=document.querySelector("canvas").getContext("2d");c.fillStyle="black";c.fillRect(10,10,100,100);</script></body></html>';
    let officialRequests=0;
    profile.webRequest.onCompleted(()=>{officialRequests++;});
    xhs=new DesktopXhs(win,{partition,openExternal:async()=>{throw Error('Unexpected external open during backend test');}});
    backend=await startPythonBackend({root:resolve('.'),resources:resolve('release/win-unpacked/resources'),packaged,dataDir:folder,
      native:async(method,params)=>{
        if(method==='pick-folder')return {path:join(folder,'project')};
        if(method==='xhs:disconnect')return xhs.disconnect();
        throw Error('unexpected native method');
      }});
    assert.equal(backend.backend,'python');
    assert.equal((await fetch(backend.origin+'/api/dev/state')).status,403);
    const headers={Cookie:'shujin_session='+backend.token,'Content-Type':'application/json'};
    const request=async(path,data)=>{const response=await fetch(backend.origin+path,{headers,method:data===undefined?'GET':'POST',body:data===undefined?undefined:JSON.stringify(data)});const result=await response.json();assert.equal(response.status,200,JSON.stringify(result));return result;};
    assert.match(await fetch(backend.origin,{headers}).then(r=>r.text()),/筱竹书瑾/);
    assert.deepEqual((await request('/api/dev/state')).projects,[]);
    const skill=await request('/api/dev/skills/software-development');
    assert.equal(skill.id,'software-development');assert.match(skill.content,/read_skill_resource/);assert.equal(skill.resources.length,3);
    await mkdir(join(folder,'project'));
    const picked=await request('/api/dev/pick-folder',{});
    const project=await request('/api/dev/projects',picked);
    assert.equal(project.path,picked.path);
    assert.equal((await request('/api/xhs/status')).status,'automation_disabled');
    for(const path of ['/api/xhs/connect','/api/xhs/login/refresh','/api/xhs/recommendations?more=1','/api/xhs/messages?kind=private&open=1']){
      const response=await fetch(backend.origin+path,{headers,method:'POST'});
      assert.equal(response.status,410);assert.match((await response.json()).error,/已停用/);
    }
    assert.equal(officialRequests,0);
    await request('/api/xhs/disconnect',{});
    // Exercise the frozen Python runtime's Node supervision without a real provider.
    const executable=packaged?resolve('release/win-unpacked/resources/backend/shujin-backend.exe'):resolve('.venv/Scripts/python.exe');
    const {stdout}=await promisify(execFile)(executable,[...(packaged?[]:['-m','backend']),'--self-test'],{cwd:resolve('.'),windowsHide:true,
      env:{...process.env,PYTHONUTF8:'1',SHUJIN_NODE_EXEC:process.execPath,SHUJIN_NODE_IS_ELECTRON:'1'}});
    assert.equal(JSON.parse(stdout.trim()).passed,true);
    assert.equal(JSON.parse(stdout.trim()).skill.digest,skill.digest);
    const stopped=await backend.stop();assert.equal(stopped.code,0);
    await xhs.close();
    await mkdir(resolve('.local/python-check'),{recursive:true});
    await writeFile(resolve('.local/python-check',packaged?'desktop-packaged.json':'desktop-source.json'),JSON.stringify({passed:true,backend:'python',manualOnly:true,officialRequests,retiredApi:410,folderPicker:true,noAuth:403,runtime:JSON.parse(stdout.trim()),shutdownCode:stopped.code},null,2));
    win.destroy();
    await rm(folder,{recursive:true,force:true}).catch(error=>{if(!['EBUSY','EPERM'].includes(error.code))throw error;});
    console.log('PYTHON_DESKTOP_PASS '+(packaged?'packaged':'source'));
    app.exit(0);
  } catch(error) {
    console.error(error.stack);
    if(backend)await backend.stop().catch(()=>{});
    if(xhs)await xhs.close().catch(()=>{});
    if(win&&!win.isDestroyed())win.destroy();
    app.exit(1);
  }
});
