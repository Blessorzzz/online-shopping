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
            toolbar.style.display = "flex";
            accessibilityBtn.style.display = "none"; // ✅ 只隐藏按钮本身，不隐藏整个 <li> 元素

    
            menu.style.position = "fixed"; 
            menu.style.top = "60px";  // ✅ 让菜单下移
            menu.style.display = "flex";
            menu.style.zIndex = "10000"; 

            contentWrapper.style.paddingTop = "110px";  // ✅ 确保内容不会被遮挡
        }
    });    
});

// 关闭工具栏（同时恢复页面位置）
function closeToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityBtn = document.getElementById("accessibility-btn"); // 重新获取按钮

    toolbar.style.display = "none";

    menu.style.top = "0";  // ✅ 让菜单回到顶部
    menu.style.position = "fixed";  
    menu.style.display = "flex";  
    menu.style.visibility = "visible";  
    menu.style.opacity = "1";  
    menu.style.zIndex = "10000";

    document.body.style.marginTop = "10px"; // ✅ 让整个页面回归正常
    contentWrapper.style.paddingTop = "40px"; // ✅ 让内容恢复
    accessibilityBtn.style.display = "block"; // ✅ 重新显示 Web Accessibility 按钮

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
