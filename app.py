
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import sqlite3
import os

app = Flask(__name__)

# Secret key for displaying messages
app.secret_key = "localmart-development-secret-key"

# Database location
DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


# Connect to database
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create users table
def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Customer registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check empty fields
        if not name or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "error")

        # Check password length
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")

        # Check password confirmation
        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        else:

            connection = get_db_connection()

            try:

                # Hash password before storing it
                hashed_password = generate_password_hash(password)

                connection.execute("""
                    INSERT INTO users (name, email, password_hash)
                    VALUES (?, ?, ?)
                """, (name, email, hashed_password))

                connection.commit()

                flash("Account created successfully!", "success")
                return redirect(url_for("home"))

            except sqlite3.IntegrityError:
                flash("This email is already registered.", "error")

            finally:
                connection.close()

    return render_template("register.html")


# Start application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
