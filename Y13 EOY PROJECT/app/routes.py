from app import app
from sqlalchemy.exc import IntegrityError
from flask import render_template, abort, request, redirect, url_for,flash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "clash.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images')
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_signup'

import app.models as models
from app.models import Cards, User
from app.forms import Add_Card, RegisterForm, LoginForm



@app.route("/")
def home():
    # Render the home page
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    form = Add_Card()

    if request.method == "POST":
        if form.validate_on_submit():
            new_card = models.Cards()
            new_card.name=form.name.data,
            new_card.description=form.description.data,
            new_card.rarity=form.rarity.data,
            new_card.card_target=form.target.data,
            new_card.Min_trophies_unlocked=form.trophies.data,
            new_card.evolution=form.evolution.data,
            new_card.speed=form.speed.data,
            new_card.Special=form.special.data,
            new_card.spawn_time=form.spawn_time.data,
            new_card.elixir=form.elixir.data

            # Handle file upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Ensure the upload folder exists
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                # Save the file
                form.image.data.save(file_path)
                new_card.image = f'images/{filename}'
            else:
                new_card.image = None

            try:
                db.session.add(new_card)
                db.session.commit()
                return redirect(url_for('details', ref=new_card.id))
            except IntegrityError:
                db.session.rollback()
                flash('Card with this name already exists. Please choose a different name.', 'danger')
                return render_template('add_card.html', form=form, title="Add A Card")

        else:
            flash("Form validation failed. Please correct the errors and try again.")
            return render_template('add_card.html', form=form, title="Add A Card")

    return render_template("add_card.html", form=form, title="Add A Card")


@app.route('/details/<int:ref>')
def details(ref):
    deets = models.Cards.query.filter_by(id=ref).first_or_404()
    return render_template("card.html", card=deets, title=deets.name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login_signup', methods=['GET', 'POST'])
def login_signup():
    register_form = RegisterForm()
    login_form = LoginForm()

    if request.method == 'POST':
        if 'LOGIN' in request.form:  # Check if the login form was submitted
            if login_form.validate_on_submit():
                user = User.query.filter_by(email=login_form.email.data).first()
                if user and check_password_hash(user.password, login_form.password.data):
                    login_user(user)
                    return redirect(url_for('welcome'))
                else:
                    flash('Invalid email or password', 'danger')
            else:
                flash('Login form validation failed', 'danger')

        elif 'REGISTER' in request.form:  # Check if the registration form was submitted
            if register_form.validate_on_submit():
                if register_form.password.data == register_form.confirm.data:
                    hashed_password = generate_password_hash(register_form.password.data, method='sha256')
                    new_user = User(full_name=register_form.full_name.data, email=register_form.email.data, password=hashed_password)
                    db.session.add(new_user)
                    db.session.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login_signup'))
                else:
                    flash('Passwords do not match', 'danger')
            else:
                flash('Registration form validation failed', 'danger')
                print(f"Form Data: {request.form}")

    return render_template('login_signup.html', register_form=register_form, login_form=login_form)

@app.route('/welcome')
@login_required
def welcome():
    return f"Welcome, {current_user.full_name}!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_signup'))

@app.route('/cards')
def cards():
    cards = models.Cards.query.all()
    return render_template('cards.html', cards=cards)


@app.route('/card/<int:id>')
def card(id):
    card = models.Cards.query.filter_by(id=id).first()
    card_health = card.card_health
    return render_template('card.html', card=card, card_health=card_health)

 
if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
