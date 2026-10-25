const ASSETS = {
  skincare:'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=900&q=85',
  coffee:'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
  interior:'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85',
  work:'https://images.unsplash.com/photo-1497215842964-222b430dc094?auto=format&fit=crop&w=900&q=85',
  food:'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=85',
  design:'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=85'
};

const posts = [
  {id:'p1',category:'美妆护肤',title:'把早八通勤的五分钟，还给真正重要的事',description:'极简护肤流程｜换季也能维持稳定的轻盈感',creator:'林间慢调',initials:'林',date:'2 小时前',views:18200,likes:1240,saves:836,heat:96,engagement:11.4,growth:'+32%',asset:'skincare',label:'轻盈护肤',topic:'轻量护肤',keywords:['精简步骤','油敏肌','晨间流程'],insight:'这篇内容用清晰的步骤结构拆解早间护肤，收藏数达到点赞数的约三分之二。用户重视可复用的流程，愿意保存后续参考。',opportunity:'“几分钟可完成”的明确场景，让护肤内容更容易进入通勤与高效生活的讨论。'},
  {id:'p2',category:'生活方式',title:'一个人住以后，我的周日早晨变成这样了',description:'没有打卡清单的周末｜给生活留一些空白',creator:'June 的日常',initials:'J',date:'4 小时前',views:26400,likes:2150,saves:1960,heat:92,engagement:15.6,growth:'+26%',asset:'coffee',label:'慢一点生活',topic:'周末仪式感',keywords:['独居生活','松弛感','晨间仪式'],insight:'这类独居日常的互动来自具体的小习惯与真实空间。收藏和转发意愿高，说明用户倾向把内容当作生活灵感。',opportunity:'围绕“低成本但舒服的周末”持续做系列，更容易形成稳定的内容记忆。'},
  {id:'p3',category:'家居设计',title:'小户型也能拥有自己的阅读角落',description:'12㎡客厅改造｜靠一盏灯和一把椅子完成',creator:'白墙计划',initials:'白',date:'昨天',views:41700,likes:3870,saves:3210,heat:89,engagement:17.0,growth:'+41%',asset:'interior',label:'小空间设计',topic:'空间效率',keywords:['小户型','阅读角','灯光布置'],insight:'明确面积与改造结果使家居笔记具有很强的参考价值。读者通过收藏表达“稍后照做”，评论中常会追问尺寸和购买方式。',opportunity:'用平面图、预算与尺寸补充美学图集，能让种草内容更接近实际决策。'},
  {id:'p4',category:'职场效率',title:'我终于搭出了不会让我分心的工作桌面',description:'桌面整理前后对比｜留白真的会提升专注感',creator:'阿禾在工作',initials:'禾',date:'昨天',views:15600,likes:980,saves:1120,heat:81,engagement:13.5,growth:'+18%',asset:'work',label:'专注工作台',topic:'桌面整理',keywords:['桌面布置','专注力','工作习惯'],insight:'“整理前后对比”提供即时反馈，容易吸引高效生活和职场人群。用户更想了解物品如何取舍以及桌面的日常维护。',opportunity:'展示同一桌面的不同工作状态，让空间整理从审美分享延伸到真实工作效率。'},
  {id:'p5',category:'生活方式',title:'一周备餐：下班后也能吃到舒服的一餐',description:'两小时备好五份饭｜给忙碌工作日的留白',creator:'小满的餐桌',initials:'满',date:'昨天',views:22900,likes:1740,saves:2480,heat:79,engagement:18.4,growth:'+22%',asset:'food',label:'轻松备餐',topic:'效率备餐',keywords:['一周备餐','工作日','饮食管理'],insight:'高收藏互动表明备餐攻略具有明确的实用价值。切分步骤和保存方式是内容里最值得补充的决策信息。',opportunity:'把食谱、准备时间与冷藏方案放进同一条笔记，让操作成本一眼就能判断。'},
  {id:'p6',category:'家居设计',title:'不换家具，让出租屋一点点变成家的样子',description:'租房软装清单｜先从光线和织物开始',creator:'住在小房子',initials:'住',date:'2 天前',views:19800,likes:1570,saves:1890,heat:76,engagement:17.5,growth:'+16%',asset:'design',label:'租房改造',topic:'租房软装',keywords:['出租屋','软装清单','预算控制'],insight:'租房改造内容同时满足空间表达与预算决策。低成本、可移动的物品是评论区反复询问的重点。',opportunity:'提供“带得走的软装清单”，能连接灵感收藏和后续购买决策。'}
];

const defaults = [
  {id:'t1',keyword:'极简护肤',category:'美妆护肤',frequency:'每天',active:true},
  {id:'t2',keyword:'小户型收纳',category:'家居设计',frequency:'每天',active:true},
  {id:'t3',keyword:'高效生活',category:'生活方式',frequency:'每周',active:true}
];
const readJson = (key,fallback) => {try {const value=localStorage.getItem(key);return value?JSON.parse(value):fallback;}catch{return fallback;}};
const saveJson = (key,value) => {try{localStorage.setItem(key,JSON.stringify(value));}catch{}};
const $ = (selector,parent=document) => parent.querySelector(selector);
const $$ = (selector,parent=document) => Array.from(parent.querySelectorAll(selector));
const escapeHtml = value => String(value).replace(/[&<>"']/g,char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const icon = name => '<svg class="icon" aria-hidden="true"><use href="#i-'+name+'"/></svg>';
const fmt = n => n>=10000?(n/10000).toFixed(1).replace('.0','')+'万':n.toLocaleString('zh-CN');
const findPost = id => posts.find(post => post.id===id);
let tasks=readJson('guanshu_tasks',defaults);
let saved=readJson('guanshu_saved',[]);
let selectedPostId='p1';
let activeView='developer';
let activeTab='focus';
let activeCategory='全部';
let searchQuery='';
let sortMode='heat';
let toastTimer;

function showToast(message){
  const node=$('#toast');node.textContent=message;node.classList.add('visible');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.classList.remove('visible'),2600);
}
function setDate(){
  const date=new Date();
  $('#todayText').textContent=new Intl.DateTimeFormat('zh-CN',{month:'long',day:'numeric',weekday:'long',timeZone:'Asia/Shanghai'}).format(date);
  $('#briefDate').textContent=new Intl.DateTimeFormat('zh-CN',{month:'2-digit',day:'2-digit',timeZone:'Asia/Shanghai'}).format(date);
}
function visiblePosts(){
  let list=posts.filter(post=>(activeCategory==='全部'||post.category===activeCategory)&&(!searchQuery||(post.title+' '+post.creator+' '+post.category+' '+post.description+' '+post.topic).toLowerCase().includes(searchQuery.toLowerCase())));
  if(activeTab==='hot')list=list.filter(post=>post.heat>=80);
  if(sortMode==='recent'||activeTab==='latest')list.sort((a,b)=>a.id.localeCompare(b.id));
  else list.sort((a,b)=>b[sortMode]-a[sortMode]);
  return list;
}
function postCard(post){
  const isSaved=saved.includes(post.id), number=posts.indexOf(post)+1;
  return [
    '<article class="post-card '+(selectedPostId===post.id?'selected':'')+'" data-post-card="'+post.id+'">',
      '<div class="post-cover" data-select-post="'+post.id+'" role="button" tabindex="0" aria-label="查看'+escapeHtml(post.title)+'的分析">',
        '<img src="'+ASSETS[post.asset]+'" alt="'+escapeHtml(post.label)+'主题图片" loading="lazy"/>',
        '<span class="cover-tag">'+escapeHtml(post.category)+'</span>',
        '<div class="cover-caption"><small>INSIGHT NOTE · '+String(number).padStart(2,'0')+'</small><strong>'+escapeHtml(post.label)+'</strong></div>',
        '<span class="cover-index">'+String(number).padStart(2,'0')+' / '+String(posts.length).padStart(2,'0')+'</span>',
      '</div>',
      '<button class="cover-save '+(isSaved?'saved':'')+'" data-save-post="'+post.id+'" aria-label="'+(isSaved?'取消收藏':'收藏')+'">'+icon('bookmark')+'</button>',
      '<div class="post-body"><div class="post-type-row"><span class="category-label">'+escapeHtml(post.topic)+'</span><span class="growth-badge">'+icon('up')+' '+post.growth+'</span></div>',
        '<h3 class="post-title" data-select-post="'+post.id+'">'+escapeHtml(post.title)+'</h3>',
        '<p class="post-description">'+escapeHtml(post.description)+'</p>',
        '<div class="post-author"><span class="author-info"><span class="author-avatar avatar-'+number+'">'+escapeHtml(post.initials)+'</span>'+escapeHtml(post.creator)+'</span><span class="post-time">'+escapeHtml(post.date)+'</span></div>',
        '<div class="post-stats"><span class="post-stat">'+icon('eye')+' '+fmt(post.views)+'</span><span class="post-stat">'+icon('heart')+' '+fmt(post.likes)+'</span><span class="post-stat">'+icon('bookmark')+' '+fmt(post.saves)+'</span><span class="post-stat">热度 '+post.heat+'</span></div>',
      '</div>',
    '</article>'
  ].join('');
}
function renderPosts(){
  const list=visiblePosts();
  $('#postGrid').innerHTML=list.length?list.map(postCard).join(''):'<div class="empty-state">'+icon('search')+'<h3>没有找到匹配的内容</h3><p>试试调整筛选条件，或搜索「护肤」「空间」等关键词。</p></div>';
  $('#resultCount').textContent=String(list.length).padStart(2,'0');
  $('#feedFooterCount').textContent='显示 '+list.length+' 篇内容';
  renderAnalysis();
}
function renderAnalysis(){
  const post=findPost(selectedPostId)||posts[0];
  $('#selectedAnalysis').innerHTML=[
    '<div class="analysis-note"><img class="analysis-thumb" src="'+ASSETS[post.asset]+'" alt=""/><div><span class="analysis-tag">正在分析</span><div class="analysis-note-title">'+escapeHtml(post.title)+'</div></div></div>',
    '<div class="analysis-section-title"><span class="small-blue-dot"></span>核心观察</div><p class="analysis-copy">'+escapeHtml(post.insight)+'</p>',
    '<div class="analysis-section-title"><span class="small-blue-dot"></span>关联关键词</div><div class="keyword-row">'+post.keywords.map(word=>'<span>'+escapeHtml(word)+'</span>').join('')+'</div>',
    '<div class="opportunity-card"><strong>'+icon('spark')+' 内容机会</strong><p>'+escapeHtml(post.opportunity)+'</p></div>'
  ].join('');
}
function renderTasks(){
  $('#taskList').innerHTML=tasks.length?tasks.map(task=>[
    '<div class="task-row '+(task.active?'':'paused')+'"><div class="task-icon">'+icon('target')+'</div>',
    '<div class="task-details"><strong>'+escapeHtml(task.keyword)+'</strong><p>'+escapeHtml(task.category)+' · '+escapeHtml(task.frequency)+'更新 · 创建于本地</p></div>',
    '<span class="task-status">'+(task.active?'监测中':'已暂停')+'</span>',
    '<button class="task-toggle" data-toggle-task="'+task.id+'">'+(task.active?'暂停':'启用')+'</button></div>'
  ].join('')).join(''):'<div class="empty-state">'+icon('target')+'<h3>还没有监测任务</h3><p>新建一个主题，开始整理你关心的内容方向。</p><button class="primary-button" data-open-task>'+icon('plus')+'新建任务</button></div>';
  const taskCounter=$('#taskNavCount');if(taskCounter)taskCounter.textContent=tasks.length;
  $('#activeTaskMetric').innerHTML=tasks.filter(task=>task.active).length+' <span class="metric-unit">个任务</span>';
  $('#taskCountBadge').textContent=tasks.length+' 个任务';
}
function renderSaved(){
  const list=saved.map(findPost).filter(Boolean);
  const savedCounter=$('#savedNavCount');if(savedCounter)savedCounter.textContent=list.length;
  $('#savedCountBadge').textContent=list.length+' 篇内容';
  $('#savedGrid').innerHTML=list.length?list.map(postCard).join(''):'<div class="empty-state">'+icon('bookmark')+'<h3>收藏夹还是空的</h3><p>在内容卡片右上角点选书签，随手收集值得研究的灵感。</p><button class="secondary-button" data-go-radar>浏览内容发现</button></div>';
}
function renderReport(){
  const selected=findPost(selectedPostId)||posts[0];
  const top=[...posts].sort((a,b)=>b.heat-a.heat).slice(0,3);
  $('#reportContent').innerHTML=[
    '<article class="report-paper"><span class="report-kicker">INSIGHT BRIEF · DEMO DATA</span>',
    '<h2>生活方式内容观察<br/>趋势机会与选题方向</h2>',
    '<p class="report-meta">筱竹书瑾 · '+escapeHtml($('#todayText').textContent)+' · 基于 '+posts.length+' 篇模拟样例</p>',
    '<h3><span>01</span> 趋势观察</h3><p>样例内容中，用户对“省时间、可复用、低成本”的日常方案反应积极。轻量护肤、空间效率与松弛感生活共同指向一个内容机会：在有限时间和空间里，获得可感知的品质提升。</p>',
    '<h3><span>02</span> 值得关注的内容</h3><ul>'+top.map(post=>'<li>'+escapeHtml(post.title)+'（互动率样例 '+post.engagement+'%）</li>').join('')+'</ul>',
    '<h3><span>03</span> 下一步选题建议</h3><ul><li>以明确场景切入：早晨通勤、下班之后、小户型改造。</li><li>用步骤、预算或时间成本降低行动门槛。</li><li>建立系列化观察，将“灵感”与“真实使用方法”组合呈现。</li></ul>',
    '<div class="report-summary"><strong>当前选中内容 · '+escapeHtml(selected.topic)+'</strong><p>'+escapeHtml(selected.opportunity)+'</p></div>',
    '<p class="report-source">数据说明：此页面的笔记、热度和互动指标均为虚构演示数据，不能代表小红书平台上的真实内容、趋势或用户反馈。连接合规数据源后，才可生成真实业务简报。</p></article>'
  ].join('');
}
function showView(view){
  if(!['developer','radar','account','recommendations','messages','tasks','saved','report'].includes(view))view='developer';
  activeView=view;
  document.body.dataset.view=view;
  $('.environment-tag').innerHTML='<span></span> '+(view==='developer'?'本地开发':'演示环境');
  $$('.workspace-view').forEach(section=>section.classList.toggle('hidden',section.id!==view+'View'));
  $$('.nav-item').forEach(button=>{button.classList.toggle('active',button.dataset.view===view);button.setAttribute('aria-label',button.querySelector('span')?.textContent||'导航');});
  $$('.activity-button').forEach(button=>{const selected=button.dataset.view===(view==='developer'?'developer':'account');button.classList.toggle('active',selected);button.setAttribute('aria-pressed',String(selected));});
  $('#breadcrumbCurrent').textContent={developer:'开发 Agent',radar:'内容雷达',account:'小红书账号',recommendations:'我的推荐',messages:'消息中心',tasks:'监测任务',saved:'收藏夹',report:'策略简报'}[view];
  if(view==='tasks')renderTasks();if(view==='saved')renderSaved();if(view==='report')renderReport();
  window.scrollTo({top:0,behavior:'smooth'});
  if(location.hash.slice(1)!==view)history.replaceState(null,'','#'+view);
  document.dispatchEvent(new CustomEvent('workspace:view',{detail:view}));
}
function toggleSave(id){
  saved=saved.includes(id)?saved.filter(item=>item!==id):[...saved,id];
  saveJson('guanshu_saved',saved);renderPosts();renderSaved();
  showToast(saved.includes(id)?'已加入收藏夹':'已从收藏夹移除');
}
function selectPost(id){
  selectedPostId=id;
  $$('.post-card').forEach(card=>card.classList.toggle('selected',card.dataset.postCard===id));
  renderAnalysis();if(activeView==='report')renderReport();
}
function openTaskModal(){$('#taskModal').classList.remove('hidden');document.body.style.overflow='hidden';setTimeout(()=>$('#taskKeyword').focus(),40);}
function closeTaskModal(){$('#taskModal').classList.add('hidden');document.body.style.overflow='';$('#taskForm').reset();}
function addMessage(value,type){
  const node=document.createElement('div');node.className='chat-message '+type;node.textContent=value;$('#chatMessages').append(node);$('#chatMessages').scrollTop=$('#chatMessages').scrollHeight;
}
function answerQuestion(question){
  const q=question.toLowerCase();let response;
  if(/趋势|总结|热点/.test(q))response='从当前样例看，「效率与轻盈感」正在多个主题中出现：轻量护肤强调更短流程，家居内容强调小空间的有效使用。建议持续跟踪“时间成本、空间效率、日常可复用”这三个切口。';
  else if(/选题|灵感/.test(q))response='可以试试这三个选题方向：\n1. 五分钟完成的通勤晨间流程\n2. 不换大件，把小空间重新用起来\n3. 下班后仍能坚持的低成本生活习惯\n每个方向都可以补上清晰的时间、预算或步骤。';
  else if(/受众|情绪|评论/.test(q))response='样例互动体现出三类需求：想直接照做的实用感、对低成本方案的安全感，以及对“生活可以更松弛”的情绪认同。这只是当前样例笔记的观察，需要真实评论数据进一步验证。';
  else response='结合「'+(findPost(selectedPostId)?.topic||'当前关注内容')+'」这个主题，建议先明确读者遇到的具体情境，再给出可以当天尝试的步骤。当前工作台使用演示笔记，实际结论需以接入的数据为准。';
  setTimeout(()=>addMessage(response,'assistant'),360);
}
function downloadReport(){
  const top=[...posts].sort((a,b)=>b.heat-a.heat).slice(0,3);
  const report='# 生活方式内容观察：趋势机会与选题方向\n\n筱竹书瑾 · '+$('#todayText').textContent+'\n数据说明：以下均为虚构演示数据。\n\n## 趋势观察\n\n样例内容中，用户对“省时间、可复用、低成本”的日常方案反应积极。\n\n## 值得关注的内容\n\n'+top.map(post=>'- '+post.title+'（互动率样例 '+post.engagement+'%）').join('\n')+'\n\n## 下一步选题建议\n\n- 以明确场景切入：早晨通勤、下班之后、小户型改造。\n- 用步骤、预算或时间成本降低行动门槛。\n- 建立系列化观察，将灵感与真实使用方法组合呈现。\n\n## 数据说明\n\n所有笔记、热度和互动指标都是虚构演示数据，不能代表小红书平台上的真实内容或用户反馈。\n';
  const link=document.createElement('a');const url=URL.createObjectURL(new Blob([report],{type:'text/markdown;charset=utf-8'}));link.href=url;link.download='筱竹书瑾-内容观察简报.md';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);showToast('简报已导出为 Markdown');
}

document.addEventListener('click',event=>{
  const nav=event.target.closest('[data-view]');if(nav&&nav!==document.body){showView(nav.dataset.view);return;}
  const saveButton=event.target.closest('[data-save-post]');if(saveButton){event.stopPropagation();toggleSave(saveButton.dataset.savePost);return;}
  const postTarget=event.target.closest('[data-select-post]');if(postTarget){selectPost(postTarget.dataset.selectPost);return;}
  const category=event.target.closest('[data-category]');if(category){activeCategory=category.dataset.category;$$('.filter-chip').forEach(chip=>chip.classList.toggle('active',chip===category));renderPosts();return;}
  const tab=event.target.closest('[data-tab]');if(tab){activeTab=tab.dataset.tab;$$('.tab').forEach(button=>button.classList.toggle('active',button===tab));renderPosts();return;}
  const prompt=event.target.closest('[data-prompt]');if(prompt){addMessage(prompt.dataset.prompt,'user');answerQuestion(prompt.dataset.prompt);return;}
  const toggle=event.target.closest('[data-toggle-task]');if(toggle){tasks=tasks.map(task=>task.id===toggle.dataset.toggleTask?{...task,active:!task.active}:task);saveJson('guanshu_tasks',tasks);renderTasks();showToast('监测任务状态已更新');return;}
  if(event.target.closest('[data-open-task]')){openTaskModal();return;}
  if(event.target.closest('[data-go-radar]')){showView('radar');return;}
  if(event.target.closest('#closeTaskModal')||event.target.closest('#cancelTaskModal')||event.target.id==='taskModal')closeTaskModal();
});
document.addEventListener('keydown',event=>{
  const target=event.target.closest('[data-save-post]')?null:event.target.closest('[data-select-post]');
  if(target&&(event.key==='Enter'||event.key===' ')){event.preventDefault();selectPost(target.dataset.selectPost);}
  if(event.key==='Escape'&&!$('#taskModal').classList.contains('hidden'))closeTaskModal();
});
$('#postSearch').addEventListener('input',event=>{searchQuery=event.target.value.trim();renderPosts();});
$('#sortSelect').addEventListener('change',event=>{sortMode=event.target.value;renderPosts();});
$('#taskForm').addEventListener('submit',event=>{
  event.preventDefault();const data=new FormData(event.currentTarget);const keyword=String(data.get('keyword')||'').trim();if(!keyword)return;
  tasks.unshift({id:'t'+Date.now(),keyword,category:String(data.get('category')),frequency:String(data.get('frequency')),active:true});
  saveJson('guanshu_tasks',tasks);renderTasks();closeTaskModal();showToast('已创建「'+keyword+'」监测任务');
});
$('#chatForm').addEventListener('submit',event=>{event.preventDefault();const input=$('#chatInput'),question=input.value.trim();if(!question)return;addMessage(question,'user');input.value='';answerQuestion(question);});
$('#refreshButton').addEventListener('click',event=>{const image=event.currentTarget.querySelector('.icon');image.classList.add('spinning');setTimeout(()=>image.classList.remove('spinning'),650);renderPosts();showToast('已重新载入演示数据');});
$('#briefButton').addEventListener('click',()=>showView('report'));
$('#savedReportButton').addEventListener('click',()=>showView('report'));
$('#downloadReportButton').addEventListener('click',downloadReport);
$('#accountQuickButton').addEventListener('click',()=>showView('account'));
$('#notificationButton').addEventListener('click',()=>showView('messages'));
window.addEventListener('hashchange',()=>showView(location.hash.slice(1)));

setDate();renderPosts();renderTasks();renderSaved();
showView(location.hash.slice(1)||'developer');
