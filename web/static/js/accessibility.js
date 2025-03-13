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

    // 如果不希望页面加载时自动显示大字幕，请注释掉下面这段代码
    
    // 仅当固定模式开启时，才恢复大字幕状态
    if (stickyActive) {
        const largeCaptionSetting = localStorage.getItem("largeCaptionEnabled");
        if (largeCaptionSetting === "true") {
            largeCaptionEnabled = true;
            const captionBox = document.getElementById("large-caption");
            captionBox.style.display = "block";
            contentWrapper.style.paddingBottom = "120px";
            document.addEventListener("mouseover", updateCaption);
        }
    }

    
});

// ---------------------- 缩放功能 ----------------------
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
};

function resetColorScheme() {
    // 删除 data-theme 属性
    delete document.body.dataset.theme;
    localStorage.removeItem('accessibilityTheme');
    currentTheme = null;
    // 恢复 body 默认样式
    document.body.style.cssText = 'display: block;';
    // 移除通过 JS 设置的 CSS 变量，恢复 CSS 文件中定义的默认值
    document.documentElement.style.removeProperty('--bg-color');
    document.documentElement.style.removeProperty('--text-color');
    document.documentElement.style.removeProperty('--button-bg');
    document.documentElement.style.removeProperty('--button-text');
    document.documentElement.style.removeProperty('--border-color');
    // 清除相关元素的内联样式，确保默认样式生效
    document.querySelectorAll("button, #menu, form.nav-right button, .product-card").forEach(el => {
        el.style.backgroundColor = "";
        el.style.color = "";
        el.style.borderColor = "";
    });
}

// 初始化加载时应用保存的主题
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
        // 启用固定模式：保存当前状态
        localStorage.setItem("stickyMode", "true");
        localStorage.setItem("savedZoomLevel", zoomLevel);
        if (stickyBtn) stickyBtn.classList.add("active");
    } else {
        // 关闭固定模式：清除保存状态
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

    // 2) 恢复“工具栏已开启”时的布局，让菜单避免被遮挡
    const toolbar = document.getElementById("accessibility-toolbar");
    toolbar.style.display = "flex"; // 工具栏保持显示

    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    // 菜单下移到与 toolbar 不重叠的位置
    menu.style.position = "fixed";
    menu.style.top = "103px";
    menu.style.height = "80px";
    menu.style.display = "flex";
    menu.style.zIndex = "10000";
    contentWrapper.style.paddingTop = "160px";

    // 移除 body 顶部额外边距（避免页面整体上移过多）
    document.body.style.marginTop = "";

    // 3) 关闭“大字幕”功能，重置颜色主题（同时清除相关内联样式）
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

// ---------------------- 关闭工具栏功能（退出服务） ----------------------
function closeToolbar() {
    console.log("🔒 Closing accessibility toolbar...");
    // 1) 先重置所有无障碍设置
    resetAccessibility();

    // 2) 隐藏工具栏，恢复“Web Accessibility”入口按钮
    const toolbar = document.getElementById("accessibility-toolbar");
    const accessibilityBtn = document.getElementById("accessibility-btn");
    toolbar.style.display = "none";
    accessibilityBtn.style.display = "block";

    // 3) 让菜单回到默认（与 toolbar 不再并存）
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    menu.style.top = "0";
    menu.style.position = "fixed";
    menu.style.display = "flex";
    menu.style.zIndex = "10000";
    // 可以视需要增加/去除 body 顶部边距
    document.body.style.marginTop = "10px";
    contentWrapper.style.paddingTop = "40px";

    // 4) 滚动到顶部
    window.scrollTo({ top: 0, behavior: "smooth" });

    console.log("✅ Accessibility toolbar closed!");
}

// ---------------------- 大字幕功能 ----------------------
let largeCaptionEnabled = false;

function toggleLargeCaptions() {
    largeCaptionEnabled = !largeCaptionEnabled;
    // 将大字幕状态存入 localStorage，便于跨页面保存
    localStorage.setItem("largeCaptionEnabled", largeCaptionEnabled);
    const captionBox = document.getElementById("large-caption");
    const contentWrapper = document.getElementById("content-wrapper");
    if (largeCaptionEnabled) {
        captionBox.style.display = "block";
        contentWrapper.style.paddingBottom = "120px";
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
        return;
    }
    captionBox.innerText = text;
}
