from flask import Blueprint

bp = Blueprint("traveler", __name__, url_prefix="/traveler")

@bp.route("/dashboard")
def dashboard():
    return "<h1>Traveler dashboard coming soon</h1>"

@bp.route("/notifications")
def notifications():
    return "<h1>Traveler notifications coming soon</h1>"