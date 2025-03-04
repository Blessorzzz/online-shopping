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





