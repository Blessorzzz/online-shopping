document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.createElement("div");
    toolbar.id = "accessibility-toolbar";
    toolbar.innerHTML = `
        <button onclick="increaseZoom()" title="Zoom In">
            <span>➕</span><small>Zoom In</small>
        </button>
        <button onclick="decreaseZoom()" title="Zoom Out">
            <span>➖</span><small>Zoom Out</small>
        </button>
        <button onclick="toggleCursorMode()" title="Cursor Mode">
            <span>🖱️</span><small>Cursor</small>
        </button>
        <button onclick="toggleCrosshair()" title="Crosshair Mode">
            <span>🎯</span><small>Crosshair</small>
        </button>
        <button onclick="toggleLargeCaptions()" title="Large Captions">
            <span>🔠</span><small>Captions</small>
        </button>
        <button onclick="toggleColorScheme()" title="Color Settings">
            <span>🎨</span><small>Colors</small>
        </button>
        <button onclick="resetAccessibility()" title="Reset">
            <span>🔄</span><small>Reset</small>
        </button>
        <button onclick="toggleStickyMode()" title="Sticky Mode">
            <span>📌</span><small>Sticky</small>
        </button>
        <button onclick="showAccessibilityInfo()" title="Information">
            <span>ℹ️</span><small>Info</small>
        </button>
        <button onclick="closeToolbar()" title="Exit Service" class="exit">
            <span>⏻</span><small>Exit</small>
        </button>
    `;
    document.body.prepend(toolbar);

    // 默认隐藏工具栏 & 页面不移动
    toolbar.style.display = "none";
    document.body.style.marginTop = "0px";
    const menu = document.getElementById("menu"); // 选择导航栏

    // 点击 Web Accessibility 按钮，显示/隐藏工具栏
    accessibilityBtn.addEventListener("click", function () {
        if (toolbar.style.display === "none") {
            toolbar.style.display = "flex";
            document.body.style.marginTop = "80px"; // ✅ 页面整体下移
            if (menu) {
                menu.style.marginTop = "20px"; // ✅ 让导航栏再往下 20px
            }
        } else {
            toolbar.style.display = "none";
            document.body.style.marginTop = "0px"; // ✅ 复原
            if (menu) {
                menu.style.marginTop = "0px"; // ✅ 复原导航栏位置
            }
        }
    });
});

// 关闭工具栏（同时恢复页面位置）
function closeToolbar() {
    document.getElementById("accessibility-toolbar").style.display = "none";
    document.body.style.marginTop = "0px";
    const menu = document.getElementById("menu");
    if (menu) {
        menu.style.marginTop = "0px"; // ✅ 关闭时复原导航栏
    }
}


let zoomLevel = 1.0;

function increaseZoom() {
    const content = document.querySelector("body");
    const menu = document.getElementById("menu");

    if (!content || !menu) {
        console.error("❌ Error: .main-content or #menu not found!");
        return;
    }

    if (zoomLevel < 1.4) {
        zoomLevel += 0.1;
        content.style.transform = `scale(${zoomLevel})`;
        content.style.transformOrigin = "top center";

        // ✅ 让页面高度同步调整，防止出现空白
        document.body.style.height = `${document.body.scrollHeight * zoomLevel}px`;
        
        // ✅ 让导航栏始终可见，不会消失
        menu.style.position = "fixed";
        menu.style.top = "0";
        menu.style.width = "100%";
        menu.style.zIndex = "9999"; // 确保在最前面
    }
}

function decreaseZoom() {
    const content = document.querySelector("body");
    const menu = document.getElementById("menu");

    if (!content || !menu) {
        console.error("❌ Error: .main-content or #menu not found!");
        return;
    }

    if (zoomLevel > 0.8) {
        zoomLevel -= 0.1;
        content.style.transform = `scale(${zoomLevel})`;
        content.style.transformOrigin = "top center";

        // ✅ 让页面高度同步调整，防止出现空白
        document.body.style.height = `${document.body.scrollHeight * zoomLevel}px`;

        // ✅ 让导航栏始终可见，不会消失
        menu.style.position = "fixed";
        menu.style.top = "0";
        menu.style.width = "100%";
        menu.style.zIndex = "9999";
    }
}

let currentTheme = null;

function toggleColorScheme() {
    const themes = ['high-contrast', 'protanopia', 'deuteranopia', 'tritanopia', 'grayscale', null];
    let savedTheme = localStorage.getItem('accessibilityTheme');

    // 如果当前主题未定义或是最后一个主题，则回到第一个主题
    let currentIndex = themes.indexOf(savedTheme);
    if (currentIndex === -1) {
        currentIndex = 0; // 如果 localStorage 里存了错误的值，默认使用第一个主题
    }
    let nextIndex = (currentIndex + 1) % themes.length;
    let nextTheme = themes[nextIndex];

    console.log("Switching theme to:", nextTheme); // ✅ 调试信息

    // 应用新的主题
    applyColorScheme(nextTheme);
}

function applyColorScheme(theme) {
    const body = document.body;

    if (theme) {
        body.dataset.theme = theme;
        localStorage.setItem('accessibilityTheme', theme);
        
        // 强制刷新所有相关 UI 组件的颜色
        document.documentElement.style.setProperty('--bg-color', getComputedStyle(body).getPropertyValue('--bg-color'));
        document.documentElement.style.setProperty('--text-color', getComputedStyle(body).getPropertyValue('--text-color'));
        document.documentElement.style.setProperty('--button-bg', getComputedStyle(body).getPropertyValue('--button-bg'));
        document.documentElement.style.setProperty('--button-text', getComputedStyle(body).getPropertyValue('--button-text'));
        document.documentElement.style.setProperty('--border-color', getComputedStyle(body).getPropertyValue('--border-color'));

        console.log("Applied theme:", theme); // ✅ 调试信息

        // 确保所有按钮、导航栏、搜索框颜色也即时更新
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
  
  // 强制重绘
  document.body.style.cssText = 'display: block;';
}

// 初始化加载时应用保存的主题
document.addEventListener("DOMContentLoaded", function() {
  const savedTheme = localStorage.getItem('accessibilityTheme');
  if(savedTheme) {
    applyColorScheme(savedTheme);
  }
});

function resetColorScheme() {
    // 移除data属性
    delete document.body.dataset.theme;
    
    // 清除本地存储
    localStorage.removeItem('accessibilityTheme');
    
    // 强制浏览器重绘
    document.body.style.cssText = 'display: block;';
  }




