// Runs in the game window before the page. It gives the page the three things only the desktop app can do,
// and nothing else: the page finds them as window.zdhDesktop, which does not exist on the web or on phones.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('zdhDesktop', {
  isFullScreen: () => ipcRenderer.sendSync('zdh-is-fullscreen') === true,
  setFullScreen: on => ipcRenderer.send('zdh-set-fullscreen', !!on),
  quit: () => ipcRenderer.send('zdh-quit'),
});
