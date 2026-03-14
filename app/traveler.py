from flask import
(
    Blueprint, render_template, request, flash, redirect, url_for, g, session
)
from app.auth import login_required
from app.db import get_db
from app.patterns.factory import ProviderFactory

bp = Blueprint("traveler", __name__, url_prefix="/traveler")

@bp.before_request
@login_required
def traveler_only():
    # Only Travelers and Admins can access these routes
    if g.user['role'] != 'traveler' and g.user['role'] != 'admin':
        return redirect(url_for('auth.login'))

@bp.route("/dashboard")
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

    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        depart_date = request.form.get('date')
        return_date = request.form.get('return_date')
        trip_type = request.form.get('trip_type')
        
        # If One Way selected, clear the return date so the Provider knows logic to use
        if trip_type == 'one_way':
            return_date = None
        
        # Get the correct provider (Mock or Live) from our Factory
        provider = ProviderFactory.get_provider()
        
        # Pass all arguments to the provider
        # The new serpapi_prov.py is expecting these 4 arguments now
        results = provider.search_flights(origin, destination, depart_date, return_date)
        
    return render_template('traveler/search.html', 
                           results=results, 
                           origin=origin, 
                           destination=destination, 
                           date=depart_date,
                           return_date=return_date,
                           trip_type=trip_type)

@bp.route('/watch', methods=['POST'])

@bp.route('/delete_watch/<int:id>', methods=['POST'])


@bp.route("/notifications")
def notifications():
    return "<h1>Traveler notifications coming soon</h1>"

@bp.route('/notifications/clear', methods=['POST'])
