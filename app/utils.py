import json
import secrets
from functools import wraps
from pathlib import Path
from urllib.parse import quote

from flask import current_app, flash, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from .models import Product

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)
    return session["csrf_token"]


def csrf_valid():
    return request.form.get("csrf_token") == session.get("csrf_token")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def save_upload(file_storage, folder):
    if not file_storage or not file_storage.filename:
        return None
    extension = Path(file_storage.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Use a JPG, PNG, or WEBP image.")
    filename = secure_filename(file_storage.filename.rsplit(".", 1)[0]) or "image"
    filename = f"{filename}-{secrets.token_hex(4)}.{extension}"
    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(target_dir / filename)
    return f"uploads/{folder}/{filename}"


def cart_items(cart):
    products = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if not product or not product.published:
            continue
        quantity = max(1, min(int(quantity), product.stock or 1))
        line_total = float(product.price) * quantity
        products.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
    return products, total


def whatsapp_link(items, total, number):
    lines = ["Hello Wispers Glow, I would like to place an order.", "", "Products:"]
    for item in items:
        lines.append(f"{item['product'].name} × {item['quantity']}")
    lines.extend(["", f"Estimated total: ₦{total:,.0f}", "", "Please let me know the next steps."])
    return f"https://wa.me/{number}?text={quote(chr(10).join(lines))}"


def parse_benefits(raw):
    if isinstance(raw, list):
        return [item.strip() for item in raw if item.strip()]
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except (ValueError, TypeError):
        pass
    return [line.strip() for line in (raw or "").splitlines() if line.strip()]