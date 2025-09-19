const { app, BrowserWindow, ipcMain, Tray, nativeImage, globalShortcut, Menu } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let tray;
let backendProcess;

// ---------- CREATE WINDOW ----------
function createWindow() {
  const iconPath = path.join(__dirname, "assets", "icon.png"); // icon for window & tray

  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 600,
    minHeight: 400,
    frame: false,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, "renderer", "index.js"),
    },
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  // Restore "always on top" setting
  mainWindow.webContents.executeJavaScript(
    'localStorage.getItem("alwaysOnTop") === "true"'
  ).then((val) => mainWindow.setAlwaysOnTop(val));

  mainWindow.on("minimize", (event) => {
    event.preventDefault();
    mainWindow.hide();
    createTray(iconPath);
  });

  mainWindow.on("close", (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      mainWindow.hide();
      createTray(iconPath);
    }
  });

  // ---------- START BACKEND ----------
  startBackend();

  // ---------- LAUNCH ON STARTUP ----------
  setupLaunchOnStartup();
}

// ---------- START BACKEND PROCESS ----------
function startBackend() {
  const backendPath = app.isPackaged
    ? path.join(process.resourcesPath, "backend", "app.exe")
    : path.join(__dirname, "backend", "app.exe");

  try {
    backendProcess = spawn(backendPath, [], { stdio: "inherit", detached: true });
    backendProcess.unref();

    backendProcess.on("error", (err) => {
      console.error("Backend failed to start:", err);
    });

    backendProcess.on("exit", (code, signal) => {
      console.log(`Backend exited with code ${code}, signal ${signal}`);
    });
  } catch (err) {
    console.error("Failed to start backend:", err);
  }
}

// ---------- TRAY ----------
function createTray(iconPath) {
  if (tray) return;
  tray = new Tray(nativeImage.createFromPath(iconPath));
  tray.setToolTip("NeuroDesk Clipboard");

  const trayMenu = Menu.buildFromTemplate([
    { label: "Restore", click: () => restoreWindow() },
    { type: "separator" },
    { label: "Quit", click: () => { app.isQuiting = true; app.quit(); } }
  ]);

  tray.setContextMenu(trayMenu);
  tray.on("double-click", () => restoreWindow());
}

// ---------- HELPERS ----------
function restoreWindow() {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
  }
}

// ---------- IPC HANDLERS ----------
ipcMain.on("set-always-on-top", (event, value) => { if (mainWindow) mainWindow.setAlwaysOnTop(value); });
ipcMain.on("set-launch-on-start", (event, value) => {
  app.setLoginItemSettings({ openAtLogin: value, openAsHidden: true });
});
ipcMain.on("minimize-to-tray", () => { if (mainWindow) mainWindow.minimize(); });
ipcMain.on("window-minimize", () => { if (mainWindow) mainWindow.minimize(); });
ipcMain.on("window-maximize", () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
      mainWindow.webContents.send("window-is-restored");
    } else {
      mainWindow.maximize();
      mainWindow.webContents.send("window-is-maximized");
    }
  }
});
ipcMain.on("window-close", () => { if (mainWindow) mainWindow.close(); });

// ---------- GLOBAL SHORTCUTS ----------
function registerShortcuts() {
  if (!mainWindow) return;
  globalShortcut.register("Control+M", () => { if (mainWindow) mainWindow.minimize(); });
  globalShortcut.register("Control+N", () => { restoreWindow(); });
}

// ---------- LAUNCH ON STARTUP SETUP ----------
function setupLaunchOnStartup() {
  // Default to enabled if first run
  const launchItemSettings = app.getLoginItemSettings();
  const firstRun = !localStorageLaunchSet();
  
  if (firstRun || !launchItemSettings.openAtLogin) {
    app.setLoginItemSettings({ openAtLogin: true, openAsHidden: true });
    mainWindow.webContents.executeJavaScript(`localStorage.setItem("launchOnStart", true)`);
  } else {
    mainWindow.webContents.executeJavaScript(`localStorage.setItem("launchOnStart", ${launchItemSettings.openAtLogin})`);
  }
}

function localStorageLaunchSet() {
  // Checks if localStorage has launchOnStart set
  // Since localStorage is in renderer, ask via mainWindow only if exists
  if (!mainWindow) return false;
  return mainWindow.webContents.executeJavaScript(`localStorage.getItem("launchOnStart") !== null`);
}

// ---------- APP ----------
app.whenReady().then(() => {
  createWindow();
  registerShortcuts();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// ---------- CLEANUP ----------
app.on("will-quit", () => {
  globalShortcut.unregisterAll();
  if (tray) tray.destroy();
  if (backendProcess) backendProcess.kill();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
