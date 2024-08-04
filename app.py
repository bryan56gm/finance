import os
import re  # Regular expression
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
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

    # Query SQL to obtain the necessary information.
    portfolio_info = db.execute(
        """
        SELECT t.symbol, SUM(t.shares) AS total_shares, MAX(t.price) AS price
        FROM transactions AS t
        WHERE t.user_id = ?
        GROUP BY t.symbol
        HAVING total_shares > 0
    """,
        session["user_id"],
    )

    cash_balance = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"]
    )[0]["cash"]

    total_value = cash_balance

    # Calculate the total value of each participation and the grand total
    for stock in portfolio_info:
        symbol = stock["symbol"]
        shares = stock["total_shares"]
        price = stock["price"]
        quote_info = lookup(symbol)
        if quote_info:
            stock["price"] = quote_info["price"]  
            stock["total_value"] = shares * stock["price"] 
            total_value += stock["total_value"]


    return render_template(
        "index.html",
        portfolio_info=portfolio_info,
        cash_balance=cash_balance,
        total_value=total_value,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        if not shares:
            return apology("must provide number of shares")
        if not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")

        quote_info = lookup(symbol)

        if not quote_info:
            return apology("symbol not found")

        total_cost = int(shares) * quote_info["price"]
        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )[0]["cash"]

        if total_cost > user_cash:
            return apology("insufficient funds")

        # Get current time
        transacted_at = datetime.now()

        # Update user's cash
        db.execute(
            "UPDATE users SET cash = cash - ? WHERE id = ?",
            total_cost,
            session["user_id"],
        )

        # Record the purchase
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, transacted_at) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            symbol,
            shares,
            quote_info["price"],
            transacted_at,
        )

        flash("Bought successfully!", "success")
        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Fetch user's transaction history
    transactions = db.execute(
        "SELECT symbol, shares, price, transacted_at FROM transactions WHERE user_id = ? ORDER BY transacted_at DESC",
        session["user_id"],
    )

    return render_template("history.html", transactions=transactions)


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
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote_info = lookup(symbol)

        if quote_info:
            return render_template("quoted.html", quote_info=quote_info)
        else:
            return apology("symbol not found")

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submited
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Check password complecity
        password = request.form.get("password")
        print(password)
        if not re.match(
            r"^(?=.*[A-Z])(?=.*[\d@#$%^&+=!.ñ])[A-Za-z\d@#$%^&+=!.ñ]{8,}$", password
        ):
            return apology(
                "passwords must have at least 8 characters, including at least one letter, one number and one speacial character"
            )

        # Hash the password
        hashed_password = generate_password_hash(request.form.get("password"))

        # Insert user into the database
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                request.form.get("username"),
                hashed_password,
            )
            return redirect("/")
        except:
            return apology("username already exists")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol and shares are provided
        if not symbol:
            return apology("must provide symbol")
        if not shares:
            return apology("must provide number of shares")
        if not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")

        # Look up the symbol to get the current price
        quote_info = lookup(symbol)

        if not quote_info:
            return apology("symbol not found")

        # Get the user's current shares of the selected stock
        user_shares = db.execute(
            "SELECT SUM(shares) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ?",
            session["user_id"],
            symbol,
        )[0]["total_shares"]

        # Ensure the user has enough shares to sell
        if not user_shares or int(shares) > user_shares:
            return apology("insufficient shares")

        # Calculate the total sale value
        total_sale_value = int(shares) * quote_info["price"]

        # Update user's cash balance
        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?",
            total_sale_value,
            session["user_id"],
        )

        # Record the sale transaction
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, transacted_at) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            symbol,
            -int(shares),
            quote_info["price"],
            datetime.now(),
        )

        flash("Sold successfully!", "success")
        return redirect("/")

    # Render the sell page with a list of owned stocks
    user_stocks = db.execute(
        "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
        session["user_id"],
    )
    return render_template("sell.html", user_stocks=user_stocks)
