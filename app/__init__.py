from flask import Flask

def create_app():
    app = Flask(__name__)

# Import routes
    from .routes import main
    from app.Routes.spread_dt9 import spread_dt9_bp
    app.register_blueprint(spread_dt9_bp)


    from app.scheduler import init_scheduler
    init_scheduler(app)

    app.run(debug=True, use_reloader=False)

    return app