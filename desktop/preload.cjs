const {contextBridge, ipcRenderer} = require('electron');
contextBridge.exposeInMainWorld('shujinDesktop', {
  version:'1.0.1',
  openOfficial:url=>ipcRenderer.invoke('xhs:open', url),
  closeOfficial:()=>ipcRenderer.invoke('xhs:hide'),
  refreshOfficial:()=>ipcRenderer.invoke('xhs:refresh'),
  onOfficial:callback=> { const listener=(_event,state)=>callback(state); ipcRenderer.on('xhs:view',listener); return ()=>ipcRenderer.removeListener('xhs:view',listener); }
});
