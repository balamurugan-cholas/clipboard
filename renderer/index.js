const { ipcRenderer } = require("electron");

window.addEventListener("DOMContentLoaded", () => {
  // ---------- ELEMENTS ----------
  const historyContainer = document.getElementById("historyContainer");
  const searchBar = document.getElementById("searchBar");
  const pauseBtn = document.getElementById("pause");
  const statusText = document.getElementById("status");
  const clearAllBtn = document.getElementById("clearAll");
  const exportBtn = document.getElementById("export");
  const settingsBtn = document.getElementById("settingsBtn");
  const settingsOverlay = document.getElementById("settingsOverlay");
  const closeSettings = document.getElementById("closeSettings");

  const showAllBtn = document.getElementById("showAll");
  const showFavoritesBtn = document.getElementById("showFavorites");
  const favCountBadge = document.getElementById("favCount");

  const popup = document.getElementById("popup");
  const popupText = document.getElementById("popupText");
  const popupCopy = document.getElementById("popupCopy");
  const popupPin = document.getElementById("popupPin");
  const popupFav = document.getElementById("popupFav");
  const popupDelete = document.getElementById("popupDelete");
  const popupClose = document.getElementById("popupClose");

  // Settings Elements
  const alwaysOnTopCheckbox = document.getElementById("alwaysOnTop");
  const launchOnStartCheckbox = document.getElementById("launchOnStart");
  const minimizeBtn = document.getElementById("minimizeBtn");
  const dropdownBtns = document.querySelectorAll(".dropdown-btn");

  // ---------- INITIAL SETTINGS STATE ----------
  alwaysOnTopCheckbox.checked = localStorage.getItem("alwaysOnTop") === "true";
  launchOnStartCheckbox.checked = localStorage.getItem("launchOnStart") === "true";

  // ---------- TOAST ----------
  const toastContainer = document.createElement("div");
  toastContainer.className = "toast-container";
  document.body.appendChild(toastContainer);
  let toastQueue = [];

  function showToast(msg) {
    if (toastQueue.length >= 2) {
      const old = toastQueue.shift();
      toastContainer.removeChild(old);
    }
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = msg;
    toastContainer.appendChild(toast);
    toastQueue.push(toast);
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
      toastQueue = toastQueue.filter(t => t !== toast);
    }, 2000);
  }

  // ---------- CLEAR ALL MODAL ----------
  const clearModal = document.createElement("div");
  clearModal.className = "clear-modal hidden";
  clearModal.innerHTML = `
    <div class="clear-modal-content">
      <p id="clearModalText">Are you sure you want to clear items?</p>
      <div class="clear-modal-buttons">
        <button id="clearYes">Yes</button>
        <button id="clearNo">No</button>
      </div>
    </div>
  `;
  document.body.appendChild(clearModal);
  const clearYesBtn = clearModal.querySelector("#clearYes");
  const clearNoBtn = clearModal.querySelector("#clearNo");

  function openClearModal(text) {
    document.getElementById("clearModalText").textContent = text;
    clearModal.classList.remove("hidden");
  }
  function closeClearModal() { clearModal.classList.add("hidden"); }

  // ---------- STATE ----------
  let clipboardData = [];
  let monitoring = true;
  let searchQuery = "";
  let currentPopupItem = null;
  let currentView = "All"; // "All" or "Favorites"

  // ---------- HELPERS ----------
  function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
  }

  // ---------- FETCH & RENDER ----------
  async function fetchClipboardHistory() {
    try {
      const response = await fetch("http://127.0.0.1:5000/history");
      const data = await response.json();
      clipboardData = data.map(item => ({
        id: item.id,
        text: item.content,
        is_favourite: item.is_favourite,
        is_pinned: item.is_pinned,
        timestamp: new Date(item.timestamp).toLocaleString(),
      }));
      updateFavBadge();
      renderClipboard();
    } catch (err) {
      showToast("Failed to fetch clipboard");
    }
  }

  function updateFavBadge() {
    const count = clipboardData.filter(i => i.is_favourite).length;
    favCountBadge.textContent = count;
  }

  function renderClipboard() {
    historyContainer.innerHTML = "";
    let items = [...clipboardData];

    if (currentView === "All") items = items.filter(i => !i.is_favourite);
    if (currentView === "Favorites") items = items.filter(i => i.is_favourite);

    if (searchQuery) {
      items = items.filter(i => i.text.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    if (items.length === 0) {
      historyContainer.innerHTML = '<div class="no-items">No clipboard items found.</div>';
      return;
    }

    items.sort((a, b) => {
      if (b.is_pinned !== a.is_pinned) return b.is_pinned - a.is_pinned;
      return new Date(b.timestamp) - new Date(a.timestamp);
    });

    items.forEach(item => {
      const div = document.createElement("div");
      div.className = "clipboard-item";
      if (item.is_pinned) div.classList.add("pinned");
      if (item.is_favourite) div.classList.add("favourite");

      const shortText = item.text.split(" ").slice(0, 8).join(" ") +
        (item.text.split(" ").length > 8 ? "..." : "");
      div.innerHTML = `
        <div class="item-info">
          <div class="item-text">${highlightText(shortText, searchQuery)}</div>
          <div class="timestamp">${item.timestamp}</div>
        </div>
      `;
      div.addEventListener("click", () => openPopup(item));
      historyContainer.appendChild(div);
    });
  }

  // ---------- POPUP ----------
  function openPopup(item) {
    currentPopupItem = item;
    popupText.innerHTML = highlightText(item.text, searchQuery);
    popup.classList.remove("hidden");
  }

  function closePopup() { popup.classList.add("hidden"); currentPopupItem = null; }

  popupCopy.addEventListener("click", () => {
    if (currentPopupItem) {
      navigator.clipboard.writeText(currentPopupItem.text);
      showToast("Copied to clipboard");
    }
  });

  popupPin.addEventListener("click", async () => {
    if (!currentPopupItem) return;
    await fetch(`http://127.0.0.1:5000/pin/${currentPopupItem.id}`, { method: "POST" });
    currentPopupItem = null;
    closePopup();
    await fetchClipboardHistory();
  });

  popupFav.addEventListener("click", async () => {
    if (!currentPopupItem) return;
    await fetch(`http://127.0.0.1:5000/favourite/${currentPopupItem.id}`, { method: "POST" });
    currentPopupItem = null;
    closePopup();
    await fetchClipboardHistory();
  });

  popupDelete.addEventListener("click", async () => {
    if (!currentPopupItem) return;
    await fetch(`http://127.0.0.1:5000/delete/${currentPopupItem.id}`, { method: "DELETE" });
    currentPopupItem = null;
    closePopup();
    await fetchClipboardHistory();
  });

  popupClose.addEventListener("click", closePopup);

  // ---------- MENU ----------
  showAllBtn.addEventListener("click", () => {
    currentView = "All";
    showAllBtn.classList.add("active");
    showFavoritesBtn.classList.remove("active");
    renderClipboard();
  });

  showFavoritesBtn.addEventListener("click", () => {
    currentView = "Favorites";
    showFavoritesBtn.classList.add("active");
    showAllBtn.classList.remove("active");
    renderClipboard();
  });

  // ---------- CONTROLS ----------
  searchBar.addEventListener("input", e => {
    searchQuery = e.target.value.trim();
    renderClipboard();
  });

  pauseBtn.addEventListener("click", async () => {
    monitoring = !monitoring;
    await fetch(`http://127.0.0.1:5000${monitoring ? "/resume" : "/pause"}`, { method: "POST" });
    statusText.textContent = monitoring ? "Monitoring" : "Paused";
    pauseBtn.innerHTML = monitoring ? '<i class="fa-solid fa-pause"></i>' : '<i class="fa-solid fa-play"></i>';
    showToast(monitoring ? "Monitoring resumed" : "Monitoring paused");
  });

  // ---------- CLEAR ALL ----------
  clearAllBtn.addEventListener("click", () => {
    const itemsToDelete = clipboardData.filter(i =>
      currentView === "All" ? !i.is_favourite : i.is_favourite
    );
    if (itemsToDelete.length === 0) {
      showToast("No items to clear!");
      return;
    }
    openClearModal(`Are you sure you want to clear all ${currentView === "All" ? "items" : "favorites"}?`);
  });

  clearYesBtn.addEventListener("click", async () => {
    const itemsToDelete = clipboardData.filter(i =>
      currentView === "All" ? !i.is_favourite : i.is_favourite
    );
    for (const item of itemsToDelete) {
      await fetch(`http://127.0.0.1:5000/delete/${item.id}`, { method: "DELETE" });
    }
    showToast(currentView === "All" ? "Cleared All Items" : "Cleared Favorites");
    await fetchClipboardHistory();
    closeClearModal();
  });

  clearNoBtn.addEventListener("click", closeClearModal);

  // ---------- EXPORT ----------
  exportBtn.addEventListener("click", () => {
    const itemsToExport = clipboardData.filter(i =>
      currentView === "All" ? !i.is_favourite : i.is_favourite
    );
    if (!itemsToExport.length) {
      showToast("No clipboard text to export!");
      return;
    }
    const allText = itemsToExport.map(i => `- ${i.text}`).join("\n\n");
    const blob = new Blob([allText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "clipboard_history.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Exported clipboard");
  });

  // ---------- SETTINGS ----------
  settingsBtn.addEventListener("click", () => settingsOverlay.classList.add("active"));
  closeSettings.addEventListener("click", () => settingsOverlay.classList.remove("active"));

  // Always on Top
  alwaysOnTopCheckbox.addEventListener("change", (e) => {
    const val = e.target.checked;
    localStorage.setItem("alwaysOnTop", val);
    ipcRenderer.send("set-always-on-top", val);
  });

  // Launch on Start
  launchOnStartCheckbox.addEventListener("change", (e) => {
    const val = e.target.checked;
    localStorage.setItem("launchOnStart", val);
    ipcRenderer.send("set-launch-on-start", val);
  });

  // Minimize to Tray
  if (minimizeBtn) {
    minimizeBtn.addEventListener("click", () => ipcRenderer.send("minimize-to-tray"));
  }

  // Dropdown toggles
  dropdownBtns.forEach(btn => {
    const content = btn.nextElementSibling;
    btn.addEventListener("click", () => {
      content.classList.toggle("active");
      const icon = btn.querySelector("i");
      if (icon) icon.classList.toggle("fa-caret-up");
    });
  });

  // ---------- KEYBOARD SHORTCUTS ----------
  document.addEventListener("keydown", (e) => {
    // Ctrl + Space → Open All Items
    if (e.ctrlKey && !e.altKey && e.code === "Space") {
      e.preventDefault();
      if (showAllBtn) showAllBtn.click();
    }

    // Ctrl + Alt + Space → Open Favorites
    if (e.ctrlKey && e.altKey && e.code === "Space") {
      e.preventDefault();
      if (showFavoritesBtn) showFavoritesBtn.click();
    }

    // Ctrl + Backspace → Clear All
    if (e.ctrlKey && e.key === "Backspace") {
      e.preventDefault();
      if (clearAllBtn) clearAllBtn.click();
    }

    // Ctrl + S → Focus Search
    if (e.ctrlKey && e.key.toLowerCase() === "s") {
      e.preventDefault();
      if (searchBar) searchBar.focus();
    }

    // Ctrl + P → Pause / Resume
    if (e.ctrlKey && e.key.toLowerCase() === "p") {
      e.preventDefault();
      if (pauseBtn) pauseBtn.click();
    }

    // Ctrl + M → Minimize to Tray
    if (e.ctrlKey && e.key.toLowerCase() === "m") {
      e.preventDefault();
      ipcRenderer.send("minimize-to-tray");
    }
  });

  // ---------- AUTO REFRESH ----------
  setInterval(() => { if (monitoring) fetchClipboardHistory(); }, 2000);

  fetchClipboardHistory();
});
