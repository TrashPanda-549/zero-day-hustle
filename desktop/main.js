// Desktop shell: opens the game page (www/index.html) in a window.
const { app, BrowserWindow, Menu, screen, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');

// The game starts in true full screen, on the screen it is launched on. F11 (or Alt+Enter, or the game's
// own menu) switches to an ordinary window and back. It comes back the way it was left: full screen or
// windowed, and the window's size and place and whether it was maximized. That is kept in window-state.json
// in the user-data folder.
const MIN_W = 360, MIN_H = 560;          // small enough for the phone layout, which the page still has
const DEF_W = 1280, DEF_H = 800;         // the windowed size before the player has chosen one
const stateFile = () => path.join(app.getPath('userData'), 'window-state.json');

function loadState() {
  try {
    const s = JSON.parse(fs.readFileSync(stateFile(), 'utf8'));
    if (s && [s.x, s.y, s.width, s.height].every(Number.isFinite)) return s;
  } catch (e) {}
  return null;
}

// Where the window goes when it is neither full screen nor maximized (full screen then happens on the screen
// this lands on). A saved place is only used if enough of it is still on a screen to grab (a monitor may have
// been unplugged since); otherwise the window is centred on the screen the mouse pointer is on.
function normalBounds(saved) {
  const fit = (want, room) => Math.min(want, room);
  if (saved) {
    const b = { x: Math.round(saved.x), y: Math.round(saved.y),
      width: Math.max(MIN_W, Math.round(saved.width)), height: Math.max(MIN_H, Math.round(saved.height)) };
    const area = screen.getDisplayMatching(b).workArea;
    const seenW = Math.min(b.x + b.width, area.x + area.width) - Math.max(b.x, area.x);
    const seenH = Math.min(b.y + b.height, area.y + area.height) - Math.max(b.y, area.y);
    const titleBarOn = b.y >= area.y - 8 && b.y <= area.y + area.height - 40;
    if (seenW >= 120 && seenH >= 80 && titleBarOn) {
      b.width = fit(b.width, area.width);
      b.height = fit(b.height, area.height);
      return b;
    }
  }
  const area = screen.getDisplayNearestPoint(screen.getCursorScreenPoint()).workArea;
  const width = fit(saved ? Math.max(MIN_W, saved.width) : DEF_W, area.width);
  const height = fit(saved ? Math.max(MIN_H, saved.height) : DEF_H, area.height);
  return { width, height, x: Math.round(area.x + (area.width - width) / 2), y: Math.round(area.y + (area.height - height) / 2) };
}

function createWindow() {
  const saved = loadState();
  let normal = normalBounds(saved);   // the windowed size and place, kept up to date below
  const win = new BrowserWindow({
    ...normal,
    minWidth: MIN_W,
    minHeight: MIN_H,
    show: false,
    backgroundColor: '#04070a',
    title: 'Zero Day Hustle',
    autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true,
      preload: path.join(__dirname, 'preload.js') },
  });

  // Remembering: the windowed size and place are tracked apart from full screen and maximized, so leaving
  // full screen on a later launch goes back to them.
  let maximized = saved ? !!saved.maximized : true;
  const fullScreen = saved ? saved.fullScreen !== false : true;
  let timer = null;
  const save = () => {
    clearTimeout(timer);
    timer = null;
    if (win.isDestroyed()) return;
    const full = win.isFullScreen();
    if (!full && !win.isMinimized()) {
      maximized = win.isMaximized();
      if (!maximized) normal = win.getBounds();
    }
    try {
      fs.mkdirSync(path.dirname(stateFile()), { recursive: true });
      fs.writeFileSync(stateFile(), JSON.stringify({ ...normal, maximized, fullScreen: full }));
    } catch (e) {}
  };
  const saveSoon = () => { if (!timer) timer = setTimeout(save, 400); };
  for (const ev of ['resize', 'move', 'maximize', 'unmaximize', 'enter-full-screen', 'leave-full-screen', 'restore']) win.on(ev, saveSoon);
  win.on('close', save);

  // Full screen keys: F11 or Alt+Enter (on a Mac the View menu and the green button do it, with the usual
  // Ctrl+Cmd+F). Escape is left alone: it belongs to the game. Alt+F4 closes the window as always.
  if (process.platform !== 'darwin') {
    win.webContents.on('before-input-event', (event, input) => {
      if (input.type !== 'keyDown' || input.isAutoRepeat) return;
      const f11 = input.key === 'F11' && !input.alt && !input.control && !input.meta;
      const altEnter = input.key === 'Enter' && input.alt && !input.control && !input.meta && !input.shift;
      if (!f11 && !altEnter) return;
      event.preventDefault();
      win.setFullScreen(!win.isFullScreen());
    });
  }

  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.loadFile(path.join(__dirname, '..', 'www', 'index.html'));
  if (maximized) win.maximize();
  if (fullScreen) win.setFullScreen(true);
  win.show();
}

// What the game's own menu can ask for (see preload.js): full screen on or off, and quit.
const windowOf = event => BrowserWindow.fromWebContents(event.sender);
ipcMain.on('zdh-is-fullscreen', event => { const w = windowOf(event); event.returnValue = !!w && w.isFullScreen(); });
ipcMain.on('zdh-set-fullscreen', (event, on) => { const w = windowOf(event); if (w) w.setFullScreen(!!on); });
ipcMain.on('zdh-quit', () => app.quit());

app.whenReady().then(() => {
  if (process.platform !== 'darwin') Menu.setApplicationMenu(null);
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => app.quit());
