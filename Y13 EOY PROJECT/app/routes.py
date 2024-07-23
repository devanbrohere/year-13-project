from app import app
from flask import render_template, abort, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "clash.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db = SQLAlchemy(app)


import app.models as models
from app.forms import Add_Card

@app.route("/")
def home():
    # Render the home page
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    rarities = models.Rarity.query.all()
    rarity_choices = [(rarity.id, rarity.type) for rarity in rarities]
    targets = models.Targets.query.all()
    target_choices = [(target.id, target.type) for target in targets]
    trophies = models.Trophies.query.all()
    trophy_choices = [(trophy.id, trophy.trophies) for trophy in trophies]
    evolutions = models.Evolution.query.all()
    evolution_choices = [(evolution.id, evolution.cycles) for evolution in evolutions]

    form = Add_Card(
        rarity_choices=rarity_choices,
        target_choices=target_choices,
        trophy_choices=trophy_choices,
        evolution_choices=evolution_choices
    )

    if request.method == "GET":
        return render_template("add_card.html", form=form, title="Add A Card")
    else:
        if form.validate_on_submit():
            new_card = models.Cards()
            new_card.name = form.name.data
            new_card.rarity = form.rarity.data
            new_card.target = form.target.data
            new_card.pro_con = form.pro_con.data
            new_card.trophies = form.trophies.data
            new_card.evolution = form.evolution.data
            new_card.speed = form.speed.data
            new_card.spawn_time = form.spawn_time.data
            new_card.elixir = form.elixir.data
            new_card.description = form.description.data
            new_card.image = form.image.data

            db.session.add(new_card)
            db.session.commit()  # Don't forget to commit the session
            return redirect(url_for('details', ref=new_card.id))
        else:
            return render_template('add_card.html', form=form, title="Add A Card")




@app.route('/details/<int:ref>')
def details(ref):
    deets = models.Cards.query.filter_by(id=ref).first_or_404()
    return render_template("card_deets.html", cards=deets, title=deets.name)


# Route to render the login and signup page
@app.route('/login_signup')
def login_signup():
    return render_template("login_signup.html")



@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = models.User.query.filter_by(email=email, password=password).first()
    if user:
        login_user(user)
        return redirect(url_for('welcome'))
    else:
        # If the user is not found, return an error message
        return "Invalid email or password"

# Route to handle signup form submission
@app.route('/signup', methods=['POST'])
def signup():
    # Get full name, email, and password from the form
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    new_user = User(full_name=full_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login_signup'))


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
    return render_template('card.html', card=card)


if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
