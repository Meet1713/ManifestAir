from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/dashboard")
def dashboard():
    return "<h1>Admin dashboard coming soon</h1>"

@bp.route("/cms")
def cms():
    return "<h1>Admin CMS page coming soon</h1>"