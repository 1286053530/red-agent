(() => {
  const bridge=window.shujinDesktop;
  if(bridge){
    const overlay=document.createElement('section');
    overlay.className='manual-official hidden';
    overlay.setAttribute('aria-label','手动访问小红书官网');
    overlay.innerHTML='<div class="manual-official-toolbar"><button id="manualOfficialBack" class="secondary-button">返回工作台并关闭官网</button><strong>小红书官网 · 手动操作</strong><button id="manualOfficialExternal" class="secondary-button">用系统浏览器打开</button></div><p id="manualOfficialState" role="status">官网可能要求登录或验证；工作台不读取消息，也不自动操作。</p>';
    document.body.append(overlay);
    const state=overlay.querySelector('#manualOfficialState');
    bridge.onOfficial(result=>{overlay.classList.toggle('hidden',!result.visible);state.textContent=result.error||'官网可能要求登录或验证；工作台不读取消息，也不自动操作。';});
    overlay.querySelector('#manualOfficialBack').addEventListener('click',event=>{if(event.isTrusted)void bridge.closeOfficial().catch(error=>{state.textContent=error.message;});});
    overlay.querySelector('#manualOfficialExternal').addEventListener('click',event=>{if(event.isTrusted)void bridge.openExternal().catch(error=>{state.textContent=error.message;});});
    document.querySelectorAll('[data-open-xhs]').forEach(link=>{link.textContent='在工作台内打开官网';});
    document.querySelector('#accountView .account-hero-copy>p').textContent='点击后在工作台内打开官方页面，由你手动登录、查看和回复。返回工作台或最小化窗口会关闭官网页面；账号可能仍受平台限制。';
    document.querySelector('#accountView .account-access-note p').textContent='清理仅影响本软件内嵌官网及旧版本的登录数据，不会清理系统浏览器，也不会访问官网执行退出。';
    document.querySelector('#clearConnectionButton').textContent='清理本软件登录数据';
    document.addEventListener('keydown',event=>{if(event.isTrusted&&event.key==='Escape'&&!overlay.classList.contains('hidden'))void bridge.closeOfficial();});
  }
  const errorTarget = document.querySelector('#connectionError');
  const report = message => {
    if (errorTarget) { errorTarget.textContent = message; errorTarget.classList.toggle('hidden', !message); }
  };
  // Official access only follows an actual user click. No startup requests,
  // visibility handlers, view-change requests, timers, login checks or extraction.
  document.addEventListener('click', async event => {
    const link = event.target.closest('[data-open-xhs]');
    if (!link) return;
    if (!event.isTrusted) { event.preventDefault(); return; }
    if (!window.shujinDesktop) return; // A normal browser follows the explicit link.
    event.preventDefault();
    try { await window.shujinDesktop.openOfficial(); report(''); }
    catch (error) { report(error.message || '未能打开官网，请手动使用系统浏览器。'); }
  });
  const clear = document.querySelector('#clearConnectionButton');
  if (clear) clear.addEventListener('click', async event => {
    if (!event.isTrusted || clear.disabled) return;
    if (!confirm('关闭内嵌官网并清除本软件保存的小红书登录数据？不会清理系统浏览器。')) return;
    clear.disabled = true;
    try {
      const response = await fetch('/api/xhs/disconnect', { method: 'POST', cache: 'no-store' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '清理失败，请重试。');
      report(''); showToast('已清理本软件的旧登录数据');
    } catch (error) { report(error.message); }
    finally { clear.disabled = false; }
  });
})();
