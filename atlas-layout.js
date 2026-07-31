(() => {
  const STORAGE_KEY = "dino-atlas-layout-v1";
  const DEFAULT_INSPECTOR_WIDTH = 360;
  const MIN_INSPECTOR_WIDTH = 320;
  const MAX_INSPECTOR_WIDTH = 680;
  const MIN_MAP_WIDTH = 520;
  const RESIZER_WIDTH = 10;

  const panel = document.querySelector("#atlasView .map-panel");
  const resizer = document.querySelector("#mapInspectorResizer");
  if (!panel || !resizer) return;

  let dragPointerId = null;
  let pendingWidth = null;
  let resizeFrame = 0;
  let preferredWidth = DEFAULT_INSPECTOR_WIDTH;

  function getSavedWidth() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      return Number(saved.inspectorWidth) || DEFAULT_INSPECTOR_WIDTH;
    } catch {
      return DEFAULT_INSPECTOR_WIDTH;
    }
  }

  function getWidthBounds() {
    const panelWidth = panel.getBoundingClientRect().width;
    const availableMaximum = Math.max(
      MIN_INSPECTOR_WIDTH,
      panelWidth - MIN_MAP_WIDTH - RESIZER_WIDTH,
    );
    return {
      minimum: MIN_INSPECTOR_WIDTH,
      maximum: Math.min(MAX_INSPECTOR_WIDTH, availableMaximum),
    };
  }

  function clampInspectorWidth(width) {
    const bounds = getWidthBounds();
    return Math.round(Math.max(bounds.minimum, Math.min(bounds.maximum, width)));
  }

  function persistWidth(width) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ inspectorWidth: width }));
    } catch {
      // The layout remains usable when storage is unavailable.
    }
  }

  function applyInspectorWidth(width, { persist = false } = {}) {
    const bounds = getWidthBounds();
    const nextWidth = clampInspectorWidth(width);
    panel.style.setProperty("--map-inspector-width", `${nextWidth}px`);
    resizer.setAttribute("aria-valuemin", String(bounds.minimum));
    resizer.setAttribute("aria-valuemax", String(bounds.maximum));
    resizer.setAttribute("aria-valuenow", String(nextWidth));
    if (persist) {
      preferredWidth = nextWidth;
      persistWidth(nextWidth);
    }
    return nextWidth;
  }

  function queueWidth(width) {
    pendingWidth = width;
    if (resizeFrame) return;
    resizeFrame = requestAnimationFrame(() => {
      resizeFrame = 0;
      applyInspectorWidth(pendingWidth);
    });
  }

  function finishResize(event) {
    if (dragPointerId === null) return;
    if (event?.pointerId !== undefined && event.pointerId !== dragPointerId) return;
    if (resizeFrame) {
      cancelAnimationFrame(resizeFrame);
      resizeFrame = 0;
    }
    const width = applyInspectorWidth(pendingWidth ?? preferredWidth, { persist: true });
    dragPointerId = null;
    pendingWidth = null;
    document.body.classList.remove("map-inspector-resizing");
    resizer.setAttribute("aria-valuenow", String(width));
    try {
      if (resizer.hasPointerCapture?.(event?.pointerId)) {
        resizer.releasePointerCapture(event.pointerId);
      }
    } catch {
      // Pointer capture may already be released by the browser.
    }
    window.dispatchEvent(new Event("resize"));
  }

  preferredWidth = getSavedWidth();
  applyInspectorWidth(preferredWidth);

  resizer.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    dragPointerId = event.pointerId;
    pendingWidth = Number(resizer.getAttribute("aria-valuenow")) || DEFAULT_INSPECTOR_WIDTH;
    document.body.classList.add("map-inspector-resizing");
    try {
      resizer.setPointerCapture?.(event.pointerId);
    } catch {
      // Window-level pointer tracking below remains available.
    }
    event.preventDefault();
  });

  window.addEventListener("pointermove", (event) => {
    if (event.pointerId !== dragPointerId) return;
    const panelRight = panel.getBoundingClientRect().right;
    queueWidth(panelRight - event.clientX - RESIZER_WIDTH / 2);
  });

  window.addEventListener("pointerup", finishResize);
  window.addEventListener("pointercancel", finishResize);
  resizer.addEventListener("lostpointercapture", finishResize);
  window.addEventListener("blur", finishResize);

  resizer.addEventListener("keydown", (event) => {
    const current = Number(resizer.getAttribute("aria-valuenow")) || DEFAULT_INSPECTOR_WIDTH;
    const step = event.shiftKey ? 64 : 24;
    let nextWidth = current;
    if (event.key === "ArrowLeft") nextWidth += step;
    else if (event.key === "ArrowRight") nextWidth -= step;
    else if (event.key === "Home") nextWidth = MIN_INSPECTOR_WIDTH;
    else if (event.key === "End") nextWidth = MAX_INSPECTOR_WIDTH;
    else return;
    event.preventDefault();
    applyInspectorWidth(nextWidth, { persist: true });
    window.dispatchEvent(new Event("resize"));
  });

  resizer.addEventListener("dblclick", () => {
    applyInspectorWidth(DEFAULT_INSPECTOR_WIDTH, { persist: true });
    window.dispatchEvent(new Event("resize"));
  });

  window.addEventListener("resize", () => {
    applyInspectorWidth(preferredWidth);
  });
})();
