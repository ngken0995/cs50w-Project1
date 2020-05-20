import os

from flask import Flask, session, render_template, request
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

        if db.execute("SELECT * FROM account WHERE username = :username", {"username": username}).rowcount == 0:
            db.execute("INSERT INTO account (username, password) VALUES (:username, :password)", {"username":username, "password":password})
            db.commit()
            return render_template("success.html")
        else:
            return render_template("error.html", message="Username taken.")


