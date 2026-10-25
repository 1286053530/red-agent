(() => {
  const bridge=window.shujinDesktop;
  let openEmbedded;
  if(bridge){
    const overlay=document.createElement('section');
    overlay.className='manual-official hidden';
    overlay.setAttribute('aria-label','手动访问小红书官网');
    overlay.innerHTML='<div class="manual-official-toolbar"><strong>小红书官网</strong><button id="manualOfficialBack" class="secondary-button">关闭官网</button></div><p id="manualOfficialState" role="status">官网可能要求登录或验证；工作台不读取消息，也不自动操作。</p><div class="manual-official-viewport" aria-label="官网显示区域"></div>';
    const accountView=document.querySelector('#accountView');
    accountView.append(overlay);
    const viewport=overlay.querySelector('.manual-official-viewport');
    const state=overlay.querySelector('#manualOfficialState');
    const setVisible=visible=>{overlay.classList.toggle('hidden',!visible);accountView.classList.toggle('official-active',visible);};
    const bounds=()=>{
      const rect=viewport.getBoundingClientRect();
      const topbar=document.querySelector('.topbar').getBoundingClientRect();
      const x=Math.max(0,rect.left),y=Math.max(0,topbar.bottom,rect.top);
      return {x,y,width:Math.min(innerWidth,rect.right)-x,height:Math.min(innerHeight,rect.bottom)-y};
    };
    let frame=0;
    let retained=false, outOfView=false;
    const resize=()=>{
      cancelAnimationFrame(frame);
      frame=requestAnimationFrame(()=>{
        if(overlay.classList.contains('hidden') || document.body.dataset.view!=='account')return;
        const rect=bounds();
        if(rect.width<1||rect.height<1){outOfView=true;void bridge.hideOfficial();return;}
        if(outOfView&&retained){outOfView=false;void bridge.resumeOfficial(rect).catch(error=>{state.textContent=error.message;});return;}
        void bridge.resizeOfficial(rect).catch(error=>{state.textContent=error.message;});
      });
    };
    new ResizeObserver(resize).observe(viewport);
    window.addEventListener('resize',resize);
    window.addEventListener('scroll',resize,true);
    bridge.onOfficial(result=>{
      retained=result.retained===true;
      if(!retained)outOfView=false;
      if(result.visible&&document.body.dataset.view!=='account'){setVisible(false);void bridge.hideOfficial();return;}
      setVisible(retained&&document.body.dataset.view==='account');
      state.textContent=result.error||'由你手动浏览；工作台不读取消息，也不自动操作。';
      if(result.visible)resize();
    });
    document.addEventListener('workspace:view',event=>{
      if(event.detail!=='account'&&!overlay.classList.contains('hidden')){setVisible(false);void bridge.hideOfficial();}
      else if(event.detail==='account'&&retained){
        setVisible(true);
        const rect=bounds();
        if(rect.width>0&&rect.height>0)void bridge.resumeOfficial(rect).catch(error=>{state.textContent=error.message;});
      }
    });
    openEmbedded=async()=>{
      showView('account');setVisible(true);
      const rect=bounds();
      if(rect.width<1||rect.height<1){setVisible(false);throw Error('官网显示区域不可用。');}
      await bridge.openOfficial(rect);
    };
    overlay.querySelector('#manualOfficialBack').addEventListener('click',event=>{if(event.isTrusted)void bridge.closeOfficial().catch(error=>{state.textContent=error.message;});});
    document.querySelectorAll('[data-open-xhs]').forEach(link=>{link.textContent='在工作台内打开官网';});
    document.querySelector('#accountView .page-intro p').textContent='在工作台内嵌官网中，由你手动浏览。';
    document.querySelector('#accountView .account-hero-copy>p').textContent='点击后手动登录和浏览。切换到 Agent 后会保留网页，回来继续浏览；点击“关闭官网”或退出软件时才关闭。官网自身的后台连接可能继续运行。';
    document.querySelector('#accountView .account-access-note p').textContent='清理仅影响本软件内嵌官网及旧版本的登录数据，不会清理系统浏览器，也不会访问官网执行退出。';
    document.querySelector('#clearConnectionButton').textContent='清理本软件登录数据';
    document.addEventListener('keydown',event=>{if(event.isTrusted&&event.key==='Escape'&&!overlay.classList.contains('hidden'))void bridge.closeOfficial();});
  }
  const errorTarget = document.querySelector('#connectionError');
  const report = message => {
    if (errorTarget) { errorTarget.textContent = message; errorTarget.classList.toggle('hidden', !message); }
  };
  // A new official page only follows an actual user click. View switches can
  // reveal that same retained page; they never navigate it or inspect its content.
  document.addEventListener('click', async event => {
    const link = event.target.closest('[data-open-xhs]');
    if (!link) return;
    if (!event.isTrusted) { event.preventDefault(); return; }
    if (!window.shujinDesktop) return; // A normal browser follows the explicit link.
    event.preventDefault();
    try { await openEmbedded(); report(''); }
    catch (error) { report(error.message || '未能打开内嵌官网，请手动重试。'); }
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
