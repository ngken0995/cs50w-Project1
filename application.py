import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sign-up", methods=["GET", "POST"])
def signUp():
    if request.method == "GET":
        return render_template("signUp.html")
    else:
        username = request.form.get("username").upper()
        password = request.form.get("password")

        if db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).rowcount == 0:
            db.execute("INSERT INTO accounts (username, password) VALUES (:username, :password)", {"username":username, "password":password})
            db.commit()
            return render_template("success.html")
        else:
            return redirect(url_for('signUp'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user" in session:
            return redirect(url_for("profile"))
        
        return render_template("login.html")
    else:
        username = request.form.get("username").upper()
        password = request.form.get("password")

        if db.execute("SELECT * FROM accounts WHERE username = :username AND password = :password", {"username": username, "password":password}).rowcount == 0:
            return redirect(url_for('login')) 
        else:
            session["user"] = username
            return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    if "user" in session:
        username = session["user"]
        return render_template("profile.html", username=username)
    else:
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
