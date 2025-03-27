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

// 关闭工具栏（同时恢复页面位置）
function closeToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityBtn = document.getElementById("accessibility-btn");

    resetAccessibility();

    toolbar.style.display = "none";

    menu.style.top = "0";  // 让菜单回到顶部
    menu.style.position = "fixed";  
    menu.style.display = "flex";  
    menu.style.visibility = "visible";  
    menu.style.opacity = "1";  
    menu.style.zIndex = "10000";

    document.body.style.marginTop = "10px"; // 让整个页面回归正常
    contentWrapper.style.paddingTop = "40px"; // 让内容恢复
    accessibilityBtn.style.display = "block"; // 重新显示 Web Accessibility 按钮

    window.scrollTo({ top: 0, behavior: "smooth" });
}

let zoomLevel = 1.0;
let targetZoomLevel = 1.0;
let animationFrameId = null;

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

// Declare isLargeCursorActive before using it
let isLargeCursorActive = false;
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

    // 1) 重置缩放
    zoomLevel = 1.0;
    targetZoomLevel = 1.0;
    document.querySelectorAll("#menu, #content-wrapper").forEach(element => {
        element.style.transform = "scale(1)";
        element.style.transformOrigin = "top left";
    });

    // Reset cursor mode
    const body = document.body;
    if (isLargeCursorActive) {
        body.classList.remove('large-cursor');
        isLargeCursorActive = false;
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

// Cursor Mode Functionality
let isCursorModeActive = false;
function toggleCursorMode() {
    const body = document.body;
    if (isLargeCursorActive) {
        body.classList.remove('large-cursor');
    } else {
        body.classList.add('large-cursor');
    }
    isLargeCursorActive = !isLargeCursorActive;
        // 更新 ARIA 属性以提高可访问性
        const button = document.querySelector('button[onclick="toggleCursorMode()"]');
        button.setAttribute("aria-pressed", isLargeCursorActive ? "true" : "false");
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
let largeCaptionEnabled = false;

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
    // 如果文本较长，启用多行显示；这里阈值可根据实际情况调整
    if (text.length > 100) {
        captionBox.classList.add("multiline");
        // 清除之前设置的内联样式，确保 .multiline 样式生效
        captionBox.style.whiteSpace = "";
        captionBox.style.height = "";
        captionBox.style.lineHeight = "";
        captionBox.style.overflowY = "";
    } else {
        captionBox.classList.remove("multiline");
        // 单行模式下设置内联样式
        captionBox.style.whiteSpace = "nowrap";
        captionBox.style.height = "100px";
        captionBox.style.lineHeight = "90px";
        captionBox.style.overflowY = "hidden";
    }
    captionBox.innerText = text;
}




let isCrosshairModeActive = false;
let crosshairElement = null;

function toggleCrosshair() {
    const body = document.body;
    isCrosshairModeActive = !isCrosshairModeActive;

    if (isCrosshairModeActive) {
        // 不隐藏默认光标，保留鼠标可见性
        body.classList.add("crosshair-mode-active");
        document.querySelector('button[onclick="toggleCrosshair()"]').setAttribute("aria-pressed", "true");

        // 创建十字线元素
        crosshairElement = document.createElement('div');
        crosshairElement.classList.add('crosshair');
        body.appendChild(crosshairElement);

        // 添加鼠标移动事件监听
        document.addEventListener('mousemove', moveCrosshair);
    } else {
        body.classList.remove("crosshair-mode-active");
        document.querySelector('button[onclick="toggleCrosshair()"]').setAttribute("aria-pressed", "false");

        // 移除十字线元素和事件监听
        if (crosshairElement) {
            crosshairElement.remove();
            crosshairElement = null;
        }
        document.removeEventListener('mousemove', moveCrosshair);
    }
}

// 动态更新十字线位置
function moveCrosshair(event) {
    if (crosshairElement) {
        crosshairElement.style.left = `${event.clientX}px`;
        crosshairElement.style.top = `${event.clientY}px`;
    }
}