import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup

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
@login_required
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        isbn = '%' + request.form.get("isbn") + '%'
        title = '%' + request.form.get("title") + '%'
        author = '%' + request.form.get("author") + '%'

        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author", 
                            {"isbn": isbn, "title": title, "author": author}).fetchall()
        if len(books) == 0:
            return apology("No Matches")
        
        return render_template("result.html", books=books)

@app.route("/book/<string:isbn>")
@login_required
def book(isbn):

    session["isbn"] = isbn
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": session["isbn"]}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    return render_template("book.html", book=book, reviews=reviews)

@app.route("/review", methods=["POST"])
@login_required
def review():
    review = request.form.get("review")
    rate = request.form.get("rate")

    row = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = :isbn",
                        {"user_id":session["user_id"], "isbn":session["isbn"]}).fetchone()

    if row is not None:
        return apology("Review has been entered")

    db.execute("INSERT INTO reviews(user_id, review, rate, isbn) VALUES (:user_id, :review, :rate, :isbn)",
                {"user_id":session["user_id"], "review":review, "rate":rate, "isbn":session["isbn"]})

    return redirect("/book",isbn=session["isbn"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username").upper()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure username exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            return apology("username exist")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        if password != confirmation:
            return apology("Password doesn't match.")

        hashPass = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                        {"username":username, "hash":hashPass})
        db.commit()

        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        row = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username").upper()}).fetchone()

        # Ensure username exists and password is correct
        if row is None or not check_password_hash(row['hash'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
