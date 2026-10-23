import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {DevWorkspace} from '../dev-agent.mjs';
import {runProcess,validateCommand,boundedHistory} from '../agent-runtime.mjs';

const call=(name,args={})=>({id:crypto.randomUUID(),type:'function',function:{name,arguments:JSON.stringify(args)}});
const plan={summary:'修复边界值并保持原行为',criteria:'现有行为测试全部通过',next_action:'读取实现与测试'};
async function fixture(t,fetcher=fetch) {
  const root=await mkdtemp(join(tmpdir(),'shujin-loop-')),path=join(root,'project'),dataDir=join(root,'data');await mkdir(path);
  await writeFile(join(path,'package.json'),JSON.stringify({type:'module',scripts:{test:'node --test app.test.mjs'}}));
  await writeFile(join(path,'app.mjs'),'export const add = (a,b) => a-b;\n');
  await writeFile(join(path,'app.test.mjs'),"import {test} from 'node:test'; import assert from 'node:assert/strict'; import {add} from './app.mjs'; test('adds positive and negative inputs',()=>{assert.equal(add(2,3),5);assert.equal(add(-2,3),1)});\n");
  const workspace=new DevWorkspace({dataDir,fetcher});await workspace.ready;
  const project=await workspace.importProject(path),provider=await workspace.saveProvider({name:'test',protocol:'compatible',baseUrl:'https://example.com/v1',model:'fixture'}),pub=await workspace.createSession({projectId:project.id});
  t.after(async()=>{await workspace.shutdown();await rm(root,{recursive:true,force:true});});
  return {root,path,dataDir,workspace,project,provider,session:workspace.session(pub.id),execute:(name,args)=>workspace.executeTool(workspace.session(pub.id),call(name,args))};
}
async function settle(workspace) {while(workspace.runTasks.size||workspace.commandTasks.size)await Promise.allSettled([...workspace.runTasks,...workspace.commandTasks]);}

test('real Node task: failed fix, feedback, correction, passing test, final diff and evidence',async t=>{
  const steps=[
    ['update_plan',plan],['list_files',{}],['read_file',{path:'app.mjs'}],['read_file',{path:'app.test.mjs'}],
    ['propose_file',{path:'app.mjs',content:'export const add = (a,b) => a*b;\n',reason:'first attempt'}],
    ['run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'verify sum behavior'}],
    ['update_plan',{...plan,failure:'测试显示 6 !== 5，乘法不符合加法；修复实现',next_action:'改为 a+b 并重新测试'}],
    ['read_file',{path:'app.mjs'}],['propose_file',{path:'app.mjs',content:'export const add = (a,b) => a+b;\n',reason:'correct failed assertion'}],
    ['run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'verify regression after correction'}],
    ['review_diff',{}],['finish_task',{summary:'已修复加法实现',evidence:'实际 Node 行为测试通过，退出码 0，最终 diff 仅修正加法。'}]
  ];let index=0,failedObserved=false;
  const f=await fixture(t,async(_,request)=>{
    const body=JSON.parse(request.body);assert.ok(body.messages.every(m=>!('usage' in m)));
    if(index===6){assert.match(JSON.stringify(body.messages),/failed/);failedObserved=true;}
    const [name,args]=steps[index++];return {ok:true,json:async()=>({choices:[{message:{tool_calls:[call(name,args)]}}],usage:{prompt_tokens:10,completion_tokens:5}})};
  });
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'修复 add，并用现有测试证明',acceptance:'正负输入相加均正确，原测试通过',permissions:{edits:true,commands:true}});
  await settle(f.workspace);
  assert.equal(f.session.status,'completed',f.session.error);assert.equal(index,steps.length);assert.equal(failedObserved,true);
  assert.deepEqual(f.session.commands.map(c=>[c.status,c.exitCode]),[['failed',1],['passed',0]]);
  assert.equal(f.session.task.metrics.failedCommands,1);assert.equal(f.session.task.metrics.inputTokens,120);
  assert.equal(await readFile(join(f.path,'app.mjs'),'utf8'),'export const add = (a,b) => a+b;\n');
  const log=(await readFile(join(f.dataDir,'runs',f.session.task.id+'.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);
  assert.equal(log.at(-1).type,'task_completed');assert.ok(log.some(e=>e.type==='command_finished'&&e.command.status==='failed'));
});

test('completion gate rejects missing, running, stale and syntax-only evidence; latest failure wins',async t=>{
  const f=await fixture(t,async()=>({ok:true,json:async()=>({choices:[{message:{content:'完成'}}]})}));
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'修复'});await settle(f.workspace);
  assert.equal(f.session.status,'needs_help');await f.execute('update_plan',plan);
  const finish=()=>f.execute('finish_task',{summary:'done',evidence:'verified'});
  await assert.rejects(finish,/行为测试/);
  f.session.task.permissions.commands=true;
  await f.execute('run_command',{command:'node',args:['--check','app.mjs'],purpose:'syntax'});await settle(f.workspace);
  await f.execute('review_diff');await assert.rejects(finish,/行为测试/);
  await writeFile(join(f.path,'app.mjs'),'export const add=(a,b)=>a+b;\n');
  await f.execute('run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'behavior'});
  await assert.rejects(finish,/未结束命令/);await settle(f.workspace);
  await assert.rejects(finish,/review_diff/);
  await f.execute('review_diff');
  await writeFile(join(f.path,'app.mjs'),'export const add=(a,b)=>a-b;\n');
  await assert.rejects(finish,/行为测试/);
  await f.execute('run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'regression'});await settle(f.workspace);
  await f.execute('review_diff');await assert.rejects(finish,/行为测试/);
});

test('command approvals are explicit, denial resumes with feedback, duplicate check does not rerun',async t=>{
  const steps=[['update_plan',plan],['run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'baseline'}]];let index=0;
  const f=await fixture(t,async()=>({ok:true,json:async()=>({choices:[{message:index<steps.length?{tool_calls:[call(...steps[index++])]}:{content:'无法继续，需要反馈。'}}]})}));
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'验证'});await settle(f.workspace);
  const command=f.session.commands[0];assert.equal(f.session.status,'waiting');assert.equal(command.status,'pending_approval');assert.equal(command.startedAt,undefined);
  await f.workspace.commandDecision(f.session.id,command.id,'approve');await settle(f.workspace);
  assert.equal(command.status,'failed');assert.equal(f.session.status,'needs_help');
  f.session.task.permissions.commands=true;
  const duplicate=await f.execute('run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'same check'});
  assert.equal(duplicate.deduplicated,true);assert.equal(f.session.commands.length,1);
  const retry=await f.execute('run_command',{command:'node',args:['--test','app.test.mjs'],purpose:'explicit retry',retry_id:command.id});await settle(f.workspace);
  assert.notEqual(retry.id,command.id);assert.equal(f.session.commands.length,2);
  f.session.task.permissions.commands=false;
  const pending=await f.execute('run_command',{command:'node',args:['--check','app.mjs'],purpose:'syntax'});
  await f.workspace.commandDecision(f.session.id,pending.id,'deny');await settle(f.workspace);assert.equal(pending.status,'denied');
});

test('checks track timeout, interruption, output truncation and npm exit',async t=>{
  const f=await fixture(t);
  await writeFile(join(f.path,'hang.test.mjs'),"import {test} from 'node:test'; test('wait',()=>new Promise(()=>setInterval(()=>{},1000)));\n");
  const timed=await runProcess({command:'node',args:['--test','hang.test.mjs'],cwd:f.path,timeoutMs:200});
  assert.equal(timed.status,'timed_out');assert.notEqual(timed.status,'passed');
  const controller=new AbortController();
  const run=runProcess({command:'node',args:['--test','hang.test.mjs'],cwd:f.path,signal:controller.signal,onStart:()=>controller.abort()});
  assert.equal((await run).status,'interrupted');
  await writeFile(join(f.path,'loud.test.mjs'),"import {test} from 'node:test'; test('output',()=>console.log('x'.repeat(30000)));\n");
  const loud=await runProcess({command:'node',args:['--test','loud.test.mjs'],cwd:f.path});
  assert.equal(loud.status,'passed');assert.equal(loud.truncated,true);assert.ok(loud.output.length<=24000);assert.equal(loud.output.includes('\uFFFD'),false);
  await writeFile(join(f.path,'unicode.test.mjs'),"import {test} from 'node:test'; test('中文',()=>console.log('验证通过'));\n");
  const unicode=await runProcess({command:'node',args:['--test','unicode.test.mjs'],cwd:f.path});assert.match(unicode.output,/验证通过/);
  const npm=await runProcess({command:'npm',args:['test'],cwd:f.path});assert.equal(npm.status,'failed');assert.equal(npm.exitCode,1);assert.match(npm.output,/adds positive/);
  for(const [command,args] of [['cmd',['/c','del']],['node',['--eval','x']],['node',['--test','--import=evil']],['npm',['install']],['npm',['run','deploy']]])assert.throws(()=>validateCommand(command,args));
});

test('stop kills verification, restart preserves checkpoints, unknown command is never repeated',async t=>{
  const f=await fixture(t,async()=>({ok:true,json:async()=>({choices:[{message:{tool_calls:[call('run_command',{command:'node',args:['--test','hang.test.mjs'],purpose:'test stop'})]}}]})}));
  await writeFile(join(f.path,'hang.test.mjs'),"import {test} from 'node:test'; test('wait',()=>new Promise(()=>setInterval(()=>{},1000)));\n");
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'验证停止',permissions:{commands:true}});
  while(!f.session.commands.length)await new Promise(r=>setTimeout(r,10));
  await f.workspace.stop(f.session.id);await settle(f.workspace);
  assert.equal(f.session.status,'stopped');assert.equal(f.session.commands[0].status,'interrupted');assert.equal(f.workspace.processes.size,0);
  await f.execute('update_plan',{...plan,failure:'用户中断，结果未知'});
  f.session.status='running';f.session.commands[0].status='running';await f.workspace.save();
  const reloaded=new DevWorkspace({dataDir:f.dataDir});await reloaded.ready;
  const session=reloaded.session(f.session.id);assert.equal(session.status,'stopped');assert.equal(session.commands[0].status,'interrupted');assert.equal(session.task.checkpoint.failure,'用户中断，结果未知');assert.equal(reloaded.processes.size,0);
  await reloaded.shutdown();
});

test('paged reads, conflict-aware restoration and protocol-safe compaction',async t=>{
  const f=await fixture(t);
  await f.execute('read_file',{path:'app.mjs'});
  const change=await f.execute('propose_file',{path:'app.mjs',content:'export const add=(a,b)=>a+b;\n',reason:'fix'});
  await f.workspace.applyChange(f.session.id,change.changeId,'apply');
  await f.workspace.applyChange(f.session.id,change.changeId,'revert');
  assert.equal(await readFile(join(f.path,'app.mjs'),'utf8'),'export const add = (a,b) => a-b;\n');
  await writeFile(join(f.path,'long.mjs'),Array.from({length:450},(_,i)=>'// '+i).join('\n'));
  const first=await f.execute('read_file',{path:'long.mjs'});assert.equal(first.hasMore,true);assert.equal(first.end_line,200);
  await assert.rejects(()=>f.execute('propose_file',{path:'long.mjs',content:'// replaced',reason:'x'}),/读完/);
  await f.execute('read_file',{path:'long.mjs',start_line:201,end_line:450});
  assert.equal((await f.execute('propose_file',{path:'long.mjs',content:'// replaced',reason:'x'})).status,'pending_review');
  const history=[{role:'user',content:'old'.repeat(5000)},{role:'assistant',tool_calls:[call('read_file',{path:'app.mjs'})]},{role:'tool',tool_call_id:'old',content:'x'.repeat(5000)},{role:'assistant',tool_calls:[{id:'latest',function:{name:'list_files',arguments:'{}'}}]},{role:'tool',tool_call_id:'latest',content:'ok'}];
  const kept=boundedHistory(history,1000);assert.equal(kept[0].tool_calls[0].id,'latest');assert.equal(kept[1].tool_call_id,'latest');
});


test('read-only analysis finishes with source evidence and rejects writes and commands',async t=>{
  const steps=[['update_plan',plan],['read_file',{path:'app.mjs'}],['propose_file',{path:'app.mjs',content:'no',reason:'not allowed'}],['run_command',{command:'node',args:['--test'],purpose:'not allowed'}],['finish_task',{summary:'源码使用减法而非加法',evidence:'已读取 app.mjs，实现为 a-b；本次只读，未执行代码。'}]];let index=0;
  const f=await fixture(t,async()=>({ok:true,json:async()=>({choices:[{message:{tool_calls:[call(...steps[index++])]}}]})}));
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'分析实现',kind:'inspect',permissions:{edits:true,commands:true}});await settle(f.workspace);
  assert.equal(f.session.status,'completed');assert.equal(f.session.commands.length,0);assert.equal(f.session.changes.length,0);assert.equal(f.session.events.filter(e=>e.status==='error').length,2);
});

test('empty test suites cannot pass completion and pending work reserves the project',async t=>{
  const f=await fixture(t,async()=>({ok:true,json:async()=>({choices:[{message:{tool_calls:[call('read_file',{path:'app.mjs'}),call('propose_file',{path:'app.mjs',content:'export const add=(a,b)=>a+b;\n',reason:'fix'})]}}]})}));
  await f.workspace.startRun(f.session.id,{providerId:f.provider.id,message:'fix'});await settle(f.workspace);
  const second=await f.workspace.createSession({projectId:f.project.id});
  await assert.rejects(()=>f.workspace.startRun(second.id,{providerId:f.provider.id,message:'other'}),/待审核/);
  await writeFile(join(f.path,'empty.test.mjs'),'// no tests\n');
  f.session.changes[0].status='discarded';f.session.task.permissions.commands=true;
  await f.execute('run_command',{command:'node',args:['--test','empty.test.mjs'],purpose:'empty'});await settle(f.workspace);
  assert.equal(f.session.commands[0].status,'failed');assert.match(f.session.commands[0].error,/没有发现测试用例/);
});
