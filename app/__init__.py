import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance"), exist_ok=True)
    db.init_app(app)

    from app.routes.employee_routes import employee_bp
    app.register_blueprint(employee_bp)

    with app.app_context():
        from app.models.employee import Employee
        db.create_all()

    return app
