from flask import Blueprint, render_template, g, session
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        g.user = cursor.fetchone()
        
        # Get Unread Notifications Count
        cursor.execute("SELECT COUNT(*) as c FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
        res = cursor.fetchone()
        g.unread_count = res['c'] if res else 0

@bp.route('/')
def index():
    # FETCH DYNAMIC DESTINATIONS FROM DB
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM destinations WHERE is_active = TRUE ORDER BY id DESC LIMIT 4")
    destinations = cursor.fetchall()
    
    return render_template('main/index.html', destinations=destinations)

@bp.route('/about')
def about():
    return render_template('main/about.html')

# --- FOOTER LINKS ---

@bp.route('/help')
def help_center():
    return render_template('main/generic.html', title="Help Center", content="How can we assist you today? Check our FAQ below.")

@bp.route('/terms')
def terms():
    return render_template('main/generic.html', title="Terms of Service", content="By using ManifestAir, you agree to our terms of service regarding data usage and booking responsibilities.")

@bp.route('/privacy')
def privacy():
    return render_template('main/generic.html', title="Privacy Policy", content="Your privacy is paramount. We do not sell your personal data to third parties.")

@bp.route('/careers')
def careers():
    return render_template('main/generic.html', title="Careers", content="Join the team! We are currently looking for Python developers and Data Scientists.")

@bp.route('/press')
def press():
    return render_template('main/generic.html', title="Press", content="For media inquiries, please contact press@manifestair.com.")
