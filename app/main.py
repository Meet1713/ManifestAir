from flask import Blueprint, render_template

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("main/index.html")

@bp.route("/about")
def about():
    return "<h1>About page coming soon</h1>"

@bp.route("/careers")
def careers():
    return "<h1>Careers page coming soon</h1>"

@bp.route("/press")
def press():
    return "<h1>Press page coming soon</h1>"

@bp.route("/help-center")
def help_center():
    return "<h1>Help Center page coming soon</h1>"

@bp.route("/terms")
def terms():
    return "<h1>Terms of Service page coming soon</h1>"

@bp.route("/privacy")
def privacy():
    return "<h1>Privacy Policy page coming soon</h1>"