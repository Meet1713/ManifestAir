from flask import Blueprint

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login")
def login():
    return "<h1>Login page coming soon</h1>"

@bp.route("/register")
def register():
    return "<h1>Register page coming soon</h1>"

@bp.route("/logout")
def logout():
    return "<h1>Logout route coming soon</h1>"

@bp.route("/admin-login")
def admin_login():
    return "<h1>Admin login page coming soon</h1>"