from flask import Blueprint

bp = Blueprint("traveler", __name__, url_prefix="/traveler")

@bp.route("/dashboard")
def dashboard():
    return "Traveler dashboard working"