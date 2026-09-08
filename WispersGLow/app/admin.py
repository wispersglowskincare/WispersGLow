import json
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .models import Product, Promotion, SiteSettings, Testimonial, unique_slug
from .utils import admin_required, csrf_token, csrf_valid, parse_benefits, save_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _product_from_form(product=None):
    name = request.form.get("name", "").strip()
    try:
        price = Decimal(request.form.get("price", "0"))
        stock = max(0, int(request.form.get("stock", "0")))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Price and stock must be valid numbers.")
    if not name or price < 0:
        raise ValueError("Add a product name and a valid price.")
    if product is None:
        product = Product(slug=unique_slug(name))
        db.session.add(product)
    elif product.name != name:
        product.slug = unique_slug(name, product.id)
    product.name = name
    product.price = price
    product.stock = stock
    product.short_description = request.form.get("short_description", "").strip()
    product.full_description = request.form.get("full_description", "").strip()
    product.benefits = json.dumps(parse_benefits(request.form.get("benefits", "")))
    product.how_to_use = request.form.get("how_to_use", "").strip()
    product.featured = request.form.get("featured") == "on"
    product.published = request.form.get("published") == "on"
    product.promotion_enabled = request.form.get("promotion_enabled") == "on"
    product.promotion_text = request.form.get("promotion_text", "").strip()
    product.free_gift = request.form.get("free_gift", "").strip()
    for field, folder in (("main_image", "products"), ("before_image", "before_after"), ("after_image", "before_after")):
        uploaded = save_upload(request.files.get(field), folder)
        if uploaded:
            setattr(product, field, uploaded)
    if not product.main_image:
        raise ValueError("A main product image is required.")
    return product


@admin_bp.get("")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", products=Product.query.count(), testimonials=Testimonial.query.count(), promotions=Promotion.query.count())


@admin_bp.route("/products", methods=["GET", "POST"])
@admin_required
def products():
    if request.method == "POST":
        if not csrf_valid():
            flash("Your form expired. Please try again.", "error")
        else:
            try:
                _product_from_form()
                db.session.commit()
                flash("Product created.", "success")
                return redirect(url_for("admin.products"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")
    return render_template("admin/products.html", products=Product.query.order_by(Product.created_at.desc()).all(), csrf_token=csrf_token())


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def product_new():
    if request.method == "POST":
        if not csrf_valid():
            flash("Your form expired. Please try again.", "error")
        else:
            try:
                _product_from_form()
                db.session.commit()
                flash("Product created.", "success")
                return redirect(url_for("admin.products"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")
    return render_template("admin/product_form.html", product=None, csrf_token=csrf_token())


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        if not csrf_valid():
            flash("Your form expired. Please try again.", "error")
        else:
            try:
                _product_from_form(product)
                db.session.commit()
                flash("Product updated.", "success")
                return redirect(url_for("admin.products"))
            except ValueError as error:
                db.session.rollback()
                flash(str(error), "error")
    return render_template("admin/product_form.html", product=product, csrf_token=csrf_token())


@admin_bp.post("/products/<int:product_id>/delete")
@admin_required
def product_delete(product_id):
    if not csrf_valid():
        flash("Your form expired. Please try again.", "error")
    else:
        db.session.delete(Product.query.get_or_404(product_id))
        db.session.commit()
        flash("Product removed.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/testimonials", methods=["GET", "POST"])
@admin_required
def testimonials():
    if request.method == "POST":
        if not csrf_valid():
            flash("Your form expired. Please try again.", "error")
        else:
            rating = max(1, min(5, int(request.form.get("rating", "5"))))
            db.session.add(Testimonial(
                customer_name=request.form.get("customer_name", "").strip(),
                text=request.form.get("text", "").strip(),
                rating=rating,
                published=request.form.get("published") == "on",
            ))
            db.session.commit()
            flash("Testimonial saved.", "success")
        return redirect(url_for("admin.testimonials"))
    return render_template("admin/testimonials.html", testimonials=Testimonial.query.order_by(Testimonial.created_at.desc()).all(), csrf_token=csrf_token())


@admin_bp.post("/testimonials/<int:testimonial_id>/delete")
@admin_required
def testimonial_delete(testimonial_id):
    if csrf_valid():
        db.session.delete(Testimonial.query.get_or_404(testimonial_id))
        db.session.commit()
        flash("Testimonial removed.", "success")
    return redirect(url_for("admin.testimonials"))


@admin_bp.route("/promotions", methods=["GET", "POST"])
@admin_required
def promotions():
    if request.method == "POST":
        if csrf_valid():
            db.session.add(Promotion(title=request.form.get("title", "").strip(), body=request.form.get("body", "").strip(), enabled=request.form.get("enabled") == "on"))
            db.session.commit()
            flash("Promotion saved.", "success")
        return redirect(url_for("admin.promotions"))
    return render_template("admin/promotions.html", promotions=Promotion.query.order_by(Promotion.created_at.desc()).all(), csrf_token=csrf_token())


@admin_bp.post("/promotions/<int:promotion_id>/delete")
@admin_required
def promotion_delete(promotion_id):
    if csrf_valid():
        db.session.delete(Promotion.query.get_or_404(promotion_id))
        db.session.commit()
        flash("Promotion removed.", "success")
    return redirect(url_for("admin.promotions"))


@admin_bp.route("/homepage", methods=["GET", "POST"])
@admin_required
def homepage():
    settings = SiteSettings.query.first()
    if request.method == "POST":
        if not csrf_valid():
            flash("Your form expired. Please try again.", "error")
        else:
            for field in ("hero_eyebrow", "hero_title", "hero_subtitle", "hero_button", "delivery_text", "before_title", "before_description", "about_title", "about_body", "whatsapp_number"):
                setattr(settings, field, request.form.get(field, "").strip())
            settings.delivery_enabled = request.form.get("delivery_enabled") == "on"
            for field, folder in (("hero_image", "site"), ("before_image", "before_after"), ("after_image", "before_after")):
                uploaded = save_upload(request.files.get(field), folder)
                if uploaded:
                    setattr(settings, field, uploaded)
            db.session.commit()
            flash("Homepage updated.", "success")
            return redirect(url_for("admin.homepage"))
    return render_template("admin/homepage.html", settings=settings, csrf_token=csrf_token())


@admin_bp.get("/orders")
@admin_required
def orders():
    from .models import Order
    return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())