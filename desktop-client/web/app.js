document.addEventListener("DOMContentLoaded", () => {
  // --- 1. ELEMENT SELECTORS ---
  const canvas = document.getElementById("cgi-canvas");
  const introSequence = document.getElementById("introSequence");
  const cyclingText = document.getElementById("cyclingText");
  const appContainer = document.getElementById("appContainer");
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const overlay = document.getElementById("overlay");
  const sidebarThemeToggle = document.querySelector(
    ".sidebar-footer #themeToggle"
  );
  const menuItems = document.querySelectorAll(".menu-item");
  const widgetButtons = document.querySelectorAll("[data-widget]");
  const allToggles = document.querySelectorAll(".toggle-switch");

  // --- 2. STATE MANAGEMENT ---
  let isAppLaunched = false;
  let currentTheme = "dark";
  let cycleInterval;

  // --- 3. DUAL-MODE CGI ANIMATION ---
  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  let particles = [];
  class Particle {
    /* ... full particle class from previous version ... */
  }
  function setupParticles() {
    /* ... full setupParticles function ... */
  }
  function animateParticles() {
    /* ... full animateParticles function ... */
  }

  // --- 4. ICON DEFINITIONS ---
  const icons = {
    sun: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`,
    moon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`,
  };

  // --- 5. THEME MANAGEMENT ---
  function applyTheme(theme) {
    /* ... full applyTheme function ... */
  }
  if (sidebarThemeToggle) {
    sidebarThemeToggle.addEventListener("click", () => {
      applyTheme(currentTheme === "dark" ? "light" : "dark");
    });
  }

  // --- 6. "ATTRACT MODE" SEQUENCE LOGIC ---
  const introLine = "Intelligently automating your digital workflow.";
  const promptLine = "Open the Command Deck to begin your work";
  const fillerLines = [
    "Connecting to Neural Nexus...",
    /* ... */ "Welcome, Operator.",
  ];

  function startIntroCycle() {
    /* ... full startIntroCycle function ... */
  }

  // --- 7. CORE APP INTERACTIVITY ---
  function showIntro() {
    /* ... full showIntro function ... */
  }
  function launchApp() {
    /* ... full launchApp function ... */
  }
  function toggleSidebar() {
    /* ... full toggleSidebar function ... */
  }

  sidebarToggle.addEventListener("click", toggleSidebar);
  overlay.addEventListener("click", toggleSidebar);
  menuItems.forEach((item) => {
    /* ... full menu item logic ... */
  });
  widgetButtons.forEach((button) => {
    /* ... full widget button logic ... */
  });
  allToggles.forEach((toggle) => {
    /* ... full toggle logic ... */
  });

  // --- 8. INITIALIZE APP ---
  applyTheme("dark");
  animateParticles();
  startIntroCycle();
});
