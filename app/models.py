import json
import re
from datetime import datetime

from flask import current_app
from werkzeug.security import generate_password_hash

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    main_image = db.Column(db.String(255), nullable=False)
    before_image = db.Column(db.String(255))
    after_image = db.Column(db.String(255))
    short_description = db.Column(db.String(300), nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    benefits = db.Column(db.Text, default="[]")
    how_to_use = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=True)
    promotion_enabled = db.Column(db.Boolean, default=False)
    promotion_text = db.Column(db.String(255))
    free_gift = db.Column(db.String(160))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def benefit_list(self):
        try:
            return json.loads(self.benefits or "[]")
        except (TypeError, ValueError):
            return []


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    image = db.Column(db.String(255))
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(220), nullable=False)
    hero_subtitle = db.Column(db.Text, nullable=False)
    hero_eyebrow = db.Column(db.String(120), nullable=False)
    hero_button = db.Column(db.String(80), nullable=False)
    hero_image = db.Column(db.String(255))
    delivery_enabled = db.Column(db.Boolean, default=True)
    delivery_text = db.Column(db.String(220), nullable=False)
    before_title = db.Column(db.String(160), nullable=False)
    before_description = db.Column(db.Text, nullable=False)
    before_image = db.Column(db.String(255))
    after_image = db.Column(db.String(255))
    about_title = db.Column(db.String(160), nullable=False)
    about_body = db.Column(db.Text, nullable=False)
    whatsapp_number = db.Column(db.String(30), nullable=False)

    def as_dict(self):
        return {
            "hero_title": self.hero_title,
            "hero_subtitle": self.hero_subtitle,
            "hero_eyebrow": self.hero_eyebrow,
            "hero_button": self.hero_button,
            "hero_image": self.hero_image,
            "delivery_enabled": self.delivery_enabled,
            "delivery_text": self.delivery_text,
            "before_title": self.before_title,
            "before_description": self.before_description,
            "before_image": self.before_image,
            "after_image": self.after_image,
            "about_title": self.about_title,
            "about_body": self.about_body,
            "whatsapp_number": self.whatsapp_number,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    total = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_name = db.Column(db.String(160), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "product"


def unique_slug(name, current_id=None):
    base = slugify(name)
    slug = base
    counter = 2
    while Product.query.filter(Product.slug == slug, Product.id != current_id).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def seed_database(app):
    """Create a usable first launch without overwriting owner content."""
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin")
        admin.set_password("admin1234")
        db.session.add(admin)

    if not SiteSettings.query.first():
        db.session.add(
            SiteSettings(
                hero_eyebrow="THE WISPERS GLOW EDIT",
                hero_title="Rituals for your most confident skin.",
                hero_subtitle="Thoughtfully made body care for soft, luminous skin — with room for your real routine.",
                hero_button="Explore the edit",
                hero_image="uploads/site/hero-glow.svg",
                delivery_enabled=True,
                delivery_text="Complimentary delivery across Nigeria on every order.",
                before_title="See the ritual. Feel the difference.",
                before_description="A calm, honest look at the care behind the glow. Real images can be added from the admin dashboard.",
                before_image="uploads/before_after/demo-before.svg",
                after_image="uploads/before_after/demo-after.svg",
                about_title="A softer standard for skin care.",
                about_body="Wispers Glow is a space for simple, considered rituals. Replace this demo story with your mother's own words from the admin dashboard.",
                whatsapp_number=app.config["WHATSAPP_NUMBER"],
            )
        )

    if Product.query.count() == 0:
        demo = [
            ("Radiance Body Wash", 15000, "A silky daily cleanse with a fresh, cushiony finish.", "A gentle body wash for the first step of a slower, more intentional routine.", ["Gently cleanses", "Leaves skin feeling fresh", "Comfortable everyday texture"], "Massage onto damp skin, then rinse.", "demo-body-wash.svg", True),
            ("Velvet Body Lotion", 18000, "A rich veil of moisture for skin that feels beautifully cared for.", "A nourishing lotion with a soft-touch finish. Layer it into your routine after bathing.", ["Helps lock in moisture", "Softens the feel of skin", "Easy to layer"], "Apply generously to clean, damp skin.", "demo-lotion.svg", True),
            ("Cloud Face Cream", 12000, "A quiet, plush cream for your evening wind-down.", "A comforting face cream designed to make the final step of your routine feel considered and easy.", ["Comforting daily hydration", "Smooth, plush texture", "Made for slow rituals"], "Press into clean skin as the final step.", "demo-cream.svg", False),
        ]
        for name, price, short, full, benefits, how, image, featured in demo:
            db.session.add(
                Product(
                    slug=unique_slug(name),
                    name=name,
                    price=price,
                    stock=25,
                    main_image=f"uploads/products/{image}",
                    before_image="uploads/before_after/demo-before.svg",
                    after_image="uploads/before_after/demo-after.svg",
                    short_description=short,
                    full_description=full,
                    benefits=json.dumps(benefits),
                    how_to_use=how,
                    featured=featured,
                    published=True,
                    promotion_enabled=name == "Radiance Body Wash",
                    promotion_text="A thoughtful little extra with this ritual.",
                    free_gift="Mini body polish",
                )
            )

    if Testimonial.query.count() == 0:
        db.session.add_all(
            [
                Testimonial(customer_name="Demo note", text="Replace this clearly marked demo note with a real customer story.", rating=5, published=True),
                Testimonial(customer_name="Your customer here", text="A placeholder for the real words that make the brand feel human.", rating=5, published=True),
            ]
        )

    if Promotion.query.count() == 0:
        db.session.add(Promotion(title="A little extra glow", body="Selected rituals may include a small complimentary gift while stock lasts.", enabled=True))

    db.session.commit()