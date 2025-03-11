document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");

    const accessibilityLink = document.querySelector('#accessibility-btn').parentElement;


    // 默认隐藏工具栏 & 页面不移动
    toolbar.style.display = "none";

    // 点击 Web Accessibility 按钮，显示/隐藏工具栏
    accessibilityBtn.addEventListener("click", function () {
        if (toolbar.style.display === "none") {
            toolbar.style.display = "flex";
            accessibilityBtn.style.display = "none"; // ✅ 只隐藏按钮本身，不隐藏整个 <li> 元素

    
            menu.style.position = "fixed"; 
            menu.style.top = "103px";  // ✅ 让菜单下移
            menu.style.height = "80px";
            menu.style.display = "flex";
            menu.style.zIndex = "10000"; 

            contentWrapper.style.paddingTop = "160px";  // ✅ 确保内容不会被遮挡
        }
    });    
});

// 关闭工具栏（同时恢复页面位置）
function closeToolbar() {
    const toolbar = document.getElementById("accessibility-toolbar");
    const menu = document.getElementById("menu");
    const contentWrapper = document.getElementById("content-wrapper");
    const accessibilityBtn = document.getElementById("accessibility-btn"); // 重新获取按钮

    resetAccessibility();

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
        zoomLevel += (targetZoomLevel - zoomLevel) * 0.2;
        if (Math.abs(targetZoomLevel - zoomLevel) < 0.001) {
            zoomLevel = targetZoomLevel;
        } else {
            animationFrameId = requestAnimationFrame(animate);
        }

        // ✅ 强制同步布局并同时设置两个元素的缩放
        const menu = document.getElementById("menu");
        const contentWrapper = document.getElementById("content-wrapper");
        
        // 使用 requestAnimationFrame 确保同一帧内更新
        requestAnimationFrame(() => {
            menu.style.transform = `scale(${zoomLevel})`;
            menu.style.transformOrigin = "top left";
            contentWrapper.style.transform = `scale(${zoomLevel})`;
            contentWrapper.style.transformOrigin = "top left"; // 确保基准点一致
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


function resetAccessibility() {
    console.log("🔄 Resetting accessibility settings...");

    zoomLevel = 1.0;
    targetZoomLevel = 1.0;

    document.querySelectorAll("#menu, #content-wrapper").forEach(element => {
        element.style.transform = "scale(1)";
        element.style.transformOrigin = "top left"; 
    });

    document.body.style.marginTop = "5px";
    window.scrollTo({ top: 0, behavior: "smooth" });

    // **隐藏字幕框**
    document.getElementById("large-caption").style.display = "none";
    largeCaptionEnabled = false; // 关闭字幕功能
    document.removeEventListener("mouseover", updateCaption);


    console.log("✅ Accessibility settings reset!");
}

let largeCaptionEnabled = false;

function toggleLargeCaptions() {
    largeCaptionEnabled = !largeCaptionEnabled;
    const captionBox = document.getElementById("large-caption");
    const contentWrapper = document.getElementById("content-wrapper");

    if (largeCaptionEnabled) {
        captionBox.style.display = "block"; // 显示字幕框
        contentWrapper.style.paddingBottom = "120px"; // 为内容区增加底部内边距
        captionBox.innerText = "";
        document.addEventListener("mouseover", updateCaption);
    } else {
        captionBox.style.display = "none"; // 隐藏字幕框
        contentWrapper.style.paddingBottom = "40px"; // 恢复原始内边距（根据你的页面设计调整）
        document.removeEventListener("mouseover", updateCaption);
    }
}


function updateCaption(event) {
    if (!largeCaptionEnabled) return; // ✅ 仅在 "Large Captions" 开启时生效

    const captionBox = document.getElementById("large-caption");
    let targetElement = event.target;

    // 1️⃣ 获取文本信息
    let text = (
        targetElement.innerText?.trim() ||
        targetElement.getAttribute("alt")?.trim() ||
        targetElement.getAttribute("title")?.trim()
    );

    // 2️⃣ 过滤无意义元素（空白区域）
    const structuralTags = ["BODY", "HTML","DIV", "SECTION", "HEADER", "MAIN"];
    const isStructuralTag = structuralTags.includes(targetElement.tagName);
    const isInvisible = targetElement.offsetWidth === 0 || targetElement.offsetHeight === 0;

    if (!text || isStructuralTag || isInvisible) {
        captionBox.innerText = ""; // ✅ 鼠标未悬停在文本上时，字幕框仍然可见，但不显示文字
        return;
    }

    // 3️⃣ 显示字幕内容
    captionBox.innerText = text;
}





