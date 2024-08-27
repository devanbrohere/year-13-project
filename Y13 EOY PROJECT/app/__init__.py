from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login_signup'
app = Flask(__name__, static_url_path='/static')

from app import routes

app.run(debug=True)

