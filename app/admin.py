from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g
)
from firebase_admin import auth as firebase_auth
from app.auth import login_required
from app.db import get_db
# NEW IMPORTS for CMS & Trends
from app.services.geo_service import fetch_place_data
from app.services.cms_service import refresh_trending_destinations
from app.patterns.observer import PriceSubject, NotificationObserver
from app.patterns.factory import ProviderFactory

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
def admin_only():
    if g.user['role'] != 'admin':
        flash("Access Denied: Administrator privileges required.")
        return redirect(url_for('traveler.dashboard'))

@bp.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Live Metrics
    cursor.execute("SELECT COUNT(*) as u FROM users")
    metrics = {'users': cursor.fetchone()['u']}
    
    cursor.execute("SELECT COUNT(*) as w FROM watches WHERE is_active = TRUE")
    metrics['watches'] = cursor.fetchone()['w']
    
    # Real API Usage Count
    try:
        cursor.execute("SELECT metric_value FROM system_metrics WHERE metric_key = 'api_usage_daily' AND last_updated = CURRENT_DATE")
        api_row = cursor.fetchone()
        metrics['api_calls'] = api_row['metric_value'] if api_row else 0
    except:
        metrics['api_calls'] = 0 
    
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'provider_mode'")
    mode_row = cursor.fetchone()
    mode = mode_row['setting_value'] if mode_row else 'mock'
    
    return render_template('admin/dashboard.html', metrics=metrics, mode=mode)

# --- NEW: REFRESH TRENDS ROUTE ---
@bp.route('/generate_trending', methods=['POST'])
def generate_trending():
    try:
        count = refresh_trending_destinations(4)
        flash(f"Success! Refreshed homepage with {count} verified Canadian destinations.")
    except Exception as e:
        flash(f"Error refreshing trends: {e}")
    return redirect(url_for('admin.dashboard'))

@bp.route('/users')
def users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, first_name, last_name, email, role, is_banned, created_at FROM users ORDER BY created_at DESC")
    all_users = cursor.fetchall()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    db = get_db()
    cursor = db.cursor()
    if user_id == g.user['id']:
        flash("You cannot ban your own admin account!")
        return redirect(url_for('admin.users'))
    cursor.execute("UPDATE users SET is_banned = NOT is_banned WHERE id = %s", (user_id,))
    flash(f"User status updated.")
    return redirect(url_for('admin.users'))

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if user_id == g.user['id']:
        flash("You cannot delete your own admin account!")
        return redirect(url_for('admin.users'))
    try:
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            email = user['email']
            try:
                firebase_user = firebase_auth.get_user_by_email(email)
                firebase_auth.delete_user(firebase_user.uid)
            except Exception:
                pass 
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        flash(f"User deleted successfully.")
    except Exception as e:
        flash(f"Error deleting user: {e}")
    return redirect(url_for('admin.users'))

# --- CMS ROUTE (Handles GET and POST) ---
@bp.route('/cms', methods=('GET', 'POST'))
def cms():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Manual Add Logic
        city_input = request.form['city']
        price = request.form['price']
        image = request.form['image']
        
        # Try to auto-detect country, else default to Canada
        geo_data = fetch_place_data(city_input)
        if geo_data:
            final_city = geo_data['city']
            final_country = geo_data['country']
        else:
            final_city = city_input
            final_country = "Canada"
            
        cursor.execute("INSERT INTO destinations (city, country, price_estimate, image_url) VALUES (%s, %s, %s, %s)",
                       (final_city, final_country, price, image))
        db.commit()
        flash(f"Added {final_city} to homepage!")
        return redirect(url_for('admin.cms'))
        
    cursor.execute("SELECT * FROM destinations ORDER BY id DESC")
    destinations = cursor.fetchall()
    return render_template('admin/cms.html', destinations=destinations)

@bp.route('/cms/delete/<int:dest_id>', methods=['POST'])
def delete_dest(dest_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM destinations WHERE id = %s", (dest_id,))
    db.commit()
    flash("Destination removed.")
    return redirect(url_for('admin.cms'))

@bp.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    new_mode = request.form['mode']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("REPLACE INTO settings (setting_key, setting_value) VALUES ('provider_mode', %s)", (new_mode,))
    db.commit()
    flash(f"System switched to {new_mode.upper()} mode.")
    return redirect(url_for('admin.dashboard'))

@bp.route('/refresh_all', methods=['POST'])
def refresh_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM watches WHERE is_active = TRUE")
    watches = cursor.fetchall()
    provider = ProviderFactory.get_provider()
    observer = NotificationObserver()
    count = 0
    notifications_sent = 0
    for watch in watches:
        flights = provider.search_flights(watch['origin'], watch['destination'], watch['depart_date'])
        if flights:
            lowest = min(flights, key=lambda x: x['price'])
            if lowest['price'] <= watch['threshold_price']:
                subject = PriceSubject(watch['id'], watch['user_id'], watch['threshold_price'], watch['origin'], watch['destination'])
                subject.attach(observer)
                subject.notify(lowest['price'], lowest['provider'])
                notifications_sent += 1
            count += 1
    flash(f"Scanned {count} routes. {notifications_sent} Price Alerts generated!")
    return redirect(url_for('admin.dashboard'))
