import os
from flask import Flask, g
from .config import config
from .currency import get_usd_to_cad_rate
from .db import get_db, init_app as init_db
from .firebase_auth import init_firebase

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    env_name = os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config[env_name])

    if test_config:
        app.config.from_mapping(test_config)

    init_db(app)
    init_firebase()

    from . import auth, main, traveler, admin

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(traveler.bp)
    app.register_blueprint(admin.bp)
    """
    @app.before_request
    def load_user():
        g.user = None
    """
    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.context_processor
    def inject_globals():
    from flask import g
    return dict(
        current_rate=get_usd_to_cad_rate(),
        unread_count=getattr(g, 'unread_count', 0)
    )

    return app