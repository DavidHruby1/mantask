(() => {
    const viewport = document.querySelector(".graph-viewport");
    const canvas = document.querySelector(".graph-canvas");
    if (!viewport || !canvas) {
        return;
    }

    let scale = 1;
    let dragging = false;
    let startX = 0;
    let startY = 0;
    let startLeft = 0;
    let startTop = 0;

    const applyScale = () => {
        canvas.style.transform = `scale(${scale})`;
        canvas.style.marginRight = `${canvas.width.baseVal.value * (scale - 1)}px`;
        canvas.style.marginBottom = `${canvas.height.baseVal.value * (scale - 1)}px`;
    };

    document.querySelector("[data-zoom-in]")?.addEventListener("click", () => {
        scale = Math.min(1.5, scale + 0.1);
        applyScale();
    });

    document.querySelector("[data-zoom-out]")?.addEventListener("click", () => {
        scale = Math.max(0.8, scale - 0.1);
        applyScale();
    });

    document.querySelector("[data-zoom-reset]")?.addEventListener("click", () => {
        scale = 1;
        applyScale();
    });

    viewport.addEventListener("pointerdown", (event) => {
        if (event.button !== 0) {
            return;
        }
        dragging = true;
        startX = event.clientX;
        startY = event.clientY;
        startLeft = viewport.scrollLeft;
        startTop = viewport.scrollTop;
        viewport.classList.add("dragging");
        viewport.setPointerCapture(event.pointerId);
    });

    viewport.addEventListener("pointermove", (event) => {
        if (!dragging) {
            return;
        }
        viewport.scrollLeft = startLeft - (event.clientX - startX);
        viewport.scrollTop = startTop - (event.clientY - startY);
    });

    const stopDragging = () => {
        dragging = false;
        viewport.classList.remove("dragging");
    };

    viewport.addEventListener("pointerup", stopDragging);
    viewport.addEventListener("pointercancel", stopDragging);
})();
