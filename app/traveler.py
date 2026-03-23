from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from app.auth import login_required
from app.db import get_db
from app.patterns.factory import ProviderFactory
from app.currency import get_usd_to_cad_rate

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
@bp.route('/search', methods=('GET', 'POST'))  
def search():
    results = []
    origin = ""
    destination = ""
    depart_date = ""
    return_date = ""
    trip_type = "one_way"
    current_rate = get_usd_to_cad_rate()

    if request.method == 'POST':
        origin = request.form.get('origin','').strip()
        destination = request.form.get('destination', '').strip()
        depart_date = request.form.get('date')
        return_date = request.form.get('return_date')
        trip_type = request.form.get('trip_type','one_way')
        
        # If One Way selected, clear the return date so the Provider knows logic to use
        if trip_type == 'one_way':
            return_date = None
        
        # Get the correct provider (Mock or Live) from our Factory
        provider = ProviderFactory.get_provider()
        
        # Pass all arguments to the provider
        # The new serpapi_prov.py is expecting these 4 arguments now
        results = provider.search_flights(origin, destination, depart_date, return_date)
        
        # usd_to_cad_rate = get_usd_to_cad_rate()
        # print(f"🔁 Using USD->CAD rate: {usd_to_cad_rate}")

        for flight in results:
            usd_price = float(flight.get("price", 0) or 0)
            flight["usd_price"] = round(usd_price, 2)
            flight["cad_price"] = round(usd_price * current_rate, 2)
    
    return render_template('traveler/search.html', 
                           results=results, 
                           origin=origin, 
                           destination=destination, 
                           date=depart_date,
                           return_date=return_date,
                           trip_type=trip_type,
                           current_rate=current_rate
                           )

@bp.route('/watch', methods=['POST'])
def watch_route():
    origin = request.form['origin']
    destination = request.form['destination']
    price = float(request.form['price'])
    # Default depart date for the watch (simplified for MVP, sets it to 7 days from now)
    import datetime
    depart_date = datetime.date.today() + datetime.timedelta(days=7)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO watches (user_id, origin, destination, depart_date, threshold_price) VALUES (%s, %s, %s, %s, %s)",
        (g.user['id'], origin, destination, depart_date, price)
    )
    flash(f"Now watching {origin} -> {destination} for price drops below ${price:.2f}")
    return redirect(url_for('traveler.dashboard'))

@bp.route('/delete_watch/<int:id>', methods=['POST'])
def delete_watch(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM watches WHERE id = %s AND user_id = %s", (id, g.user['id']))
    flash("Watch removed.")
    return redirect(url_for('traveler.dashboard'))


@bp.route('/notifications')
@login_required
def notifications():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (g.user['id'],))
    notifs = cursor.fetchall()
    
    
    # Mark as read immediately when viewed
    cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (g.user['id'],))
    
    return render_template('traveler/notifications.html', notifications=notifs)

@bp.route('/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (g.user['id'],))
    flash("Notifications cleared.")
    return redirect(url_for('traveler.notifications'))