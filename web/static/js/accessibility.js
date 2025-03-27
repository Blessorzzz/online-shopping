document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    // 默认隐藏工具栏
    toolbar.style.display = "none";

    // 检查 localStorage 是否开启了固定模式
    const stickyActive = localStorage.getItem("stickyMode") === "true";
    if (stickyActive) {
        // 固定模式开启时，显示工具栏、隐藏入口按钮
        toolbar.style.display = "flex";
        accessibilityBtn.style.display = "none";

        // 固定导航菜单位置 + 下移以防止遮挡
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.display = "flex";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "160px";

        // 恢复保存的缩放级别
        const savedZoom = localStorage.getItem("savedZoomLevel");
        if (savedZoom) {
            zoomLevel = parseFloat(savedZoom);
            targetZoomLevel = parseFloat(savedZoom);
            menu.style.transform = `scale(${zoomLevel})`;
            menu.style.transformOrigin = "top left";
            contentWrapper.style.transform = `scale(${zoomLevel})`;
            contentWrapper.style.transformOrigin = "top left";
        }
        // 激活固定模式按钮样式（高亮）
        const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
        if (stickyBtn) {
            stickyBtn.classList.add("active");
        }

        const infoButton = document.getElementById("accessibility-info-button");
        if (infoButton) {
            infoButton.addEventListener("click", function () {
                const url = this.getAttribute("data-href");
                if (url) window.location.href = url;
            });
        }

        // 恢复屏幕阅读器和十字线状态（如果之前启用过）
        const savedScreenReader = localStorage.getItem("screenReaderOn") === "true";
        if (savedScreenReader && !isScreenReaderOn) {
            isScreenReaderOn = true;
            document.addEventListener("mouseover", debouncedScreenReaderHandler);
            document.addEventListener("focusin", debouncedScreenReaderHandler, true);
            const srButton = document.querySelector('button[onclick="toggleScreenReader()"]');
            if (srButton) srButton.setAttribute("aria-pressed", "true");
            speak("Screen reader turned on");
        }
        const savedCrosshair = localStorage.getItem("crosshairOn") === "true";
        if (savedCrosshair && !isCrosshairModeActive) {
            isCrosshairModeActive = true;
            const body = document.body;
            body.classList.add("crosshair-mode-active");
            const crosshairBtn = document.querySelector('button[onclick="toggleCrosshair()"]');
            if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "true");
            if (!crosshairElement) {
                crosshairElement = document.createElement('div');
                crosshairElement.classList.add('crosshair');
                body.appendChild(crosshairElement);
            }
            document.addEventListener('mousemove', moveCrosshair);
        }
    }

    // 点击 Web Accessibility 按钮，显示工具栏及调整页面布局
    accessibilityBtn.addEventListener("click", function () {
        if (toolbar.style.display === "none") {
            toolbar.style.display = "flex";
            accessibilityBtn.style.display = "none"; // 只隐藏按钮本身，不隐藏整个 <li> 元素

            // 固定导航菜单位置 + 下移以防止遮挡
            menu.style.position = "fixed";
            menu.style.top = "103px";
            menu.style.height = "80px";
            menu.style.display = "flex";
            menu.style.zIndex = "10000";

            contentWrapper.style.paddingTop = "160px";  // 确保内容不会被遮挡
        }
    });

    // 针对固定模式下大字幕状态的恢复
    if (stickyActive) {
        const largeCaptionSetting = localStorage.getItem("largeCaptionEnabled");
        if (largeCaptionSetting === "true") {
            largeCaptionEnabled = true;
            const captionBox = document.getElementById("large-caption");
            captionBox.style.display = "block";
            // 检测是否为登录页（通过判断 .login-box 是否存在）
            const isLoginPage = document.querySelector('.login-box') !== null;
            if (!isLoginPage) {
                contentWrapper.style.paddingBottom = "120px";
            } else {
                contentWrapper.style.paddingBottom = "0";
            }
            document.addEventListener("mouseover", updateCaption);
        }
    }
});

// 全局变量声明
let zoomLevel = 1.0;
let targetZoomLevel = 1.0;
let animationFrameId = null;
let isScreenReaderOn = false;
let isCrosshairModeActive = false;
let crosshairElement = null;
let largeCaptionEnabled = false;

// 防抖函数
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// 创建防抖版本的屏幕阅读器处理函数，延迟300毫秒
const debouncedScreenReaderHandler = debounce(screenReaderHandler, 300);

function smoothZoom() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    function animate() {
        zoomLevel += (targetZoomLevel - zoomLevel) * 0.2;
        if (Math.abs(targetZoomLevel - zoomLevel) < 0.001) {
            zoomLevel = targetZoomLevel;
        } else {
            animationFrameId = requestAnimationFrame(animate);
        }
        const menu = document.getElementById("menu");
        const contentWrapper = document.getElementById("content-wrapper");
        requestAnimationFrame(() => {
            menu.style.transform = `scale(${zoomLevel})`;
            menu.style.transformOrigin = "top left";
            contentWrapper.style.transform = `scale(${zoomLevel})`;
            contentWrapper.style.transformOrigin = "top left";
        });
    }
    animate();
}

function increaseZoom() {
    if (targetZoomLevel < 1.8) {
        targetZoomLevel += 0.1;
        smoothZoom();
        // 固定模式开启时，更新保存的缩放值
        if (localStorage.getItem("stickyMode") === "true") {
            localStorage.setItem("savedZoomLevel", targetZoomLevel);
        }
    }
}

function decreaseZoom() {
    if (targetZoomLevel > 1.0) {
        targetZoomLevel -= 0.1;
        smoothZoom();
        if (localStorage.getItem("stickyMode") === "true") {
            localStorage.setItem("savedZoomLevel", targetZoomLevel);
        }
    }
}

// ---------------------- 颜色主题功能 ----------------------
let currentTheme = null;

function toggleColorScheme() {
    const themes = ['high-contrast', 'protanopia', 'tritanopia', 'grayscale', null];
    let savedTheme = localStorage.getItem('accessibilityTheme');
    let currentIndex = themes.indexOf(savedTheme);
    if (currentIndex === -1) {
        currentIndex = 0;
    }
    let nextIndex = (currentIndex + 1) % themes.length;
    let nextTheme = themes[nextIndex];
    console.log("Switching theme to:", nextTheme);
    applyColorScheme(nextTheme);
}

function applyColorScheme(theme) {
    const body = document.body;
    if (theme) {
        body.dataset.theme = theme;
        localStorage.setItem('accessibilityTheme', theme);
        document.documentElement.style.setProperty('--bg-color', getComputedStyle(body).getPropertyValue('--bg-color'));
        document.documentElement.style.setProperty('--text-color', getComputedStyle(body).getPropertyValue('--text-color'));
        document.documentElement.style.setProperty('--button-bg', getComputedStyle(body).getPropertyValue('--button-bg'));
        document.documentElement.style.setProperty('--button-text', getComputedStyle(body).getPropertyValue('--button-text'));
        document.documentElement.style.setProperty('--border-color', getComputedStyle(body).getPropertyValue('--border-color'));
        console.log("Applied theme:", theme);
        document.querySelectorAll("button, #menu, form.nav-right button, .product-card").forEach(el => {
            el.style.backgroundColor = getComputedStyle(body).getPropertyValue('--button-bg');
            el.style.color = getComputedStyle(body).getPropertyValue('--button-text');
            el.style.borderColor = getComputedStyle(body).getPropertyValue('--border-color');
        });
    } else {
        resetColorScheme();
    }
};

function resetColorScheme() {
    delete document.body.dataset.theme;
    localStorage.removeItem('accessibilityTheme');
    currentTheme = null;
    document.body.style.cssText = 'display: block;';
    document.documentElement.style.removeProperty('--bg-color');
    document.documentElement.style.removeProperty('--text-color');
    document.documentElement.style.removeProperty('--button-bg');
    document.documentElement.style.removeProperty('--button-text');
    document.documentElement.style.removeProperty('--border-color');
    document.querySelectorAll("button, #menu, form.nav-right button, .product-card").forEach(el => {
        el.style.backgroundColor = "";
        el.style.color = "";
        el.style.borderColor = "";
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const savedTheme = localStorage.getItem('accessibilityTheme');
    if (savedTheme) {
        applyColorScheme(savedTheme);
    }
});

// ---------------------- 固定模式功能 ----------------------
function toggleStickyMode() {
    const stickyActive = localStorage.getItem("stickyMode") === "true";
    const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
    if (!stickyActive) {
        localStorage.setItem("stickyMode", "true");
        localStorage.setItem("savedZoomLevel", zoomLevel);
        if (stickyBtn) stickyBtn.classList.add("active");
    } else {
        localStorage.removeItem("stickyMode");
        localStorage.removeItem("savedZoomLevel");
        if (stickyBtn) stickyBtn.classList.remove("active");
    }
}

// ---------------------- 重置功能（仅重置功能，保持工具栏显示） ----------------------
function resetAccessibility() {
    console.log("🔄 Resetting accessibility settings...");

    // 关闭屏幕阅读器功能
    if (isScreenReaderOn) {
        speak("Screen reader turned off");
        document.removeEventListener("mouseover", debouncedScreenReaderHandler);
        document.removeEventListener("focusin", debouncedScreenReaderHandler, true);
        const srButton = document.querySelector('button[onclick="toggleScreenReader()"]');
        if (srButton) srButton.setAttribute("aria-pressed", "false");
        isScreenReaderOn = false;
        localStorage.removeItem("screenReaderOn");
    }

    // 关闭十字线功能
    if (isCrosshairModeActive) {
        document.removeEventListener('mousemove', moveCrosshair);
        if (crosshairElement) {
            crosshairElement.remove();
            crosshairElement = null;
        }
        const crosshairBtn = document.querySelector('button[onclick="toggleCrosshair()"]');
        if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "false");
        isCrosshairModeActive = false;
        localStorage.removeItem("crosshairOn");
    }

    // 1) 重置缩放
    zoomLevel = 1.0;
    targetZoomLevel = 1.0;
    document.querySelectorAll("#menu, #content-wrapper").forEach(element => {
        element.style.transform = "scale(1)";
        element.style.transformOrigin = "top left";
    });

    // Reset 大光标功能（若启用）
    const body = document.body;
    if (body.classList.contains('large-cursor')) {
        body.classList.remove('large-cursor');
        const button = document.querySelector('button[onclick="toggleCursorMode()"]');
        if (button) button.setAttribute("aria-pressed", "false");
    }

    document.body.style.marginTop = "5px";
    // 2) 恢复“工具栏已开启”时的布局，让菜单避免被遮挡
    const toolbar = document.getElementById("accessibility-toolbar");
    toolbar.style.display = "flex";

    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    menu.style.position = "fixed";
    menu.style.top = "103px";
    menu.style.height = "80px";
    menu.style.display = "flex";
    menu.style.zIndex = "10000";
    contentWrapper.style.paddingTop = "160px";

    document.body.style.marginTop = "";
    
    // 3) 关闭“大字幕”功能，重置颜色主题
    const captionBox = document.getElementById("large-caption");
    captionBox.style.display = "none";
    document.removeEventListener("mouseover", updateCaption);
    largeCaptionEnabled = false;
    resetColorScheme();

    // 4) 清除固定模式状态
    localStorage.removeItem("stickyMode");
    localStorage.removeItem("savedZoomLevel");
    const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
    if (stickyBtn) stickyBtn.classList.remove("active");

    // 5) 回到页面顶部
    window.scrollTo({ top: 0, behavior: "smooth" });

    console.log("✅ Accessibility settings reset!");
}

// ---------------------- 光标模式功能 ----------------------
function toggleCursorMode() {
    const body = document.body;
    if (body.classList.contains('large-cursor')) {
        body.classList.remove('large-cursor');
        const button = document.querySelector('button[onclick="toggleCursorMode()"]');
        if (button) button.setAttribute("aria-pressed", "false");
    } else {
        body.classList.add('large-cursor');
        const button = document.querySelector('button[onclick="toggleCursorMode()"]');
        if (button) button.setAttribute("aria-pressed", "true");
    }
}

// ---------------------- 关闭工具栏功能（退出服务） ----------------------
function closeToolbar() {
    console.log("🔒 Closing accessibility toolbar...");
    resetAccessibility();
    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    toolbar.style.display = "none";
    accessibilityBtn.style.display = "block";
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    menu.style.top = "0";
    menu.style.position = "fixed";
    menu.style.display = "flex";
    menu.style.zIndex = "10000";
    document.body.style.marginTop = "10px";
    contentWrapper.style.paddingTop = "40px";
    window.scrollTo({ top: 0, behavior: "smooth" });
    console.log("✅ Accessibility toolbar closed!");
}

// ---------------------- 大字幕功能 ----------------------
function toggleLargeCaptions() {
    largeCaptionEnabled = !largeCaptionEnabled;
    localStorage.setItem("largeCaptionEnabled", largeCaptionEnabled);
    const captionBox = document.getElementById("large-caption");
    const contentWrapper = document.getElementById("content-wrapper");
    const isLoginPage = document.querySelector('.login-box') !== null;
    if (largeCaptionEnabled) {
        captionBox.style.display = "block";
        if (!isLoginPage) {
            contentWrapper.style.paddingBottom = "120px";
        } else {
            contentWrapper.style.paddingBottom = "0";
        }
        captionBox.innerText = "";
        document.addEventListener("mouseover", updateCaption);
    } else {
        captionBox.style.display = "none";
        contentWrapper.style.paddingBottom = "40px";
        document.removeEventListener("mouseover", updateCaption);
    }
}

function updateCaption(event) {
    if (!largeCaptionEnabled) return;
    const captionBox = document.getElementById("large-caption");
    let targetElement = event.target;
    let text = (
        targetElement.innerText?.trim() ||
        targetElement.getAttribute("alt")?.trim() ||
        targetElement.getAttribute("title")?.trim()
    );
    const structuralTags = ["BODY", "HTML", "DIV", "SECTION", "HEADER", "MAIN"];
    const isStructuralTag = structuralTags.includes(targetElement.tagName);
    const isInvisible = targetElement.offsetWidth === 0 || targetElement.offsetHeight === 0;
    if (!text || isStructuralTag || isInvisible) {
        captionBox.innerText = "";
        captionBox.classList.remove("multiline");
        return;
    }
    if (text.length > 100) {
        captionBox.classList.add("multiline");
        captionBox.style.whiteSpace = "";
        captionBox.style.height = "";
        captionBox.style.lineHeight = "";
        captionBox.style.overflowY = "";
    } else {
        captionBox.classList.remove("multiline");
        captionBox.style.whiteSpace = "nowrap";
        captionBox.style.height = "100px";
        captionBox.style.lineHeight = "90px";
        captionBox.style.overflowY = "hidden";
    }
    captionBox.innerText = text;
}

// ---------------------- 屏幕阅读器朗读功能 ----------------------
function screenReaderHandler(event) {
    const el = event.target;
    let text = el.getAttribute("aria-label") ||
               el.getAttribute("alt") ||
               el.innerText || "";
    text = text.trim();
    if (text.length > 0) {
        speak(text);
    }
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const lang = document.documentElement.lang || 'en';
    utterance.lang = lang;
    utterance.rate = 1;
    setTimeout(() => {
        window.speechSynthesis.speak(utterance);
    }, 100);
}

function toggleScreenReader() {
    isScreenReaderOn = !isScreenReaderOn;
    const btn = document.querySelector('button[onclick="toggleScreenReader()"]');
    if (btn) {
        btn.setAttribute("aria-pressed", isScreenReaderOn.toString());
    }
    if (isScreenReaderOn) {
        speak("Screen reader turned on");
        document.addEventListener("mouseover", debouncedScreenReaderHandler);
        document.addEventListener("focusin", debouncedScreenReaderHandler, true);
    } else {
        speak("Screen reader turned off");
        document.removeEventListener("mouseover", debouncedScreenReaderHandler);
        document.removeEventListener("focusin", debouncedScreenReaderHandler, true);
    }
    if (localStorage.getItem("stickyMode") === "true") {
         localStorage.setItem("screenReaderOn", isScreenReaderOn.toString());
    }
}

// ---------------------- 十字线功能 ----------------------
function toggleCrosshair() {
    const body = document.body;
    isCrosshairModeActive = !isCrosshairModeActive;
    const crosshairBtn = document.querySelector('button[onclick="toggleCrosshair()"]');
    if (isCrosshairModeActive) {
        body.classList.add("crosshair-mode-active");
        if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "true");
        crosshairElement = document.createElement('div');
        crosshairElement.classList.add('crosshair');
        body.appendChild(crosshairElement);
        document.addEventListener('mousemove', moveCrosshair);
    } else {
        body.classList.remove("crosshair-mode-active");
        if (crosshairBtn) crosshairBtn.setAttribute("aria-pressed", "false");
        if (crosshairElement) {
            crosshairElement.remove();
            crosshairElement = null;
        }
        document.removeEventListener('mousemove', moveCrosshair);
    }
    if (localStorage.getItem("stickyMode") === "true") {
         localStorage.setItem("crosshairOn", isCrosshairModeActive.toString());
    }
}

function moveCrosshair(event) {
    if (crosshairElement) {
        crosshairElement.style.left = `${event.clientX}px`;
        crosshairElement.style.top = `${event.clientY}px`;
    }
}

document.addEventListener("keydown", function (e) {
    if (!e.altKey) return;
    if (e.key.toLowerCase() === 'w') {
        toggleAccessibilityToolbar();
        return;
    }
    const toolbar = document.getElementById("accessibility-toolbar");
    if (toolbar && toolbar.style.display !== "flex") return;
    switch (e.key.toLowerCase()) {
        case 'r': toggleScreenReader(); break;
        case '=': increaseZoom(); break;
        case '-': decreaseZoom(); break;
        case 'm': toggleCursorMode(); break;
        case 'x': toggleCrosshair(); break;
        case 'l': toggleLargeCaptions(); break;
        case 'c': toggleColorScheme(); break;
        case 's': toggleStickyMode(); break;
        case '0': resetAccessibility(); break;
        case 'q': closeToolbar(); break;
        case 'h': window.location.href = "/accessibility-info/"; break;
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const infoButton = document.getElementById("accessibility-info-button");
    if (infoButton) {
        infoButton.addEventListener("click", function () {
            const url = this.getAttribute("data-href");
            if (url) window.location.href = url;
        });
    }
});

function toggleAccessibilityToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    if (!toolbar || !menu || !contentWrapper || !accessibilityBtn) return;
    const isHidden = toolbar.style.display === "none" || !toolbar.style.display;
    if (isHidden) {
        toolbar.style.display = "flex";
        accessibilityBtn.style.display = "none";
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "160px";
    } else {
        toolbar.style.display = "none";
        accessibilityBtn.style.display = "block";
        menu.style.position = "fixed";
        menu.style.top = "0";
        contentWrapper.style.paddingTop = "40px";
    }
}
