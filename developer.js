(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const icon = name => '<svg class="icon"><use href="#i-' + name + '"/></svg>';
  const api = async (path, body) => {
    const response = await fetch('/api/dev/' + path, { method: body === undefined ? 'GET' : 'POST', headers: body === undefined ? {} : { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store' });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || '请求失败，请重试。'); return data;
  };
  const state = { skills: [], projects: [], providers: [], sessions: [], projectId: localStorage.getItem('devProject') || '', sessionId: localStorage.getItem('devSession') || '', files: [], file: '', session: null, busy: false };
  let draftImages = [], addingImages = false, sending = false, creatingSession = false, draftGeneration = 0;
  let pollGeneration = 0, pollingId = '', settingsTrigger;
  let reasoningSaving = false;
  const reasoningLabels = {default: '默认', none: '关闭推理', minimal: '极低', low: '低', medium: '中', high: '高', xhigh: '极高', max: '最高'};
  let accessProjectId = null, accessSaveQueue = Promise.resolve();
  const accessDrafts = new Map();
  const rememberSelection = () => { localStorage.setItem('devProject', state.projectId); localStorage.setItem('devSession', state.sessionId); };
  const root = $('#developerView');
  if (!root) return;
  let collapsedProjectIds;
  try { collapsedProjectIds = JSON.parse(localStorage.getItem('devCollapsedProjects') || '[]'); }
  catch { collapsedProjectIds = []; }
  const collapsedProjects = new Set(Array.isArray(collapsedProjectIds) ? collapsedProjectIds.filter(id => typeof id === 'string') : []);
  let sidebarCollapsed = localStorage.getItem('devSidebarCollapsed') === '1';
  let filesCollapsed = localStorage.getItem('devFilesCollapsed') === '1';

  root.innerHTML = `
    <div class="dev-workbench" id="devWorkbench">
      <section class="dev-agent-panel"><div class="dev-agent-heading"><div class="dev-agent-avatar">${icon('spark')}</div><div><strong id="devConversationTitle">开发 Agent</strong><small id="devAgentStatus"><i></i>准备就绪</small></div><button class="dev-panel-more" id="devSettingsQuick" aria-label="模型设置">···</button></div><div class="dev-agent-info"><span class="dev-agent-project-icon">{ }</span><div><strong id="devAgentProjectName">尚未选择项目</strong><small id="devAgentProviderStatus">配置模型以开始</small></div></div><div class="dev-skill-bar"><label for="devSkillSelect">开发 Skill</label><select id="devSkillSelect"><option value="software-development">软件开发 · 内置</option></select><button id="devViewSkill" type="button">查看指引</button></div><details class="dev-skill-details" id="devSkillDetails"><summary>Skill 说明</summary><p id="devSkillDescription">新任务默认使用内置软件开发流程。</p><pre id="devSkillContent" class="hidden"></pre></details><div id="devConversation" class="dev-conversation"><div class="dev-empty-agent"><span class="dev-agent-spark">✳</span><strong>你好，我是你的开发 Agent</strong><p>我可以先阅读项目源码，帮你梳理结构、定位问题并提出代码修改。可逐项审核修改和检查命令，也可为本次任务授权持续执行。</p><div class="dev-agent-suggestions"><button data-dev-prompt="请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。">梳理项目结构 ${icon('arrow')}</button><button data-dev-prompt="阅读项目的 README 和主要源码，说明如何运行项目，并指出最值得优先改进的地方。">阅读项目并给出建议 ${icon('arrow')}</button></div></div></div><div id="devExecution" class="dev-execution"></div><div id="devPendingChanges" class="dev-pending-list"></div><div class="dev-model-row"><label for="devModelSelect">执行模型</label><select id="devModelSelect"><option value="">添加模型后可开始</option></select><button id="devManageModel" class="dev-plain-button">配置</button></div><details class="dev-task-options"><summary>任务标准与执行权限</summary><label>任务类型<select id="devTaskKind"><option value="auto">自动识别（审查默认只读）</option><option value="change">代码修改与验证</option><option value="inspect">只读分析</option></select></label><label>完成标准<input id="devAcceptance" maxlength="4000" placeholder="例如：修复空输入报错，原有测试继续通过"></label><label class="dev-permission"><input type="checkbox" id="devAllowEdits">本次任务自动应用源码修改（保留恢复记录）</label><label class="dev-permission"><input type="checkbox" id="devAllowCommands">本次任务允许运行项目检查</label><small>未授权的动作会逐项审核。项目检查会执行本机代码，请仅对可信项目授权。文件与网络未隔离，详见访问范围。</small></details><form class="dev-composer" id="devComposer"><textarea id="devPrompt" rows="2" maxlength="16000" placeholder="描述你想完成的开发任务…" disabled></textarea><div class="dev-composer-bottom"><span id="devComposerHint">请先导入一个项目</span><div><button type="button" id="devStopButton" class="dev-stop-button hidden">停止</button><button type="submit" id="devSendButton" class="dev-send-button hidden" disabled aria-label="发送">${icon('send')}</button></div></div></form><div id="devError" class="dev-inline-error hidden" role="alert"></div></section>
      <section class="dev-editor-area"><div class="dev-editor-toolbar"><div class="dev-breadcrumb" id="devEditorTitle">项目文件 <span>/</span> 选择文件</div><div class="dev-editor-tools"><span class="dev-editor-language" id="devFileType">SOURCE</span><button class="dev-plain-button" id="devRefreshFiles">${icon('refresh')}刷新</button></div></div><div class="dev-code-layout"><aside class="dev-file-tree" id="devFileTree"><div class="dev-tree-label">项目文件</div><div class="dev-empty-files">导入项目以浏览源码</div></aside><div class="dev-file-preview" id="devFilePreview"><div class="dev-code-empty"><span class="dev-empty-icon">{ }</span><strong>项目代码，尽在掌握</strong><p>导入本地项目后，可以浏览源码或让 Agent 帮你分析代码结构。</p><button class="primary-button" id="devEmptyImport">${icon('plus')}导入本地项目</button></div></div></div></section></div>
    <div class="dev-bottom-strip"><span>${icon('check')} 模型 API Key 加密保存在本机</span><span>执行检查 → 反馈纠错 → 证据验收</span><button id="devBottomSettings">配置接入模型 ${icon('arrow')}</button></div>
    <div class="dev-modal-backdrop hidden" id="devSettingsModal" role="presentation"><div class="dev-settings-modal" role="dialog" aria-modal="true" aria-labelledby="devSettingsTitle"><div class="dev-modal-title"><div><div class="eyebrow"><span class="eyebrow-line"></span> MODEL PROVIDERS</div><h2 id="devSettingsTitle">模型接入设置</h2></div><button id="devCloseSettings" class="dev-square-button" aria-label="关闭">×</button></div><p class="dev-modal-description">接入 OpenAI Chat Completions、Responses 或 Anthropic Messages API。需要你自备 API Key 与模型权限。执行任务时，任务描述、添加的图片和 Agent 读取的源码将发送给所选模型服务。图片输入需要模型支持视觉能力。</p><div id="devSettingsError" class="dev-inline-error hidden" role="alert"></div><div id="devProviderList" class="dev-provider-list"></div><form id="devProviderForm" class="dev-provider-form"><input type="hidden" id="devProviderId"><label>配置名称<input id="devProviderName" maxlength="60" placeholder="如 DeepSeek 主力模型" required></label><label>接口协议<select id="devProviderProtocol"><option value="compatible">OpenAI Chat Completions</option><option value="responses">OpenAI Responses API</option><option value="anthropic">Anthropic Messages API</option></select></label><label class="dev-provider-wide">Base URL<input id="devProviderUrl" type="url" placeholder="https://api.deepseek.com/v1" required></label><label>模型名称<input id="devProviderModel" maxlength="150" placeholder="deepseek-chat" required></label><label>API Key<input id="devProviderKey" type="password" autocomplete="new-password" placeholder="sk-…（保留当前密钥请留空）"></label><div class="dev-provider-actions"><button type="button" class="secondary-button" id="devProviderCancel">取消</button><button type="submit" class="primary-button" id="devProviderSave">保存模型</button></div></form><div class="dev-modal-footer"><span>${icon('check')} 密钥使用本机密钥加密后存储</span><button type="button" id="devAddProvider">${icon('plus')}添加模型配置</button></div></div></div>`;

  const composerTools = document.createElement('div');
  composerTools.className = 'dev-composer-tools';
  composerTools.innerHTML = '<details id="devAccessPicker" class="dev-composer-picker"><summary aria-label="访问权限"><svg class="icon" viewBox="0 0 24 24"><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z"/></svg><span id="devAccessLabel">逐项审核</span><span class="dev-picker-chevron">⌄</span></summary><div class="dev-picker-popover"><strong>访问权限</strong><div class="dev-access-modes" role="radiogroup" aria-label="访问权限模式"><label><input type="radio" name="devAccessMode" value="readonly"><span>只读分析<small>仅阅读源码，不修改或运行代码</small></span></label><label><input type="radio" name="devAccessMode" value="review" checked><span>逐项审核<small>修改和检查命令逐项确认</small></span></label><label><input type="radio" name="devAccessMode" value="automatic"><span>自动执行<small>允许应用修改、运行受支持的检查</small></span></label></div><p>权限仅对下一次新任务生效；当前任务权限保持不变。自动执行仍受已导入目录和命令范围限制。</p><div id="devAdvancedOptions"></div></div></details><details id="devModelPicker" class="dev-composer-picker"><summary aria-label="选择模型"><span id="devModelLabel">未配置模型</span><span class="dev-picker-chevron">⌄</span></summary><div class="dev-picker-popover"><strong>执行模型</strong><div id="devModelOptions"></div></div></details>';
  const composerFooter = $('.dev-composer-bottom');
  $('#devPrompt').insertAdjacentHTML('beforebegin', '<div id="devImageDrafts" class="dev-image-drafts hidden" aria-label="待发送的图片"></div>');
  root.insertAdjacentHTML('beforeend', '<dialog id="devImageViewer" class="dev-image-viewer" aria-label="查看图片"><form method="dialog"><button aria-label="关闭图片">×</button></form><img alt=""></dialog>');
  root.insertAdjacentHTML('beforeend', '<dialog id="devConfirmationDialog" class="dev-confirmation-dialog" aria-labelledby="devConfirmationTitle" aria-describedby="devConfirmationQuestion"><form id="devConfirmationForm"><h2 id="devConfirmationTitle">任务需要你确认</h2><p id="devConfirmationReason" class="dev-confirmation-reason"></p><p id="devConfirmationQuestion" class="dev-confirmation-question"></p><p id="devConfirmationSummary" class="dev-confirmation-summary hidden"></p><label for="devConfirmationAnswer">你的回答</label><textarea id="devConfirmationAnswer" rows="4" maxlength="16000" required placeholder="在这里回答，提交后继续同一任务"></textarea><p id="devConfirmationError" class="dev-inline-error hidden" role="alert"></p><div class="dev-confirmation-actions"><button id="devConfirmationLater" type="button" class="secondary-button">稍后回答</button><button id="devConfirmationSubmit" type="submit" class="primary-button">提交并继续</button></div></form></dialog>');
  const confirmationDialog = $('#devConfirmationDialog');
  const confirmationDrafts = new Map();
  let deferredConfirmationKey = '';
  const confirmationKey = session => session?.status === 'awaiting_user' && session.task?.outcome?.question && !session.archivedAt
    ? [session.id, session.task.id, session.task.outcome.at, session.task.outcome.question].join(':') : '';
  function syncConfirmationDialog() {
    const key = confirmationKey(state.session);
    if (!key) { if (confirmationDialog.open) confirmationDialog.close(); confirmationDialog.dataset.key = ''; return; }
    if (confirmationDialog.dataset.key !== key) {
      confirmationDialog.dataset.key = key;
      const outcome = state.session.task.outcome;
      $('#devConfirmationReason').textContent = outcome.reason || '';
      $('#devConfirmationQuestion').textContent = outcome.question;
      $('#devConfirmationSummary').textContent = outcome.summary || '';
      $('#devConfirmationSummary').classList.toggle('hidden', !outcome.summary);
      $('#devConfirmationAnswer').value = confirmationDrafts.get(key) || '';
      $('#devConfirmationError').classList.add('hidden');
    }
    if (document.body.dataset.view === 'developer' && key !== deferredConfirmationKey && !confirmationDialog.open && !sending) {
      closeComposerPickers(); confirmationDialog.showModal(); $('#devConfirmationAnswer').focus();
    }
  }
  $('#devConversation').addEventListener('click', event => {
    const button = event.target.closest('[data-view-image]');
    if (!button) return;
    const image = button.querySelector('img'), viewer = $('#devImageViewer');
    viewer.querySelector('img').src = image.src;
    viewer.querySelector('img').alt = image.alt;
    viewer.showModal();
  });
  composerFooter.insertBefore(composerTools, composerFooter.lastElementChild);
  $('#devModelOptions').append($('.dev-model-row'));
  $('#devModelOptions').append($('.dev-skill-bar'), $('#devSkillDetails'));
  document.querySelector('label[for="devSkillSelect"]').textContent = '内置 Skill';
  $('#devSkillSelect').innerHTML = '<option value="auto">自动选择</option>';
  $('#devSkillSelect').setAttribute('aria-describedby', 'devSkillStatus');
  $('.dev-skill-bar').insertAdjacentHTML('beforeend', `<small id="devSkillStatus" class="dev-skill-status" role="status"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg><span></span></small>`);
  $('#devManageModel').insertAdjacentHTML('beforebegin', `<div class="dev-reasoning-control"><label for="devReasoningSelect">推理强度</label><select id="devReasoningSelect" aria-describedby="devReasoningHint">${Object.entries(reasoningLabels).map(([value,label]) => `<option value="${value}">${label}${value === 'default' ? '（服务端设置）' : ` · ${value}`}</option>`).join('')}</select><small id="devReasoningHint" role="status"></small></div>`);
  $('#devAdvancedOptions').append($('.dev-task-options'));
  $('#devAdvancedOptions').insertAdjacentHTML('beforebegin', '<details id="devAccessScope"><summary>目录、命令、联网与敏感配置范围</summary><div id="devAccessScopeBody"></div></details>');
  $('#devAccessPicker .dev-picker-popover>p').textContent = '选择后自动保存到本项目，新对话自动选中上次保存的权限；没有记录时默认逐项审核。设置仅对新任务生效；当前任务的实际权限显示在任务轨迹中。自动执行只减少审批，项目检查进程没有文件或网络隔离。';
  $('.dev-access-modes').insertAdjacentHTML('afterend', '<small id="devAccessSaveStatus" role="status"></small>');
  $('#devManageModel').type = 'button';
  const pickers = [$('#devAccessPicker'), $('#devModelPicker')];
  function closeComposerPickers() { pickers.forEach(picker=>{picker.open=false;}); }
  pickers.forEach(picker=>picker.addEventListener('toggle',()=>{
    if(picker.open)pickers.filter(other=>other!==picker).forEach(other=>{other.open=false;});
  }));
  document.addEventListener('pointerdown',event=>{if(!composerTools.contains(event.target))closeComposerPickers();});
  composerTools.addEventListener('keydown',event=>{
    if(event.key==='Enter'&&event.target.matches('input')){
      event.preventDefault();closeComposerPickers();$('#devPrompt').focus();
    }
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'){
      const opened=pickers.find(picker=>picker.open);
      if(opened){opened.open=false;opened.querySelector('summary').focus();}
    }
  });
  document.querySelector('.sidebar').id = 'workspaceSidebar';
  const sidebarToggle = document.createElement('button');
  sidebarToggle.id = 'devToggleSidebar';
  sidebarToggle.className = 'dev-square-button';
  sidebarToggle.setAttribute('aria-controls', 'workspaceSidebar');
  sidebarToggle.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></svg>';
  function placeSidebarToggle(view) {
    (view === 'developer' ? $('.dev-agent-heading') : document.querySelector('.breadcrumb')).prepend(sidebarToggle);
  }
  placeSidebarToggle(document.body.dataset.view);
  $('#devSettingsQuick').textContent = '模型设置';
  $('#devSettingsQuick').className = 'dev-plain-button dev-heading-settings';
  $('#devConversationTitle').parentElement.classList.add('dev-heading-title');
  const filesPanel = $('.dev-editor-area');
  filesPanel.id = 'devFilesPanel';
  const filesToggle = document.createElement('button');
  filesToggle.id = 'devToggleFiles';
  filesToggle.className = 'dev-square-button';
  filesToggle.setAttribute('aria-controls', 'devFilesPanel');
  filesToggle.textContent = '›';
  filesPanel.querySelector('.dev-editor-toolbar').prepend(filesToggle);
  const restoreFiles = document.createElement('button');
  restoreFiles.id = 'devRestoreFiles';
  restoreFiles.className = 'dev-plain-button hidden';
  restoreFiles.textContent = '展开项目文件';
  restoreFiles.setAttribute('aria-controls', 'devFilesPanel');
  $('.dev-agent-heading').insertBefore(restoreFiles, $('#devSettingsQuick'));
  function applyPanelLayout() {
    document.body.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    root.classList.toggle('files-collapsed', filesCollapsed);
    sidebarToggle.setAttribute('aria-expanded', String(!sidebarCollapsed));
    sidebarToggle.setAttribute('aria-label', sidebarCollapsed ? '展开侧栏' : '收起侧栏');
    sidebarToggle.title = sidebarCollapsed ? '展开侧栏' : '收起侧栏';
    filesToggle.setAttribute('aria-expanded', String(!filesCollapsed));
    filesToggle.setAttribute('aria-label', filesCollapsed ? '展开项目文件' : '收起项目文件');
    filesToggle.title = '收起项目文件';
    restoreFiles.setAttribute('aria-expanded', String(!filesCollapsed));
    restoreFiles.classList.toggle('hidden', !filesCollapsed);
  }
  $('.dev-agent-panel').addEventListener('click', event => {
    if (!event.target.closest('#devConversation')) return;
    if (event.target.closest('[data-result-diff], [data-result-trace], [data-result-file-path]')) return;
    if (rightTab !== 'browser' || filesCollapsed) return;
    filesCollapsed = true;
    localStorage.setItem('devFilesCollapsed', '1');
    applyPanelLayout();
    document.dispatchEvent(new Event('workspace:right-panel'));
  });
  applyPanelLayout();
  const fileContextMenu = document.createElement('div');
  fileContextMenu.className = 'dev-file-context-menu hidden';
  fileContextMenu.setAttribute('role', 'menu');
  fileContextMenu.innerHTML = '<button type="button" role="menuitem" data-open-file-folder>在文件夹中显示</button>';
  document.body.append(fileContextMenu);
  let contextFilePath = '';
  function closeFileContextMenu() { fileContextMenu.classList.add('hidden'); contextFilePath = ''; }
  $('#devFileTree').addEventListener('contextmenu', event => {
    const row = event.target.closest('[data-file-path]');
    if (!row) return;
    event.preventDefault();
    contextFilePath = row.dataset.filePath;
    fileContextMenu.classList.toggle('hidden', typeof window.shujinDesktop?.showItemInFolder !== 'function');
    if (fileContextMenu.classList.contains('hidden')) return;
    const {innerWidth, innerHeight} = window;
    fileContextMenu.style.left = Math.min(event.clientX, innerWidth - fileContextMenu.offsetWidth - 8) + 'px';
    fileContextMenu.style.top = Math.min(event.clientY, innerHeight - fileContextMenu.offsetHeight - 8) + 'px';
  });
  document.addEventListener('click', event => { if (!event.target.closest('.dev-file-context-menu')) closeFileContextMenu(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeFileContextMenu(); });
  fileContextMenu.addEventListener('click', async event => {
    const item = event.target.closest('[data-open-file-folder]');
    if (!item || !contextFilePath) return;
    const path = contextFilePath;
    closeFileContextMenu();
    try { await window.shujinDesktop.showItemInFolder(activeProject()?.id, path); }
    catch (error) { setError(error.message); }
  });
  const filesTabPanel = document.createElement('section');
  filesTabPanel.id = 'devFilesTabPanel';
  filesTabPanel.className = 'dev-files-tabpanel';
  filesTabPanel.setAttribute('role', 'tabpanel');
  filesTabPanel.setAttribute('aria-labelledby', 'devFilesTab');
  while (filesPanel.firstChild) filesTabPanel.append(filesPanel.firstChild);
  const traceTabPanel = document.createElement('section');
  traceTabPanel.id = 'devTraceTabPanel';
  traceTabPanel.className = 'dev-trace-tabpanel hidden';
  traceTabPanel.setAttribute('role', 'tabpanel');
  traceTabPanel.setAttribute('aria-labelledby', 'devTraceTab');
  traceTabPanel.append($('#devExecution'));
  const browserTabPanel = document.createElement('section');
  browserTabPanel.id = 'devBrowserTabPanel';
  browserTabPanel.className = 'dev-browser-tabpanel hidden';
  browserTabPanel.setAttribute('role', 'tabpanel');
  browserTabPanel.setAttribute('aria-labelledby', 'devBrowserTab');
  browserTabPanel.innerHTML = '<div class="dev-browser-empty"><strong>小红书小窗</strong><p>在这里浏览小红书，同时继续 Agent 任务。</p><a class="primary-button" href="https://www.xiaohongshu.com/explore" target="_blank" rel="noopener noreferrer" data-open-xhs data-xhs-mode="mini">打开小红书</a></div>';
  const rightTabs = document.createElement('div');
  rightTabs.className = 'dev-right-tabs';
  rightTabs.innerHTML = '<div role="tablist" aria-label="项目与任务"><button id="devFilesTab" role="tab" aria-controls="devFilesTabPanel" aria-selected="true">项目文件</button><button id="devTraceTab" role="tab" aria-controls="devTraceTabPanel" aria-selected="false" tabindex="-1">任务轨迹</button><button id="devBrowserTab" role="tab" aria-controls="devBrowserTabPanel" aria-selected="false" tabindex="-1">页面浏览</button></div>';
  rightTabs.prepend(filesToggle);
  filesPanel.append(rightTabs, filesTabPanel, traceTabPanel, browserTabPanel);
  let rightTab = 'files';
  function selectRightTab(tab) {
    rightTab = tab;
    for (const [name, button, panel] of [['files', $('#devFilesTab'), filesTabPanel], ['trace', $('#devTraceTab'), traceTabPanel], ['browser', $('#devBrowserTab'), browserTabPanel]]) {
      button.setAttribute('aria-selected', String(tab === name));
      button.tabIndex = tab === name ? 0 : -1;
      panel.classList.toggle('hidden', tab !== name);
    }
    document.dispatchEvent(new Event('workspace:right-panel'));
  }
  rightTabs.addEventListener('keydown', event => {
    if (event.target.getAttribute('role') === 'tab' && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      const tabs = ['files', 'trace', 'browser'];
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 2 : (tabs.indexOf(rightTab) + (event.key === 'ArrowRight' ? 1 : 2)) % 3;
      selectRightTab(tabs[next]);
      rightTabs.querySelector('[aria-selected="true"]').focus();
    }
  });
  const workbench = $('#devWorkbench');
  const rightResize = document.createElement('div');
  rightResize.id = 'devRightResize';
  rightResize.className = 'dev-right-resize';
  rightResize.tabIndex = 0;
  rightResize.setAttribute('role', 'separator');
  rightResize.setAttribute('aria-orientation', 'vertical');
  rightResize.setAttribute('aria-label', '调整右侧页面栏宽度');
  rightResize.setAttribute('aria-controls', 'devFilesPanel');
  rightResize.title = '左右拖动调整宽度；双击恢复默认宽度';
  workbench.insertBefore(rightResize, filesPanel);
  let preferredRightWidth = Number(localStorage.getItem('devRightPanelWidth')) || 0, rightDrag;
  function updateRightWidth(width, remember = false) {
    const maximum = Math.max(280, workbench.getBoundingClientRect().width - (innerWidth > 1100 ? 340 : 300) - 8);
    const effective = Math.round(Math.max(280, Math.min(maximum, width)));
    if (width) workbench.style.setProperty('--dev-right-track', effective + 'px');
    else workbench.style.removeProperty('--dev-right-track');
    rightResize.setAttribute('aria-valuemin', '280');
    rightResize.setAttribute('aria-valuemax', String(Math.floor(maximum)));
    rightResize.setAttribute('aria-valuenow', String(Math.round(filesPanel.getBoundingClientRect().width)));
    if (remember) {
      preferredRightWidth = width ? effective : 0;
      if (width) localStorage.setItem('devRightPanelWidth', String(effective));
      else localStorage.removeItem('devRightPanelWidth');
    }
  }
  rightResize.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    event.preventDefault();
    rightDrag = { x: event.clientX, width: filesPanel.getBoundingClientRect().width };
    rightResize.setPointerCapture(event.pointerId);
    document.body.classList.add('right-panel-resizing');
    document.dispatchEvent(new Event('workspace:right-panel'));
  });
  rightResize.addEventListener('pointermove', event => {
    if (rightDrag) updateRightWidth(rightDrag.width + rightDrag.x - event.clientX);
  });
  const finishRightDrag = () => {
    if (!rightDrag) return;
    updateRightWidth(filesPanel.getBoundingClientRect().width, true);
    rightDrag = null;
    document.body.classList.remove('right-panel-resizing');
    document.dispatchEvent(new Event('workspace:right-panel'));
  };
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) rightResize.addEventListener(name, finishRightDrag);
  rightResize.addEventListener('dblclick', () => updateRightWidth(0, true));
  rightResize.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home'].includes(event.key)) return;
    event.preventDefault();
    updateRightWidth(event.key === 'Home' ? 0 : filesPanel.getBoundingClientRect().width + (event.key === 'ArrowLeft' ? 16 : -16), true);
  });
  new ResizeObserver(() => updateRightWidth(preferredRightWidth)).observe(workbench);
  updateRightWidth(preferredRightWidth);
  const toast = message => window.showToast ? showToast(message) : void 0;
  const setError = message => { const box = $('#devSettingsModal').classList.contains('hidden') ? $('#devError') : $('#devSettingsError'); box.textContent = message || ''; box.classList.toggle('hidden', !message); };
  const openSettings = () => { settingsTrigger = $('#devModelPicker > summary'); closeComposerPickers(); $('#devSettingsModal').classList.remove('hidden'); renderProviders(); $('#devCloseSettings').focus(); };
  const projectSidebar = document.createElement('section');
  projectSidebar.className = 'dev-project-sidebar';
  projectSidebar.setAttribute('aria-label', '开发项目与会话');
  projectSidebar.innerHTML = `<div class="dev-project-sidebar-heading"><strong>项目</strong><button id="devImportButton" class="dev-square-button" aria-label="导入本地项目" title="导入本地项目">${icon('plus')}</button></div><div id="devProjectGroups" class="dev-project-groups"></div><div class="dev-project-sidebar-footer"><span id="devSessionCount">选择项目后开始</span><span id="devProjectMeta" title="项目文件留在本机">项目文件留在本机</span></div>`;
  document.querySelector('.main-nav').insertAdjacentElement('afterend', projectSidebar);
  const sidebarResize = document.createElement('div');
  sidebarResize.id = 'devSidebarResize';
  sidebarResize.className = 'dev-sidebar-resize';
  sidebarResize.tabIndex = 0;
  sidebarResize.setAttribute('role', 'separator');
  sidebarResize.setAttribute('aria-orientation', 'vertical');
  sidebarResize.setAttribute('aria-label', '调整任务侧栏宽度');
  sidebarResize.title = '左右拖动调整宽度；双击恢复默认宽度';
  projectSidebar.parentElement.append(sidebarResize);
  let preferredSidebarWidth = Number(localStorage.getItem('devSidebarWidth')) || 0;
  const sidebarWidthLimit = () => Math.max(180, Math.min(420, innerWidth - 56 - 360));
  function updateSidebarWidth(width, remember = false) {
    const effective = Math.round(Math.max(180, Math.min(sidebarWidthLimit(), width)));
    if (width) document.documentElement.style.setProperty('--project-sidebar-width', effective + 'px');
    else document.documentElement.style.removeProperty('--project-sidebar-width');
    sidebarResize.setAttribute('aria-valuemin', '180');
    sidebarResize.setAttribute('aria-valuemax', String(sidebarWidthLimit()));
    sidebarResize.setAttribute('aria-valuenow', String(Math.round(projectSidebar.parentElement.getBoundingClientRect().width)));
    if (remember) {
      preferredSidebarWidth = width ? effective : 0;
      if (width) localStorage.setItem('devSidebarWidth', String(effective));
      else localStorage.removeItem('devSidebarWidth');
    }
  }
  updateSidebarWidth(preferredSidebarWidth);
  let sidebarDrag;
  sidebarResize.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    event.preventDefault();
    sidebarDrag = { x: event.clientX, width: projectSidebar.parentElement.getBoundingClientRect().width };
    sidebarResize.setPointerCapture(event.pointerId);
    document.body.classList.add('sidebar-resizing');
  });
  sidebarResize.addEventListener('pointermove', event => {
    if (sidebarDrag) updateSidebarWidth(sidebarDrag.width + event.clientX - sidebarDrag.x);
  });
  const finishSidebarDrag = () => {
    if (!sidebarDrag) return;
    updateSidebarWidth(projectSidebar.parentElement.getBoundingClientRect().width, true);
    sidebarDrag = null;
    document.body.classList.remove('sidebar-resizing');
  };
  sidebarResize.addEventListener('pointerup', finishSidebarDrag);
  sidebarResize.addEventListener('lostpointercapture', finishSidebarDrag);
  sidebarResize.addEventListener('pointercancel', finishSidebarDrag);
  sidebarResize.addEventListener('dblclick', () => updateSidebarWidth(0, true));
  sidebarResize.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home'].includes(event.key)) return;
    event.preventDefault();
    updateSidebarWidth(event.key === 'Home' ? 0 : projectSidebar.parentElement.getBoundingClientRect().width + (event.key === 'ArrowRight' ? 16 : -16), true);
  });
  window.addEventListener('resize', () => updateSidebarWidth(preferredSidebarWidth));
  const xhsTaskStrip = document.createElement('section');
  xhsTaskStrip.id = 'xhsTaskStrip';
  xhsTaskStrip.className = 'xhs-task-strip';
  xhsTaskStrip.setAttribute('aria-label', 'Agent 任务状态');
  $('#accountView').prepend(xhsTaskStrip);
  const closeSettings = () => { $('#devSettingsModal').classList.add('hidden'); settingsTrigger?.focus(); };
  const activeProject = () => state.projects.find(p => p.id === state.projectId);
  const currentSession = () => state.session;
  function renderProjects() {
    renderProjectGroups();
    const project = activeProject();
    $('#devProjectMeta').textContent = project ? project.path + (project.gitBranch ? ' · Git: ' + project.gitBranch : '') : '项目文件留在本机';
    $('#devProjectMeta').title = project ? project.path + (project.gitBranch ? ' · 当前分支：' + project.gitBranch : '') : '项目文件留在本机';
    $('#devAgentProjectName').textContent = project?.name || '尚未选择项目';
    $('#devConversationTitle').textContent = state.session?.title || (project ? '新开发会话' : '开发 Agent');
    $('#devConversationTitle').title = $('#devConversationTitle').textContent;
    $('#devPrompt').disabled = sending || creatingSession || !!state.session?.archivedAt;
    $('#devAgentStatus').textContent = state.session?.archivedAt ? '已归档 · 可恢复后继续' : statusLabel(state.session?.status || 'idle');
    $('#devComposerHint').textContent = !project ? '请先导入一个项目' : state.busy ? 'Enter 补充要求 · Shift + Enter 换行' : state.providers.length ? 'Enter 发送 · Shift + Enter 换行' : '请先配置模型';
    $('#devSessionCount').textContent = project ? `${state.sessions.filter(s => s.projectId === project.id && !s.archivedAt).length} 个会话` : '选择项目后开始';
    $('#devAgentProviderStatus').textContent = state.providers.length ? `${state.providers.length} 个模型配置可用` : '配置模型以开始';
    renderModelSelect(); renderSkills(); renderAccessControl();
  }
  function renderSkills() {
    const select=$('#devSkillSelect'), selected=select.value || 'auto';
    select.innerHTML='<option value="auto">自动选择（推荐）</option>'+state.skills.map(skill=>`<option value="${escapeHtml(skill.id)}">${escapeHtml(skill.name)}</option>`).join('')+'<option value="none">不使用 Skill</option>';
    select.value=['auto','none'].includes(selected)||state.skills.some(skill=>skill.id===selected)?selected:'auto';
    select.disabled=state.busy;
    $('.dev-skill-bar').classList.toggle('is-locked', state.busy);
    select.title=state.busy?'任务执行中，暂不可切换 Skill':'选择新任务使用的 Skill';
    const currentTask=state.session?.task;
    const currentSkill=currentTask?.skill?.name || (currentTask?.classificationComplete?'不使用 Skill':'正在自动选择');
    $('#devSkillStatus span').textContent=state.busy?`执行中，暂不可切换 · 当前：${currentSkill}`:'仅对新任务生效';
    const skill=state.skills.find(skill=>skill.id===select.value);
    $('#devSkillDescription').textContent=skill?skill.description+(skill.limitations?' '+skill.limitations:'')+' 手动指定仅对新任务生效。':select.value==='auto'?`根据对话和 ${state.skills.length} 个 Skill 的用途自动选择，也可不使用；只按需加载相关资料。`:'不加载内置 Skill；基础工具、审批和验证规则仍然生效。';
    $('#devViewSkill').disabled=select.value==='none';
    $('#devViewSkill').textContent=select.value==='auto'?'查看技能库':'查看指引';
  }
  function renderModelSelect() {
    const select = $('#devModelSelect'), selected = select.value || state.session?.providerId || localStorage.getItem('devSelectedProvider') || '';
    select.innerHTML = '<option value="">选择执行模型</option>' + state.providers.map(p => `<option value="${escapeHtml(p.id)}">${escapeHtml(p.name)} · ${escapeHtml(p.model)}</option>`).join('');
    select.value = state.providers.some(p => p.id === selected) ? selected : state.providers[0]?.id || '';
    updateSendButton();
    $('#devModelSelect').disabled = state.busy || reasoningSaving || sending;
    renderModelLabel();
    if (select.value) localStorage.setItem('devSelectedProvider', select.value);
  }
  function composerResumes(message) {
    if (!state.session?.task) return false;
    if (state.session.status === 'awaiting_user') return true;
    return ['failed', 'needs_help', 'stopped'].includes(state.session.status) && /^(?:(?:请)?(?:(?:继续|接着)(?:完成|执行|处理)?(?:(?:当前|上次|之前|原来|未完成)(?:的)?)?(?:任务|工作)?|重试(?:当前任务)?|再试一次)|continue|resume|retry)$/i.test(message.trim().replace(/[。.!！ ]+$/, '').trim());
  }
  function updateSendButton() {
    resizePrompt();
    const hasText = !!$('#devPrompt').value.trim() || draftImages.length > 0;
    $('#devSendButton').classList.toggle('hidden', !hasText);
    const awaiting = state.session?.status === 'awaiting_user';
    const resuming = composerResumes($('#devPrompt').value);
    const sendLabel = state.busy ? '补充要求' : awaiting ? '回答并继续' : resuming ? '继续当前任务' : '发送';
    $('#devSendButton').setAttribute('aria-label', sendLabel);
    $('#devSendButton').innerHTML = state.busy ? '补充要求' : icon('send');
    $('#devSendButton').classList.toggle('is-supplement', state.busy);
    $('#devPrompt').placeholder = state.busy ? '随时补充要求，例如“只修改登录页”；下一次模型请求前接收…' : awaiting ? '任务等待确认，请在弹出的确认框回答…' : !state.projectId ? '描述你想完成的开发任务，选择项目后发送…' : ['failed','needs_help','stopped'].includes(state.session?.status) ? '输入“继续”续作当前任务，或描述新任务…' : '描述你想完成的开发任务…';
    if ($('#devResumeTask')) $('#devResumeTask').disabled = addingImages || sending || creatingSession || !!state.session?.archivedAt;
    $('#devSendButton').disabled = !hasText || !state.projectId || (!state.busy && !resuming && !$('#devModelSelect').value) || addingImages || sending || reasoningSaving || creatingSession || !!state.session?.archivedAt;
    $('#devSendButton').title = state.busy ? '补充要求：保存后在下一次模型请求前纳入当前任务' : !state.projectId ? (state.projects.length ? '请先选择左侧项目' : '请先导入本地项目') : sendLabel;
    renderModelLabel();
  }
  function resizePrompt() {
    const prompt = $('#devPrompt');
    if (!prompt.getClientRects().length) return;
    const scrollTop = prompt.scrollTop;
    prompt.style.overflowY = 'hidden';
    prompt.style.height = 'auto';
    prompt.style.height = prompt.scrollHeight + 'px';
    prompt.style.overflowY = prompt.scrollHeight > prompt.clientHeight ? 'auto' : 'hidden';
    prompt.scrollTop = scrollTop;
  }
  function clearImages() {
    draftGeneration++;
    draftImages = [];
    renderImageDrafts();
  }
  function renderImageDrafts() {
    const target = $('#devImageDrafts');
    target.classList.toggle('hidden', !draftImages.length);
    target.innerHTML = draftImages.map((image, index) => `<figure><img src="${image.dataUrl}" alt="${escapeHtml(image.name)}"><figcaption>${escapeHtml(image.name)}</figcaption><button type="button" data-remove-image="${index}" aria-label="移除图片 ${escapeHtml(image.name)}">×</button></figure>`).join('');
    updateSendButton();
  }
  function renderMessageImages(images, sessionId) {
    if (!images?.length) return '';
    return '<div class="dev-message-images">' + images.map(image => {
      const url = `/api/dev/sessions/${encodeURIComponent(sessionId)}/images/${encodeURIComponent(image.id)}`;
      return `<button type="button" data-view-image aria-label="查看图片 ${escapeHtml(image.name)}"><img src="${url}" alt="${escapeHtml(image.name)}" loading="lazy"></button>`;
    }).join('') + '</div>';
  }
  async function addImages(files) {
    if (!files.length || addingImages || sending || state.session?.archivedAt) return;
    const generation = draftGeneration;
    addingImages = true; updateSendButton();
    try {
      if (files.length + draftImages.length > 4) throw new Error('每条消息最多添加 4 张图片。');
      if (files.some(file => !['image/png', 'image/jpeg', 'image/webp'].includes(file.type))) throw new Error('仅支持 PNG、JPEG 和 WebP 图片。');
      if (files.some(file => file.size > 5 * 1024 * 1024)) throw new Error('单张图片不能超过 5 MB。');
      if ([...files, ...draftImages].reduce((sum, file) => sum + file.size, 0) > 12 * 1024 * 1024) throw new Error('每条消息图片合计不能超过 12 MB。');
      const images = await Promise.all(files.map(async file => {
        const dataUrl = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = () => reject(new Error('无法读取图片，请重新选择。'));
          reader.readAsDataURL(file);
        });
        await new Promise((resolve, reject) => {
          const image = new Image();
          image.onload = resolve;
          image.onerror = () => reject(new Error('图片无法打开，请选择有效图片。'));
          image.src = dataUrl;
        });
        return {name: file.name || '粘贴的图片.png', dataUrl, size: file.size};
      }));
      if (generation !== draftGeneration) return;
      draftImages.push(...images); renderImageDrafts(); setError('');
    } catch (error) { if (generation === draftGeneration) setError(error.message); }
    finally { addingImages = false; updateSendButton(); }
  }
  $('#devImageDrafts').addEventListener('click', event => {
    const button = event.target.closest('[data-remove-image]');
    if (!button || sending || addingImages || state.session?.archivedAt) return;
    draftImages.splice(Number(button.dataset.removeImage), 1); renderImageDrafts();
  });
  $('#devPrompt').addEventListener('paste', event => {
    const files = [...(event.clipboardData?.files || [])];
    if (!files.length) return;
    event.preventDefault(); void addImages(files);
  });
  $('#devComposer').addEventListener('dragover', event => {
    if (event.dataTransfer?.types.includes('Files')) event.preventDefault();
  });
  $('#devComposer').addEventListener('drop', event => {
    if (!event.dataTransfer?.files.length) return;
    event.preventDefault(); void addImages([...event.dataTransfer.files]);
  });
  function renderModelLabel() {
    const provider = state.providers.find(p=>p.id===$('#devModelSelect').value);
    const locked = state.busy || composerResumes($('#devPrompt').value);
    const taskProvider = locked ? state.providers.find(p=>p.id===state.session?.providerId) : null;
    const displayedProvider = taskProvider || provider;
    if (taskProvider) $('#devModelSelect').value = taskProvider.id;
    const effort = locked ? state.session?.task?.reasoningEffort || 'default' : provider?.reasoningEffort || 'default';
    const levels = displayedProvider?.reasoningEfforts || ['default'];
    $('#devReasoningSelect').innerHTML = levels.map(value => `<option value="${value}">${reasoningLabels[value] || value}${value === 'default' ? '（服务端设置）' : ` · ${value}`}</option>`).join('');
    $('#devReasoningSelect').value = effort;
    $('#devReasoningSelect').disabled = !provider || locked || reasoningSaving || sending;
    $('#devReasoningHint').textContent = reasoningSaving ? '正在保存…' : locked ? '当前任务沿用启动时的推理强度。' : !provider ? '选择模型后可设置。' : '自动保存到此模型；可用强度取决于模型和服务。';
    $('#devModelLabel').textContent = displayedProvider ? displayedProvider.model + (effort !== 'default' ? ` · ${reasoningLabels[effort] || effort}` : '') : '未配置模型';
    $('#devModelSelect').disabled = locked || reasoningSaving || sending;
    $('#devModelPicker > summary').title = provider ? `${provider.name} · ${provider.model}` : '选择或配置模型';
    renderAccessPolicy();
  }
  async function saveReasoningEffort(effort) {
    const provider = state.providers.find(p=>p.id===$('#devModelSelect').value);
    if (!provider || reasoningSaving || state.busy) return;
    const previous = provider.reasoningEffort || 'default';
    provider.reasoningEffort = effort;
    reasoningSaving = true; renderModelLabel(); updateSendButton();
    try {
      const saved = await api(`providers/${encodeURIComponent(provider.id)}/reasoning`, {reasoningEffort: effort});
      const current = state.providers.find(p=>p.id===provider.id);
      if (current) Object.assign(current, saved);
      setError('');
    } catch (error) {
      const current = state.providers.find(p=>p.id===provider.id);
      if (current) current.reasoningEffort = previous;
      setError('推理强度保存失败：' + error.message);
    } finally { reasoningSaving = false; renderModelLabel(); updateSendButton(); }
  }
  function accessScopeHtml(scope, policy) {
    if (!policy) return '<p>正在读取后端权限范围…</p>';
    const labels={directories:'目录',commands:'命令',network:'联网',sensitive:'敏感配置',process:'进程执行范围'};
    return `<p>项目目录：${escapeHtml(scope?.root || '尚未选择项目')}</p><p>当前 Git 分支：${escapeHtml(scope?.gitBranch || '无 Git 分支或处于 detached HEAD')}</p><p>模型数据发送地址：${escapeHtml(scope?.model?.baseUrl || '尚未选择模型')}</p>${Object.entries(labels).map(([key,label])=>`<p><b>${label}：</b>${escapeHtml(policy[key])}</p>`).join('')}`;
  }
  function renderAccessPolicy() {
    const project=state.projects.find(p=>p.id===state.projectId), provider=state.providers.find(p=>p.id===$('#devModelSelect').value);
    $('#devAccessScopeBody').innerHTML=accessScopeHtml({root:project?.path,model:provider},state.accessPolicy);
  }
  function accessSettings() {
    return {kind: $('#devTaskKind').value, permissions: {edits: $('#devAllowEdits').checked, commands: $('#devAllowCommands').checked}};
  }
  function restoreProjectAccess() {
    const settings = accessDrafts.get(state.projectId)?.settings || activeProject()?.taskSettings;
    $('#devTaskKind').value = settings?.kind || 'auto';
    $('#devAllowEdits').checked = settings?.permissions?.edits === true;
    $('#devAllowCommands').checked = settings?.permissions?.commands === true;
    accessProjectId = state.projectId;
    renderAccessControl();
  }
  function saveProjectAccess() {
    const projectId = state.projectId;
    if (!projectId) return;
    const draft = {settings: accessSettings(), pending: true, error: ''};
    accessDrafts.set(projectId, draft);
    renderAccessControl();
    accessSaveQueue = accessSaveQueue.then(async () => {
      try {
        const settings = await api(`projects/${encodeURIComponent(projectId)}/task-settings`, draft.settings);
        const project = state.projects.find(project => project.id === projectId);
        if (project) project.taskSettings = settings;
        // Keep the latest local selection if an older state response arrives later.
      } catch (error) {
        draft.error = '权限保存失败：' + error.message + ' 请重新选择权限后重试。';
        if (state.projectId === projectId && accessDrafts.get(projectId) === draft) setError(draft.error);
      } finally {
        draft.pending = false;
        if (state.projectId === projectId) renderAccessControl();
      }
    });
  }
  async function flushProjectAccess(projectId) {
    let pending;
    do { pending = accessSaveQueue; await pending; } while (pending !== accessSaveQueue);
    const error = accessDrafts.get(projectId)?.error;
    if (error) throw new Error(error);
  }
  function renderAccessControl() {
    const readOnly = $('#devTaskKind').value === 'inspect';
    if(readOnly){$('#devAllowEdits').checked=false;$('#devAllowCommands').checked=false;}
    const edits = $('#devAllowEdits').checked, commands = $('#devAllowCommands').checked;
    const mode = readOnly ? 'readonly' : edits && commands ? 'automatic' : !edits && !commands ? 'review' : 'custom';
    composerTools.dataset.access=mode;
    const label = {readonly:'只读分析',review:'逐项审核',automatic:'自动执行',custom:'自定义权限'}[mode];
    $('#devAccessLabel').textContent = label;
    const draft = accessDrafts.get(state.projectId);
    $('#devAccessSaveStatus').textContent = draft?.pending ? '正在保存本项目权限…' : draft?.error || (draft || activeProject()?.taskSettings ? '已保存到本机，供本项目的新对话使用。' : '本项目暂无保存记录，默认逐项审核。');
    const disabled = state.busy || sending || creatingSession || !state.projectId;
    composerTools.querySelectorAll('[name="devAccessMode"]').forEach(input=>{input.checked=input.value===mode;input.disabled=disabled;});
    $('#devTaskKind').disabled=disabled;
    ['#devAllowEdits','#devAllowCommands'].forEach(selector=>{$(selector).disabled=disabled||readOnly;});
    renderAccessPolicy();
  }
  function renderProviders() {
    $('#devProviderList').innerHTML = state.providers.length ? state.providers.map(p => `<article class="dev-provider-card"><div class="dev-provider-card-icon">${p.protocol === 'anthropic' ? 'A' : 'AI'}</div><div class="dev-provider-card-body"><strong>${escapeHtml(p.name)}</strong><small>${escapeHtml(p.model)} · ${p.protocol === 'anthropic' ? 'Anthropic API' : p.protocol === 'responses' ? 'OpenAI Responses API' : 'OpenAI Chat Completions'}</small><span>${escapeHtml(p.baseUrl)} · ${p.hasKey ? 'API Key 已加密' : '未配置 API Key'}</span></div><div class="dev-provider-card-actions"><button data-edit-provider="${escapeHtml(p.id)}">编辑</button><button data-test-provider="${escapeHtml(p.id)}">测试连接</button><button class="dev-provider-delete" data-delete-provider="${escapeHtml(p.id)}" aria-label="删除 ${escapeHtml(p.name)}">删除</button></div></article>`).join('') : '<div class="dev-provider-empty"><strong>还没有模型配置</strong><span>添加模型厂商并填写 Base URL、模型名称和 API Key。</span></div>';
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
      const next = await api('state'); state.skills = next.skills || []; state.projects = next.projects; state.providers = next.providers; state.sessions = next.sessions;
      state.accessPolicy = next.accessPolicy;
      if (state.projectId && !state.projects.some(p => p.id === state.projectId)) state.projectId = '';
      if (state.sessionId && !state.sessions.some(s => s.id === state.sessionId && s.projectId === state.projectId)) state.sessionId = '';
      if (!state.sessionId) { state.session = null; state.busy = false; }
      if (accessProjectId !== state.projectId) restoreProjectAccess();
      rememberSelection();
      renderProjects(); renderProviders(); renderAccessControl();
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
    $('#devSessionCount').textContent = `${state.sessions.filter(s => s.projectId === projectId && !s.archivedAt).length} 个会话`;
    renderProjectGroups();
  }
  function renderProjectGroups() {
    renderXhsTasks();
    const expandedArchives = new Set([...document.querySelectorAll('.dev-archived-sessions[open]')].map(details=>details.dataset.archivedProject));
    const row = session => {
      const s = session.id === state.sessionId && state.session ? {...session,status:state.session.status,title:state.session.title} : session;
      const action = s.archivedAt ? 'restore' : 'archive';
      const label = s.archivedAt ? '恢复会话' : '归档会话';
      const disabled = !s.archivedAt && ['running','waiting','review'].includes(s.status);
      return `<div class="dev-session-row"><button class="dev-session-item ${s.id===state.sessionId?'active':''}" data-session-id="${escapeHtml(s.id)}" title="${escapeHtml(s.title)}"><span class="dev-session-copy"><strong>${escapeHtml(s.title)}</strong></span><span class="dev-session-status ${escapeHtml(s.status)}" role="img" aria-label="${escapeHtml(statusLabel(s.status))}" title="${escapeHtml(statusLabel(s.status))}"></span></button><button class="dev-session-archive" data-session-archive="${escapeHtml(s.id)}" data-archive-action="${action}" aria-label="${label} ${escapeHtml(s.title)}" title="${disabled?'请先停止任务并处理审核':label}" ${disabled?'disabled':''}><svg class="icon" viewBox="0 0 24 24">${s.archivedAt?'<path d="M9 4 4 9l5 5M4 9h10a6 6 0 0 1 0 12"/>':'<path d="M3 4h18v4H3zM5 8v12h14V8M9 12h6"/>'}</svg></button></div>`;
    };
    $('#devProjectGroups').innerHTML = state.projects.length ? state.projects.map(project => {
      const sessions = state.sessions.filter(s=>s.projectId===project.id);
      const active = sessions.filter(s=>!s.archivedAt), archived = sessions.filter(s=>s.archivedAt);
      const collapsed = collapsedProjects.has(project.id);
      return `<div class="dev-project-group"><div class="dev-project-header"><button class="dev-project-row ${project.id===state.projectId?'active':''}" data-project-id="${escapeHtml(project.id)}" aria-pressed="${project.id===state.projectId}" aria-expanded="${!collapsed}" aria-controls="project-sessions-${escapeHtml(project.id)}" title="${escapeHtml(project.path)}"><span class="dev-project-chevron">${collapsed?'▸':'▾'}</span><svg class="icon" viewBox="0 0 24 24"><path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1l-2 11H3L1 9a1 1 0 0 1 1-1h18"/></svg><span>${escapeHtml(project.name)}</span><small>${active.length}</small></button><button ${project.id===state.projectId?'id="devNewSessionButton"':''} class="dev-project-new-session" data-new-session-project="${escapeHtml(project.id)}" aria-label="创建新会话" title="创建新会话" ${sending||creatingSession?'disabled':''}>${icon('plus')}</button></div><div class="dev-project-sessions ${collapsed?'hidden':''}" id="project-sessions-${escapeHtml(project.id)}">${active.map(row).join('')||'<div class="dev-project-no-sessions">暂无会话</div>'}${archived.length?`<details class="dev-archived-sessions" data-archived-project="${escapeHtml(project.id)}" ${(expandedArchives.has(project.id)||state.session?.archivedAt&&state.projectId===project.id)?'open':''}><summary>已归档 (${archived.length})</summary>${archived.map(row).join('')}</details>`:''}</div></div>`;
    }).join('') : '<div class="dev-session-empty">导入本地项目后，项目和会话会显示在这里。</div>';
  }
  function renderXhsTasks() {
    const sessions = state.sessions.filter(s=>!s.archivedAt).map(s=>s.id===state.sessionId&&state.session?{...s,status:state.session.status,title:state.session.title}:s);
    xhsTaskStrip.innerHTML = [['running','运行中'],['completed','已完成']].map(([status,label])=>{
      const tasks = sessions.filter(s=>s.status===status).sort((a,b)=>String(b.updatedAt).localeCompare(String(a.updatedAt)));
      const visible = status==='completed'?tasks.slice(0,5):tasks;
      return `<div class="xhs-task-group" role="group" aria-label="${label}"><span class="xhs-task-label">${status==='running'&&tasks.length?'<i class="xhs-task-spinner" aria-hidden="true"></i>':''}${label}</span><div class="xhs-task-names">${visible.map(s=>`<button class="xhs-task-name" data-task-session-id="${escapeHtml(s.id)}" title="${escapeHtml((state.projects.find(p=>p.id===s.projectId)?.name||'')+' / '+s.title)}">${escapeHtml(s.title)}</button>`).join('')||`<span class="xhs-task-empty">暂无${label==='运行中'?'运行':'完成'}任务</span>`}</div></div>`;
    }).join('');
  }
  const directoryPages = new Map(), expandedDirectories = new Set();
  let treeGeneration = 0, previewGeneration = 0, previewPage, previewOffsets = [0], previewIndex = 0;
  async function loadDirectory(path = '', append = false) {
    const projectId = state.projectId, generation = treeGeneration;
    const previous = directoryPages.get(path);
    if (previous?.loading) return;
    directoryPages.set(path, { ...previous, loading: true }); renderFileTree();
    try {
      const offset = append ? previous?.next_offset || 0 : 0;
      const result = await api(`projects/${encodeURIComponent(projectId)}/files?path=${encodeURIComponent(path)}&offset=${offset}`);
      if (projectId !== state.projectId || generation !== treeGeneration) return;
      directoryPages.set(path, { ...result, entries: [...(append ? previous.entries : []), ...result.entries] });
      renderFileTree();
    } catch (error) {
      if (projectId !== state.projectId || generation !== treeGeneration) return;
      directoryPages.set(path, { ...previous, error: error.message }); renderFileTree(); setError(error.message);
    }
  }
  async function loadFiles() {
    treeGeneration++; directoryPages.clear(); expandedDirectories.clear();
    if (state.projectId) await loadDirectory();
  }
  function renderFileTree() {
    const tree = $('#devFileTree'), rows = [];
    function renderDirectory(path, depth) {
      const page = directoryPages.get(path);
      for (const node of page?.entries || []) {
        const folder = node.type === 'directory', open = expandedDirectories.has(node.path);
        rows.push(`<button class="dev-file-row ${node.path === state.file ? 'active' : ''} ${folder ? 'folder' : ''}" style="--depth:${depth}" ${folder ? `data-directory-path="${escapeHtml(node.path)}" aria-expanded="${open}"` : `data-file-path="${escapeHtml(node.path)}"`} title="${escapeHtml(node.path)}"><span class="dev-file-symbol">${folder ? (open ? '▾' : '▸') : fileSymbol(node.path)}</span><span>${escapeHtml(node.name)}</span></button>`);
        if (folder && open) renderDirectory(node.path, depth + 1);
      }
      if (page?.loading) rows.push('<div class="dev-empty-files" role="status">正在加载目录…</div>');
      else if (page?.error || page?.hasMore) rows.push(`<button class="dev-tree-more" data-directory-more="${escapeHtml(path)}" data-directory-retry="${!!page.error}">${page.error ? '加载失败，点击重试' : '加载更多文件'}</button>`);
      else if (!page?.entries?.length && page) rows.push('<div class="dev-empty-files">此目录没有可预览文件</div>');
    }
    renderDirectory('', 0);
    tree.innerHTML = '<div class="dev-tree-label">项目文件</div>' + rows.join('');
  }
  async function locateProjectFile(path) {
    const projectId = state.projectId;
    if (!projectId || typeof path !== 'string' || !path) return;
    filesCollapsed = false; applyPanelLayout(); selectRightTab('files');
    const parts = path.split('/');
    let directory = '';
    for (let index = 0; index < parts.length; index++) {
      const name = parts[index];
      let page = directoryPages.get(directory);
      while (page && !page.entries.some(entry => entry.name === name) && page.hasMore && projectId === state.projectId) {
        await loadDirectory(directory, true);
        page = directoryPages.get(directory);
      }
      const entry = page?.entries.find(item => item.name === name);
      if (!entry) { setError('此文件未出现在当前项目目录中，请刷新文件树后重试。'); return; }
      if (index === parts.length - 1) {
        if (entry.type !== 'file') { setError('结果路径不是文件。'); return; }
        renderFileTree();
        const row = [...$('#devFileTree').querySelectorAll('[data-file-path]')].find(item => item.dataset.filePath === path);
        row?.scrollIntoView({block: 'nearest'});
        await openFile(path);
        return;
      }
      if (entry.type !== 'directory') { setError('结果路径中的目录结构已变化。'); return; }
      expandedDirectories.add(entry.path);
      directory = entry.path;
      if (!directoryPages.has(directory)) await loadDirectory(directory);
    }
  }
  function fileSymbol(path) { const ext = path.split('.').at(-1).toLowerCase(); return ({ js: 'JS', mjs: 'JS', ts: 'TS', tsx: 'TS', jsx: 'JS', css: 'CSS', html: '<>', json: '{}', md: 'MD', py: 'PY', go: 'GO', rs: 'RS', vue: 'VUE' })[ext] || '·'; }
  async function openFile(path, more = false, previous = false) {
    const projectId = state.projectId;
    if (more && previewPage?.loading) return;
    const generation = more ? previewGeneration : ++previewGeneration;
    const nextIndex = more ? Math.max(0, previewIndex + (previous ? -1 : 1)) : 0;
    const offset = more ? (previous ? previewOffsets[nextIndex] : previewPage?.next_offset || 0) : 0;
    previewPage = { ...previewPage, loading: true };
    if (!more) { state.file = path; renderFileTree(); $('#devFilePreview').innerHTML = '<div class="dev-empty-files" role="status">正在读取文件…</div>'; }
    else $('#devFilePreview').querySelectorAll('[data-file-more]').forEach(button => button.disabled = true);
    try {
      const result = await api(`projects/${encodeURIComponent(projectId)}/file?path=${encodeURIComponent(path)}&offset=${offset}`);
      if (projectId !== state.projectId || path !== state.file || generation !== previewGeneration) return;
      if (more && result.digest !== previewPage.digest) { setError('文件已变化，请重新选择文件读取。'); previewPage.loading = false; return; }
      previewPage = result;
      if (!more) previewOffsets = [0];
      previewIndex = nextIndex; previewOffsets[previewIndex] = offset;
      $('#devEditorTitle').innerHTML = '<span>' + escapeHtml(activeProject()?.name || '项目') + '</span> / ' + escapeHtml(path);
      $('#devFileType').textContent = fileSymbol(path);
      const preview = $('#devFilePreview');
      const rows = result.content.split('\n').map((line, index) => `<span class="dev-source-line"><i>${result.start_line + index}</i><span>${escapeHtml(line.replace(/\r$/, ''))}</span></span>`).join('');
      preview.innerHTML = `<pre class="dev-source"><code>${rows}</code></pre><div class="dev-source-pagination"><span>字符 ${result.offset.toLocaleString()}–${result.next_offset.toLocaleString()} / ${result.total_chars.toLocaleString()}</span>${previewIndex ? `<button class="dev-source-more" data-file-more="${escapeHtml(path)}" data-file-previous="true">上一段</button>` : ''}${result.hasMore ? `<button class="dev-source-more" data-file-more="${escapeHtml(path)}">下一段</button>` : ''}</div>`;
      preview.scrollTop = 0;
      setError('');
    } catch (error) {
      if (projectId !== state.projectId || path !== state.file || generation !== previewGeneration) return;
      previewPage.loading = false; $('#devFilePreview').querySelectorAll('[data-file-more]').forEach(button => button.disabled = false); setError(error.message);
    }
  }
  async function createSession(preserveDraft = false, projectId = state.projectId) {
    if (!projectId || creatingSession || (sending && !preserveDraft)) return;
    let selectedSessionId = state.sessionId;
    creatingSession = true; renderProjects();
    try {
      if (projectId !== state.projectId) {
        await selectProject(projectId);
        if (projectId !== state.projectId) return;
        selectedSessionId = state.sessionId;
      }
      await flushProjectAccess(projectId);
      if (projectId !== state.projectId || selectedSessionId !== state.sessionId) return;
      const session = await api('sessions', { projectId });
      if (projectId !== state.projectId || selectedSessionId !== state.sessionId) return;
      collapsedProjects.delete(projectId);
      localStorage.setItem('devCollapsedProjects', JSON.stringify([...collapsedProjects]));
      if (!preserveDraft) clearImages();
      state.sessionId = session.id;
      restoreProjectAccess();
      renderAccessControl(); rememberSelection(); await loadSession(session.id);
      if (projectId !== state.projectId || state.sessionId !== session.id) return;
      return session.id;
    }
    catch (error) { setError(error.message); }
    finally {
      creatingSession = false; renderProjects();
      if (projectId === state.projectId && !sending && !state.session?.archivedAt) $('#devPrompt').focus();
    }
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
      const tasks = [...(session.tasks || []), ...(session.task ? [session.task] : [])];
      const rendered = new Set();
      container.innerHTML = session.messages.map(m => {
        const task = m.role === 'assistant' ? tasks.find(t => t.result && !rendered.has(t.id) && (m.type === 'task_result' ? m.taskId === t.id : m.content === t.result.summary + '\n\n验证依据：' + t.result.evidence)) : null;
        if (task) rendered.add(task.id);
        const supplement = m.supplementId ? tasks.find(t => t.id === m.taskId)?.supplements?.find(s => s.id === m.supplementId) : null;
        const receipt = !supplement ? '' : supplement.status === 'included' ? '已纳入本次任务' : '待接收' + (session.task?.id === m.taskId && session.status === 'running' ? ' · 当前操作已开始，后续步骤生效' : ' · 继续任务后接收');
        return `<article class="dev-chat-message ${m.role === 'user' ? 'user' : 'assistant'}"><span class="dev-message-avatar">${m.role === 'user' ? '我' : icon('spark')}</span><div class="dev-message-content">${m.role === 'user' ? `<p>${escapeHtml(m.content)}</p>${renderMessageImages(m.images, session.id)}${receipt ? `<small class="dev-supplement-status" role="status">${escapeHtml(receipt)}</small>` : ''}` : task ? renderResultCard(session, task) : (m.type === 'task_result' ? '<p class="dev-result-warning">此结果已失效，请重新验证。</p>' : '') + formatAssistant(m.content)}</div></article>`;
      }).join('');
    }
    if (state.busy) container.insertAdjacentHTML('beforeend', '<div class="dev-thinking"><i></i><i></i><i></i><span>正在阅读项目与处理任务…</span></div>');
    container.scrollTop = container.scrollHeight;
    $('#devStopButton').classList.toggle('hidden', !state.busy);
    updateSendButton();
  }
  function formatAssistant(value) {
    let safe = escapeHtml(value);
    safe = safe.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_, language, code) => `<pre><code>${code.trim()}</code></pre>`);
    safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
    safe = safe.replace(/^### (.+)$/gm, '<h4>$1</h4>').replace(/^## (.+)$/gm, '<h4>$1</h4>');
    safe = safe.replace(/^[-*] (.+)$/gm, '<li>$1</li>').replace(/(<li>[\s\S]+?<\/li>\s*)+/g, '<ul>$&</ul>');
    return safe.split(/\n{2,}/).map(block => /^<(?:pre|ul|h4)>/.test(block) ? block : '<p>' + block.replace(/\n/g, '<br>') + '</p>').join('');
  }
  const statusLabel = status => ({idle:'准备就绪',running:'执行中',review:'等待变更审核',waiting:'等待命令授权',completed:'已完成',awaiting_user:'等待用户回答',needs_help:'执行失败',stopped:'已停止',passed:'通过',failed:'失败',timed_out:'超时',interrupted:'结果未知',denied:'已拒绝',pending_approval:'待授权',queued:'排队中',spawn_error:'启动失败',error:'执行错误',output_limit:'输出超限'})[status] || status;
  function renderResultTopics(task) {
    const result = task.result;
    const cards = Array.isArray(result.cards) ? result.cards.filter(card => typeof card?.title === 'string' && Array.isArray(card.items) && card.items.every(item => typeof item === 'string') && !/^(分析依据与范围|分析依据|验证依据|验证与范围)$/.test(card.title.trim())) : [];
    const topic = (title, content, index, extra = '') => `<li class="dev-result-topic ${extra}"><div class="dev-result-topic-heading"><span class="dev-result-number" aria-hidden="true">${index}</span><h4>${escapeHtml(title)}</h4></div><div class="dev-result-topic-body">${content}</div></li>`;
    const topics = cards.length ? cards.map((card, index) => topic(card.title, `<ul>${card.items.map(item => `<li>${formatAssistant(item)}</li>`).join('')}</ul>`, index + 1)) : [topic('完成内容', formatAssistant(result.summary), 1)];
    return `${cards.length ? `<div class="dev-result-summary">${formatAssistant(result.summary)}</div>` : ''}<ol class="dev-result-topics" aria-label="结果要点">${topics.join('')}</ol>`;
  }
  function resultEvidenceNote(task) {
    const evidence = String(task.result.evidence || '').replace(/\s+/g, ' ').trim();
    if (!evidence) return '';
    const firstSentence = evidence.match(/^[^。！？!?]+[。！？!?]?/)?.[0]?.trim() || evidence;
    const preview = firstSentence.length <= 100 ? firstSentence : firstSentence.slice(0, 96).replace(/[，、；;\s]+$/, '') + '…';
    const more = evidence.length > firstSentence.length || firstSentence.length > 100 ? ' 详细依据与范围见任务记录。' : '';
    return '<p class="dev-result-note">说明：' + escapeHtml(preview + more) + '</p>';
  }
  function renderResultCard(session, task) {
    const changes = session.changes.filter(c => c.taskId === task.id && ['applied', 'reverted'].includes(c.status));
    const files = task.result.files || [...new Set(changes.map(c => c.path))].map(path => ({path}));
    const totals = files.reduce((sum, file) => ({additions: sum.additions + (file.additions || 0), deletions: sum.deletions + (file.deletions || 0)}), {additions: 0, deletions: 0});
    const stats = file => file.additions == null ? '' : `<span class="dev-result-stats"><span class="added">+${file.additions}</span><span class="removed">−${file.deletions}</span></span>`;
    const commands = session.commands.filter(c => c.taskId === task.id);
    const verification = commands.find(c => c.id === task.verification?.commandId);
    const verified = verification?.status === 'passed' && !verification.stale;
    const stale = !!verification?.stale || changes.some(c => c.status === 'reverted');
    const verificationWarning = task.kind !== 'inspect' && !verified;
    const applied = changes.some(c => c.status === 'applied');
    const canRevert = applied && session.task?.id === task.id && !state.busy && !session.archivedAt && task.kind === 'change' && changes.some(c => c.status === 'applied' && c.original !== null);
    const fileRow = file => `<div class="dev-result-file"><button type="button" class="dev-result-file-locate" data-result-file-path="${escapeHtml(file.path)}" title="在右侧目录中定位文件">${escapeHtml(file.path)}</button>${stats(file)}</div>`;
    return `<section class="dev-result-card" aria-label="任务结果卡片" data-result-task="${escapeHtml(task.id)}">
      ${renderResultTopics(task)}
      ${verificationWarning ? '<p class="dev-result-warning">缺少有效的行为测试记录，请核对验证依据。</p>' : ''}
      ${stale ? '<p class="dev-result-warning">源码已变化 · 需重新验证</p>' : ''}
      ${files.length ? `<div class="dev-result-files"><div class="dev-result-files-head"><span class="dev-result-file-icon">${icon('file')}</span><div class="dev-result-files-title"><strong>已修改 ${files.length} 个文件</strong>${stats(totals)}</div><div class="dev-result-file-actions">${canRevert ? `<button type="button" data-result-revert="${escapeHtml(task.id)}" title="选择文件并撤销修改">撤销 ↶</button>` : ''}${applied ? `<button type="button" class="dev-result-view" data-result-diff="${escapeHtml(task.id)}">查看修改</button>` : ''}</div></div>${files.slice(0, 4).map(fileRow).join('')}${files.length > 4 ? `<details class="dev-result-more-files"><summary>展开其余 ${files.length - 4} 个文件</summary>${files.slice(4).map(fileRow).join('')}</details>` : ''}</div>` : ''}
      <div class="dev-result-records">${commands.length ? `<details class="dev-result-checks"><summary>检查记录（${commands.length}）</summary>${commands.map(c => `<article><strong>${escapeHtml([c.command, ...(c.args || [])].join(' '))}</strong><span>${escapeHtml(statusLabel(c.status))}${c.exitCode != null ? ' · exit ' + escapeHtml(c.exitCode) : ''}${c.stale ? ' · 源码已变化' : ''}</span><p>${escapeHtml(c.purpose)}</p><pre>${escapeHtml(c.output || c.error || '没有输出记录')}</pre></article>`).join('')}</details>` : ''}${session.task?.id === task.id ? '<button type="button" data-result-trace>任务记录</button>' : ''}</div>
      ${resultEvidenceNote(task)}
    </section>`;
  }
  function renderExecution() {
    const session=state.session, task=session?.task, target=$('#devExecution');
    if(!task){target.innerHTML='<div class="dev-trace-empty">开始任务后，这里显示计划、工具调用和执行结果。</div>';syncConfirmationDialog();return;}
    const previousDetails = target.dataset.taskId === task.id ? [...target.querySelectorAll('details')].map(detail => detail.open) : [];
    const previousScroll = target.dataset.taskId === task.id ? target.scrollTop : 0;
    target.dataset.taskId = task.id;
    if (['waiting','awaiting_user','failed','needs_help','stopped'].includes(session.status)) {
      filesCollapsed = false; applyPanelLayout(); selectRightTab('trace');
    }
    const metrics=task.metrics, events=session.events.filter(e=>!e.taskId||e.taskId===task.id).slice(-12);
    const workflowLabel=task.skill?.workflow?` · 当前指引：${escapeHtml(task.skill.workflow.name)}`:'';
    const phase=({classify:'判断任务类型',understand:'理解目标',context:'获取上下文',act:'执行修改',verify:'验证结果',review:'复核变更',complete:'完成',failed:'本次未完成',awaiting_user:'等待回答',awaiting_approval:'等待审核'})[task.phase] || task.phase;
    const elapsed=Math.round((new Date(task.finishedAt || Date.now())-new Date(task.startedAt))/1000);
    const checkpoint=task.checkpoint || {};
    const evidence=(checkpoint.evidence || []).map(item=>`<li>${escapeHtml(item.claim)} <small>来源：${escapeHtml(item.source)}${item.path?` · ${escapeHtml(item.path)}`:''}${item.valid===false?' · 已变化，需重新核实':''}</small></li>`).join('');
    const todo=(checkpoint.todo || []).map(item=>`<li>${escapeHtml(item)}</li>`).join('');
    const unresolved=session.commands.filter(c=>c.taskId===task.id&&['interrupted','running','queued'].includes(c.status));
    target.innerHTML=`<div class="dev-execution-head"><strong>${escapeHtml(statusLabel(session.status))}</strong><span>${escapeHtml(phase)}</span><button id="devExportLogs">导出记录</button></div><div class="dev-run-metrics"><span>${task.rounds} 轮 / ${task.calls} 次工具</span><span>${elapsed}s</span><span>${metrics.inputTokens+metrics.outputTokens} tokens</span><span>${metrics.failedCommands} 次检查失败 / ${metrics.toolErrors || 0} 次工具错误 / ${metrics.interventions} 次交互</span></div><p class="dev-active-skill">${task.skill?`任务 Skill：${escapeHtml(task.skill.name)} · v${escapeHtml(task.skill.version)}${workflowLabel} · 已加载 ${task.skill.loadedResources.length} 份补充指引`:'任务未加载内置 Skill'}</p><details><summary>任务计划与执行轨迹</summary><p>目标：${escapeHtml(task.goal)}</p><p>验收：${escapeHtml(task.acceptance)}</p><p>当前：${escapeHtml(checkpoint.summary || '正在明确任务')}</p><p>下一步：${escapeHtml(checkpoint.next_action || '读取相关源码')}</p>${checkpoint.failure?`<p class="dev-run-error">失败反馈：${escapeHtml(checkpoint.failure)}</p>`:''}${evidence?`<p>已确认的关键证据</p><ul>${evidence}</ul>`:''}${todo?`<p>待办</p><ol>${todo}</ol>`:''}${unresolved.length?`<p class="dev-run-error">中断的命令结果未知，请检查记录后重试：${unresolved.map(c=>escapeHtml(c.command+' '+c.args.join(' '))).join('；')}</p>`:''}<ol>${events.map(e=>`<li><strong>${escapeHtml(e.name)}</strong> · ${escapeHtml(e.detail)} <span>${escapeHtml(e.status==='completed'?'已执行':statusLabel(e.status))}</span>${e.error?`<p class="dev-run-error">${escapeHtml(e.error)}</p>`:''}${e.recovery?`<p>处理建议：${escapeHtml(e.recovery)}</p>`:''}</li>`).join('')}</ol><small>Token 由服务商返回，费用以厂商账单为准。完整记录包含工具输入、结果和时间。</small></details>${session.commands.filter(c=>c.taskId===task.id).map(c=>`<article class="dev-command-card"><div><strong>${escapeHtml(c.command+' '+c.args.join(' '))}</strong><span>${escapeHtml(statusLabel(c.status))}${c.exitCode!==null?' · exit '+c.exitCode:''}</span></div><p>${escapeHtml(c.purpose)}</p>${c.script?`<pre>${escapeHtml(c.script)}</pre>`:''}${c.output||c.error?`<details><summary>查看输出${c.truncated?'（仅保留末尾，已截断）':''}${c.stale?' · 源码已变化':''}</summary><pre>${escapeHtml(c.output || c.error)}</pre></details>`:''}${c.status==='pending_approval'?`<small>批准后以本机账号执行项目代码，可访问项目外文件和网络；执行范围见本任务访问范围。</small><div class="dev-command-actions"><button data-command-id="${c.id}" data-command-action="deny">拒绝</button><button data-command-id="${c.id}" data-command-action="approve" ${task.kind==='inspect'||session.archivedAt?'disabled':''}>批准本次命令</button></div>`:''}</article>`).join('')}${task.result?`<p class="dev-verification">验证依据：${escapeHtml(task.result.evidence)}</p>`:''}${['failed','needs_help','stopped','awaiting_user'].includes(session.status)?`<button id="devResumeTask" class="secondary-button">${session.status==='awaiting_user'?'回答并继续当前任务':session.status==='failed'?'重试当前任务':'继续当前任务'}</button>`:''}`;
    const taskMode=task.kind==='inspect'?'只读分析':task.permissions.edits&&task.permissions.commands?'自动执行':!task.permissions.edits&&!task.permissions.commands?'逐项审核':'自定义权限';
    const taskActions=task.kind==='inspect'?'禁止修改和运行代码':`修改${task.permissions.edits?'自动应用':'需审核'} · 命令${task.permissions.commands?'自动执行':'需审核'}`;
    target.querySelector('.dev-active-skill').insertAdjacentHTML('afterend', `<section id="devTaskAccess"><p><strong>当前任务权限：${taskMode}</strong> · ${taskActions}</p><details><summary>本任务访问范围</summary>${accessScopeHtml(task.accessScope,state.accessPolicy)}</details></section>`);
    const routing=task.lastIntent;
    if(routing?.type==='development'){
      const kind=routing.effectiveKind==='inspect'?'只读分析':'修改与验证';
      const tasks=(routing.tasks||[]).map(escapeHtml).join('；') || '执行中按目标确定';
      const tools=(routing.tools||[]).map(escapeHtml).join('、') || '执行中按需选择';
      target.querySelector('#devTaskAccess').insertAdjacentHTML('afterend', '<p class="dev-task-routing" id="devTaskRouting">模型判断：'+kind+' · 任务：'+tasks+' · 建议工具：'+tools+'</p>');
    }
    target.querySelectorAll('details').forEach((detail,index)=>{detail.open=previousDetails[index] ?? index===1;});
    target.scrollTop=previousScroll;
    if (task.outcome && ['failed','awaiting_user'].includes(session.status)) {
      const outcome = task.outcome;
      target.querySelector('.dev-execution-head').insertAdjacentHTML('afterend', `<section class="dev-task-outcome ${session.status}" id="devTaskOutcome" role="status"><strong>${escapeHtml(statusLabel(session.status))}</strong><p>${escapeHtml(outcome.reason)}</p>${outcome.question?`<p><b>${escapeHtml(outcome.question)}</b></p>`:''}${outcome.evidence?`<p>已有证据：${escapeHtml(outcome.evidence)}</p>`:''}<small>${session.status==='awaiting_user'?'在输入框回答后继续同一任务。':'未计为完成；可查看轨迹、调整后重试。'}</small></section>`);
    }
    if (session.status === 'awaiting_user' && task.outcome?.question) {
      $('#devResumeTask').textContent = '打开确认框';
      $('#devTaskOutcome small').textContent = '请在确认框回答；稍后也可重新打开。';
    }
    updateSendButton();
    if (session.archivedAt && $('#devResumeTask')) { $('#devResumeTask').disabled = true; $('#devResumeTask').title = '恢复会话后可继续任务'; }
    syncConfirmationDialog();
  }
  function renderPending() {
    const changes=state.session?.changes || [], pending=changes.filter(c=>c.status==='pending'), target=$('#devPendingChanges');
    const appliedDetailsOpen=!!target.querySelector('.dev-applied-changes')?.open;
    const card=(c,applied=false)=>{
      const cannotWrite=state.busy||state.session?.task?.kind==='inspect'||!!state.session?.archivedAt;
      const fileId=escapeHtml(c.id);
      const oldLines=(c.original??'').split(/\r?\n/).filter(Boolean).length, newLines=c.content.split(/\r?\n/).filter(Boolean).length;
      const label=applied?'已应用':c.status==='reverted'?'已恢复':'待审核';
      return `<article class="dev-change-card" data-change-card="${fileId}"><div class="dev-change-head"><span class="dev-change-badge">${c.original===null?'A':'M'}</span><strong>${escapeHtml(c.path)}</strong><span>${label}</span></div><p>${escapeHtml(c.reason||'未提供修改说明')}</p><div class="dev-change-stats"><span>${oldLines} 行 → ${newLines} 行</span><span>${c.original===null?'新建文件':c.status==='reverted'?'已恢复':'查看行级差异'}</span></div><details data-diff-details="${fileId}"><summary>查看行级差异</summary><div class="dev-diff-view"><p>正在读取差异…</p></div></details><div class="dev-change-actions">${applied?`<button data-change-action="revert" data-change-id="${fileId}" ${cannotWrite||c.original===null?'disabled':''}>恢复此修改前内容</button>`:`<button data-change-action="discard" data-change-id="${fileId}" ${state.busy?'disabled':''}>拒绝此项</button><button class="primary-button" data-change-action="apply" data-change-id="${fileId}" ${cannotWrite?'disabled':''}>接受并应用</button>`}</div></article>`;
    };
    target.innerHTML=(pending.length?`<div class="dev-review-heading"><div><strong>待审核的代码变更</strong><span>${pending.length} 个文件</span></div><small>应用后继续验证</small></div>`+pending.map(c=>card(c)).join(''):'')+(changes.some(c=>c.status==='applied')?'<details class="dev-applied-changes"><summary>已应用的变更与恢复</summary>'+changes.filter(c=>c.status==='applied').map(c=>card(c,true)).join('')+'</details>':'');
    for(const details of target.querySelectorAll('[data-diff-details]'))details.addEventListener('toggle',()=>{
      if(!details.open||details.dataset.loaded)return;
      details.dataset.loaded='1';
      const container=details.querySelector('.dev-diff-view');
      api(`sessions/${encodeURIComponent(state.sessionId)}/changes/diff`,{changeId:details.dataset.diffDetails}).then(result=>{
        if(result.tooLarge){container.innerHTML='<p class="dev-diff-too-large">此文件差异超过 24 KB，界面不加载完整文件对比；可通过项目文件预览查看源码。</p>';return;}
        const lines=(result.diff||'').split('\n');
        container.innerHTML=`<div class="dev-diff-summary"><span>−${result.deletions} 删除</span><span>+${result.additions} 新增</span><span>${escapeHtml(result.path)}</span></div><pre class="dev-diff-code">${lines.map(line=>`<span class="${line.startsWith('+++')||line.startsWith('---')?'meta':line.startsWith('+')?'added':line.startsWith('-')?'removed':'context'}">${escapeHtml(line||' ')}</span>`).join('\n')}</pre>`;
      }).catch(error=>{container.innerHTML=`<p class="dev-diff-error">${escapeHtml(error.message)}</p>`;details.dataset.loaded='';});
    });
    const appliedDetails=target.querySelector('.dev-applied-changes');
    if(appliedDetails)appliedDetails.open=appliedDetailsOpen;
  }
  async function selectProject(projectId, preferredSessionId) {
    if (state.projectId) clearImages();
    pollGeneration++; pollingId = ''; state.projectId = projectId; state.sessionId = ''; state.session = null; state.busy = false; state.file = ''; state.files = []; rememberSelection();
    restoreProjectAccess();
    renderProjects(); renderFileTree(); renderConversation(); renderPending(); renderExecution(); setError('');
    $('#devEditorTitle').textContent = '项目文件 / 选择文件';
    $('#devFileType').textContent = 'SOURCE';
    $('#devFilePreview').innerHTML = '<div class="dev-code-empty"><strong>选择文件预览源码</strong></div>';
    if (!projectId) return;
    const sessionId = preferredSessionId || state.sessions.find(s => s.projectId === projectId && !s.archivedAt)?.id;
    await Promise.all([loadFiles(), loadSessions()]);
    if (sessionId && state.projectId === projectId) { state.sessionId = sessionId; rememberSelection(); await loadSession(sessionId); }
  }
  async function sendMessage(message) {
    if ((!message.trim() && !draftImages.length) || sending || creatingSession || addingImages) return;
    if (!state.projectId) { setError('请先导入一个本地项目。'); return; }
    if (state.busy) {
      const sessionId = state.sessionId, taskId = state.session?.task?.id;
      const images = draftImages.map(({name, dataUrl}) => ({name, dataUrl}));
      sending = true; renderProjects();
      try {
        await api(`sessions/${encodeURIComponent(sessionId)}/supplement`, {taskId, message, images});
        if (state.sessionId === sessionId) { $('#devPrompt').value = ''; clearImages(); await loadSession(sessionId); setError(''); }
      } catch (error) {
        if (state.sessionId === sessionId) { await loadSession(sessionId).catch(() => {}); setError(error.message); }
      } finally { sending = false; renderProjects(); updateSendButton(); }
      return;
    }
    const resuming = composerResumes(message);
    if (reasoningSaving) { setError('正在保存推理强度，请稍后发送。'); return; }
    const providerId = $('#devModelSelect').value;
    if (!resuming && !providerId) { openSettings(); setError('请先配置并选择执行模型。'); return; }
    const images = draftImages.map(({name, dataUrl}) => ({name, dataUrl}));
    sending = true; renderProjects();
    let sessionId;
    try {
      const projectId = state.projectId, selectedSessionId = state.sessionId;
      if (!resuming) await flushProjectAccess(projectId);
      if (projectId !== state.projectId || selectedSessionId !== state.sessionId) return;
      if (!state.sessionId) {
        const createdId = await createSession(true);
        if (!createdId || state.sessionId !== createdId) return;
      }
      if (projectId !== state.projectId || !state.sessionId) return;
      sessionId = state.sessionId;
      closeComposerPickers(); setError('');
      const body = resuming ? {feedback: message, images} : {providerId, message, images, reasoningEffort: $('#devReasoningSelect').value,
        acceptance: $('#devAcceptance').value, kind: $('#devTaskKind').value, skillId: $('#devSkillSelect').value,
        permissions: {edits: $('#devAllowEdits').checked, commands: $('#devAllowCommands').checked}};
      await api(`sessions/${encodeURIComponent(sessionId)}/${resuming ? 'resume' : 'run'}`, body);
      if (state.sessionId === sessionId) { $('#devPrompt').value = ''; clearImages(); await loadSession(sessionId); }
    } catch (error) {
      if (sessionId && state.sessionId === sessionId) await loadSession(sessionId).catch(() => {});
      setError(error.message);
    } finally { sending = false; renderProjects(); updateSendButton(); syncConfirmationDialog(); }
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
  document.addEventListener('click', async event => {
    const button = event.target.closest('button'); if (!button) return;
    if (button.hasAttribute('data-task-session-id')) {
      const session = state.sessions.find(s=>s.id===button.dataset.taskSessionId);
      if (session) { showView('developer'); await selectProject(session.projectId,session.id); }
      return;
    }
    if (button.hasAttribute('data-session-archive')) {
      button.disabled = true;
      const id = button.dataset.sessionArchive, action = button.dataset.archiveAction;
      const wasCurrent = id === state.sessionId, projectId = state.projectId;
      try {
        await api(`sessions/${encodeURIComponent(id)}/${action}`, {});
        if (wasCurrent && action === 'archive') {
          pollGeneration++; pollingId = ''; state.sessionId = ''; state.session = null; state.busy = false; rememberSelection();
        }
        await loadState();
        if (wasCurrent && action === 'archive') await selectProject(projectId);
        toast(action === 'archive' ? '会话已归档，记录已保留' : '会话已恢复');
        setError('');
      } catch(error) { setError(error.message); }
      finally { button.disabled = false; }
      return;
    }
    if (['devFilesTab', 'devTraceTab', 'devBrowserTab'].includes(button.id)) { selectRightTab({devFilesTab:'files', devTraceTab:'trace', devBrowserTab:'browser'}[button.id]); return; }
    if (button.hasAttribute('data-result-diff') || button.hasAttribute('data-result-trace') || button.hasAttribute('data-result-revert')) {
      filesCollapsed = false; applyPanelLayout();
      if (button.hasAttribute('data-result-trace')) { selectRightTab('trace'); $('#devExecution').scrollTop = 0; $('#devTraceTab').focus(); }
      else {
        selectRightTab('files');
        const reverting = button.hasAttribute('data-result-revert');
        const change = state.session.changes.find(c => c.taskId === (reverting ? button.dataset.resultRevert : button.dataset.resultDiff) && c.status === 'applied' && (!reverting || c.original !== null));
        const card = [...root.querySelectorAll('[data-change-card]')].find(el => el.dataset.changeCard === change?.id);
        if (card) { const group = card.closest('.dev-applied-changes'); if (group) group.open = true; const diff = card.querySelector('details'); diff.open = true; card.scrollIntoView({block:'nearest'}); (reverting ? card.querySelector('[data-change-action="revert"]') : diff.querySelector('summary')).focus(); }
      }
      return;
    }
    if (button.hasAttribute('data-result-file-path')) {
      await locateProjectFile(button.dataset.resultFilePath);
      return;
    }
    if (button.id === 'devToggleSidebar') {
      sidebarCollapsed = !sidebarCollapsed;
      localStorage.setItem('devSidebarCollapsed', sidebarCollapsed ? '1' : '0');
      applyPanelLayout(); return;
    }
    if (button.id === 'devToggleFiles' || button.id === 'devRestoreFiles') {
      filesCollapsed = !filesCollapsed;
      localStorage.setItem('devFilesCollapsed', filesCollapsed ? '1' : '0');
      applyPanelLayout();
      document.dispatchEvent(new Event('workspace:right-panel'));
      (filesCollapsed ? restoreFiles : filesToggle).focus(); return;
    }
    if(button.id==='devViewSkill') {
      const skillId=$('#devSkillSelect').value;
      if(skillId==='auto') {
        $('#devSkillContent').textContent=state.skills.map(skill=>`${skill.name} · ${skill.id}\n${skill.description}${skill.limitations?'\n'+skill.limitations:''}`).join('\n\n');
        $('#devSkillContent').classList.remove('hidden');$('#devSkillDetails').open=true;return;
      }
      try {const skill=await api('skills/'+encodeURIComponent(skillId));if($('#devSkillSelect').value!==skillId)return;$('#devSkillContent').textContent=skill.content;$('#devSkillContent').classList.remove('hidden');$('#devSkillDetails').open=true;}
      catch(error){setError(error.message);}return;
    }
    if(button.id==='devExportLogs') {
      try {const data=await api(`sessions/${state.sessionId}/logs`);const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='shujin-task-'+state.session.task.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){setError(error.message);}return;
    }
    if(button.id==='devResumeTask' && confirmationKey(state.session)) { deferredConfirmationKey = ''; syncConfirmationDialog(); return; }
    if(button.id==='devResumeTask'||button.hasAttribute('data-command-action')) {
      const resuming = button.id==='devResumeTask';
      if (resuming && (sending || creatingSession || addingImages)) return;
      button.disabled=true;
      if (resuming) { sending=true; renderProjects(); }
      try {
        const sessionId=state.sessionId;
        const path=resuming?'resume':`commands/${button.dataset.commandId}`;
        const body=resuming?{feedback:$('#devPrompt').value,images:draftImages.map(({name,dataUrl})=>({name,dataUrl}))}:{action:button.dataset.commandAction};
        await api(`sessions/${sessionId}/${path}`,body);
        if(state.sessionId!==sessionId)return;
        if(resuming){$('#devPrompt').value='';clearImages();updateSendButton();}
        await loadSession(sessionId);setError('');
      }catch(error){setError(error.message);button.disabled=false;}
      finally{if(resuming){sending=false;renderProjects();updateSendButton();syncConfirmationDialog();}}return;
    }
    if (button.id === 'devImportButton' || button.id === 'devEmptyImport') { await importProject(); return; }
    if (button.id === 'devRefreshFiles') { await loadFiles(); return; }
    if (button.id === 'devSettingsButton' || button.id === 'devSettingsQuick' || button.id === 'devManageModel' || button.id === 'devBottomSettings') { openSettings(); return; }
    if (button.id === 'devCloseSettings') { closeSettings(); return; }
    if (button.id === 'devAddProvider') { openProviderForm(); return; }
    if (button.id === 'devProviderCancel') { resetProviderForm(); return; }
    if (button.hasAttribute('data-new-session-project')) { await createSession(false, button.dataset.newSessionProject); return; }
    if (button.hasAttribute('data-dev-prompt')) { if (!state.projectId) { setError('请先点击「导入本地项目」选择项目。'); return; } $('#devPrompt').value = button.dataset.devPrompt; updateSendButton(); $('#devPrompt').focus(); return; }
    if (button.hasAttribute('data-directory-path')) {
      const path = button.dataset.directoryPath;
      if (expandedDirectories.has(path)) expandedDirectories.delete(path);
      else { expandedDirectories.add(path); if (!directoryPages.has(path)) { await loadDirectory(path); return; } }
      renderFileTree(); return;
    }
    if (button.hasAttribute('data-directory-more')) { await loadDirectory(button.dataset.directoryMore, button.dataset.directoryRetry !== 'true'); return; }
    if (button.hasAttribute('data-file-more')) { await openFile(button.dataset.fileMore, true, button.dataset.filePrevious === 'true'); return; }
    if (button.hasAttribute('data-file-path')) { await openFile(button.dataset.filePath); return; }
    if (button.hasAttribute('data-project-id')) {
      if (document.body.dataset.view !== 'developer') showView('developer');
      const id = button.dataset.projectId;
      if (id === state.projectId) {
        if (collapsedProjects.has(id)) collapsedProjects.delete(id); else collapsedProjects.add(id);
      } else collapsedProjects.delete(id);
      localStorage.setItem('devCollapsedProjects', JSON.stringify([...collapsedProjects]));
      renderProjectGroups();
      if (id !== state.projectId) await selectProject(id);
      return;
    }
    if (button.hasAttribute('data-session-id')) {
      if (document.body.dataset.view !== 'developer') showView('developer');
      const session = state.sessions.find(s => s.id === button.dataset.sessionId);
      if (!session) return;
      if (session.projectId !== state.projectId) { await selectProject(session.projectId, session.id); return; }
      clearImages(); pollGeneration++; pollingId = ''; state.sessionId = session.id; state.busy = false; rememberSelection(); await loadSession(state.sessionId); setError(''); return;
    }
    if (button.hasAttribute('data-change-action')) { await performChange(button.dataset.changeId, button.dataset.changeAction); return; }
    if (button.hasAttribute('data-edit-provider')) { const p = state.providers.find(item => item.id === button.dataset.editProvider); if (p) openProviderForm(p); return; }
    if (button.hasAttribute('data-test-provider')) { button.disabled = true; button.textContent = '测试中…'; try { const result = await api('providers/' + encodeURIComponent(button.dataset.testProvider) + '/test', {}); toast(result.message); } catch (error) { setError(error.message); } finally { button.disabled = false; button.textContent = '测试连接'; } return; }
    if (button.hasAttribute('data-delete-provider')) { if (!confirm('删除此模型配置？已有会话记录仍会保留。')) return; try { await api('providers/' + encodeURIComponent(button.dataset.deleteProvider) + '/remove', {}); await loadState(); toast('已删除模型配置'); } catch (error) { setError(error.message); } return; }
    if (button.id === 'devStopButton') { await api(`sessions/${encodeURIComponent(state.sessionId)}/stop`, {}); return; }
  });
  root.addEventListener('change', async event => {
    if(event.target.name==='devAccessMode'){
      const mode=event.target.value;
      $('#devTaskKind').value=mode==='readonly'?'inspect':'auto';
      $('#devAllowEdits').checked=mode==='automatic';
      $('#devAllowCommands').checked=mode==='automatic';
      renderAccessControl();saveProjectAccess();$('#devAccessPicker').open=false;
    }
    if(['devTaskKind','devAllowEdits','devAllowCommands'].includes(event.target.id)){renderAccessControl();saveProjectAccess();}
    if(event.target.id==='devSkillSelect'){$('#devSkillContent').classList.add('hidden');renderSkills();}
    if (event.target.id === 'devModelSelect') { localStorage.setItem('devSelectedProvider', event.target.value); renderModelLabel(); updateSendButton(); renderConversation(); $('#devModelPicker').open=false; }
    if (event.target.id === 'devReasoningSelect') void saveReasoningEffort(event.target.value);
  });
  $('#devComposer').addEventListener('submit', event => { event.preventDefault(); void sendMessage($('#devPrompt').value); });
  $('#devConfirmationAnswer').addEventListener('input', event => {
    confirmationDrafts.set(confirmationDialog.dataset.key, event.target.value);
    $('#devConfirmationError').classList.add('hidden');
  });
  $('#devConfirmationLater').addEventListener('click', () => { deferredConfirmationKey = confirmationDialog.dataset.key; confirmationDialog.close(); });
  confirmationDialog.addEventListener('close', () => {
    if (confirmationDialog.dataset.key === confirmationKey(state.session)) deferredConfirmationKey = confirmationDialog.dataset.key;
  });
  $('#devConfirmationForm').addEventListener('submit', async event => {
    event.preventDefault();
    const answer = $('#devConfirmationAnswer').value.trim();
    const key = confirmationDialog.dataset.key, sessionId = state.sessionId;
    if (!answer) {
      $('#devConfirmationError').textContent = '请填写回答，或选择“稍后回答”。';
      $('#devConfirmationError').classList.remove('hidden');
      $('#devConfirmationAnswer').focus();
      return;
    }
    if (!key || key !== confirmationKey(state.session) || sending) return;
    const submit = $('#devConfirmationSubmit');
    sending = true; submit.disabled = true; submit.textContent = '提交中…'; renderProjects();
    try {
      await api('sessions/' + encodeURIComponent(sessionId) + '/resume', {feedback: answer});
      confirmationDrafts.delete(key);
      if (state.sessionId === sessionId) {
        confirmationDialog.close();
        await loadSession(sessionId);
        setError('');
      }
    } catch (error) {
      $('#devConfirmationError').textContent = error.message;
      $('#devConfirmationError').classList.remove('hidden');
    } finally {
      sending = false; submit.disabled = false; submit.textContent = '提交并继续'; renderProjects(); updateSendButton(); syncConfirmationDialog();
    }
  });
  $('#devPrompt').addEventListener('input', updateSendButton);
  let promptWidth = 0;
  const promptObserver = new ResizeObserver(([entry]) => {
    if (entry.contentRect.width === promptWidth) return;
    promptWidth = entry.contentRect.width;
    resizePrompt();
  });
  promptObserver.observe($('#devPrompt'));
  window.addEventListener('resize', resizePrompt);
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
  document.addEventListener('workspace:view', event => { placeSidebarToggle(event.detail); if (event.detail === 'developer') void loadState(); else if (confirmationDialog.open) confirmationDialog.close(); });
  let refreshingSessions = false;
  setInterval(async () => {
    if (refreshingSessions || document.hidden || !state.sessions.some(s => s.status === 'running')) return;
    refreshingSessions = true;
    try { const next = await api('state'); state.sessions = next.sessions; renderProjectGroups(); }
    catch { /* A temporary local API failure leaves the last known state intact. */ }
    finally { refreshingSessions = false; }
  }, 2000);
  void loadState();
})();
