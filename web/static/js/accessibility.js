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
    window.location.href = '';
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