document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    const accessibilityLink = document.querySelector('#accessibility-btn').parentElement;


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

    // 点击 Web Accessibility 按钮，显示/隐藏工具栏
    accessibilityBtn.addEventListener("click", function () {
        if (toolbar.style.display === "none") {
            // 显示工具栏时隐藏链接
            toolbar.style.display = "flex";
            accessibilityLink.classList.add("hidden"); // 隐藏导航栏中的按钮
            menu.style.top = "60px";
            contentWrapper.style.paddingTop = "120px"; // 调整内容区域间距
        }
    });
});

// 关闭工具栏（同时恢复页面位置）
function closeToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityLink = document.querySelector('#accessibility-btn').parentElement;

    toolbar.style.display = "none";
    accessibilityLink.classList.remove("hidden"); // 改用 classList 操作
    menu.style.top = "0";
    contentWrapper.style.paddingTop = "60px";
}



let zoomLevel = 1.0;
let targetZoomLevel = 1.0;
let animationFrameId = null;

function smoothZoom() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }

    function animate() {
        zoomLevel += (targetZoomLevel - zoomLevel) * 0.2; // ✅ 让缩放平滑过渡

        if (Math.abs(targetZoomLevel - zoomLevel) < 0.001) {
            zoomLevel = targetZoomLevel; // ✅ 避免浮点误差
        } else {
            animationFrameId = requestAnimationFrame(animate);
        }

        const content = document.querySelector("#content-wrapper");
        if (content) {
            content.style.transform = `scale(${zoomLevel})`;
            content.style.transformOrigin = "top left"; // ✅ 从屏幕中心缩放
        }
    }

    animate();
}

function increaseZoom() {
    if (targetZoomLevel < 2.0) {
        targetZoomLevel += 0.1;
        smoothZoom();
    }
}

function decreaseZoom() {
    if (targetZoomLevel > 0.8) {
        targetZoomLevel -= 0.1;
        smoothZoom();
    }
}

function resetAccessibility() {
    console.log("🔄 Resetting accessibility settings...");

    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    // ✅ **恢复默认缩放级别**
    zoomLevel = 1.0;
    targetZoomLevel = 1.0;
    if (contentWrapper) {
        contentWrapper.style.transform = "scale(1)";
        contentWrapper.style.transformOrigin = "top left";
        contentWrapper.style.paddingTop = "120px"; // ✅ **恢复默认间距**
    }


    // ✅ **恢复 body 的 margin**
    document.body.style.marginTop = "5px";

    // ✅ **滚动回到顶部**
    window.scrollTo({ top: 0, behavior: "smooth" });

    console.log("✅ Accessibility settings reset!");
}
