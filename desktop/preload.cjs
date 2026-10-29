const {contextBridge, ipcRenderer} = require('electron');
contextBridge.exposeInMainWorld('shujinDesktop', {
  version:'2.1.52',
  openOfficial:bounds=>ipcRenderer.invoke('xhs:open',bounds),
  resizeOfficial:bounds=>ipcRenderer.invoke('xhs:bounds',bounds),
  setOfficialZoom:factor=>ipcRenderer.invoke('xhs:zoom',factor),
  hideOfficial:()=>ipcRenderer.invoke('xhs:hide'),
  resumeOfficial:bounds=>ipcRenderer.invoke('xhs:resume',bounds),
  closeOfficial:()=>ipcRenderer.invoke('xhs:close'),
  onOfficial:callback=>{const listener=(_event,state)=>callback(state);ipcRenderer.on('xhs:view',listener);return ()=>ipcRenderer.removeListener('xhs:view',listener);}
});
