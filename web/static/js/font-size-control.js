let fontSizeLevel = parseFloat(localStorage.getItem("fontSizeLevel")) || 1.0;

function applyFontSize() {
    document.body.style.fontSize = `${fontSizeLevel}em`;
}

function increaseFontSize() {
    if (fontSizeLevel < 1.8) {
        fontSizeLevel += 0.1;
        localStorage.setItem("fontSizeLevel", fontSizeLevel);
        applyFontSize();
    }
}

function decreaseFontSize() {
    if (fontSizeLevel > 0.8) {
        fontSizeLevel -= 0.1;
        localStorage.setItem("fontSizeLevel", fontSizeLevel);
        applyFontSize();
    }
}

document.addEventListener("DOMContentLoaded", applyFontSize);
