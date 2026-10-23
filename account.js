(() => {
  let session = { status: 'disconnected', profileSaved: false, name: '' };
  let pending = false, polling = false, messageKind = 'notifications', notes = [], messageData = null;
  let loadedRecommendations = false, loadedMessages = false, serviceError = '';
  const connected = () => session.status === 'connected';
  const empty = (symbol, title, description, action = '') => '<div class="personal-empty"><span class="personal-empty-icon">'+icon(symbol)+'</span><h2>'+escapeHtml(title)+'</h2><p>'+escapeHtml(description)+'</p>'+action+'</div>';
  const connectAction = '<button class="primary-button" data-connect-xhs>'+icon('account')+'扫码登录小红书</button>';
  const time = value => new Date(value).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  const safeUrl = (value, image = false) => {
    try { const u = new URL(value); return u.protocol === 'https:' && (image ? /\.(xhscdn\.com|xiaohongshu\.com)$/.test(u.hostname) : u.hostname === 'www.xiaohongshu.com') ? escapeHtml(u.href) : ''; } catch { return ''; }
  };

  async function request(path, post = false) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60000);
    try {
      const response = await fetch('/api/xhs/'+path, { method: post ? 'POST' : 'GET', cache: 'no-store', signal: controller.signal });
      const data = await response.json();
      if (!response.ok) { const error = new Error(data.error || '操作未完成，请重试。'); error.status = response.status; throw error; }
      return data;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('连接超时，请在当前页面重试。');
      if (error instanceof TypeError || error instanceof SyntaxError) throw new Error('无法连接本地服务，请启动或重启工作台后重试。');
      throw error;
    } finally { clearTimeout(timeout); }
  }

  function notice(id, text = '') {
    $(id).textContent = text;
    $(id).classList.toggle('hidden', !text);
  }

  function renderSession() {
    if (!connected()) {
      $('#recommendationsUpdated').textContent = '登录后读取官方页面';
      $('#messagesUpdated').textContent = '登录后读取官方页面';
    }
    const labels = { disconnected: session.profileSaved ? '会话已保存 · 待连接' : '未连接账号', awaiting_login: '等待扫码登录', connected: '账号已连接', verification_required: '官网暂时限制登录' };
    $$('[data-account-status]').forEach(node => {
      node.innerHTML = '<span></span>'+escapeHtml(labels[session.status] || '检查连接中');
      node.classList.toggle('is-connected', connected());
      node.classList.toggle('is-waiting', ['awaiting_login', 'verification_required'].includes(session.status));
    });
    const descriptions = {
      disconnected: ['准备连接你的账号', session.profileSaved ? '本机已保存登录会话，点击连接可恢复；需要重新登录时，二维码会在本页展示。' : '点击扫码登录，在本页使用手机小红书扫描官方二维码。'],
      awaiting_login: ['在此页面扫码登录', '使用手机小红书扫描右侧二维码，并在手机确认登录。账号状态会自动更新。'],
      connected: [session.name || '我的小红书账号', '账号已连接。现在可以直接进入「我的推荐」和「消息中心」。'],
      verification_required: ['小红书暂时限制登录', session.login?.message || '官网要求额外验证，暂时无法提供二维码，请稍后在本页重试。']
    };
    const description = descriptions[session.status] || descriptions.disconnected;
    $('#connectionTitle').textContent = description[0];
    $('#connectionDescription').textContent = description[1];
    notice('#connectionError', serviceError || session.error || '');
    $('#clearConnectionButton').classList.toggle('hidden', !session.profileSaved && session.status === 'disconnected');
    $$('[data-connect-xhs]').forEach(button => {
      const label = pending ? '正在连接…' : session.busy ? '正在加载会话…' : connected() ? '查看我的推荐' : session.status === 'awaiting_login' || session.status === 'verification_required' ? '刷新二维码' : '扫码登录小红书';
      const span = button.querySelector('span');
      if (span) span.textContent = label; else button.innerHTML = icon('account')+label;
      button.disabled = pending || session.busy;
    });
    $$('#checkConnectionButton, #clearConnectionButton, #syncRecommendations, #syncMessages, #loadMoreRecommendations, #openOfficialMessages, #refreshQrButton').forEach(button => button.disabled = pending || session.busy);
    $('.profile strong').textContent = connected() ? session.name || '我的账号' : '本地工作台';
    $('.profile small').textContent = connected() ? '小红书已连接' : '未连接小红书';
    if (!connected()) $('.profile-avatar').textContent = '筱';
    else $('.profile-avatar').textContent = (session.name || '我').slice(0,1);
    const personal = ['account','recommendations','messages'].includes(activeView);
    $('.environment-tag').innerHTML = '<span></span> '+(activeView === 'developer' ? '本地开发' : personal ? '本地工作台' : '演示环境');
    $('.source-row small').textContent = personal ? connected() ? '个人账号已连接' : '待连接账号' : '演示数据';
    $('.source-indicator').style.background = personal && connected() ? '#70ac8b' : '';
    renderLogin();
  }

  function renderLogin() {
    const login = session.login || { status: session.status === 'awaiting_login' ? 'loading' : 'idle' };
    const state = connected() ? 'connected' : pending ? 'loading' : login.status;
    const titles = { idle:'扫码登录小红书', loading:'正在加载官方二维码', ready:'使用小红书 App 扫码', scanned:'已扫码，等待手机确认', expired:'二维码已过期', error:'暂未获取到二维码', restricted:'官网暂时限制登录', connected:'账号连接成功' };
    const messages = { idle:'点击下方按钮，二维码将在这里显示', loading:'官网加载可能需要一些时间，请保持页面打开', ready:'打开小红书 · 左上角扫一扫', scanned:'请在手机小红书上确认登录', expired:'点击刷新，获取新的官方登录二维码', error:'请稍后点击刷新重试', restricted:session.login?.message || '请稍后重试', connected:'可以开始浏览你的推荐和消息了' };
    $('#qrLoginTitle').textContent = titles[state] || titles.idle;
    $('#qrLoginHint').textContent = messages[state] || messages.idle;
    if(state === 'error' && login.message) $('#qrLoginHint').textContent = login.message;
    $('#qrLoginCard').dataset.state = state;
    const img = $('#loginQrImage');
    const validImage = state === 'ready' && /^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(login.image || '');
    img.classList.toggle('hidden',!validImage);
    if(validImage) { if(img.getAttribute('src') !== login.image) img.src = login.image; }
    else img.removeAttribute('src');
    $('#qrStatusVisual').classList.toggle('hidden',validImage);
    $('#qrStatusVisual').innerHTML = state === 'loading' ? '<span class="qr-loader"></span>' : icon(state === 'connected' || state === 'scanned' ? 'check' : state === 'restricted' || state === 'error' ? 'clock' : 'account');
    $('#refreshQrButton').classList.toggle('hidden',state === 'idle' || state === 'connected' || state === 'loading');
    $('#qrStartButton').classList.toggle('hidden',state !== 'idle');
    $('#qrSuccessButton').classList.toggle('hidden',state !== 'connected');
  }

  function renderRecommendations() {
    $('#loadMoreContainer').classList.toggle('hidden', !connected() || !notes.length);
    if (!connected()) {
      $('#recommendationsContent').innerHTML = empty('spark','让推荐回到你的账号','连接并登录小红书后，在这里查看官方页面中的个性化推荐。',connectAction);
      return;
    }
    if (!notes.length) {
      $('#recommendationsContent').innerHTML = empty('grid',loadedRecommendations ? '暂未读到推荐内容' : '准备读取你的推荐',loadedRecommendations ? '请确认官方页面已显示推荐笔记，然后点击刷新推荐。' : '点击刷新推荐，读取当前账号的官方推荐页面。');
      return;
    }
    $('#recommendationsContent').innerHTML = '<div class="personal-note-grid">'+notes.map(note => {
      const url = safeUrl(note.url), cover = safeUrl(note.cover, true);
      return '<article class="personal-note"><a class="personal-note-cover" href="'+url+'" target="_blank" rel="noopener noreferrer">'+(cover ? '<img src="'+cover+'" alt="'+escapeHtml(note.title)+'" loading="lazy" referrerpolicy="no-referrer" />' : '<span class="cover-placeholder">'+icon('file')+'查看原文图片</span>')+'<span class="personal-note-type">'+escapeHtml(note.type)+'</span></a><div class="personal-note-body"><a class="personal-note-title" href="'+url+'" target="_blank" rel="noopener noreferrer">'+escapeHtml(note.title)+'</a><div class="personal-note-meta"><span>'+escapeHtml(note.author || '小红书创作者')+'</span><span>'+icon('heart')+' '+escapeHtml(note.likes || '—')+'</span></div></div></article>';
    }).join('')+'</div>';
  }

  function renderMessages() {
    if (!connected()) {
      $('#messagesContent').innerHTML = empty('message','你的消息，集中在这里','登录后可查看官方页面中的互动通知与私信会话。',connectAction);
      return;
    }
    if (!messageData) {
      $('#messagesContent').innerHTML = empty('message','准备查看'+(messageKind === 'private' ? '私信会话' : '互动通知'),'点击刷新消息，打开官网相应面板并读取其中可见的内容。');
      return;
    }
    if (!messageData.readable) {
      $('#messagesContent').innerHTML = empty('eye','请在官方页面查看','官网面板已尝试打开，目前无法在工作台读取该面板。可点击上方「在官方页面查看」，直接查看完整消息。');
      return;
    }
    const items = messageData.items || [];
    $('#messagesContent').innerHTML = items.length ? '<div class="personal-messages">'+items.map(item => '<article class="personal-message"><span class="message-item-icon">'+icon(messageKind === 'private' ? 'message' : 'bell')+'</span><p>'+escapeHtml(item.text)+'</p></article>').join('')+'</div>' : '<div class="official-message-snapshot"><span class="snapshot-label">小红书官方页面 · '+(messageKind === 'private' ? '私信会话' : '互动通知')+'</span><p>'+escapeHtml(messageData.text || '官网面板中暂未显示消息内容。')+'</p></div>';
  }

  async function checkStatus() {
    if (polling || pending || document.hidden) return;
    polling = true;
    try {
      const previous = session.status, previousIdentity = session.accountId || session.name;
      session = await request('status'); serviceError = '';
      const changedAccount = previous === 'connected' && connected() && previousIdentity !== (session.accountId || session.name);
      if (previous === 'connected' && (!connected() || changedAccount)) {
        notes = []; messageData = null; loadedRecommendations = false; loadedMessages = false;
        $('#recommendationsUpdated').textContent = '登录后读取官方页面';
        $('#messagesUpdated').textContent = '登录后读取官方页面';
        renderRecommendations(); renderMessages();
      }
      renderSession();
      if ((previous !== 'connected' || changedAccount) && connected()) {
        showToast('小红书账号已连接'); renderRecommendations(); renderMessages();
        if (activeView === 'recommendations') void syncRecommendations();
        if (activeView === 'messages') void syncMessages();
      }
    } catch (error) { serviceError = error.message; renderSession(); }
    finally { polling = false; }
  }

  async function connect(refresh = false) {
    if (pending || session.busy) return;
    if (connected()) { showView('recommendations'); return; }
    if (activeView !== 'account') showView('account');
    pending = true; serviceError = ''; renderSession();
    try { session = await request(refresh || session.status !== 'disconnected' ? 'login/refresh' : 'connect',true); if(connected()) showToast('小红书账号已连接'); }
    catch (error) { serviceError = error.message; session.login = { status:'error', message:error.message }; }
    finally { pending = false; renderSession(); renderRecommendations(); renderMessages(); }
  }

  async function syncRecommendations(more = false) {
    if (pending) return;
    if (!connected()) { showView('account'); return; }
    pending = true; renderSession(); notice('#recommendationsNotice', more ? '正在读取更多推荐…' : '正在读取官方推荐内容…');
    try {
      const data = await request('recommendations'+(more ? '?more=1' : ''),true);
      const combined = more ? [...notes,...data.items] : data.items;
      notes = [...new Map(combined.map(note => [note.id,note])).values()];
      loadedRecommendations = true;
      $('#recommendationsUpdated').textContent = '已读取 '+notes.length+' 篇 · 更新于 '+time(data.updatedAt);
      notice('#recommendationsNotice', more && combined.length && notes.length === combined.length - data.items.length ? '官方页面暂未加载新的笔记，可稍后重试。' : '');
    } catch (error) { notice('#recommendationsNotice',error.message); if(error.status === 401) void checkStatusAfter(); }
    finally { pending = false; renderSession(); renderRecommendations(); }
  }

  async function syncMessages(open = false) {
    if (pending) return;
    if (!connected()) { showView('account'); return; }
    pending = true; renderSession(); notice('#messagesNotice','正在打开官方'+(messageKind === 'private' ? '消息' : '通知')+'面板…');
    try {
      messageData = await request('messages?kind='+messageKind+(open ? '&open=1' : ''),true);
      loadedMessages = true;
      $('#messagesUpdated').textContent = messageData.readable ? '读取于 '+time(messageData.updatedAt)+' · 官网可见内容' : '请在客户端内查看官网面板';
      notice('#messagesNotice','');
    } catch(error) { notice('#messagesNotice',error.message); if(error.status === 401) void checkStatusAfter(); }
    finally { pending = false; renderSession(); renderMessages(); }
  }
  async function checkStatusAfter() { setTimeout(checkStatus,50); }

  document.addEventListener('click',async event => {
    if (event.target.closest('[data-connect-xhs]')) { await connect(); return; }
    if (event.target.closest('[data-open-recommendations]')) { showView('recommendations'); return; }
    if (event.target.closest('[data-open-messages]')) { showView('messages'); return; }
    const tab = event.target.closest('[data-message-kind]');
    if (tab && !pending && messageKind !== tab.dataset.messageKind) {
      messageKind = tab.dataset.messageKind; messageData = null; loadedMessages = false;
      $$('[data-message-kind]').forEach(button => { button.classList.toggle('active',button === tab); button.setAttribute('aria-selected',String(button === tab)); });
      renderMessages(); if(connected()) await syncMessages();
    }
  });
  $('#checkConnectionButton').addEventListener('click',checkStatus);
  $('#refreshQrButton').addEventListener('click',()=>connect(true));
  $('#syncRecommendations').addEventListener('click',()=>syncRecommendations());
  $('#loadMoreRecommendations').addEventListener('click',()=>syncRecommendations(true));
  $('#syncMessages').addEventListener('click',()=>syncMessages());
  $('#openOfficialMessages').addEventListener('click',()=>syncMessages(true));
  $('#clearConnectionButton').addEventListener('click',async () => {
    if(pending)return;
    pending = true; renderSession();
    try { session = await request('disconnect',true); serviceError = ''; notes = []; messageData = null; loadedRecommendations = false; loadedMessages = false; showToast('已清除本机小红书登录会话'); }
    catch(error) { serviceError = error.message; }
    finally { pending = false; renderSession(); renderRecommendations(); renderMessages(); }
  });
  document.addEventListener('workspace:view',event => {
    renderSession();
    if(event.detail === 'recommendations') { renderRecommendations(); if(connected() && !loadedRecommendations) void syncRecommendations(); }
    if(event.detail === 'messages') { renderMessages(); if(connected() && !loadedMessages) void syncMessages(); }
    if(['account','recommendations','messages'].includes(event.detail)) void checkStatus();
  });
  document.addEventListener('visibilitychange',()=>{ if(!document.hidden) void checkStatus(); });
  renderSession(); renderRecommendations(); renderMessages(); void checkStatus();
  setInterval(()=>{ if(['account','recommendations','messages'].includes(activeView)) void checkStatus(); },4000);
})();
