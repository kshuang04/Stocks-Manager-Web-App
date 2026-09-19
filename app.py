import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from pytz import timezone
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Aggregate stocks and calculate total
    stocks = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE id = ? GROUP BY symbol HAVING total_shares > 0 ORDER BY symbol", session["user_id"])

    total = 0
    for stock in stocks:
        # Do calculations first
        stock["price"] = lookup(stock["symbol"])["price"]
        stock["total"] = stock["price"] * stock["total_shares"]
        total += stock["total"]

        # Format values to usd
        stock["price"] = usd(stock["price"])
        stock["total"] = usd(stock["total"])

    # Get cash
    cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Calculate grand total
    total += cash

    # Format values to usd
    cash = usd(cash)
    total = usd(total)

    return render_template("index.html", stocks=stocks, cash=cash, total=total)


@app.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    if request.method == "POST":
        curr_password = request.form.get("curr_password")

        if not curr_password:
            return apology("must provide current password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE id = ?", session["user_id"]
        )

        # Ensure password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], curr_password):
            return apology("incorrect password")

        new_password = request.form.get("new_password")
        new_confirmation = request.form.get("new_confirmation")

        # Check if password or confirmation is empty
        if not new_password or not new_confirmation:
            return apology("must provide new password and confirmation")

        # Check if password and confirmation match
        if new_password != new_confirmation:
            return apology("new password and confirmation do not match")

        # Update password in database
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(new_password), session["user_id"])

        flash("Successfully changed password.")
        return redirect("/")
    else:
        return render_template("reset-password.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Check that fields exist
        if not symbol or not shares:
            return apology("must provide symbol and shares")

        # Check for fractional, non-numeric and negative number for shares
        if not shares.isdigit() or int(shares) < 0:
            return apology("shares must be non-negative")

        shares = int(shares)

        # Check for symbol
        quote = lookup(symbol)
        if not quote:
            return apology("symbol not found")

        # Get user's balance
        user_balance = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Check if user has enough balance
        total = quote["price"] * shares
        if user_balance < total:
            return apology("not enough balance")

        # Complete transaction and add transaction to transactions table
        remaining_balance = user_balance - total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining_balance, session["user_id"])
        db.execute("INSERT INTO transactions (id, symbol, price, shares, date) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], quote["symbol"], quote["price"], shares, datetime.now(timezone("America/Los_Angeles")))

        # Redirect user to home page
        flash(f"Successfully bought {shares} shares of {quote["symbol"]}.")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM transactions WHERE id = ?", session["user_id"])

    for row in history:
        row["price"] = usd(row["price"])

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Welcome back!")
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide symbol")

        quote = lookup(symbol)

        if not quote:
            return apology("failed to get quote")

        # Format price to usd
        quote["price"] = usd(quote["price"])

        return render_template("quoted.html", quote=quote)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was provided
        if not username:
            return apology("must provide username")

        # Check if password or confirmation is empty
        if not password or not confirmation:
            return apology("must provide password and confirmation")

        # Check if password and confirmation match
        if password != confirmation:
            return apology("password and confirmation do not match")

        # Check if username already exists and add user to database (hash password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       username, generate_password_hash(password))
        except ValueError:
            return apology("username already exists")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Redirect to "/" (login after registration)
        session.clear()
        session["user_id"] = rows[0]["id"]

        flash("Successfully registered. Welcome!")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Check if symbol
        if not symbol:
            return apology("must provide symbol")

        # Check if shares is non-negative
        if shares < 0:
            return apology("shares must be non-negative")

        # Check if user owns symbol
        target_shares = db.execute(
            "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE id = ? GROUP BY symbol HAVING symbol = ?", session["user_id"], symbol)
        if not target_shares:
            return apology("must own stock to sell")

        # Check if user owns enough shares
        num_shares = target_shares[0]["total_shares"]
        if num_shares < shares:
            return apology("too many shares")

        # Sell stock and add transaction to transactions table
        try:
            quote = lookup(symbol)
        except ValueError:
            return apology("invalid symbol")

        if not quote:
            return apology("failed to get quote")

        total = quote["price"] * shares
        curr_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        print(curr_cash)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", curr_cash + total, session["user_id"])
        db.execute("INSERT INTO transactions (id, symbol, price, shares, date) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], quote["symbol"], quote["price"], -shares, datetime.now(timezone("America/Los_Angeles")))

        # Redirect user to home page
        flash(f"Successfully sold {shares} shares of {quote["symbol"]}.")
        return redirect("/")

    # User reached route via GET
    else:
        stocks = db.execute(
            "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE id = ? GROUP BY symbol ORDER BY symbol", session["user_id"])
        seen = set()
        for stock in stocks:
            seen.add(stock["symbol"])

        return render_template("sell.html", stocks=seen)
