const { ipcRenderer } = require("electron");

document.addEventListener("DOMContentLoaded", () => {
  const minimizeBtn = document.getElementById("minimize");
  const maximizeBtn = document.getElementById("maximize");
  const closeBtn = document.getElementById("close");
  const topBar = document.querySelector(".top-bar");

  minimizeBtn.addEventListener("click", () => ipcRenderer.send("window-minimize"));
  maximizeBtn.addEventListener("click", () => ipcRenderer.send("window-maximize"));
  closeBtn.addEventListener("click", () => ipcRenderer.send("window-close"));

  topBar.addEventListener("dblclick", () => ipcRenderer.send("window-maximize"));

  ipcRenderer.on("window-is-maximized", () => maximizeBtn.textContent = "❐");
  ipcRenderer.on("window-is-restored", () => maximizeBtn.textContent = "▢");
});