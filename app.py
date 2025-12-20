import os
import re
from datetime import datetime
from sqlalchemy import text

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from helpers import apology, login_required, lookup, usd

# Load environment variables from .env
load_dotenv()

# Configure application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------------
# MODELOS
# ---------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    cash = db.Column(db.Float, default=10000.0)
    transactions = db.relationship("Transaction", backref="user", lazy=True)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transacted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tablas automáticamente si no existen
with app.app_context():
    db.create_all()

# ---------------------
# RUTAS
# ---------------------
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    portfolio_info = (
        db.session.query(
            Transaction.symbol,
            db.func.sum(Transaction.shares).label("total_shares"),
            db.func.max(Transaction.price).label("price")
        )
        .filter(Transaction.user_id == session["user_id"])
        .group_by(Transaction.symbol)
        .having(db.func.sum(Transaction.shares) > 0)
        .all()
    )

    user = User.query.get(session["user_id"])
    cash_balance = user.cash
    total_value = cash_balance

    portfolio = []
    for stock in portfolio_info:
        quote_info = lookup(stock.symbol)
        if quote_info:
            price = quote_info["price"]
            total = stock.total_shares * price
            total_value += total
            portfolio.append({
                "symbol": stock.symbol,
                "total_shares": stock.total_shares,
                "price": price,
                "total_value": total
            })

    return render_template(
        "index.html",
        portfolio_info=portfolio,
        cash_balance=cash_balance,
        total_value=total_value
    )

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")

        quote_info = lookup(symbol)
        if not quote_info:
            return apology("symbol not found")

        total_cost = int(shares) * quote_info["price"]
        user = User.query.get(session["user_id"])
        if total_cost > user.cash:
            return apology("insufficient funds")

        user.cash -= total_cost
        transaction = Transaction(
            user_id=user.id,
            symbol=symbol,
            shares=int(shares),
            price=quote_info["price"],
            transacted_at=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Bought successfully!", "success")
        return redirect("/")

    return render_template("buy.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid number of shares")

        user = User.query.get(session["user_id"])
        owned_shares = (
            db.session.query(db.func.sum(Transaction.shares))
            .filter(Transaction.user_id == user.id, Transaction.symbol == symbol)
            .scalar()
        )

        if not owned_shares or int(shares) > owned_shares:
            return apology("insufficient shares")

        quote_info = lookup(symbol)
        if not quote_info:
            return apology("symbol not found")

        total_value = int(shares) * quote_info["price"]
        user.cash += total_value

        transaction = Transaction(
            user_id=user.id,
            symbol=symbol,
            shares=-int(shares),
            price=quote_info["price"],
            transacted_at=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Sold successfully!", "success")
        return redirect("/")

    user_stocks = (
        db.session.query(Transaction.symbol)
        .filter(Transaction.user_id == session["user_id"])
        .group_by(Transaction.symbol)
        .having(db.func.sum(Transaction.shares) > 0)
        .all()
    )
    return render_template("sell.html", user_stocks=user_stocks)

@app.route("/history")
@login_required
def history():
    transactions = (
        Transaction.query.filter_by(user_id=session["user_id"])
        .order_by(Transaction.transacted_at.desc())
        .all()
    )
    return render_template("history.html", transactions=transactions)

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote_info = lookup(symbol)
        if quote_info:
            return render_template("quoted.html", quote_info=quote_info)
        return apology("symbol not found")
    return render_template("quote.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return apology("must provide username and password", 403)

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.hash, password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user.id
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("must provide all fields")

        if password != confirmation:
            return apology("passwords do not match")

        if not re.match(r"^(?=.*[A-Z])(?=.*[\d@#$%^&+=!.ñ])[A-Za-z\d@#$%^&+=!.ñ]{8,}$", password):
            return apology("password must be 8+ chars, with a letter, number, and special char")

        hashed_password = generate_password_hash(password)
        user = User(username=username, hash=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            return apology("username already exists")

        return redirect("/")

    return render_template("register.html")

# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
