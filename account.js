(() => {
  const bridge=window.shujinDesktop;
  let openEmbedded;
  if(bridge){
    const overlay=document.createElement('section');
    overlay.className='manual-official hidden';
    overlay.setAttribute('aria-label','手动访问小红书官网');
    overlay.innerHTML='<div class="manual-official-toolbar"><div class="manual-official-actions"><button id="manualOfficialZoomReset" class="secondary-button hidden" title="恢复到 80%">重置</button><button id="manualOfficialZoomOut" class="secondary-button manual-official-icon" aria-label="缩小网页内容" title="缩小网页内容：每次 10%，最低 50%"><svg class="icon" aria-hidden="true" focusable="false"><use href="#i-zoom-out"/></svg></button><button id="manualOfficialExpand" class="secondary-button manual-official-icon hidden" aria-label="放大浏览" title="放大浏览"><svg class="icon" aria-hidden="true" focusable="false"><use href="#i-expand"/></svg></button></div></div><div class="manual-official-viewport" aria-label="官网显示区域"></div>';
    const accountView=document.querySelector('#accountView');
    accountView.append(overlay);
    const viewport=overlay.querySelector('.manual-official-viewport');
    const reportEmbeddedError=error=>{
      const message=error?.message||'小红书页面操作失败。';
      if(typeof window.showToast==='function')window.showToast(message);
      else {const target=document.querySelector('#connectionError');if(target){target.textContent=message;target.classList.remove('hidden');}}
    };
    let retained=false, opening=false, nativeVisible=false, lastBounds='';
    let zoomFactor=0.8, zoomPending=false;
    const zoomOut=overlay.querySelector('#manualOfficialZoomOut'),zoomReset=overlay.querySelector('#manualOfficialZoomReset');
    const updateZoomControls=()=>{
      zoomOut.disabled=zoomPending||!retained||zoomFactor<=0.5;
      zoomReset.disabled=zoomPending||!retained;
      zoomReset.classList.toggle('hidden',zoomFactor===0.8);
    };
    const changeZoom=async factor=>{
      if(zoomPending||!retained)return;
      zoomPending=true;updateZoomControls();
      try {const result=await bridge.setOfficialZoom(factor);zoomFactor=result.zoomFactor;}
      catch(error){reportEmbeddedError(error);}
      finally{zoomPending=false;updateZoomControls();}
    };
    zoomOut.addEventListener('click',event=>{if(event.isTrusted)void changeZoom(Math.max(0.5,Math.round((zoomFactor-0.1)*100)/100));});
    zoomReset.addEventListener('click',event=>{if(event.isTrusted)void changeZoom(0.8);});
    const miniHost=()=>document.querySelector('#devBrowserTabPanel');
    const host=()=>document.body.dataset.view==='account'?accountView:
      document.body.dataset.view==='developer'&&document.querySelector('#devBrowserTab')?.getAttribute('aria-selected')==='true'?miniHost():null;
    const setSurface=()=>{
      const target=host(), active=!!target&&(retained||opening);
      if(target&&overlay.parentElement!==target)target.append(overlay);
      overlay.classList.toggle('hidden',!active);
      accountView.classList.toggle('official-active',active&&target===accountView);
      miniHost()?.classList.toggle('official-active',active&&target===miniHost());
      overlay.querySelector('#manualOfficialExpand').classList.toggle('hidden',target!==miniHost());
    };
    const bounds=()=>{
      const rect=viewport.getBoundingClientRect();
      const x=Math.max(0,rect.left),y=Math.max(0,rect.top);
      return {x,y,width:Math.min(innerWidth,rect.right)-x,height:Math.min(innerHeight,rect.bottom)-y};
    };
    let frame=0;
    const resize=()=>{
      cancelAnimationFrame(frame);
      frame=requestAnimationFrame(()=>{
        setSurface();
        const rect=bounds();
        const blocked=document.body.classList.contains('right-panel-resizing')||document.querySelector('#devSettingsModal:not(.hidden), #devImageViewer[open]');
        const visible=!!host()&&!overlay.classList.contains('hidden')&&viewport.getClientRects().length>0&&rect.width>0&&rect.height>0&&!blocked;
        const failed=reportEmbeddedError;
        if(!visible){if(nativeVisible){nativeVisible=false;void bridge.hideOfficial().catch(failed);}return;}
        if(!retained)return;
        const key=JSON.stringify(rect);
        if(!nativeVisible){nativeVisible=true;lastBounds=key;void bridge.resumeOfficial(rect).catch(failed);}
        else if(key!==lastBounds){lastBounds=key;void bridge.resizeOfficial(rect).catch(failed);}
      });
    };
    new ResizeObserver(resize).observe(viewport);
    window.addEventListener('resize',resize);
    window.addEventListener('scroll',resize,true);
    bridge.onOfficial(result=>{
      retained=result.retained===true;
      nativeVisible=result.visible===true;
      if(Number.isFinite(result.zoomFactor))zoomFactor=result.zoomFactor;
      updateZoomControls();
      if(retained)opening=false;
      setSurface();
      if(result.error)reportEmbeddedError(new Error(result.error));
      if(result.visible||!retained)resize();
    });
    const switched=()=>{
      setSurface();
      if(!host()&&nativeVisible){nativeVisible=false;void bridge.hideOfficial().catch(reportEmbeddedError);}
      resize();
    };
    document.addEventListener('workspace:view',switched);
    document.addEventListener('workspace:right-panel',switched);
    document.addEventListener('DOMContentLoaded',()=>{
      const observer=new MutationObserver(resize);
      for(const target of [document.querySelector('#developerView'),document.querySelector('#devSettingsModal'),document.querySelector('#devImageViewer')])
        if(target)observer.observe(target,{attributes:true,attributeFilter:['class','open']});
    });
    openEmbedded=async(mode)=>{
      if(mode!=='mini')showView('account');
      opening=true;setSurface();
      const rect=bounds();
      if(rect.width<1||rect.height<1){opening=false;setSurface();throw Error('官网显示区域不可用。');}
      lastBounds=JSON.stringify(rect);
      try {await bridge.openOfficial(rect);}
      finally {opening=false;setSurface();resize();}
    };
    overlay.querySelector('#manualOfficialExpand').addEventListener('click',event=>{if(event.isTrusted)showView('account');});
    document.querySelectorAll('[data-open-xhs]').forEach(link=>{link.textContent='在工作台内打开官网';});
    document.querySelector('#accountView .page-intro p').textContent='在工作台内嵌官网中，由你手动浏览。';
    document.querySelector('#accountView .account-hero-copy>p').textContent='点击后手动登录和浏览。切换到 Agent 后会保留网页，回来继续浏览；按 Escape 或退出软件时关闭页面。官网自身的后台连接可能继续运行。';
    document.querySelector('#accountView .account-access-note p').textContent='清理仅影响本软件内嵌官网及旧版本的登录数据，不会清理系统浏览器，也不会访问官网执行退出。';
    document.querySelector('#clearConnectionButton').textContent='清理本软件登录数据';
    document.addEventListener('keydown',event=>{
      if(event.isTrusted&&event.key==='Escape'&&!overlay.classList.contains('hidden')&&
        !document.querySelector('#devSettingsModal:not(.hidden), #devImageViewer[open], .dev-composer-picker[open]'))void bridge.closeOfficial().catch(reportEmbeddedError);
    });
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
    try { await openEmbedded(link.dataset.xhsMode); report(''); }
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
