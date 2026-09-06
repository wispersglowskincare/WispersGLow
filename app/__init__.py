import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

load_dotenv()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    for folder in ("products", "before_after", "testimonials", "site"):
        Path(app.config["UPLOAD_FOLDER"], folder).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from .auth import auth_bp
    from .routes import main_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_site():
        from .models import SiteSettings
        from .utils import csrf_token

        settings = SiteSettings.query.first()
        site = settings.as_dict() if settings else {}
        return {"site": site, "cart_count": sum(_cart().values()), "csrf_token": csrf_token}

    @app.template_filter("money")
    def money(value):
        return f"₦{float(value):,.0f}"

    @app.template_filter("json_list")
    def json_list(value):
        try:
            return json.loads(value or "[]")
        except (TypeError, ValueError):
            return []

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template("errors/500.html"), 500

    with app.app_context():
        from .models import seed_database
        db.create_all()
        seed_database(app)

    return app


def _cart():
    from flask import session
    return {str(key): int(value) for key, value in session.get("cart", {}).items()}
