/* ==========================================================================
   PORTFOLIO ARCHITECTURE CORE ENGINE (script.js)
   ========================================================================== */

// Run as soon as the HTML elements finish loading on screen
document.addEventListener("DOMContentLoaded", () => {
  highlightActiveLink();
  initThemeToggle();
});

// 1. Centralized Light/Dark Theme Controller Engine
function initThemeToggle() {
  const toggleButton = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');

  if (!toggleButton) return;

  // 1. Look at what theme the <head> script already applied to the page
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  
  // 2. Synchronize the navbar moon/sun icon immediately to match it
  if (themeIcon) {
    themeIcon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
  }

  // 3. Listen for clicks to flip the theme safely
  toggleButton.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    let newTheme = theme === 'dark' ? 'light' : 'dark';
    
    // Apply changes locally to the document element
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Save to browser memory so the next page can read it!
    localStorage.setItem('theme', newTheme);
    
    // Flip the icon
    if (themeIcon) {
      themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
  });
}

// 2. Dynamic UI/UX Navigation Link Highlighter Mechanics
function highlightActiveLink() {
  const navLinks = document.querySelectorAll('.nav-link');
  const currentPath = window.location.pathname;

  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (
      linkPath === currentPath || 
      (currentPath === "/" && linkPath === "/home") ||
      (currentPath === "/home" && linkPath === "/")
    ) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// 3. Document Printing Controller Sandbox
function printResume() {
  const frameElement = document.getElementById('resume-frame');
  if (frameElement) {
    const resumeFrame = frameElement.contentWindow;
    resumeFrame.focus();
    resumeFrame.print();
  }
}