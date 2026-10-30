import { lstat, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve, sep } from 'node:path';

export async function resolveRegisteredProjectFile({origin,token,projectId,relativePath,request=fetch}) {
  if(typeof projectId!=='string'||!projectId||typeof relativePath!=='string'||!relativePath||isAbsolute(relativePath)||/[\x00-\x1f:*?"<>|]/.test(relativePath))throw Error('文件路径无效。');
  const parts=relativePath.replace(/\\/g,'/').split('/');
  if(parts.some(part=>!part||part==='.'||part==='..'||part.startsWith('~$')||part.trimEnd()!==part))throw Error('只允许打开项目内的普通文件。');
  const stateResponse=await request(origin+'/api/dev/state',{headers:{Cookie:'shujin_session='+token}});
  if(!stateResponse.ok)throw Error('无法验证项目目录。');
  const project=(await stateResponse.json()).projects.find(item=>item.id===projectId);
  if(!project)throw Error('项目未登记，无法定位文件。');
  const root=await realpath(project.path), target=resolve(root,...parts), resolved=await realpath(target);
  const escaped=relative(root,resolved);
  if(!escaped||escaped==='..'||escaped.startsWith('..'+sep)||isAbsolute(escaped))throw Error('禁止访问项目目录以外的文件。');
  if(!(await lstat(target)).isFile())throw Error('只允许定位项目内的普通文件。');
  return target;
}
