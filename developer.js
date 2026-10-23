(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const icon = name => '<svg class="icon"><use href="#i-' + name + '"/></svg>';
  const api = async (path, body) => {
    const response = await fetch('/api/dev/' + path, { method: body === undefined ? 'GET' : 'POST', headers: body === undefined ? {} : { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store' });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || '请求失败，请重试。'); return data;
  };
  const state = { projects: [], providers: [], sessions: [], projectId: localStorage.getItem('devProject') || '', sessionId: localStorage.getItem('devSession') || '', files: [], file: '', session: null, busy: false };
  let pollGeneration = 0, pollingId = '', settingsTrigger;
  const rememberSelection = () => { localStorage.setItem('devProject', state.projectId); localStorage.setItem('devSession', state.sessionId); };
  const root = $('#developerView');
  if (!root) return;

  root.innerHTML = `
    <div class="dev-page-intro"><div><div class="eyebrow"><span class="eyebrow-line"></span> SOFTWARE DEVELOPMENT AGENT</div><h1>开发工作空间<span class="heading-period">.</span></h1><p>导入本地项目，连接你的模型，开始代码分析与开发任务。</p></div><div class="dev-page-actions"><span class="dev-local-badge"><i></i> 本机运行 · 按任务授权</span><button class="secondary-button" id="devSettingsButton">${icon('filter')}模型设置</button></div></div>
    <div class="dev-project-toolbar"><div class="dev-project-select-wrap"><span class="dev-muted-label">当前项目</span><select id="devProjectSelect" class="dev-select"><option value="">选择或导入项目</option></select></div><button class="secondary-button" id="devImportButton">${icon('plus')}导入本地项目</button><button class="secondary-button" id="devNewSessionButton" disabled>${icon('file')}新开发会话</button><span class="dev-project-meta" id="devProjectMeta">项目文件留在本机</span></div>
    <div class="dev-workbench" id="devWorkbench"><aside class="dev-session-sidebar"><div class="dev-sidebar-heading"><div><strong>项目会话</strong><small id="devSessionCount">选择项目后开始</small></div><button class="dev-square-button" id="devAddSession" aria-label="新建会话" disabled>${icon('plus')}</button></div><div id="devSessionList" class="dev-session-list"></div><div class="dev-sidebar-footer"><span class="dev-safe-dot"></span><span>源码读取仅限已导入目录</span></div></aside>
      <section class="dev-editor-area"><div class="dev-editor-toolbar"><div class="dev-breadcrumb" id="devEditorTitle">项目文件 <span>/</span> 选择文件</div><div class="dev-editor-tools"><span class="dev-editor-language" id="devFileType">SOURCE</span><button class="dev-plain-button" id="devRefreshFiles">${icon('refresh')}刷新</button></div></div><div class="dev-code-layout"><aside class="dev-file-tree" id="devFileTree"><div class="dev-tree-label">项目文件</div><div class="dev-empty-files">导入项目以浏览源码</div></aside><div class="dev-file-preview" id="devFilePreview"><div class="dev-code-empty"><span class="dev-empty-icon">{ }</span><strong>项目代码，尽在掌握</strong><p>导入本地项目后，可以浏览源码或让 Agent 帮你分析代码结构。</p><button class="primary-button" id="devEmptyImport">${icon('plus')}导入本地项目</button></div></div></div></section>
      <section class="dev-agent-panel"><div class="dev-agent-heading"><div class="dev-agent-avatar">${icon('spark')}</div><div><strong>软件开发 Agent</strong><small id="devAgentStatus"><i></i>准备就绪</small></div><button class="dev-panel-more" id="devSettingsQuick" aria-label="模型设置">···</button></div><div class="dev-agent-info"><span class="dev-agent-project-icon">{ }</span><div><strong id="devAgentProjectName">尚未选择项目</strong><small id="devAgentProviderStatus">配置模型以开始</small></div></div><div id="devConversation" class="dev-conversation"><div class="dev-empty-agent"><span class="dev-agent-spark">✳</span><strong>你好，我是你的开发 Agent</strong><p>我可以先阅读项目源码，帮你梳理结构、定位问题并提出代码修改。可逐项审核修改和检查命令，也可为本次任务授权持续执行。</p><div class="dev-agent-suggestions"><button data-dev-prompt="请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。">梳理项目结构 ${icon('arrow')}</button><button data-dev-prompt="阅读项目的 README 和主要源码，说明如何运行项目，并指出最值得优先改进的地方。">阅读项目并给出建议 ${icon('arrow')}</button></div></div></div><div id="devExecution" class="dev-execution"></div><div id="devPendingChanges" class="dev-pending-list"></div><div class="dev-model-row"><label for="devModelSelect">执行模型</label><select id="devModelSelect"><option value="">添加模型后可开始</option></select><button id="devManageModel" class="dev-plain-button">配置</button></div><details class="dev-task-options"><summary>任务标准与执行权限</summary><label>任务类型<select id="devTaskKind"><option value="change">代码修改与验证</option><option value="inspect">只读分析</option></select></label><label>完成标准<input id="devAcceptance" maxlength="4000" placeholder="例如：修复空输入报错，原有测试继续通过"></label><label class="dev-permission"><input type="checkbox" id="devAllowEdits">本次任务自动应用源码修改（保留恢复记录）</label><label class="dev-permission"><input type="checkbox" id="devAllowCommands">本次任务允许运行项目检查</label><small>未授权的动作会逐项审核。项目检查会执行本机代码，请仅对可信项目授权。</small></details><form class="dev-composer" id="devComposer"><textarea id="devPrompt" rows="2" maxlength="16000" placeholder="描述你想完成的开发任务…" disabled></textarea><div class="dev-composer-bottom"><span id="devComposerHint">请先导入一个项目</span><div><button type="button" id="devStopButton" class="dev-stop-button hidden">停止</button><button type="submit" id="devSendButton" class="dev-send-button" disabled aria-label="发送">${icon('send')}</button></div></div></form><div id="devError" class="dev-inline-error hidden" role="alert"></div></section></div>
    <div class="dev-bottom-strip"><span>${icon('check')} 模型 API Key 加密保存在本机</span><span>执行检查 → 反馈纠错 → 证据验收</span><button id="devBottomSettings">配置接入模型 ${icon('arrow')}</button></div>
    <div class="dev-modal-backdrop hidden" id="devSettingsModal" role="presentation"><div class="dev-settings-modal" role="dialog" aria-modal="true" aria-labelledby="devSettingsTitle"><div class="dev-modal-title"><div><div class="eyebrow"><span class="eyebrow-line"></span> MODEL PROVIDERS</div><h2 id="devSettingsTitle">模型接入设置</h2></div><button id="devCloseSettings" class="dev-square-button" aria-label="关闭">×</button></div><p class="dev-modal-description">接入兼容 OpenAI Chat Completions 的模型服务或 Anthropic Messages API。需要你自备 API Key 与模型权限。执行任务时，任务描述和 Agent 读取的源码将发送给所选模型服务。</p><div id="devSettingsError" class="dev-inline-error hidden" role="alert"></div><div id="devProviderList" class="dev-provider-list"></div><form id="devProviderForm" class="dev-provider-form"><input type="hidden" id="devProviderId"><label>配置名称<input id="devProviderName" maxlength="60" placeholder="如 DeepSeek 主力模型" required></label><label>接口协议<select id="devProviderProtocol"><option value="compatible">OpenAI 兼容接口</option><option value="anthropic">Anthropic Messages API</option></select></label><label class="dev-provider-wide">Base URL<input id="devProviderUrl" type="url" placeholder="https://api.deepseek.com/v1" required></label><label>模型名称<input id="devProviderModel" maxlength="150" placeholder="deepseek-chat" required></label><label>API Key<input id="devProviderKey" type="password" autocomplete="new-password" placeholder="sk-…（保留当前密钥请留空）"></label><div class="dev-provider-actions"><button type="button" class="secondary-button" id="devProviderCancel">取消</button><button type="submit" class="primary-button" id="devProviderSave">保存模型</button></div></form><div class="dev-modal-footer"><span>${icon('check')} 密钥使用本机密钥加密后存储</span><button type="button" id="devAddProvider">${icon('plus')}添加模型配置</button></div></div></div>`;

  const toast = message => window.showToast ? showToast(message) : void 0;
  const setError = message => { const box = $('#devSettingsModal').classList.contains('hidden') ? $('#devError') : $('#devSettingsError'); box.textContent = message || ''; box.classList.toggle('hidden', !message); };
  const openSettings = () => { settingsTrigger = document.activeElement; $('#devSettingsModal').classList.remove('hidden'); renderProviders(); $('#devCloseSettings').focus(); };
  const closeSettings = () => { $('#devSettingsModal').classList.add('hidden'); settingsTrigger?.focus(); };
  const activeProject = () => state.projects.find(p => p.id === state.projectId);
  const currentSession = () => state.session;
  function renderProjects() {
    $('#devProjectSelect').innerHTML = '<option value="">选择或导入项目</option>' + state.projects.map(p => `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)}</option>`).join('');
    $('#devProjectSelect').value = state.projectId;
    const project = activeProject();
    $('#devProjectMeta').textContent = project ? project.path : '项目文件留在本机';
    $('#devAgentProjectName').textContent = project?.name || '尚未选择项目';
    $('#devNewSessionButton').disabled = !project; $('#devAddSession').disabled = !project;
    $('#devPrompt').disabled = !project || state.busy;
    $('#devAgentStatus').textContent = statusLabel(state.session?.status || 'idle');
    $('#devComposerHint').textContent = !project ? '请先导入一个项目' : state.busy ? 'Agent 正在处理任务…' : state.providers.length ? 'Enter 发送 · Shift + Enter 换行' : '请先配置模型';
    $('#devSessionCount').textContent = project ? `${state.sessions.filter(s => s.projectId === project.id).length} 个会话` : '选择项目后开始';
    $('#devAgentProviderStatus').textContent = state.providers.length ? `${state.providers.length} 个模型配置可用` : '配置模型以开始';
    $('#devNewSessionButton').title = project ? '在当前项目中新建开发会话' : '请先导入本地项目';
    renderModelSelect();
  }
  function renderModelSelect() {
    const select = $('#devModelSelect'), selected = select.value || state.session?.providerId || localStorage.getItem('devSelectedProvider') || '';
    select.innerHTML = '<option value="">选择执行模型</option>' + state.providers.map(p => `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)} · ${escapeHtml(p.model)}</option>`).join('');
    select.value = state.providers.some(p => p.id === selected) ? selected : state.providers[0]?.id || '';
    $('#devSendButton').disabled = !state.projectId || !select.value || state.busy;
    $('#devModelSelect').disabled = state.busy;
    if (select.value) localStorage.setItem('devSelectedProvider', select.value);
  }
  function renderProviders() {
    $('#devProviderList').innerHTML = state.providers.length ? state.providers.map(p => `<article class="dev-provider-card"><div class="dev-provider-card-icon">${p.protocol === 'anthropic' ? 'A' : 'AI'}</div><div class="dev-provider-card-body"><strong>${escapeHtml(p.name)}</strong><small>${escapeHtml(p.model)} · ${p.protocol === 'anthropic' ? 'Anthropic API' : 'OpenAI 兼容接口'}</small><span>${escapeHtml(p.baseUrl)} · ${p.hasKey ? 'API Key 已加密' : '未配置 API Key'}</span></div><div class="dev-provider-card-actions"><button data-edit-provider="${escapeHtml(p.id)}">编辑</button><button data-test-provider="${escapeHtml(p.id)}">测试连接</button><button class="dev-provider-delete" data-delete-provider="${escapeHtml(p.id)}" aria-label="删除 ${escapeHtml(p.name)}">删除</button></div></article>`).join('') : '<div class="dev-provider-empty"><strong>还没有模型配置</strong><span>添加模型厂商并填写 Base URL、模型名称和 API Key。</span></div>';
  }
  function resetProviderForm() {
    $('#devProviderForm').reset(); $('#devProviderId').value = ''; $('#devProviderKey').required = false;
    $('#devProviderSave').textContent = '保存模型';
    $('#devProviderForm').classList.add('hidden');
  }
  function openProviderForm(provider) {
    resetProviderForm();
    $('#devProviderForm').classList.remove('hidden');
    if (provider) {
      $('#devProviderId').value = provider.id; $('#devProviderName').value = provider.name;
      $('#devProviderProtocol').value = provider.protocol; $('#devProviderUrl').value = provider.baseUrl;
      $('#devProviderModel').value = provider.model; $('#devProviderKey').placeholder = provider.hasKey ? '已设置密钥，留空保留原值' : 'sk-…';
      $('#devProviderSave').textContent = '保存修改';
    } else $('#devProviderKey').placeholder = 'sk-…';
    $('#devProviderName').focus();
  }
  async function loadState() {
    try {
      const next = await api('state'); state.projects = next.projects; state.providers = next.providers; state.sessions = next.sessions;
      if (state.projectId && !state.projects.some(p => p.id === state.projectId)) state.projectId = '';
      if (state.sessionId && !state.sessions.some(s => s.id === state.sessionId && s.projectId === state.projectId)) state.sessionId = '';
      rememberSelection();
      renderProjects(); renderProviders();
      if (state.projectId) { await loadSessions(); await loadFiles(); }
      if (state.sessionId) await loadSession(state.sessionId);
      else { renderConversation(); renderPending(); renderExecution(); }
    } catch (error) { setError(error.message); }
  }
  async function chooseProject(path) {
    try {
      const project = await api('projects', { path });
      await loadState(); await selectProject(project.id); setError(''); toast('已导入项目「' + project.name + '」');
    } catch (error) { setError(error.message); }
  }
  async function importProject() {
    setError('');
    try { const result = await api('pick-folder', {}); if (result.path) await chooseProject(result.path); }
    catch (error) {
      if (/未能打开文件夹|当前系统/.test(error.message)) {
        const path = prompt('输入本机项目文件夹的绝对路径：\n示例：D:\\projects\\my-app');
        if (path?.trim()) await chooseProject(path.trim()); else setError('已取消选择。');
      } else setError(error.message);
    }
  }
  async function loadSessions() {
    const projectId = state.projectId;
    const result = await api('state'); if (projectId !== state.projectId) return; state.sessions = result.sessions;
    const sessions = state.sessions.filter(s => s.projectId === state.projectId);
    $('#devSessionList').innerHTML = sessions.length ? sessions.map(s => `<button class="dev-session-item ${s.id === state.sessionId ? 'active' : ''}" data-session-id="${escapeHtml(s.id)}"><span class="dev-session-icon">${icon('message')}</span><span class="dev-session-copy"><strong>${escapeHtml(s.title)}</strong><small>${s.status === 'running' ? '执行中' : new Date(s.updatedAt).toLocaleDateString()}</small></span><span class="dev-session-status ${escapeHtml(s.status)}"></span></button>`).join('') : '<div class="dev-session-empty">开始一个新会话，<br>Agent 会帮你阅读代码并完成开发任务。</div>';
  }
  async function loadFiles() {
    if (!state.projectId) return;
    const projectId = state.projectId;
    try { const result = await api(`projects/${encodeURIComponent(projectId)}/files`); if (projectId !== state.projectId) return; state.files = result.files; renderFileTree(); }
    catch (error) { setError(error.message); }
  }
  function renderFileTree() {
    const tree = $('#devFileTree');
    if (!state.files.length) { tree.innerHTML = '<div class="dev-tree-label">项目文件</div><div class="dev-empty-files">没有找到可预览的源码文件</div>'; return; }
    const folders = new Set();
    for (const path of state.files) { const parts = path.split('/'); for (let i = 1; i < parts.length; i++) folders.add(parts.slice(0, i).join('/')); }
    const rows = [];
    const nodes = [...folders].map(path => ({ path, folder: true })).concat(state.files.map(path => ({ path, folder: false }))).sort((a, b) => a.path.localeCompare(b.path));
    for (const node of nodes) {
      const depth = node.path.split('/').length - 1;
      rows.push(`<button class="dev-file-row ${node.path === state.file ? 'active' : ''} ${node.folder ? 'folder' : ''}" style="--depth:${depth}" ${node.folder ? 'disabled' : `data-file-path="${escapeHtml(node.path)}"`}><span class="dev-file-symbol">${node.folder ? '▸' : fileSymbol(node.path)}</span><span>${escapeHtml(node.path.split('/').at(-1))}</span></button>`);
    }
    tree.innerHTML = '<div class="dev-tree-label">项目文件 <span>' + state.files.length + '</span></div>' + rows.join('');
  }
  function fileSymbol(path) { const ext = path.split('.').at(-1).toLowerCase(); return ({ js: 'JS', mjs: 'JS', ts: 'TS', tsx: 'TS', jsx: 'JS', css: 'CSS', html: '<>', json: '{}', md: 'MD', py: 'PY', go: 'GO', rs: 'RS', vue: 'VUE' })[ext] || '·'; }
  async function openFile(path) {
    const projectId = state.projectId;
    try {
      state.file = path; renderFileTree();
      const result = await api(`projects/${encodeURIComponent(projectId)}/file?path=${encodeURIComponent(path)}`);
      if (projectId !== state.projectId || path !== state.file) return;
      $('#devEditorTitle').innerHTML = '<span>' + escapeHtml(activeProject()?.name || '项目') + '</span> / ' + escapeHtml(path);
      $('#devFileType').textContent = fileSymbol(path);
      $('#devFilePreview').innerHTML = `<pre class="dev-source"><code>${result.content.split('\n').map((line, index) => `<span class="dev-source-line"><i>${index + 1}</i><span>${escapeHtml(line) || ' '}</span></span>`).join('')}</code></pre>`;
      setError('');
    } catch (error) { setError(error.message); }
  }
  async function createSession() {
    if (!state.projectId) return;
    const projectId = state.projectId;
    try { const session = await api('sessions', { projectId }); if (projectId !== state.projectId) return; state.sessionId = session.id; rememberSelection(); await loadSession(session.id); $('#devPrompt').focus(); }
    catch (error) { setError(error.message); }
  }
  async function loadSession(id) {
    const session = await api('sessions/' + encodeURIComponent(id));
    if (state.sessionId !== id || session.projectId !== state.projectId) return;
    state.session = session;
    state.busy = session.status === 'running'; renderConversation(); renderPending(); renderExecution(); renderProjects(); await loadSessions();
    if (state.busy && pollingId !== id) void pollRun(id);
  }
  function renderConversation() {
    const session = currentSession(), container = $('#devConversation');
    if (!session || !session.messages.length) {
      container.innerHTML = `<div class="dev-empty-agent"><span class="dev-agent-spark">✳</span><strong>${state.projectId ? '你好，我是你的开发 Agent' : '选择项目后，开始开发任务'}</strong><p>${state.projectId ? '我可以先阅读项目源码，帮你梳理结构、定位问题并提出代码修改。可逐项审核修改和检查命令，也可为本次任务授权持续执行。' : '导入本机项目并连接模型。执行任务时，任务描述与读取的源码将发送给你配置的模型服务。'}</p><div class="dev-agent-suggestions"><button data-dev-prompt="请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。">梳理项目结构 ${icon('arrow')}</button><button data-dev-prompt="阅读项目的 README 和主要源码，说明如何运行项目，并指出最值得优先改进的地方。">阅读项目并给出建议 ${icon('arrow')}</button></div></div>`;
    } else {
      container.innerHTML = session.messages.map(m => `<article class="dev-chat-message ${m.role === 'user' ? 'user' : 'assistant'}"><span class="dev-message-avatar">${m.role === 'user' ? '我' : icon('spark')}</span><div class="dev-message-content">${m.role === 'user' ? `<p>${escapeHtml(m.content)}</p>` : formatAssistant(m.content)}</div></article>`).join('');
    }
    if (state.busy) container.insertAdjacentHTML('beforeend', '<div class="dev-thinking"><i></i><i></i><i></i><span>正在阅读项目与处理任务…</span></div>');
    container.scrollTop = container.scrollHeight;
    $('#devStopButton').classList.toggle('hidden', !state.busy);
    $('#devSendButton').disabled = !state.projectId || !$('#devModelSelect').value || state.busy;
  }
  function formatAssistant(value) {
    let safe = escapeHtml(value);
    safe = safe.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_, language, code) => `<pre><code>${code.trim()}</code></pre>`);
    safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
    safe = safe.replace(/^### (.+)$/gm, '<h4>$1</h4>').replace(/^## (.+)$/gm, '<h4>$1</h4>');
    safe = safe.replace(/^[-*] (.+)$/gm, '<li>$1</li>').replace(/(<li>[\s\S]+?<\/li>\s*)+/g, '<ul>$&</ul>');
    return safe.split(/\n{2,}/).map(block => /^<(?:pre|ul|h4)>/.test(block) ? block : '<p>' + block.replace(/\n/g, '<br>') + '</p>').join('');
  }
  const statusLabel = status => ({idle:'准备就绪',running:'执行中',review:'等待变更审核',waiting:'等待命令授权',completed:'已验证完成',needs_help:'需要反馈',stopped:'已停止',passed:'通过',failed:'失败',timed_out:'超时',interrupted:'结果未知',denied:'已拒绝',pending_approval:'待授权',queued:'排队中',spawn_error:'启动失败',error:'执行错误',output_limit:'输出超限'})[status] || status;
  function renderExecution() {
    const session=state.session, task=session?.task, target=$('#devExecution');
    if(!task){target.innerHTML='';return;}
    const metrics=task.metrics, events=session.events.filter(e=>!e.taskId||e.taskId===task.id).slice(-12);
    const phase=({understand:'理解目标',context:'获取上下文',act:'执行修改',verify:'验证结果',review:'复核变更',complete:'完成'})[task.phase] || task.phase;
    const elapsed=Math.round((new Date(task.finishedAt || Date.now())-new Date(task.startedAt))/1000);
    target.innerHTML=`<div class="dev-execution-head"><strong>${escapeHtml(statusLabel(session.status))}</strong><span>${escapeHtml(phase)}</span><button id="devExportLogs">导出记录</button></div><div class="dev-run-metrics"><span>${task.rounds} 轮 / ${task.calls} 次工具</span><span>${elapsed}s</span><span>${metrics.inputTokens+metrics.outputTokens} tokens</span><span>${metrics.failedCommands} 次检查失败 / ${metrics.interventions} 次审核</span></div><details><summary>任务计划与执行轨迹</summary><p>目标：${escapeHtml(task.goal)}</p><p>验收：${escapeHtml(task.acceptance)}</p><p>当前：${escapeHtml(task.checkpoint?.summary || '正在明确任务')}</p><p>下一步：${escapeHtml(task.checkpoint?.next_action || '读取相关源码')}</p>${task.checkpoint?.failure?`<p class="dev-run-error">失败反馈：${escapeHtml(task.checkpoint.failure)}</p>`:''}<ol>${events.map(e=>`<li><strong>${escapeHtml(e.name)}</strong> · ${escapeHtml(e.detail)} <span>${escapeHtml(e.status==='completed'?'已执行':statusLabel(e.status))}</span>${e.error?`<p class="dev-run-error">${escapeHtml(e.error)}</p>`:''}</li>`).join('')}</ol><small>Token 由服务商返回，费用以厂商账单为准。完整记录包含工具输入、结果和时间。</small></details>${session.commands.filter(c=>c.taskId===task.id).map(c=>`<article class="dev-command-card"><div><strong>${escapeHtml(c.command+' '+c.args.join(' '))}</strong><span>${escapeHtml(statusLabel(c.status))}${c.exitCode!==null?' · exit '+c.exitCode:''}</span></div><p>${escapeHtml(c.purpose)}</p>${c.script?`<pre>${escapeHtml(c.script)}</pre>`:''}${c.output||c.error?`<details><summary>查看输出${c.truncated?'（仅保留末尾，已截断）':''}${c.stale?' · 源码已变化':''}</summary><pre>${escapeHtml(c.output || c.error)}</pre></details>`:''}${c.status==='pending_approval'?`<small>此命令会执行项目代码，请确认你信任此项目。</small><div class="dev-command-actions"><button data-command-id="${c.id}" data-command-action="deny">拒绝</button><button data-command-id="${c.id}" data-command-action="approve">批准本次命令</button></div>`:''}</article>`).join('')}${task.result?`<p class="dev-verification">验证依据：${escapeHtml(task.result.evidence)}</p>`:''}${['needs_help','stopped'].includes(session.status)?'<button id="devResumeTask" class="secondary-button">继续当前任务（可在下方补充反馈）</button>':''}`;
  }
  function renderPending() {
    const changes=state.session?.changes || [], pending=changes.filter(c=>c.status==='pending'), target=$('#devPendingChanges');
    const card=(c,applied=false)=>`<article class="dev-change-card"><div class="dev-change-head"><span class="dev-change-badge">M</span><strong>${escapeHtml(c.path)}</strong><span>${applied?'已应用':'待审核'}</span></div><p>${escapeHtml(c.reason)}</p><details><summary>查看修改前后对比</summary><div class="dev-diff-label">修改前</div><pre><code>${escapeHtml(c.original ?? '（新建文件）')}</code></pre><div class="dev-diff-label">${applied?'已应用内容':'拟议内容'}</div><pre><code>${escapeHtml(c.content)}</code></pre></details><div class="dev-change-actions">${applied?`<button data-change-action="revert" data-change-id="${c.id}" ${state.busy||c.original===null?'disabled':''}>恢复此修改前内容</button>`:`<button data-change-action="discard" data-change-id="${c.id}" ${state.busy?'disabled':''}>放弃</button><button class="primary-button" data-change-action="apply" data-change-id="${c.id}" ${state.busy?'disabled':''}>审核并应用</button>`}</div></article>`;
    target.innerHTML=(pending.length?`<div class="dev-review-heading"><div><strong>待审核的代码变更</strong><span>${pending.length} 个文件</span></div><small>应用后继续验证</small></div>`+pending.map(c=>card(c)).join(''):'')+(changes.some(c=>c.status==='applied')?'<details class="dev-applied-changes"><summary>已应用的变更与恢复</summary>'+changes.filter(c=>c.status==='applied').map(c=>card(c,true)).join('')+'</details>':'');
  }
  async function selectProject(projectId) {
    pollGeneration++; pollingId = ''; state.projectId = projectId; state.sessionId = ''; state.session = null; state.busy = false; state.file = ''; state.files = []; rememberSelection();
    renderProjects(); renderFileTree(); renderConversation(); renderPending(); renderExecution(); setError('');
    $('#devEditorTitle').textContent = '项目文件 / 选择文件';
    $('#devFilePreview').innerHTML = '<div class="dev-code-empty"><strong>选择文件预览源码</strong></div>';
    if (!projectId) { $('#devSessionList').innerHTML = ''; return; }
    const sessionId = state.sessions.find(s => s.projectId === projectId)?.id;
    await Promise.all([loadFiles(), loadSessions()]);
    if (sessionId && state.projectId === projectId) { state.sessionId = sessionId; rememberSelection(); await loadSession(sessionId); }
  }
  async function sendMessage(message) {
    if (!message.trim() || state.busy) return;
    if (!state.projectId) { setError('请先导入一个本地项目。'); return; }
    const providerId = $('#devModelSelect').value;
    if (!providerId) { openSettings(); setError('请先配置并选择执行模型。'); return; }
    if (!state.sessionId) await createSession();
    if (!state.sessionId) return;
    const sessionId = state.sessionId;
    state.busy = true; $('#devPrompt').value = ''; setError(''); renderProjects();
    if (state.session) { state.session.messages.push({ role: 'user', content: message }); state.session.status = 'running'; renderConversation(); }
    try {
      await api(`sessions/${encodeURIComponent(sessionId)}/run`, { providerId, message, acceptance: $('#devAcceptance').value, kind: $('#devTaskKind').value, permissions: { edits: $('#devAllowEdits').checked, commands: $('#devAllowCommands').checked } });
      if (state.sessionId === sessionId) await pollRun(sessionId);
    } catch (error) { if (state.sessionId === sessionId) { await loadSession(sessionId); setError(error.message); } }
  }
  async function pollRun(id) {
    const generation = ++pollGeneration; pollingId = id;
    while (state.sessionId === id && generation === pollGeneration) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      if (state.sessionId !== id || generation !== pollGeneration) break;
      try {
        const session = await api('sessions/' + encodeURIComponent(id));
        if (state.sessionId !== id || generation !== pollGeneration) break;
        state.session = session;
        state.busy = session.status === 'running'; renderConversation(); renderPending(); renderExecution(); renderProjects();
        if (!state.busy) { if (session.error) setError(session.error); else setError(''); await loadSessions(); break; }
      } catch (error) { if (state.sessionId === id) setError(error.message); }
    }
    if (generation === pollGeneration) pollingId = '';
  }
  async function performChange(id, action) {
    const sessionId = state.sessionId;
    try {
      const result = await api(`sessions/${encodeURIComponent(sessionId)}/changes/${encodeURIComponent(id)}`, { action });
      if (state.sessionId !== sessionId) return;
      state.session = result; state.busy=result.status==='running'; renderPending(); renderConversation(); renderExecution(); renderProjects(); if(state.busy)void pollRun(sessionId);
      if (action === 'apply' || action === 'revert') { await loadFiles(); if (state.file) await openFile(state.file); }
      toast(action === 'apply' ? '已应用，Agent 将继续验证' : action==='revert' ? '已恢复原内容，需重新验证' : '已放弃此项变更'); setError('');
    } catch (error) { if (state.sessionId === sessionId) setError(error.message); }
  }
  root.addEventListener('click', async event => {
    const button = event.target.closest('button'); if (!button) return;
    if(button.id==='devExportLogs') {
      try {const data=await api(`sessions/${state.sessionId}/logs`);const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='shujin-task-'+state.session.task.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){setError(error.message);}return;
    }
    if(button.id==='devResumeTask'||button.hasAttribute('data-command-action')) {
      button.disabled=true;
      try {
        const path=button.id==='devResumeTask'?'resume':`commands/${button.dataset.commandId}`;
        await api(`sessions/${state.sessionId}/${path}`,{action:button.dataset.commandAction,feedback:$('#devPrompt').value});
        if(button.id==='devResumeTask')$('#devPrompt').value='';
        await loadSession(state.sessionId);setError('');
      }catch(error){setError(error.message);button.disabled=false;}return;
    }
    if (button.id === 'devImportButton' || button.id === 'devEmptyImport') { await importProject(); return; }
    if (button.id === 'devRefreshFiles') { await loadFiles(); return; }
    if (button.id === 'devSettingsButton' || button.id === 'devSettingsQuick' || button.id === 'devManageModel' || button.id === 'devBottomSettings') { openSettings(); return; }
    if (button.id === 'devCloseSettings') { closeSettings(); return; }
    if (button.id === 'devAddProvider') { openProviderForm(); return; }
    if (button.id === 'devProviderCancel') { resetProviderForm(); return; }
    if (button.id === 'devNewSessionButton' || button.id === 'devAddSession') { await createSession(); return; }
    if (button.hasAttribute('data-dev-prompt')) { if (!state.projectId) { setError('请先点击「导入本地项目」选择项目。'); return; } $('#devPrompt').value = button.dataset.devPrompt; $('#devPrompt').focus(); return; }
    if (button.hasAttribute('data-file-path')) { await openFile(button.dataset.filePath); return; }
    if (button.hasAttribute('data-session-id')) { pollGeneration++; pollingId = ''; state.sessionId = button.dataset.sessionId; state.busy = false; rememberSelection(); await loadSession(state.sessionId); setError(''); return; }
    if (button.hasAttribute('data-change-action')) { await performChange(button.dataset.changeId, button.dataset.changeAction); return; }
    if (button.hasAttribute('data-edit-provider')) { const p = state.providers.find(item => item.id === button.dataset.editProvider); if (p) openProviderForm(p); return; }
    if (button.hasAttribute('data-test-provider')) { button.disabled = true; button.textContent = '测试中…'; try { const result = await api('providers/' + encodeURIComponent(button.dataset.testProvider) + '/test', {}); toast(result.message); } catch (error) { setError(error.message); } finally { button.disabled = false; button.textContent = '测试连接'; } return; }
    if (button.hasAttribute('data-delete-provider')) { if (!confirm('删除此模型配置？已有会话记录仍会保留。')) return; try { await api('providers/' + encodeURIComponent(button.dataset.deleteProvider) + '/remove', {}); await loadState(); toast('已删除模型配置'); } catch (error) { setError(error.message); } return; }
    if (button.id === 'devStopButton') { await api(`sessions/${encodeURIComponent(state.sessionId)}/stop`, {}); return; }
  });
  root.addEventListener('change', async event => {
    if (event.target.id === 'devProjectSelect') {
      await selectProject(event.target.value);
    }
    if (event.target.id === 'devModelSelect') { localStorage.setItem('devSelectedProvider', event.target.value); renderConversation(); }
  });
  $('#devComposer').addEventListener('submit', event => { event.preventDefault(); void sendMessage($('#devPrompt').value); });
  $('#devPrompt').addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); $('#devComposer').requestSubmit(); } });
  $('#devSettingsModal').addEventListener('click', event => { if (event.target.id === 'devSettingsModal') closeSettings(); });
  $('#devProviderForm').addEventListener('submit', async event => {
    event.preventDefault(); const button = $('#devProviderSave'); button.disabled = true; button.textContent = '保存中…';
    try {
      await api('providers', { id: $('#devProviderId').value || undefined, name: $('#devProviderName').value, protocol: $('#devProviderProtocol').value, baseUrl: $('#devProviderUrl').value, model: $('#devProviderModel').value, apiKey: $('#devProviderKey').value });
      await loadState(); resetProviderForm(); setError(''); toast('模型配置已保存');
    } catch (error) { setError(error.message); }
    finally { button.disabled = false; button.textContent = $('#devProviderId').value ? '保存修改' : '保存模型'; }
  });
  document.addEventListener('keydown', event => {
    if ($('#devSettingsModal').classList.contains('hidden')) return;
    if (event.key === 'Escape') closeSettings();
    if (event.key === 'Tab') {
      const elements = [...$('#devSettingsModal').querySelectorAll('button, input, select')].filter(el => !el.disabled && el.getClientRects().length);
      const first = elements[0], last = elements.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  });
  document.addEventListener('workspace:view', event => { if (event.detail === 'developer') void loadState(); });
  void loadState();
})();
