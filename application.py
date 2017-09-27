from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    return apology("(Logged in) TODO")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    
    if request.method == "GET":
        return render_template("buy.html")
    elif request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please enter a Symbol")
        if not request.form.get("amount"):
            return apology("Please enter the amount of shares to buy")
            
        try:
            share = lookup(request.form.get("symbol"))
            if not share:
                return apology("Share with symbol " + request.form.get("symbol") + " not found")
            priceofoneshare = share["price"]
            cost = priceofoneshare * float(request.form.get("amount"))
        except:
            return apology("Error")
        
        #try:
        user = db.execute("SELECT * FROM users WHERE id = :userId", userId=str(session["user_id"]))
            #print("SELECT * FROM users WHERE id = " + session["user_id"])
        #except:
        #   return apology()
        
        if user[0]["cash"] < cost:
            return apology("Not enough cash")
        else:
            remaining = user[0]["cash"] - cost
            
            old = db.execute("SELECT * FROM stocks WHERE userId = :userId AND symbol = :symbol", userId=session["user_id"], symbol=request.form.get("symbol").upper())
            
            if len(old) != 1:
                db.execute("INSERT INTO stocks (userId,symbol,amount) VALUES (:userId,:symbol,:amount)", userId=session["user_id"], symbol=request.form.get("symbol").upper(), amount=float(request.form.get("amount")))
            else:
                db.execute("UPDATE stocks SET amount = :amount WHERE id=:rid", amount=(old[0]["amount"]+float(request.form.get("amount"))), rid=old[0]["id"])
            db.execute("INSERT INTO history (userId,symbol,amount) VALUES (:userId,:symbol,:amount)", userId=session["user_id"], symbol=request.form.get("symbol").upper(), amount=float(request.form.get("amount")))
            db.execute("UPDATE users SET cash = :cash WHERE id=:userId", cash=remaining, userId=session["user_id"])
            return apology("DONE?")
    return apology("TODO")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    elif request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Enter a symbol to search")
        else:
            symbol = request.form.get("symbol").upper()
            quote = lookup(symbol)
            if quote:
                return render_template("quoted.html", q=quote)
            else:
                return apology("Company with symbol " + symbol + " not found")
    return apology("TODO")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        else:
            db.execute("INSERT INTO users (username,hash) VALUES (:username,:hash)", username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")))
    
    return render_template("login.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    return apology("TODO")
