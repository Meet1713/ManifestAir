import os
from flask import Flask, g, send_from_directory
#from . import db, auth, main, traveler, admin
from .config import config
from .currency import get_usd_to_cad_rate
from .db import get_db
from .firebase_auth import init_firebase

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    env_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[env_name])

    if test_config:
        app.config.from_mapping(test_config)

    # Initialize Database & Firebase
    db.init_app(app)
    init_firebase()

    # Import blueprints here to avoid circular imports
    from . import auth, main, traveler, admin
    # Register Blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(traveler.bp)
    app.register_blueprint(admin.bp)

    # --- FIX: Stop Browser Loading Spinner (Favicon) ---
    @app.route('/favicon.ico')
    def favicon():
        # Returns an empty response (204 No Content) to stop the browser waiting
        return "", 204

    # --- Global Context Processor ---
    @app.context_processor
    def inject_globals():
        context = dict(current_rate=get_usd_to_cad_rate(), unread_count=0)
        
        if hasattr(g, 'user') and g.user:
            db_conn = get_db()
            if db_conn:
                cursor = db_conn.cursor()
                try:
                    cursor.execute(
                        "SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", 
                        (g.user['id'],)
                    )
                    result = cursor.fetchone()
                    if isinstance(result, dict):
                        context['unread_count'] = list(result.values())[0]
                    else:
                        context['unread_count'] = result[0]
                except Exception:
                    pass 
        return context

    return app