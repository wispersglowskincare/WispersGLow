document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (toggle && menu) toggle.addEventListener("click", () => menu.classList.toggle("is-open"));
  document.querySelectorAll("[data-quantity]").forEach(input => {
    const wrapper = input.closest(".quantity-control");
    wrapper.querySelector("[data-quantity-minus]").addEventListener("click", () => input.value = Math.max(1, Number(input.value || 1) - 1));
    wrapper.querySelector("[data-quantity-plus]").addEventListener("click", () => input.value = Math.min(Number(input.max || 99), Number(input.value || 1) + 1));
  });
});