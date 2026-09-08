document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (toggle && menu) toggle.addEventListener("click", () => menu.classList.toggle("is-open"));
  const floatingCart = document.querySelector("[data-floating-cart]");
  const showCart = document.querySelector("[data-show-cart]");
  const hideCart = document.querySelector("[data-hide-cart]");
  if (floatingCart && showCart && hideCart) {
    const hidden = window.localStorage.getItem("wispers-floating-cart-hidden") === "true";
    floatingCart.hidden = hidden;
    showCart.hidden = !hidden;
    hideCart.addEventListener("click", () => {
      floatingCart.hidden = true;
      showCart.hidden = false;
      window.localStorage.setItem("wispers-floating-cart-hidden", "true");
    });
    showCart.addEventListener("click", () => {
      floatingCart.hidden = false;
      showCart.hidden = true;
      window.localStorage.setItem("wispers-floating-cart-hidden", "false");
    });
  }
  document.querySelectorAll(".card-add-form").forEach(form => {
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const button = form.querySelector("button[type=submit]");
      const originalText = button.innerHTML;
      button.disabled = true;
      button.textContent = "Adding...";
      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest", "Accept": "application/json" }
        });
        if (!response.ok) throw new Error("Unable to add item");
        const data = await response.json();
        document.querySelectorAll(".nav-bag span, .floating-cart-count, .floating-cart-restore span").forEach(count => {
          count.textContent = data.cart_count;
        });
        const flashStack = document.querySelector(".flash-stack") || Object.assign(document.createElement("div"), { className: "flash-stack" });
        if (!flashStack.parentElement) document.body.appendChild(flashStack);
        const flash = document.createElement("div");
        flash.className = "flash success";
        flash.textContent = data.message;
        flashStack.appendChild(flash);
        window.setTimeout(() => flash.remove(), 3500);
      } catch (error) {
        form.submit();
        return;
      } finally {
        button.disabled = false;
        button.innerHTML = originalText;
      }
    });
  });
  document.querySelectorAll("[data-quantity]").forEach(input => {
    const wrapper = input.closest(".quantity-control");
    wrapper.querySelector("[data-quantity-minus]").addEventListener("click", () => input.value = Math.max(1, Number(input.value || 1) - 1));
    wrapper.querySelector("[data-quantity-plus]").addEventListener("click", () => input.value = Math.min(Number(input.max || 99), Number(input.value || 1) + 1));
  });
});