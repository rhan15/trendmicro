import sys
from flask import Flask
from app.packages import os, load_dotenv, Path

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # mode exe
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        else:
            return Path(sys.executable).parent
    else:
        # mode python normal
        return Path(__file__).resolve().parent.parent


base_dir = get_base_dir()
env_path = base_dir / "config" / ".env"

print("\n")
print("ENV PATH:", env_path)
print("ENV EXISTS:", env_path.exists())
print("\n")

load_dotenv(env_path)


def create_app():
    app = Flask(__name__)

# Import routes
    from .routes import main
    from app.Routes.spread_dt9 import spread_dt9_bp
    from app.Routes.test import test_bp
    
    app.register_blueprint(test_bp)
    app.register_blueprint(spread_dt9_bp)


    from app.scheduler import init_scheduler
    init_scheduler(app)

    return app