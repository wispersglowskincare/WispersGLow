from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .models import Product, Promotion, SiteSettings, Testimonial
from .utils import cart_items, csrf_token, whatsapp_link

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    products = Product.query.filter_by(published=True).order_by(Product.featured.desc(), Product.created_at.desc()).all()
    featured = [p for p in products if p.featured]
    settings = SiteSettings.query.first()
    testimonials = Testimonial.query.filter_by(published=True).order_by(Testimonial.created_at.desc()).limit(4).all()
    promotions = Promotion.query.filter_by(enabled=True).order_by(Promotion.created_at.desc()).limit(2).all()
    return render_template("index.html", products=products, featured=featured, settings=settings, testimonials=testimonials, promotions=promotions)


@main_bp.get("/shop")
def shop():
    query = request.args.get("q", "").strip()
    products_query = Product.query.filter_by(published=True)
    if query:
        products_query = products_query.filter(Product.name.ilike(f"%{query}%"))
    products = products_query.order_by(Product.featured.desc(), Product.name.asc()).all()
    return render_template("shop.html", products=products, query=query)


@main_bp.get("/product/<slug>")
def product(slug):
    item = Product.query.filter_by(slug=slug, published=True).first_or_404()
    related = Product.query.filter(Product.id != item.id, Product.published.is_(True)).limit(3).all()
    return render_template("product.html", product=item, related=related)


@main_bp.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = Product.query.filter_by(id=product_id, published=True).first_or_404()
    quantity = max(1, int(request.form.get("quantity", 1) or 1))
    cart = session.get("cart", {})
    current = int(cart.get(str(product_id), 0))
    cart[str(product_id)] = min(product.stock, current + quantity)
    session["cart"] = cart
    flash(f"{product.name} added to your bag.", "success")
    return redirect(request.referrer or url_for("main.shop"))


@main_bp.get("/cart")
def cart():
    items, total = cart_items(session.get("cart", {}))
    return render_template("cart.html", items=items, total=total, csrf_token=csrf_token())


@main_bp.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for key, value in request.form.items():
        if not key.startswith("quantity_"):
            continue
        product_id = key.replace("quantity_", "")
        try:
            product = Product.query.get(int(product_id))
            quantity = max(0, int(value))
            if not product or quantity == 0:
                cart.pop(product_id, None)
            else:
                cart[product_id] = min(quantity, product.stock)
        except (TypeError, ValueError):
            continue
    session["cart"] = cart
    flash("Your bag has been updated.", "success")
    return redirect(url_for("main.cart"))


@main_bp.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("main.cart"))


@main_bp.get("/order/whatsapp")
def order_whatsapp():
    items, total = cart_items(session.get("cart", {}))
    if not items:
        flash("Add something to your bag before ordering.", "error")
        return redirect(url_for("main.shop"))
    settings = SiteSettings.query.first()
    number = settings.whatsapp_number if settings else current_app.config["WHATSAPP_NUMBER"]
    return redirect(whatsapp_link(items, total, number))


@main_bp.get("/about")
def about():
    return render_template("about.html", settings=SiteSettings.query.first())


@main_bp.get("/contact")
def contact():
    settings = SiteSettings.query.first()
    return render_template("contact.html", settings=settings)