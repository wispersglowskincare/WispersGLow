document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-comparison]").forEach(slider => {
    const setPosition = event => {
      const rect = slider.getBoundingClientRect();
      const source = event.touches ? event.touches[0] : event;
      const value = Math.min(100, Math.max(0, ((source.clientX - rect.left) / rect.width) * 100));
      slider.style.setProperty("--split", `${value}%`);
    };
    let dragging = false;
    slider.addEventListener("pointerdown", event => { dragging = true; slider.setPointerCapture(event.pointerId); setPosition(event); });
    slider.addEventListener("pointermove", event => { if (dragging) setPosition(event); });
    slider.addEventListener("pointerup", () => dragging = false);
    slider.addEventListener("pointercancel", () => dragging = false);
    slider.querySelector(".comparison-handle")?.addEventListener("keydown", event => {
      const current = parseFloat(getComputedStyle(slider).getPropertyValue("--split")) || 50;
      if (event.key === "ArrowLeft") slider.style.setProperty("--split", `${Math.max(0, current - 5)}%`);
      if (event.key === "ArrowRight") slider.style.setProperty("--split", `${Math.min(100, current + 5)}%`);
    });
  });
  document.querySelectorAll(".card-comparison").forEach(card => {
    let dragging = false;
    let moved = false;
    let suppressClick = false;
    let startX = 0;
    const update = event => {
      const rect = card.getBoundingClientRect(), point = event.touches ? event.touches[0] : event;
      moved = moved || Math.abs(point.clientX - startX) > 4;
      card.style.setProperty("--split", `${Math.min(100, Math.max(0, ((point.clientX - rect.left) / rect.width) * 100))}%`);
    };
    card.addEventListener("pointerdown", event => {
      dragging = true;
      moved = false;
      startX = event.clientX;
      event.preventDefault();
      card.setPointerCapture(event.pointerId);
      update(event);
    });
    card.addEventListener("pointermove", event => { if (dragging) update(event); });
    card.addEventListener("pointerup", () => {
      dragging = false;
      if (moved) {
        suppressClick = true;
        window.setTimeout(() => suppressClick = false, 0);
      }
    });
    card.addEventListener("pointercancel", () => dragging = false);
    card.addEventListener("dragstart", event => event.preventDefault());
    card.addEventListener("click", event => {
      if (suppressClick) {
        event.preventDefault();
        event.stopPropagation();
        suppressClick = false;
      }
    });
    card.querySelector(".card-comparison-handle")?.addEventListener("keydown", event => {
      const current = parseFloat(getComputedStyle(card).getPropertyValue("--split")) || 50;
      if (event.key === "ArrowLeft") card.style.setProperty("--split", `${Math.max(0, current - 5)}%`);
      if (event.key === "ArrowRight") card.style.setProperty("--split", `${Math.min(100, current + 5)}%`);
    });
  });
});