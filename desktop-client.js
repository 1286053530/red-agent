(() => {
  const bridge=window.shujinDesktop;
  if(!bridge)return;
  document.body.classList.add('desktop-edition');
  const overlay=document.createElement('section');
  overlay.className='official-overlay hidden';
  overlay.setAttribute('aria-label','小红书官方页面');
  overlay.innerHTML='<header class="official-toolbar"><button id="officialBack">'+icon('arrow')+'返回工作台</button><div class="official-title"><strong>筱竹书瑾 / 小红书</strong><small id="officialLocation">https://www.xiaohongshu.com · 本机会话</small></div><button id="officialRefresh">'+icon('refresh')+'刷新官网</button></header><div class="official-placeholder">正在加载小红书官方页面…</div>';
  document.body.append(overlay);
  const reportError=error=>showToast(error.message||'官网暂时未响应，请稍后重试。');
  const officialButton=document.createElement('button');
  officialButton.className='qr-action';
  officialButton.id='openOfficialLoginButton';
  officialButton.textContent='打开官网 / 完成验证';
  officialButton.onclick=()=>bridge.openOfficial().catch(reportError);
  document.querySelector('#qrLoginCard').append(officialButton);
  bridge.onOfficial(state=>{
    overlay.classList.toggle('hidden',!state.visible);
    overlay.querySelector('#officialLocation').textContent=state.error || (state.url+' · 登录会话保存在本机');
  });
  overlay.querySelector('#officialBack').onclick=()=>bridge.closeOfficial().then(()=>document.dispatchEvent(new Event('visibilitychange'))).catch(reportError);
  overlay.querySelector('#officialRefresh').onclick=()=>bridge.refreshOfficial().catch(reportError);
  document.addEventListener('click',event=>{
    const link=event.target.closest('a[href^="https://www.xiaohongshu.com/"]');
    if(!link)return;
    event.preventDefault();
    bridge.openOfficial(link.href).catch(reportError);
  });
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!overlay.classList.contains('hidden'))void bridge.closeOfficial();});
  const steps=document.querySelector('.connection-steps');
  if(steps)steps.querySelector('p').textContent='在当前页面显示官方二维码';
  const note=document.querySelector('.account-access-note p');
  if(note)note.textContent='在当前页面用手机 App 扫码并确认。官网要求额外验证时，可点击「打开官网 / 完成验证」；登录后继续查看推荐与消息。';
  const officialLink=document.querySelector('[data-open-xhs]');
  if(officialLink)officialLink.innerHTML='在客户端内打开小红书 '+icon('arrow');
  const officialMessages=document.querySelector('#openOfficialMessages');
  if(officialMessages)officialMessages.innerHTML='在客户端内查看 '+icon('arrow');
})();
