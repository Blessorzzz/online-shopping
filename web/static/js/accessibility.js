document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    // 默认隐藏工具栏 & 页面不移动
    toolbar.style.display = "none";

    // 点击 Web Accessibility 按钮，显示/隐藏工具栏
    accessibilityBtn.addEventListener("click", function () {
        if (toolbar.style.display === "none") {
            toolbar.style.display = "flex";
            accessibilityBtn.style.display = "none"; // 只隐藏按钮本身，不隐藏整个 <li> 元素

            menu.style.position = "fixed"; 
            menu.style.top = "103px";  // 让菜单下移
            menu.style.height = "80px";
            menu.style.display = "flex";
            menu.style.zIndex = "10000"; 

            contentWrapper.style.paddingTop = "160px";  // 确保内容不会被遮挡
        }
    });    
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
    }
}

function decreaseZoom() {
    if (targetZoomLevel > 1.0) {
        targetZoomLevel -= 0.1;
        smoothZoom();
    }
}

let currentTheme = null;

function toggleColorScheme() {
    const themes = ['high-contrast', 'protanopia', 'deuteranopia', 'tritanopia', 'grayscale', null];
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
}

function resetColorScheme() {
    delete document.body.dataset.theme;
    localStorage.removeItem('accessibilityTheme');
    currentTheme = null;
    document.body.style.cssText = 'display: block;';
}

document.addEventListener("DOMContentLoaded", function() {
    const savedTheme = localStorage.getItem('accessibilityTheme');
    if (savedTheme) {
        applyColorScheme(savedTheme);
    }
});

// Declare isLargeCursorActive before using it
let isLargeCursorActive = false;

function resetAccessibility() {
    console.log("🔄 Resetting accessibility settings...");

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