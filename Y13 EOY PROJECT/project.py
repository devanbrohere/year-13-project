from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    # Render the home page
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
