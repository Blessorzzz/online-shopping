document.addEventListener("DOMContentLoaded", function () {
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const toolbar = document.createElement("div");
    toolbar.id = "accessibility-toolbar";
    toolbar.innerHTML = `
        <div class="accessibility-toolbar">
            <button onclick="increaseFontSize()">放大</button>
            <button onclick="decreaseFontSize()">缩小</button>
            <button onclick="toggleContrast()">高对比</button>
            <button onclick="toggleReadingMode()">阅读模式</button>
            <button onclick="resetAccessibility()">重置</button>
        </div>
    `;
    document.body.appendChild(toolbar);

    accessibilityBtn.addEventListener("click", function () {
        toolbar.style.display = toolbar.style.display === "block" ? "none" : "block";
    });
});

// **无障碍功能**
function increaseFontSize() {
    document.body.style.fontSize = (parseFloat(getComputedStyle(document.body).fontSize) + 2) + "px";
}

function decreaseFontSize() {
    document.body.style.fontSize = (parseFloat(getComputedStyle(document.body).fontSize) - 2) + "px";
}

function toggleContrast() {
    document.body.classList.toggle("high-contrast");
}

function toggleReadingMode() {
    document.body.classList.toggle("reading-mode");
}

function resetAccessibility() {
    document.body.style.fontSize = "";
    document.body.classList.remove("high-contrast", "reading-mode");
}
