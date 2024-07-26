from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login_signup'
app = Flask(__name__, static_url_path='/static')

from app import routes

app.run(debug=True)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes, models
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))