const { app, BrowserWindow, ipcMain, Tray, Menu } = require("electron");
const path = require("path");
const regedit = require("electron-regedit");

let mainWindow;
let tray;

// ---------- CREATE WINDOW ----------
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      contextIsolation: false
    },
    show: false // start hidden
  });

  mainWindow.loadFile("index.html");

  // ---------- CREATE TRAY ----------
  tray = new Tray(path.join(__dirname, "icon.png"));
  const trayMenu = Menu.buildFromTemplate([
    {
      label: "Show NeuroDesk",
      click: () => mainWindow.show()
    },
    {
      label: "Exit",
      click: () => app.quit()
    }
  ]);
  tray.setToolTip("NeuroDesk Clipboard Manager");
  tray.setContextMenu(trayMenu);

  tray.on("double-click", () => {
    mainWindow.show();
  });

  // ---------- RESTORE LAUNCH ON START ----------
  checkLaunchOnStart();
}

// ---------- CHECK IF APP STARTS ON LOGIN ----------
function checkLaunchOnStart() {
  regedit.list("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", (err, result) => {
    let enabled = false;
    if (!err && result && result["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"].values.NeuroDesk) {
      enabled = true;
    } else {
      // First run: enable launch on startup by default
      enableLaunchOnStart(true);
      enabled = true;
    }

    // Send to renderer
    mainWindow.webContents.once("did-finish-load", () => {
      mainWindow.webContents.send("launch-on-start-state", enabled);
    });
  });
}

// ---------- ENABLE / DISABLE LAUNCH ON START ----------
function enableLaunchOnStart(enable) {
  if (enable) {
    regedit.add(
      "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
      "NeuroDesk",
      `"${process.execPath}"`,
      () => console.log("Launch on Start enabled")
    );
  } else {
    regedit.del(
      "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
      "NeuroDesk",
      () => console.log("Launch on Start disabled")
    );
  }

  // Update localStorage in renderer
  if (mainWindow) {
    mainWindow.webContents.executeJavaScript(`localStorage.setItem("launchOnStart", ${enable})`);
  }
}

// ---------- IPC HANDLERS ----------
ipcMain.on("set-launch-on-start", (event, enable) => {
  enableLaunchOnStart(enable);
});

ipcMain.on("set-always-on-top", (event, enable) => {
  if (mainWindow) mainWindow.setAlwaysOnTop(enable);
});

ipcMain.on("restore-settings", (event, settings) => {
  if (settings.alwaysOnTop && mainWindow) mainWindow.setAlwaysOnTop(true);
});

// ---------- APP READY ----------
app.on("ready", createWindow);

// ---------- PREVENT QUIT ----------
app.on("window-all-closed", (event) => {
  event.preventDefault(); // Keep in tray
});
