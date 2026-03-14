from flask import
(
    Blueprint, render_template, request, flash, redirect, url_for, g, session
)
# Import few segments from the files

bp = Blueprint("traveler", __name__, url_prefix="/traveler")

@bp.before_request
@login_required
def traveler_only():
    # Only Travelers and Admins can access these routes
    if g.user['role'] != 'traveler' and g.user['role'] != 'admin':
        return redirect(url_for('auth.login'))

@bp.route("/dashboard")
# Have to write some code here
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Fetch User's Watchlist
    cursor.execute("SELECT * FROM watches WHERE user_id = %s", (g.user['id'],))
    watches = cursor.fetchall()
    return render_template('traveler/dashboard.html', watches=watches)
@dp.route('/search', methods=('GET', 'POST'))  
def search():
    results = []
    origin = ""
    destination = ""
    depart_date = ""
    return_date = ""
    trip_type = "one_way" # Default

@bp.route('/watch', methods=['POST'])

@bp.route('/delete_watch/<int:id>', methods=['POST'])


@bp.route("/notifications")
def notifications():
    return "<h1>Traveler notifications coming soon</h1>"

@bp.route('/notifications/clear', methods=['POST'])
