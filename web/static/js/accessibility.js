// ✅ Modified with full support for zoom, color scheme, and caption

let isLargeCursorActive = false;
let isCrosshairModeActive = false;
let crosshairElement = null;
let isScreenReaderOn = false;
let largeCaptionEnabled = false;
let currentTheme = null;
let zoomLevel = 1.0;
let targetZoomLevel = 1.0;
let animationFrameId = null;

function saveAccessibilityState() {
    const state = {
        zoomLevel: targetZoomLevel,
        largeCursor: isLargeCursorActive,
        crosshair: isCrosshairModeActive,
        caption: largeCaptionEnabled,
        theme: localStorage.getItem("accessibilityTheme"),
        screenReader: isScreenReaderOn,
    };
    localStorage.setItem("accessibilityState", JSON.stringify(state));
}

function restoreAccessibilityState() {
    const state = JSON.parse(localStorage.getItem("accessibilityState") || '{}');
    if (state.zoomLevel) {
        targetZoomLevel = parseFloat(state.zoomLevel);
        zoomLevel = targetZoomLevel;
        smoothZoom();
    }
    if (state.largeCursor) toggleCursorMode(true);
    if (state.crosshair) toggleCrosshair(true);
    if (state.caption) toggleLargeCaptions(true);
    if (state.theme) applyColorScheme(state.theme);
    if (state.screenReader) toggleScreenReader(true);
}

function resetAccessibility() {
    zoomLevel = 1.0;
    targetZoomLevel = 1.0;
    document.querySelectorAll("#menu, #content-wrapper").forEach(el => {
        el.style.transform = "scale(1)";
        el.style.transformOrigin = "top left";
    });
    if (isLargeCursorActive) toggleCursorMode(false);
    if (isCrosshairModeActive) toggleCrosshair(false);
    if (largeCaptionEnabled) toggleLargeCaptions(false);
    if (isScreenReaderOn) toggleScreenReader(false);
    resetColorScheme();
    localStorage.removeItem("accessibilityState");
    localStorage.removeItem("stickyMode");
    localStorage.removeItem("savedZoomLevel");
    localStorage.removeItem("largeCaptionEnabled");
    localStorage.removeItem("accessibilityTheme");
    const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
    if (stickyBtn) stickyBtn.classList.remove("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function toggleStickyMode() {
    const stickyActive = localStorage.getItem("stickyMode") === "true";
    const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
    if (!stickyActive) {
        localStorage.setItem("stickyMode", "true");
        saveAccessibilityState();
        if (stickyBtn) stickyBtn.classList.add("active");
    } else {
        localStorage.removeItem("stickyMode");
        localStorage.removeItem("accessibilityState");
        if (stickyBtn) stickyBtn.classList.remove("active");
    }
}

function closeToolbar() {
    resetAccessibility();
    document.getElementById("accessibility-toolbar").style.display = "none";
    document.getElementById("accessibility-btn").style.display = "block";
    document.getElementById("menu").style.top = "0";
    document.getElementById("content-wrapper").style.paddingTop = "40px";
}

function toggleCursorMode(force) {
    const body = document.body;
    const enable = (force !== undefined) ? force : !isLargeCursorActive;
    if (enable) body.classList.add('large-cursor');
    else body.classList.remove('large-cursor');
    isLargeCursorActive = enable;
    const cursorBtn = document.querySelector('button[onclick="toggleCursorMode()"]');
    if (cursorBtn) cursorBtn.setAttribute("aria-pressed", enable ? "true" : "false");
}

function toggleCrosshair(force) {
    const body = document.body;
    const enable = (force !== undefined) ? force : !isCrosshairModeActive;
    isCrosshairModeActive = enable;
    const crosshairBtn = document.querySelector('button[onclick="toggleCrosshair()"]');
    if (enable) {
        body.classList.add("crosshair-mode-active");
        if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "true");
        crosshairElement = document.createElement('div');
        crosshairElement.classList.add('crosshair');
        body.appendChild(crosshairElement);
        document.addEventListener("mousemove", moveCrosshair);
    } else {
        body.classList.remove("crosshair-mode-active");
        if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "false");
        if (crosshairElement) crosshairElement.remove();
        document.removeEventListener("mousemove", moveCrosshair);
        crosshairElement = null;
    }
}

function toggleLargeCaptions(force) {
    const enable = (force !== undefined) ? force : !largeCaptionEnabled;
    largeCaptionEnabled = enable;
    const captionBox = document.getElementById("large-caption");
    const contentWrapper = document.getElementById("content-wrapper");
    const isLoginPage = document.querySelector('.login-box') !== null;
    captionBox.style.display = enable ? "block" : "none";
    if (!isLoginPage) contentWrapper.style.paddingBottom = enable ? "120px" : "40px";
    else contentWrapper.style.paddingBottom = "0";
    if (enable) {
        captionBox.innerText = "";
        document.addEventListener("mouseover", updateCaption);
    } else {
        document.removeEventListener("mouseover", updateCaption);
    }
    localStorage.setItem("largeCaptionEnabled", enable);
}

function updateCaption(event) {
    const captionBox = document.getElementById("large-caption");
    const el = event.target;
    let text = el.getAttribute("aria-label") || el.getAttribute("alt") || el.innerText || "";
    captionBox.innerText = text.trim() || "";
}

function toggleScreenReader(force) {
    const enable = (force !== undefined) ? force : !isScreenReaderOn;
    isScreenReaderOn = enable;
    const btn = document.querySelector('button[onclick="toggleScreenReader()"]');
    if (btn) btn.setAttribute("aria-pressed", enable.toString());
    if (enable) {
        speak("Speak mode is on. Move your mouse over any text or button to hear it.")
        document.addEventListener("mouseover", screenReaderHandler);
        document.addEventListener("focusin", screenReaderHandler, true);
    } else {
        speak("Reading mode is off.")
        document.removeEventListener("mouseover", screenReaderHandler);
        document.removeEventListener("focusin", screenReaderHandler, true);
    }
}

function screenReaderHandler(event) {
    const el = event.target;
    let text = el.getAttribute("aria-label") || el.getAttribute("alt") || el.innerText || "";
    if (text.trim().length > 0) speak(text);
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = document.documentElement.lang || 'en';
    utterance.rate = 1;
    window.speechSynthesis.speak(utterance);
}

function moveCrosshair(event) {
    if (crosshairElement) {
        crosshairElement.style.left = `${event.clientX}px`;
        crosshairElement.style.top = `${event.clientY}px`;
    }
}

function increaseZoom() {
    targetZoomLevel += 0.1;
    if (targetZoomLevel > 2) targetZoomLevel = 2;
    smoothZoom();
    saveAccessibilityState();
}

function decreaseZoom() {
    targetZoomLevel -= 0.1;
    if (targetZoomLevel < 0.5) targetZoomLevel = 0.5;
    smoothZoom();
    saveAccessibilityState();
}

function smoothZoom() {
    cancelAnimationFrame(animationFrameId);
    function animate() {
        zoomLevel += (targetZoomLevel - zoomLevel) * 0.2;
        if (Math.abs(targetZoomLevel - zoomLevel) < 0.01) zoomLevel = targetZoomLevel;
        document.querySelectorAll("#menu, #content-wrapper").forEach(el => {
            el.style.transform = `scale(${zoomLevel})`;
            el.style.transformOrigin = "top left";
        });
        if (zoomLevel !== targetZoomLevel) {
            animationFrameId = requestAnimationFrame(animate);
        }
    }
    animate();
}

function toggleColorScheme() {
    const themes = ["high contrast", "protanopia", "tritanopia", "grayscale", null];
    let current = localStorage.getItem("accessibilityTheme");
    let nextIndex = (themes.indexOf(current) + 1) % themes.length;
    let nextTheme = themes[nextIndex];
    applyColorScheme(nextTheme);
    localStorage.setItem("accessibilityTheme", nextTheme);
    saveAccessibilityState();
}


function applyColorScheme(theme) {
    const html = document.documentElement;
    if (theme) {
        html.setAttribute("data-theme", theme); // ✅ 正确设置 data-theme
    } else {
        html.removeAttribute("data-theme");     // ✅ 移除属性时恢复默认
    }
    localStorage.setItem("accessibilityTheme", theme);
}


function resetColorScheme() {
    const html = document.documentElement;
    html.removeAttribute("data-theme");  // ✅ 这才是真正移除主题
    localStorage.removeItem("accessibilityTheme");
}


window.addEventListener("DOMContentLoaded", () => {
    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const stickyActive = localStorage.getItem("stickyMode") === "true";
    if (stickyActive) {
        toolbar.style.display = "flex";
        accessibilityBtn.style.display = "none";
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.display = "flex";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "160px";
        restoreAccessibilityState();
        const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
        if (stickyBtn) stickyBtn.classList.add("active");
    }
    accessibilityBtn.addEventListener("click", () => {
        toolbar.style.display = "flex";
        accessibilityBtn.style.display = "none";
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.display = "flex";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "160px";
    });
});
