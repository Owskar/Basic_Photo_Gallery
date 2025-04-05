# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Insecure: Using a hardcoded secret key

# Upload folder configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Database initialization
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Create users table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """
    )

    # Create images table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    # Create posts table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            post_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()


# Initialize the database when the app starts
init_db()


# Helper function to check if file extension is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route("/")
def home():
    if "user_id" in session:
        # User is logged in
        return render_template("home.html", username=session.get("username"))
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]  # Insecure: Storing plain text password
        email = request.form["email"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return render_template("register.html", error="Username already exists")

        # Insert new user
        c.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, password, email),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Insecure SQL query: susceptible to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            conn.close()
            return redirect(url_for("dashboard"))
        else:
            conn.close()
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get user details
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    # Get user posts
    c.execute(
        "SELECT * FROM posts WHERE user_id = ? ORDER BY post_date DESC", (user_id,)
    )
    posts = c.fetchall()

    conn.close()

    return render_template("dashboard.html", user=user, posts=posts)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Check if file is in the request
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

        # If user doesn't select a file
        if file.filename == "":
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Insecure: Using user-provided filename directly without sufficient validation
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Save file info to database
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute(
                "INSERT INTO images (user_id, filename) VALUES (?, ?)",
                (session["user_id"], filename),
            )
            conn.commit()
            conn.close()

            return redirect(url_for("gallery"))

    return render_template("upload.html")


@app.route("/gallery")
def gallery():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get user images
    c.execute("SELECT * FROM images WHERE user_id = ?", (user_id,))
    images = c.fetchall()

    conn.close()

    return render_template("gallery.html", images=images)


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get user details
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    conn.close()

    return render_template("profile.html", user=user)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        user_id = session["user_id"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Verify old password
        c.execute(
            "SELECT * FROM users WHERE id = ? AND password = ?", (user_id, old_password)
        )
        user = c.fetchone()

        if user:
            # Update password
            c.execute(
                "UPDATE users SET password = ? WHERE id = ?", (new_password, user_id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("profile"))
        else:
            conn.close()
            return render_template(
                "change_password.html", error="Incorrect old password"
            )

    return render_template("change_password.html")


@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form["content"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Insert new post
        c.execute(
            "INSERT INTO posts (user_id, content) VALUES (?, ?)",
            (session["user_id"], content),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("create_post.html")


if __name__ == "__main__":
    app.run(debug=True)  # Insecure: Debug mode enabled in production
