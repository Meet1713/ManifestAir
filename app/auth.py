import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from app.firebase_auth import verify_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Renders the Firebase Registration Page."""
    return render_template('auth/register.html')

@bp.route('/login')
def login():
    """Renders the Firebase Login Page."""
    return render_template('auth/login.html')

@bp.route('/reset-password')
def reset_password():
    """Renders the Password Reset Page."""
    return render_template('auth/reset_password.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

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

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/admin-login', methods=('GET', 'POST'))
def admin_login():
    """Specific login for Admins (Uses local DB password for now)."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        error = None
        
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect email or not an admin.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('admin.dashboard'))

        flash(error)

    return render_template('auth/admin_login.html')