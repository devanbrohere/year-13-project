from app import app
from flask import render_template, abort, request
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "clash.db")
db.init_app(app)

import app.models as models
from app.forms import Add_Card

@app.route("/")
def home():
    # Render the home page
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/add_card", methods=['GET','POST'])
def add_card():
    form = Add_Card()
    if request.method=="GET":
        return render_template


@app.route('/login_signup')
def login_signup():
    return render_template("login_signup.html")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = database()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return f"Welcome, {user['full_name']}!"
    else:
        return "Invalid email or password"


# Route for the sign-up page
@app.route('/signup', methods=['POST'])
def signup():
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    conn = database()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)', (full_name, email, password))
    conn.commit()
    conn.close()
    return redirect(url_for('login_signup'))


@app.route('/cards')
def cards():
    cards = models.Cards.query.all()
    return render_template('cards.html', cards=cards)

@app.route('/card/<int:id>')
def card(id):
    card = models.Cards.query.filter_by(id=id).first()
    return render_template('card.html', card=card)

if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
