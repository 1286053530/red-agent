import assert from 'node:assert/strict';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { resolveRegisteredProjectFile } from '../desktop/project-file.mjs';

test('file location requires a registered project and an ordinary contained file', async () => {
  const base=await mkdtemp(join(tmpdir(),'shujin-project-file-'));
  const root=join(base,'project');
  await mkdir(join(root,'src'),{recursive:true});
  await writeFile(join(root,'src','output.txt'),'generated');
  const request=async(url,options)=>{
    assert.equal(url,'http://127.0.0.1:3000/api/dev/state');
    assert.equal(options.headers.Cookie,'shujin_session=secret');
    return {ok:true,json:async()=>({projects:[{id:'registered-project',path:root}]})};
  };
  const args={origin:'http://127.0.0.1:3000',token:'secret',projectId:'registered-project',relativePath:'src/output.txt',request};
  try {
    assert.equal(await resolveRegisteredProjectFile(args),join(root,'src','output.txt'));
    await assert.rejects(resolveRegisteredProjectFile({...args,projectId:'unknown'}),/项目未登记/);
    await assert.rejects(resolveRegisteredProjectFile({...args,relativePath:'..\\outside.txt'}),/只允许打开项目内/);
    await assert.rejects(resolveRegisteredProjectFile({...args,relativePath:'src'}),/普通文件/);
  } finally {
    await rm(base,{recursive:true,force:true});
  }
});
