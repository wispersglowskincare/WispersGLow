from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .models import User
from .utils import csrf_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/admin/login")
def login():
    if session.get("admin_id"):
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html", csrf_token=csrf_token())


@auth_bp.post("/admin/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session.clear()
        session["admin_id"] = user.id
        session["admin_name"] = user.username
        session["csrf_token"] = csrf_token()
        return redirect(request.args.get("next") or url_for("admin.dashboard"))
    flash("That login did not match. Try again.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.get("/admin/logout")
def logout():
    session.clear()
    flash("You are logged out.", "success")
    return redirect(url_for("main.home"))