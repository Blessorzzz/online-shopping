document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    const stickyActive = localStorage.getItem("stickyMode") === "true";
    const isElderSticky = localStorage.getItem("isElderModeSticky") === "true";
    const openedByUser = localStorage.getItem("accessibilityToolbarOpen") === "true";
   
    const profile = localStorage.getItem("accessibilityProfile");

    const infoBtn = document.getElementById("accessibility-info-button");
    if (infoBtn) {
        infoBtn.addEventListener("click", function () {
            const href = infoBtn.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });
    }

    // 👉 新增：mobility 模式下强制禁止工具栏弹出
    if (profile === "mobility") {
        toolbar.style.display = "none";
        accessibilityBtn.style.display = "flex";
        return; // 🧠 提前退出，不再继续恢复其它辅助功能
    }
    
    const shouldRestoreToolbar = stickyActive || isElderSticky;
    
    if (shouldRestoreToolbar) {
        const searchBar = document.querySelector(".search-bar-wrapper");
        if (searchBar) {
            searchBar.style.position = "relative";
            //searchBar.style.top = "183px";
        }

    
        // ✅ 显示工具栏
        toolbar.style.display = "flex";
        if (openedByUser) {
            accessibilityBtn.style.display = "none";
        } else {
            accessibilityBtn.style.display = "flex";
        }
        
        //accessibilityBtn.style.display = "flex";

        // ✅ 布局调整
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.display = "flex";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "260px";

        const profile = localStorage.getItem("accessibilityProfile");
        const isElder = profile === "elder";

    if (searchBar) {
        if (!isElder) {
            searchBar.style.top = "183px"; // 只有非老年人模式才设置这个偏移
        } else {
            searchBar.style.top = "120px"; // 老年人模式恢复默认
        }
    }


        // ✅ 恢复屏幕阅读器
        const savedScreenReader = localStorage.getItem("screenReaderOn") === "true";
        if (savedScreenReader && !isScreenReaderOn) {
            isScreenReaderOn = true;
            document.addEventListener("mouseover", debouncedScreenReaderHandler);
            document.addEventListener("focusin", debouncedScreenReaderHandler, true);
            const srButton = document.querySelector('button[onclick="toggleScreenReader()"]');
            if (srButton) srButton.setAttribute("aria-pressed", "true");
            speak("Screen reader turned on");
        }

        // ✅ 恢复缩放
        const savedZoom = localStorage.getItem("savedZoomLevel");
        if (savedZoom) {
            zoomLevel = parseFloat(savedZoom);
            targetZoomLevel = zoomLevel;
            menu.style.transform = `scale(${zoomLevel})`;
            menu.style.transformOrigin = "top left";
            contentWrapper.style.transform = `scale(${zoomLevel})`;
            contentWrapper.style.transformOrigin = "top left";
            const searchBar = document.querySelector(".search-bar-wrapper");
            if (searchBar) {
                searchBar.style.transform = `scale(${zoomLevel})`;
                searchBar.style.transformOrigin = "top left";
            }
        }
        

        // ✅ 恢复十字线
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

        // ✅ 恢复颜色主题
        const savedTheme = localStorage.getItem('accessibilityTheme');
        if (savedTheme) {
            applyColorScheme(savedTheme);
        }

        // ✅ 恢复语速
        const savedRate = localStorage.getItem("speechRate");
        const savedMode = localStorage.getItem("speechRateMode");
        const btn = document.getElementById("speech-rate-btn");
        if (savedRate) {
            currentSpeechRate = parseFloat(savedRate);
        }
        if (savedMode) {
            speechRateMode = parseInt(savedMode);
            if (btn) {
                switch (speechRateMode) {
                    case 0: btn.innerHTML = "🕐 <small>Normal</small>"; break;
                    case 1: btn.innerHTML = "⏩ <small>Fast</small>"; break;
                    case 2: btn.innerHTML = "🐢 <small>Slow</small>"; break;
                }
                btn.setAttribute("aria-pressed", "true");
            }
        }

        // ✅ 修复：仅在大字幕明确开启时才恢复
        const largeCaptionSetting = localStorage.getItem("largeCaptionEnabled");
        if (largeCaptionSetting === "true") {
            largeCaptionEnabled = true;
            const captionBox = document.getElementById("large-caption");
            captionBox.style.display = "block";
            const isLoginPage = document.querySelector('.login-box') !== null;
            contentWrapper.style.paddingBottom = isLoginPage ? "0" : "120px";
            document.addEventListener("mouseover", updateCaption);
        } else {
            localStorage.removeItem("largeCaptionEnabled");
        }

    } else {
        // ❌ 没开启固定/工具栏，清除辅助功能状态
        toolbar.style.display = "none";
        accessibilityBtn.style.display = "flex";

        localStorage.removeItem("screenReaderOn");
        localStorage.removeItem("crosshairOn");
        localStorage.removeItem("largeCaptionEnabled");
        localStorage.removeItem("speechRate");
        localStorage.removeItem("speechRateMode");
        localStorage.removeItem("fontSizeLevel");
        localStorage.removeItem("accessibilityToolbarOpen");
        localStorage.removeItem("accessibilityTheme");
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    if (accessibilityBtn) {
        accessibilityBtn.addEventListener("click", toggleAccessibilityToolbar);
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
        const searchBar = document.querySelector(".search-bar-wrapper");
        requestAnimationFrame(() => {
            menu.style.transform = `scale(${zoomLevel})`;
            menu.style.transformOrigin = "top left";
            contentWrapper.style.transform = `scale(${zoomLevel})`;
            contentWrapper.style.transformOrigin = "top left";

            if (searchBar) {
                searchBar.style.transform = `scale(${zoomLevel})`;
                searchBar.style.transformOrigin = "top left";
            }
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
    document.body.removeAttribute("data-theme");
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
        // 开启 Sticky 模式
        localStorage.setItem("stickyMode", "true");
        localStorage.setItem("savedZoomLevel", zoomLevel);
        localStorage.setItem("accessibilityToolbarOpen", "true");
        if (stickyBtn) stickyBtn.classList.add("active");
        // 🟢 新增：保存当前启用的辅助功能状态，以便页面跳转后恢复
        if (isScreenReaderOn) {
            localStorage.setItem("screenReaderOn", "true");    // 保存屏幕阅读器状态
        }
        if (isCrosshairModeActive) {
            localStorage.setItem("crosshairOn", "true");       // 保存十字线状态
        }
        if (largeCaptionEnabled) {
            localStorage.setItem("largeCaptionEnabled", "true"); // 保存大字幕状态
        }
        // （语速和主题等在切换时已写入 localStorage，无需重复设置）
    } else {
        // 关闭 Sticky 模式
        localStorage.removeItem("stickyMode");
        localStorage.removeItem("savedZoomLevel");
        localStorage.removeItem("accessibilityToolbarOpen"); // ✅ 加这一行
        if (stickyBtn) stickyBtn.classList.remove("active");
        // 🟢 新增：清除所有辅助功能状态，避免页面跳转后残留
        localStorage.removeItem("screenReaderOn");       // 清除屏幕阅读器开启状态
        localStorage.removeItem("largeCaptionEnabled");  // 清除大字幕开启状态
        localStorage.removeItem("crosshairOn");          // 清除十字线开启状态
        localStorage.removeItem("speechRate");           // 清除语速设置
        localStorage.removeItem("speechRateMode");       // 清除语速模式（正常/慢速）
        localStorage.removeItem("fontSizeLevel");        // 清除字体大小级别（若有）
    }
}



// ---------------------- 重置功能（仅重置功能，保持工具栏显示） ----------------------
function resetAccessibility() {
    console.log("🔄 Resetting accessibility settings...");

    // 关闭屏幕阅读器功能（但如果是老年人模式固定状态，不关闭）
    if (isScreenReaderOn && localStorage.getItem("isElderModeSticky") !== "true") {
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
    document.querySelectorAll("#menu, #content-wrapper, .search-bar-wrapper").forEach(element => {
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

    // ========== 这部分是重点改动：根据「profile + 是否手动打开」来决定是否隐藏 ==========

    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    const profile = localStorage.getItem("accessibilityProfile");
    // 表示「根据当前模式」应不应该默认隐藏
    const shouldHideByProfile = !profile || ["default", "elder", "mobility"].includes(profile);
    // 表示「用户是否手动打开过工具栏」
    const userManuallyOpened = localStorage.getItem("accessibilityToolbarOpen") === "true";

    // 只有在“模式本该隐藏” AND “用户没手动点开过”时才真的隐藏
    if (shouldHideByProfile && !userManuallyOpened) {
        const searchBar = document.querySelector(".search-bar-wrapper");
        if (searchBar) {
            searchBar.style.top = "60px"; // 或 searchBar.style.top = "";
        }

        toolbar.style.display = "none";
        // 恢复正常布局
        menu.style.position = "";
        menu.style.top = "";
        menu.style.height = "";
        if (typeof adjustContentPadding === "function") {
            adjustContentPadding();
        } else {
            contentWrapper.style.paddingTop = "120px"; // 你的默认值
        }
    } else {
        // 否则保持（或恢复）打开
        toolbar.style.display = "flex";
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.display = "flex";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "260px";
        const searchBar = document.querySelector(".search-bar-wrapper");
        if (searchBar) {
            searchBar.style.position = "relative";
            searchBar.style.top = "183px";
        }

    }

    // ========== 以上是主要改动 ==========

    // 3) 关闭“大字幕”功能，重置颜色主题
    const captionBox = document.getElementById("large-caption");
    captionBox.style.display = "none";
    document.removeEventListener("mouseover", updateCaption);
    largeCaptionEnabled = false;
    resetColorScheme();

    const mobilityStyle = document.getElementById("mobility-mode-style");
    if (mobilityStyle) {
        mobilityStyle.remove();
    }

    // 4) 清除固定模式状态（Sticky等）
    localStorage.removeItem("stickyMode");
    localStorage.removeItem("savedZoomLevel");
    const stickyBtn = document.querySelector("#accessibility-toolbar button[onclick='toggleStickyMode()']");
    if (stickyBtn) stickyBtn.classList.remove("active");

    // 5) 回到页面顶部
    window.scrollTo({ top: 0, behavior: "smooth" });

    currentSpeechRate = 1.0;
    speechRateMode = 0;
    localStorage.removeItem("speechRate");
    localStorage.removeItem("speechRateMode");
    const speechBtn = document.getElementById("speech-rate-btn");
    if (speechBtn) {
        speechBtn.setAttribute("aria-pressed", "false");
        speechBtn.innerHTML = "🕐 <small>Normal</small>";
    }

    // 🧼 清除 mobility 模式设置的行内样式
    document.querySelectorAll("button, a, input[type='submit']").forEach(el => {
        el.style.padding = "";
        el.style.fontSize = "";
    });
    document.body.classList.remove("mobility-mode");

    console.log("✅ Accessibility settings reset!");
    if (typeof adjustContentPadding === "function") {
        adjustContentPadding();  // 自动计算 menu + searchBar 高度
    }    
    
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
    resetAccessibility(); // ✅ 这句会带回 260px 问题

    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const searchBar = document.querySelector(".search-bar-wrapper");

    toolbar.style.display = "none";
    accessibilityBtn.style.display = "flex";
    menu.style.top = "0";
    menu.style.position = "fixed";
    menu.style.display = "flex";
    menu.style.zIndex = "10000";

    // 恢复 padding 和 margin
    if (typeof adjustContentPadding === "function") {
        adjustContentPadding();
    } else {
        contentWrapper.style.paddingTop = "0px";
        document.body.style.marginTop = "0px";
    }

    // ✅ 兜底强制清除 paddingTop
    contentWrapper.style.paddingTop = "80px";

    // ✅ 恢复搜索栏位置
    if (searchBar) {
        searchBar.style.top = "60px";
    }

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
    utterance.rate = currentSpeechRate || 1;
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
        case 't': toggleSpeechRate(); break;
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
    const savedRate = localStorage.getItem("speechRate");
    const savedMode = localStorage.getItem("speechRateMode");
    const btn = document.getElementById("speech-rate-btn");

    if (savedRate) {
        currentSpeechRate = parseFloat(savedRate);
    }
    if (savedMode) {
        speechRateMode = parseInt(savedMode);
        if (btn) {
            switch (speechRateMode) {
                case 0:
                    btn.innerHTML = "🕐 <small>Normal</small>";
                    break;
                case 1:
                    btn.innerHTML = "⏩ <small>Fast</small>";
                    break;
                case 2:
                    btn.innerHTML = "🐢 <small>Slow</small>";
                    break;
            }
            btn.setAttribute("aria-pressed", "true");
        }
    }
});

function toggleAccessibilityToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const searchBar = document.querySelector(".search-bar-wrapper"); // ✅ 新增

    if (!toolbar || !menu || !contentWrapper || !accessibilityBtn) return;
    const isHidden = toolbar.style.display === "none" || !toolbar.style.display;

    if (isHidden) {
        toolbar.style.display = "flex";
        accessibilityBtn.style.display = "none";
        menu.style.position = "fixed";
        menu.style.top = "103px";
        menu.style.height = "80px";
        menu.style.zIndex = "10000";
        contentWrapper.style.paddingTop = "260px";
        localStorage.setItem("isElderModeSticky", "false");
        localStorage.setItem("accessibilityToolbarOpen", "true");

       // ✅ 设置搜索栏位置避免被遮挡
       if (searchBar) {
           searchBar.style.position = "relative";
           const profile = localStorage.getItem("accessibilityProfile");
           const isElder = (profile === "elder");

           //searchBar.style.top = "183px"; 
           if (!isElder) {
               searchBar.style.top = "183px";
           } else {
               // 老年人模式就贴近菜单栏，不要 183px
               searchBar.style.top = "200px";
           }
       }

    } else {
        toolbar.style.display = "none";
        accessibilityBtn.style.display = "block";
        menu.style.position = "fixed";
        menu.style.top = "0";
        contentWrapper.style.paddingTop = "0px";
        localStorage.removeItem("accessibilityToolbarOpen");

       // ✅ 恢复搜索栏原始位置
       if (searchBar) {
           searchBar.style.top = "60px"; // 或清空：searchBar.style.top = "";
       }
    }
}



let currentSpeechRate = 1.0;
let speechRateMode = 0; // 0 = normal, 1 = fast, 2 = slow

function toggleSpeechRate() {
    speechRateMode = (speechRateMode + 1) % 3;
    const btn = document.getElementById("speech-rate-btn");

    switch (speechRateMode) {
        case 0:
            currentSpeechRate = 1.0;
            if (btn) btn.innerHTML = "🕐 <small>Normal</small>";
            speak("Speech rate set to normal");
            break;
        case 1:
            currentSpeechRate = 1.75;
            if (btn) btn.innerHTML = "⏩ <small>Fast</small>";
            speak("Speech rate set to fast");
            break;
        case 2:
            currentSpeechRate = 0.65;
            if (btn) btn.innerHTML = "🐢 <small>Slow</small>";
            speak("Speech rate set to slow");
            break;
    }

    localStorage.setItem("speechRate", currentSpeechRate);
    localStorage.setItem("speechRateMode", speechRateMode);
    if (btn) btn.setAttribute("aria-pressed", "true");
}

function handleProfileSelect(value) {
    if (value) {
        applyAccessibilityProfile(value);
    }
}


  
//个性化无障碍
document.addEventListener("DOMContentLoaded", function () {
    const savedProfile = localStorage.getItem("accessibilityProfile");
    const select = document.getElementById("user-profile-select");
    if (savedProfile && select) {
      select.value = savedProfile;
      applyAccessibilityProfile(savedProfile);
    }
  });

  
function handleProfileSelect(mode) {
    if (!mode) return;
    localStorage.setItem("accessibilityProfile", mode);
    applyAccessibilityProfile(mode);
}

function applyAccessibilityProfile(mode) {
    resetAccessibility(); // 重置之前状态

    const captionBox = document.getElementById("large-caption");
    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    switch (mode) {
        case "elder":
            enableElderMode();
            break;

        case "default":
        default:
            if (toolbar && accessibilityBtn) {
                toolbar.style.display = "none";
                accessibilityBtn.style.display = "flex";
            }

            if (menu && contentWrapper) {
                menu.style.position = "";
                menu.style.top = "";
                menu.style.height = "";
                contentWrapper.style.paddingTop = "80px"; // ✅ 关键
                if (typeof adjustContentPadding === 'function') {
                    adjustContentPadding();
                }
            }

            // 清除所有缓存
            localStorage.removeItem("accessibilityProfile");
            localStorage.removeItem("isElderModeSticky");
            localStorage.removeItem("fontSizeLevel");
            localStorage.removeItem("accessibilityTheme");
            localStorage.removeItem("screenReaderOn");
            localStorage.removeItem("speechRate");
            localStorage.removeItem("speechRateMode");
            localStorage.removeItem("largeCaptionEnabled");
            localStorage.removeItem("savedZoomLevel");
            localStorage.removeItem("crosshairOn");
            localStorage.removeItem("accessibilityToolbarOpen");

            resetAccessibility();
            document.documentElement.classList.remove("elder-theme");

            if (isScreenReaderOn) {
                isScreenReaderOn = false;
                document.removeEventListener("mouseover", debouncedScreenReaderHandler);
                document.removeEventListener("focusin", debouncedScreenReaderHandler, true);
                const srButton = document.querySelector('button[onclick="toggleScreenReader()"]');
                if (srButton) srButton.setAttribute("aria-pressed", "false");
            }

            document.documentElement.style.fontSize = "";
            document.body.removeAttribute("data-theme");
            document.documentElement.removeAttribute("data-theme");
            resetColorScheme();

            if (captionBox) {
                captionBox.style.display = "none";
                document.removeEventListener("mouseover", updateCaption);
            }

            speak("Default mode restored");
            break;

        case "mobility":
            localStorage.setItem("accessibilityProfile", "mobility");

            // ✅ 设置字体放大
            fontSizeLevel = 1.35;
            localStorage.setItem("fontSizeLevel", fontSizeLevel);
            applyFontSize(); // <-- 正确执行放大逻辑

            // ✅ 清除颜色
            document.documentElement.classList.remove("elder-theme");
            document.body.removeAttribute("data-theme");
            document.documentElement.removeAttribute("data-theme");
            resetColorScheme();
            localStorage.removeItem("accessibilityTheme");
            localStorage.removeItem("isElderModeSticky");

            // ✅ 关闭字幕
            if (captionBox) {
                captionBox.style.display = "none";
                document.removeEventListener("mouseover", updateCaption);
            }

            if (toolbar && accessibilityBtn) {
                toolbar.style.display = "none";
                accessibilityBtn.style.display = "flex";
            }

            document.body.classList.add("mobility-mode");

            const style = document.createElement("style");
            style.innerHTML = `
                *:focus {
                    outline: 3px solid #007bff !important;
                    outline-offset: 4px;
                    border-radius: 6px;
                }
            `;
            style.id = "mobility-mode-style";
            document.head.appendChild(style);
            break;
        }  
}


  function enableElderMode() {
    //localStorage.setItem("isElderModeSticky", "true");

    // ✅ 字体变大
    fontSizeLevel = 1.5;
    document.documentElement.style.fontSize = `${fontSizeLevel}em`;
    localStorage.setItem("fontSizeLevel", fontSizeLevel);

    // ✅ 高对比色主题
    applyColorScheme("high-contrast");
    localStorage.setItem("accessibilityTheme", "high-contrast");


    // ✅ 慢速语音提示
    currentSpeechRate = 0.8;
    speechRateMode = 2;
    localStorage.setItem("speechRate", currentSpeechRate);
    localStorage.setItem("speechRateMode", speechRateMode);

    // ✅ 自动启用屏幕阅读器
    if (!isScreenReaderOn) {
        isScreenReaderOn = true;
        localStorage.setItem("screenReaderOn", "true");
        document.addEventListener("mouseover", debouncedScreenReaderHandler);
        document.addEventListener("focusin", debouncedScreenReaderHandler, true);
        const srButton = document.querySelector('button[onclick="toggleScreenReader()"]');
        if (srButton) srButton.setAttribute("aria-pressed", "true");
        speak("Screen reader turned on");
    }

    // ✅ 语音反馈提示
    speak("Elder mode enabled");

    // 显式关闭工具栏
    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    if (toolbar && accessibilityBtn) {
        toolbar.style.display = "none";
        accessibilityBtn.style.display = "flex";
    }

    // ✅ 恢复布局，避免商品被遮挡   
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    if (menu && contentWrapper) {
        menu.style.position = "";
        menu.style.top = "";
        menu.style.height = "";
        if (typeof adjustContentPadding === 'function') {
            adjustContentPadding();
        }
        
    }
    const searchBar = document.querySelector(".search-bar-wrapper");
    if (searchBar) {
        searchBar.style.top = "60px"; // ✅ 恢复正常定位
    }


    document.documentElement.classList.add("elder-theme");
  }
  
  
  




















































// --------------------- 语音搜索功能 ---------------------
// 将扩展关键词添加到表单
function addExpandedKeywordsToForm(form, expandedKeywords) {
    if (!expandedKeywords || expandedKeywords.length === 0) return;
    
    // 检查是否已存在扩展关键词隐藏字段
    let expandedInput = form.querySelector('input[name="expanded_keywords"]');
    
    // 如果不存在，创建一个
    if (!expandedInput) {
        expandedInput = document.createElement('input');
        expandedInput.type = 'hidden';
        expandedInput.name = 'expanded_keywords';
        form.appendChild(expandedInput);
    }
    
    // 设置值
    expandedInput.value = expandedKeywords.join(',');
}

// 新增：显示语音识别过程详情
    // 关键词展示
function showRecognitionDetails(data) {
    // 获取详情区域元素
    const detailsContainer = document.getElementById('voice-recognition-details');
    if (!detailsContainer) return;
    
    // 填充内容
    document.getElementById('original-text').textContent = data.originalText || '';
    
    // 分词结果
    const segmentText = data.cleanedText ? data.cleanedText.split('').join(' ') : '';
    document.getElementById('segmented-text').textContent = segmentText;
    
    // 关键词展示
    const keywordsContainer = document.getElementById('keywords');
    keywordsContainer.innerHTML = '';
    if (data.keywords && data.keywords.length > 0) {
        keywordsContainer.innerHTML = `<div class="keyword-priority">优先搜索：</div>`;
        data.keywords.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            keywordsContainer.appendChild(tag);
        });
    } else {
        keywordsContainer.textContent = '未提取到关键词';
    }
    
    // 扩展关键词展示
    const expandedKeywordsContainer = document.getElementById('expanded-keywords');
    expandedKeywordsContainer.innerHTML = '';
    if (data.expandedKeywords && data.expandedKeywords.length > 0) {
        expandedKeywordsContainer.innerHTML = `<div class="keyword-priority">次优先搜索：</div>`;
        data.expandedKeywords.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag expanded-keyword-tag';
            tag.textContent = keyword;
            expandedKeywordsContainer.appendChild(tag);
        });
    } else {
        expandedKeywordsContainer.textContent = '未找到扩展关键词';
    }
    
    // 最终查询
    document.getElementById('final-query').textContent = data.searchQuery || '';
    
    // 显示详情容器
    detailsContainer.style.display = 'block';
    
    // 添加关闭按钮事件
    const closeButton = document.getElementById('close-recognition-details');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            detailsContainer.style.display = 'none';
        });
    }
}

// --------------------- 语音搜索功能 ---------------------
document.addEventListener("DOMContentLoaded", function() {
    // 获取DOM元素
    const voiceButton = document.getElementById("voice-search-button");
    const searchInput = document.getElementById("search-input");
    const searchForm = document.getElementById("search-form");
    const statusElement = document.getElementById("voice-status");
    
    // 检查必要元素是否存在
    if (!voiceButton || !searchInput || !searchForm) {
        console.error("未找到语音搜索所需的DOM元素");
        return;
    }
    
    // 初始化变量
    let recognition = null;
    let isListening = false;
    
    // 检查浏览器支持
    const isSpeechRecognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    
    if (!isSpeechRecognitionSupported) {
        console.warn("此浏览器不支持语音识别功能");
        voiceButton.style.display = "none";
        return;
    }
    
    // 添加点击事件
    voiceButton.addEventListener("click", toggleVoiceRecognition);
    
    // 切换语音识别状态
    function toggleVoiceRecognition() {
        if (isListening) {
            stopVoiceRecognition();
        } else {
            startVoiceRecognition();
        }
    }
    
    // 开始语音识别
    function startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        // 配置语音识别
        recognition.lang = document.documentElement.lang || 'zh-CN'; // 使用页面语言或默认为中文
        recognition.interimResults = true; // 获取临时结果
        recognition.continuous = false; // 单次识别
        
        // 启动识别
        try {
            recognition.start();
            isListening = true;
            
            // 更新UI
            voiceButton.classList.add("listening");
            updateVoiceStatus(getTranslatedText('正在聆听...'), false);
            
            // 隐藏之前的详情显示
            const detailsContainer = document.getElementById('voice-recognition-details');
            if (detailsContainer) {
                detailsContainer.style.display = 'none';
            }
            
            // 如果开启了无障碍模式，记录到控制台
            if (localStorage.getItem("stickyMode") === "true") {
                console.log("语音识别已启动");
            }
        } catch (error) {
            console.error("启动语音识别失败:", error);
            updateVoiceStatus(getTranslatedText('启动语音识别失败，请重试。'), true);
        }
        
        // 设置事件处理
        setupRecognitionEvents();
    }
    
    // 停止语音识别
    function stopVoiceRecognition() {
        if (recognition && isListening) {
            recognition.stop();
            isListening = false;
            voiceButton.classList.remove("listening");
        }
    }
    
    // 设置识别事件
    function setupRecognitionEvents() {
        // 处理结果
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // 显示临时结果
            if (interimTranscript) {
                updateVoiceStatus(getTranslatedText('正在识别: ') + interimTranscript, false);
                
                // 如果开启了无障碍模式和大字幕功能，显示在大字幕中
                if (localStorage.getItem("stickyMode") === "true" && localStorage.getItem("largeCaptionEnabled") === "true") {
                    const captionBox = document.getElementById("large-caption");
                    if (captionBox) {
                        captionBox.innerText = interimTranscript;
                    }
                }
                
                // 记录到控制台
                console.log("临时识别结果:", interimTranscript);
            }
            
            // 处理最终结果
            if (finalTranscript) {
                // 清理识别文本，去除标点符号
                const cleanedText = cleanRecognitionText(finalTranscript);
                
                // 智能分析搜索意图
                analyzeSearchIntent(cleanedText).then(searchData => {
                    // 填入搜索框并更新显示
                    searchInput.value = searchData.searchQuery;
                    
                    // 记录分析过程到控制台
                    console.log("原始识别结果:", finalTranscript);
                    console.log("清理后结果:", cleanedText);
                    console.log("提取的关键词:", searchData.keywords);
                    console.log("扩展的关键词:", searchData.expandedKeywords);
                    console.log("最终搜索查询:", searchData.searchQuery);
                    
                    // 显示状态消息
                    let statusMessage = getTranslatedText('已分析: ') + cleanedText;
                    if (searchData.keywords.length > 0) {
                        statusMessage += '<br>' + getTranslatedText('关键词: ') + searchData.keywords.join(', ');
                    }
                    updateVoiceStatus(statusMessage, false, true);
                    
                    // 显示详细的识别过程
                    showRecognitionDetails({
                        originalText: finalTranscript,
                        cleanedText: cleanedText,
                        keywords: searchData.keywords,
                        expandedKeywords: searchData.expandedKeywords,
                        searchQuery: searchData.searchQuery
                    });
                    
         // 设置序列搜索界面而不是直接提交搜索
            setupSequentialSearch(searchData);
        }).catch(error => {
                    console.error("分析搜索意图失败:", error);
                    // 出错时使用原始清理后的文本
                    searchInput.value = cleanedText;
                    updateVoiceStatus(getTranslatedText('无法分析语义，使用原文搜索'), true);
                    
                    // 显示基本的识别过程
                    showRecognitionDetails({
                        originalText: finalTranscript,
                        cleanedText: cleanedText,
                        keywords: [],
                        expandedKeywords: [],
                        searchQuery: cleanedText
                    });
                    
                    // 延迟提交搜索
                    setTimeout(() => {
                        searchForm.submit();
                    }, 2000);
                });
            }
        };
        
        // 识别结束
        recognition.onend = function() {
            isListening = false;
            voiceButton.classList.remove("listening");
            console.log("语音识别已结束");
        };
        
        // 错误处理
        recognition.onerror = function(event) {
            isListening = false;
            voiceButton.classList.remove("listening");
            
            let errorMessage = '';
            switch(event.error) {
                case 'no-speech':
                    errorMessage = getTranslatedText('未检测到语音，请再次尝试。');
                    break;
                case 'audio-capture':
                    errorMessage = getTranslatedText('无法访问麦克风，请检查设备连接。');
                    break;
                case 'not-allowed':
                    errorMessage = getTranslatedText('麦克风访问被拒绝，请授予权限。');
                    break;
                default:
                    errorMessage = getTranslatedText('语音识别错误: ') + event.error;
            }
            
            updateVoiceStatus(errorMessage, true);
            console.error(errorMessage);
        };
    }
    
    // 更新语音状态显示
    function updateVoiceStatus(message, isError = false, isHTML = false) {
        if (!statusElement) return;
        
        if (isHTML) {
            statusElement.innerHTML = message;
        } else {
            statusElement.textContent = message;
        }
        
        statusElement.style.display = "block";
        
        if (isError) {
            statusElement.classList.add("error");
        } else {
            statusElement.classList.remove("error");
        }
        
        // 自动隐藏非错误消息
        if (!isError && !message.includes(getTranslatedText('正在识别'))) {
            setTimeout(() => {
                statusElement.style.display = "none";
            }, 4000); // 增加显示时间，让用户能看清分析结果
        }
    }
    
    // 清理识别文本，去除标点符号和其他不需要的字符
    function cleanRecognitionText(text) {
        if (!text) return '';
        
        // 去除常见的中文标点符号和英文标点符号
        const punctuationPattern = /[。，、；：？！""''（）【】《》…—～・,.;:?!'"()\[\]{}<>]/g;
        
        // 替换标点符号为空字符
        let cleaned = text.replace(punctuationPattern, '');
        
        // 去除多余空格并修剪
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        
        // 特殊情况处理：如果结果是空的，返回原始文本但去除标点
        if (!cleaned && text) {
            return text.replace(punctuationPattern, '');
        }
        
        return cleaned;
    }
    
    // 获取翻译文本（如果有Django翻译功能的话）
    function getTranslatedText(text) {
        // 如果页面上有Django的翻译功能，可以使用它
        if (typeof gettext === 'function') {
            return gettext(text);
        }
        return text;
    }
});

// 分析搜索意图，提取关键词并扩展 
async function analyzeSearchIntent(text) {
    // 创建返回结果对象
    const result = {
        originalText: text,
        keywords: [],
        expandedKeywords: [],
        searchQuery: text, // 默认使用原始文本
        searchMode: 'sequential' // 序列搜索模式
    };
    
    try {
        console.log("分析文本:", text);
        
        // 调用后端API提取关键词
        const response = await fetch('/api/extract-keywords/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                text: text
            })
        });
        
        const data = await response.json();
        console.log("后端返回数据:", data);
        
        if (data.success && data.keywords && data.keywords.length > 0) {
            // 使用后端提取的关键词
            result.keywords = data.keywords;
            console.log("提取的关键词:", result.keywords);
            
            // 使用后端提供的扩展关键词
            if (data.expanded_keywords && data.expanded_keywords.length > 0) {
                result.expandedKeywords = data.expanded_keywords;
            }
            console.log("扩展的关键词:", result.expandedKeywords);
            
            // 使用第一个关键词作为初始搜索
            result.searchQuery = result.keywords[0];
            
            // 将所有关键词顺序保存下来供界面展示
            result.allSearchTerms = [
                ...result.keywords.map(k => ({ term: k, type: 'original' })),
                ...result.expandedKeywords.map(k => ({ term: k, type: 'expanded' }))
            ];
            
            // 记录当前搜索的索引，从0开始
            result.currentSearchIndex = 0;
        } else {
            // 后端未能提取关键词，使用简单处理
            console.log("后端未能提取关键词，使用简单处理");
            
            // 移除问句标记和常见问句前缀
            let processedText = text
                .replace(/[?？吗呢啊么]$/, '')
                .replace(/^(请问|请给我|你能|能否|能不能)/, '');
            
            // 如果有"推荐"字样，尝试提取推荐对象
            if (processedText.includes('推荐')) {
                const parts = processedText.split('推荐');
                if (parts.length > 1 && parts[1].trim()) {
                    processedText = parts[1].trim().replace(/[?？吗呢啊么]$/, '');
                }
            }
            
            result.searchQuery = processedText;
            result.keywords = [processedText];
            result.allSearchTerms = [{ term: processedText, type: 'original' }];
            result.currentSearchIndex = 0;
        }
        
        console.log("最终搜索查询:", result.searchQuery);
        return result;
        
    } catch (error) {
        console.error("分析搜索意图错误:", error);
        
        // 如果API调用失败，回退到简单处理
        const processedText = text.replace(/[?？吗呢啊么]$/, '');
        result.searchQuery = processedText;
        result.keywords = [processedText];
        result.allSearchTerms = [{ term: processedText, type: 'original' }];
        result.currentSearchIndex = 0;
        
        return result;
    }
}

// 辅助函数：获取CSRF令牌
function getCSRFToken() {
    const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenElement ? tokenElement.value : '';
}
// 添加新函数：用于处理序列搜索
let searchData = {
    allSearchTerms: [],
    currentSearchIndex: -1,
    originalText: '',
    keywords: [],
    expandedKeywords: [],
    searchQuery: '',
    searchMode: ''
};
// 新功能：检测当前是否在支持序列搜索的页面上
function isSequentialSearchEnabledPage() {
    const path = window.location.pathname;
    return path === '/' || path.includes('/products/');
  }
// 新功能：保存搜索状态到sessionStorage
sessionStorage.setItem('pendingSequentialSearch', JSON.stringify(searchData));

// 新功能：页面加载时检查并恢复搜索状态
document.addEventListener("DOMContentLoaded", function() {
  // 检查是否从产品详情页返回继续序列搜索
  const urlParams = new URLSearchParams(window.location.search);
  const sequentialReturn = urlParams.get('sequential_return');
  
  if (sequentialReturn === 'true' && sessionStorage.getItem('pendingSequentialSearch')) {
    try {
      const savedSearchData = JSON.parse(sessionStorage.getItem('pendingSequentialSearch'));
      setupSequentialSearch(savedSearchData);
    } catch (e) {
      console.error('Failed to restore sequential search:', e);
    }
  }
});
// 新功能：在产品详情页添加返回按钮
if (window.location.pathname.includes('/products/')) {
    const returnButton = document.createElement('button');
    returnButton.id = 'return-to-search';
    returnButton.className = 'return-button';
    returnButton.innerHTML = '&larr; 返回继续搜索';
    returnButton.addEventListener('click', () => {
      window.location.href = '/?sequential_return=true';
    });
    
    // 在内容顶部插入返回按钮
    contentWrapper.insertBefore(returnButton, contentWrapper.firstChild);
  }

// 找到 setupSequentialSearch 函数并替换为以下内容
function setupSequentialSearch(searchDataInput) {
    searchData = searchDataInput;
    if (!isSequentialSearchEnabledPage()) {
        // 如果不在支持的页面上，保存搜索数据并重定向到首页
        sessionStorage.setItem('pendingSequentialSearch', JSON.stringify(searchData));
        window.location.href = '/';
        return;
      }
    // 处理传入的数据
    if (typeof searchDataInput === 'object' && searchDataInput !== null) {
        Object.assign(searchData, {
            allSearchTerms: searchDataInput.allSearchTerms || [],
            currentSearchIndex: 0,
            originalText: searchDataInput.originalText || '',
            keywords: searchDataInput.keywords || [],
            expandedKeywords: searchDataInput.expandedKeywords || [],
            searchQuery: searchDataInput.searchQuery || '',
            searchMode: searchDataInput.searchMode || 'sequential'
        });
    } else {
        return;
    }

    // 获取DOM元素
    const searchInput = document.getElementById("search-input");
    const searchForm = document.getElementById("search-form");
    const detailsContainer = document.getElementById('voice-recognition-details');
    
    // 创建或获取序列搜索容器
    let sequentialSearchContainer = document.getElementById('sequential-search-container');
    if (!sequentialSearchContainer) {
        sequentialSearchContainer = document.createElement('div');
        sequentialSearchContainer.id = 'sequential-search-container';
        sequentialSearchContainer.className = 'sequential-search mt-3';
        sequentialSearchContainer.classList.add('sticky-search-container');
        
        if (detailsContainer && detailsContainer.style.display !== 'none') {
            detailsContainer.appendChild(sequentialSearchContainer);
        } else {
            document.body.insertBefore(sequentialSearchContainer, document.body.firstChild);
        }
    }
    
    sequentialSearchContainer.innerHTML = '';
    
    // 创建头部
    const headerDiv = document.createElement('div');
    headerDiv.className = 'sequential-search-header';
    headerDiv.innerHTML = `
        <h6>按顺序搜索以下关键词:</h6>
        <div class="controls-wrapper">
            <button type="button" id="close-sequential-search" class="btn btn-sm btn-outline-danger close-btn">
                <i class="fa fa-times"></i> 关闭
            </button>
        </div>
    `;
    sequentialSearchContainer.appendChild(headerDiv);
    
    // 创建关键词列表
    const termsList = document.createElement('div');
    termsList.className = 'sequential-terms-list';
    
    searchData.allSearchTerms.forEach((item, index) => {
        const termEl = document.createElement('div');
        termEl.className = `search-term-item ${item.type === 'expanded' ? 'expanded' : 'original'} ${index === searchData.currentSearchIndex ? 'current' : ''}`;
        termEl.setAttribute('data-index', index);
        termEl.innerHTML = `
            <span class="term-text">${item.term}</span>
            ${index === searchData.currentSearchIndex ? '<span class="current-indicator">当前</span>' : ''}
        `;
        
        // 修改点击事件，使用 AJAX
        termEl.addEventListener('click', async () => {
            searchData.currentSearchIndex = index;
            if (searchInput) {
                searchInput.value = item.term;
            }
            updateSequentialSearchUI();
            
            const productListContainer = document.getElementById('product-list-container');
            if (!productListContainer) {
                console.error("未找到产品列表容器");
                return;
            }
            
            productListContainer.innerHTML = '<p>加载产品中...</p>';
            
            try {
                const response = await fetch(`/api/ajax-search-products/?q=${encodeURIComponent(item.term)}`);
                if (!response.ok) {
                    throw new Error(`HTTP错误！状态码: ${response.status}`);
                }
                const data = await response.json();
                
                productListContainer.innerHTML = data.html;
                // 重新渲染星级评分
                document.querySelectorAll('.star-rating').forEach(element => {
                    let rating = parseFloat(element.getAttribute('data-rating'));
                    let fullStars = Math.floor(rating);
                    let hasHalfStar = rating % 1 >= 0.5;
                    let starHtml = '';
                    for (let i = 0; i < fullStars; i++) {
                        starHtml += '<i class="fas fa-star custom-star"></i>';
                    }
                    if (hasHalfStar) {
                        starHtml += '<i class="fas fa-star-half-alt custom-star"></i>';
                    }
                    while (starHtml.split('fa-star').length - 1 < 5) {
                        starHtml += '<i class="far fa-star custom-star"></i>';
                    }
                    element.innerHTML = starHtml;
                });
                
                // 更新浏览器历史记录
                history.pushState(
                    { searchTerm: item.term, index: index },
                    `Search results for ${item.term}`,
                    `/?q=${encodeURIComponent(item.term)}&sequential_search=true&search_index=${index}&all_search_terms=${encodeURIComponent(JSON.stringify(searchData.allSearchTerms))}`
                );
                
                sessionStorage.setItem('sequentialSearchState', JSON.stringify(searchData));
            } catch (error) {
                console.error("搜索产品失败:", error);
                productListContainer.innerHTML = `<p>加载产品失败: ${error.message}</p>`;
            }
        });
        
        termsList.appendChild(termEl);
    });
    sequentialSearchContainer.appendChild(termsList);
    
    // 当前搜索词说明
    const currentTermInfo = document.createElement('div');
    currentTermInfo.className = 'current-term-info';
    currentTermInfo.innerHTML = `
        <p>正在搜索: <strong>${searchData.allSearchTerms[searchData.currentSearchIndex].term}</strong> 
           <span class="term-type ${searchData.allSearchTerms[searchData.currentSearchIndex].type === 'expanded' ? 'expanded' : 'original'}">
             (${searchData.allSearchTerms[searchData.currentSearchIndex].type === 'expanded' ? '扩展关键词' : '原始关键词'})
           </span>
        </p>
    `;
    sequentialSearchContainer.appendChild(currentTermInfo);
    
// 设置按钮事件
// const prevButton = document.getElementById('prev-search-term');
// const nextButton = document.getElementById('next-search-term');
const closeButton = document.getElementById('close-sequential-search');

// 删除或注释掉这些事件监听器
// prevButton.addEventListener('click', () => {
//     if (searchData.currentSearchIndex > 0) {
//         termsList.children[searchData.currentSearchIndex - 1].click();
//     }
// });

// nextButton.addEventListener('click', () => {
//     if (searchData.currentSearchIndex < searchData.allSearchTerms.length - 1) {
//         termsList.children[searchData.currentSearchIndex + 1].click();
//     }
// });

closeButton.addEventListener('click', () => {
    sequentialSearchContainer.style.display = 'none';
    sessionStorage.removeItem('sequentialSearchState');
    if (window.history && window.history.pushState) {
        const url = new URL(window.location.href);
        url.searchParams.delete('sequential_search');
        url.searchParams.delete('search_index');
        url.searchParams.delete('all_search_terms');
        window.history.pushState({}, '', url.toString());
    }
    window.location.href = '/';
});
    // 更新UI
    updateSequentialSearchUI();
    
    // 自动触发第一个关键词
    if (searchData.allSearchTerms.length > 0) {
        termsList.children[0].click();
    }
}

    
    // 更新序列搜索UI状态
    function updateSequentialSearchUI() {
        const termsList = document.querySelector('#sequential-search-container .sequential-terms-list');
        if (!termsList) return;
        
        Array.from(termsList.children).forEach((termEl, index) => {
            termEl.classList.toggle('current', index === searchData.currentSearchIndex);
            const indicator = termEl.querySelector('.current-indicator');
            if (index === searchData.currentSearchIndex && !indicator) {
                const span = document.createElement('span');
                span.className = 'current-indicator';
                span.textContent = '当前';
                termEl.appendChild(span);
            } else if (index !== searchData.currentSearchIndex && indicator) {
                indicator.remove();
            }
            
            // 移除这部分代码或用条件检查替代
            // const prevBtn = document.getElementById('prev-search-term');
            // const nextBtn = document.getElementById('next-search-term');
            // prevBtn.disabled = searchData.currentSearchIndex <= 0;
            // nextBtn.disabled = searchData.currentSearchIndex >= searchData.allSearchTerms.length - 1;
            
            const info = document.querySelector('.current-term-info p');
            if (info) {
                info.innerHTML = `
                    正在搜索: <strong>${searchData.allSearchTerms[searchData.currentSearchIndex].term}</strong> 
                    <span class="term-type ${searchData.allSearchTerms[searchData.currentSearchIndex].type === 'expanded' ? 'expanded' : 'original'}">
                      (${searchData.allSearchTerms[searchData.currentSearchIndex].type === 'expanded' ? '扩展关键词' : '原始关键词'})
                    </span>
                `;
            }
        });
    }
    // 显示序列搜索容器
    // sequentialSearchContainer.style.display = 'block';
    document.addEventListener("DOMContentLoaded", function() {
        // 检查URL参数是否包含序列搜索信息
        const urlParams = new URLSearchParams(window.location.search);
        const isSequentialSearch = urlParams.get('sequential_search') === 'true';
        
        if (isSequentialSearch) {
            try {
                // 从URL参数中恢复搜索状态
                const currentIndex = parseInt(urlParams.get('search_index') || '0');
                const allTermsJson = urlParams.get('all_search_terms');
                
                if (allTermsJson) {
                    const allTerms = JSON.parse(allTermsJson);
                    
                    // 重建搜索数据对象
                    const searchData = {
                        allSearchTerms: allTerms,
                        currentSearchIndex: currentIndex,
                        searchQuery: allTerms[currentIndex].term
                    };
                    
                    // 保存到会话存储，以便在页面跳转后恢复
                    sessionStorage.setItem('sequentialSearchState', JSON.stringify(searchData));
                    
                    // 初始化序列搜索界面
                    setupSequentialSearch(searchData);
                }
            } catch (error) {
                console.error("恢复序列搜索状态失败:", error);
            }
        } else {
            // 如果不是通过URL参数传入，但会话中有保存的状态，也尝试恢复
            const savedState = sessionStorage.getItem('sequentialSearchState');
            if (savedState) {
                try {
                    const searchData = JSON.parse(savedState);
                    setupSequentialSearch(searchData);
                } catch (error) {
                    console.error("从会话恢复搜索状态失败:", error);
                }
            }
        }
    });


// 本地关键词提取
function extractKeywordsLocally(text) {
    // 这里实现关键词提取逻辑
    const keywords = [];
    
    // 预定义的商品类别和属性关键词
    const productCategories = [
        '手机', '电脑', '笔记本', '平板', '电视', '冰箱', '洗衣机', '空调', 
        '服装', '鞋子', '帽子', '手表', '首饰', '包', '书', '食品', '饮料',
        '玩具', '娃娃', '玩偶', '汽车', '自行车', '家具', '床', '沙发', '椅子', '桌子'
    ];
    
    const attributes = [
        '红色', '蓝色', '绿色', '黄色', '黑色', '白色', '大', '小', '中',
        '便宜', '贵', '高端', '低端', '防水', '智能', '轻', '重', '快', '慢'
    ];
    
    const relations = [
        '女儿', '儿子', '妻子', '丈夫', '母亲', '父亲', '孩子', '家人', '朋友', '同事'
    ];
    
    const intentPhrases = [
        '想要', '需要', '寻找', '查找', '购买', '买', '找', '送给', '送', '给'
    ];
    
    // 简单分词（按空格和标点分割）
    const words = text.split(/\s+|[,，。.、;；:：!！?？]/);
    
    // 提取关键词
    for (const word of words) {
        if (!word) continue;
        
        
        // 检查是否为属性
        for (const attr of attributes) {
            if (word.includes(attr)) {
                if (!keywords.includes(attr)) {
                    keywords.push(attr);
                }
            }
        }
        
        // 检查是否为关系词
        for (const relation of relations) {
            if (word.includes(relation)) {
                if (!keywords.includes(relation)) {
                    keywords.push(relation);
                }
            }
        }
    }
    
    // 处理特定模式
    // 例如: "我女儿想要玩偶"
    if (text.includes('女儿') && (text.includes('玩偶') || text.includes('娃娃'))) {
        if (text.includes('玩偶') && !keywords.includes('玩偶')) keywords.push('玩偶');
        if (text.includes('娃娃') && !keywords.includes('娃娃')) keywords.push('娃娃');
        if (!keywords.includes('玩具') && keywords.length < 3) keywords.push('玩具');
    }
    
    // 如果有意图词和产品词，提取它们
    for (const intent of intentPhrases) {
        if (text.includes(intent)) {
            // 查找意图词后面可能的产品
            const intentIndex = text.indexOf(intent) + intent.length;
            const textAfterIntent = text.substring(intentIndex);
            
        }
    }
    
    // 特殊处理："想要玩偶"中的"玩偶"
    if (text.includes('想要') && text.includes('玩偶') && !keywords.includes('玩偶')) {
        keywords.push('玩偶');
    }
    
    // 如果没有找到关键词，尝试使用最长的词作为关键词
    if (keywords.length === 0) {
        const possibleNouns = words.filter(word => 
            word.length >= 2 && 
            !intentPhrases.some(phrase => word.includes(phrase))
        );
        
        if (possibleNouns.length > 0) {
            possibleNouns.sort((a, b) => b.length - a.length);
            keywords.push(...possibleNouns.slice(0, 2));
        }
    }
    
    return keywords;
}

// 扩展关键词 - 寻找近义词和相关词
async function expandKeywords(keywords) {
    if (!keywords || keywords.length === 0) return [];
    
    // 关键词近义词字典
    const synonymsDict = {
        '娃娃': ['玩偶', '洋娃娃', '毛绒玩具', '布娃娃'],
        '玩偶': ['娃娃', '洋娃娃', '毛绒玩具', '布偶'],
        '玩具': ['积木', '模型', '游戏', '玩偶'],
        '手机': ['智能手机', '手机壳', '充电器', '耳机'],
        '电脑': ['笔记本', '平板', '台式机', '显示器'],
        '服装': ['衣服', '裤子', '裙子', '外套'],
        '鞋子': ['运动鞋', '休闲鞋', '皮鞋', '靴子'],
        '红色': ['红', '粉色', '玫红'],
        '蓝色': ['蓝', '深蓝', '天蓝'],
        '小': ['迷你', '便携', '轻便'],
        '大': ['超大', '宽大', '厚重'],
        '女儿': ['女孩', '儿童', '小孩'],
        '儿子': ['男孩', '儿童', '小孩']
    };
    
    const expandedKeywords = [];
    
    // 为每个关键词找同义词或相关词
    for (const keyword of keywords) {
        if (synonymsDict[keyword]) {
            // 添加前2个同义词，避免过多
            expandedKeywords.push(...synonymsDict[keyword].slice(0, 2));
        }
    }
    
    // 去重
    return [...new Set(expandedKeywords)];
}

// 可选：服务器端分词API (如果您实现了后端jieba分词)
async function extractKeywordsWithServer(text) {
    try {
        const response = await fetch('/api/extract-keywords', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        if (!response.ok) {
            throw new Error(`服务器响应错误: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("服务器分词结果:", data);
        
        return data.keywords || [];
    } catch (error) {
        console.error("服务器分词失败:", error);
        return [];
    }
}
