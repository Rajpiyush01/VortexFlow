document.addEventListener("DOMContentLoaded", () => {
  // --- 1. ELEMENT SELECTORS ---
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const overlay = document.getElementById("overlay");
  const themeToggle = document.getElementById("themeToggle");
  const menuItems = document.querySelectorAll(
    ".sidebar-menu .menu-item > button"
  );
  const widgetButtons = document.querySelectorAll("[data-widget]");
  const appContainer = document.getElementById("appContainer");
  const introSequence = document.getElementById("introSequence");

  // --- 2. STATE ---
  let currentTheme = "dark";
  let isAppLaunched = false; // Prevents the intro from hiding again

  // --- 3. CORE FUNCTIONS ---

  function launchApp() {
    if (isAppLaunched) return;
    isAppLaunched = true;
    if (introSequence) introSequence.classList.add("hidden");
    if (appContainer) appContainer.classList.add("visible");
  }

  function toggleSidebar() {
    // The first time the sidebar is opened, launch the main app view
    if (!isAppLaunched) {
      launchApp();
    }
    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");
  }

  function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    if (themeToggle) {
      themeToggle.innerHTML =
        theme === "dark"
          ? `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`
          : `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`;
    }
  }

  function switchWidget(widgetId) {
    document
      .querySelectorAll(".widget")
      .forEach((w) => w.classList.remove("active"));
    const newWidget = document.getElementById(widgetId);
    if (newWidget) {
      newWidget.classList.add("active");
    }
    document
      .querySelectorAll(".submenu-item")
      .forEach((item) => item.classList.remove("active"));
    const activeButton = document.querySelector(
      `button[data-widget="${widgetId}"]`
    );
    if (
      activeButton &&
      activeButton.parentElement.classList.contains("submenu-item")
    ) {
      activeButton.parentElement.classList.add("active");
    }
  }

  // --- 4. EVENT LISTENERS ---

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", toggleSidebar);
  }
  if (overlay) {
    overlay.addEventListener("click", toggleSidebar);
  }
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      applyTheme(currentTheme === "dark" ? "light" : "dark");
    });
  }

  menuItems.forEach((button) => {
    button.addEventListener("click", () => {
      const parentLi = button.parentElement;
      if (button.hasAttribute("data-widget")) {
        if (!isAppLaunched) launchApp();
        switchWidget(button.dataset.widget);
        // Only close sidebar if it's a direct click, not a category expansion
        if (!parentLi.querySelector(".submenu")) {
          toggleSidebar();
        }
      } else {
        parentLi.classList.toggle("active");
      }
    });
  });

  widgetButtons.forEach((button) => {
    if (button.parentElement.classList.contains("submenu-item")) {
      button.addEventListener("click", (e) => {
        e.stopPropagation();
        if (!isAppLaunched) launchApp();
        switchWidget(button.dataset.widget);
        toggleSidebar();
      });
    }
  });

  // --- 5. INITIALIZATION ---
  applyTheme("dark");
  console.log(
    "VortexFlow UI Initialized. Click the sidebar to launch the main view."
  );
});
