const {contextBridge, ipcRenderer} = require('electron');
contextBridge.exposeInMainWorld('shujinDesktop', {
  version:'2.1.0',
  openOfficial:()=>ipcRenderer.invoke('xhs:open'),
  closeOfficial:()=>ipcRenderer.invoke('xhs:close'),
  openExternal:()=>ipcRenderer.invoke('xhs:external'),
  onOfficial:callback=>{const listener=(_event,state)=>callback(state);ipcRenderer.on('xhs:view',listener);return ()=>ipcRenderer.removeListener('xhs:view',listener);}
});
