from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.courses import courses_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(dashboard_bp)

    return app
