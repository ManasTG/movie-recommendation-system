import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify
from tmdb import get_movie_details
import sys
import os

# Parent folder ko import path me add karo
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from recommendation import recommend

app = Flask(__name__)

# Bcrypt initialize
bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return "Movie Recommendation API is Running 🚀"


# ==========================
# SIGNUP API
# ==========================
@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, hashed_password)
        )

        conn.commit()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "message": "Email already exists"
        }), 400

    finally:
        conn.close()


# ==========================
# LOGIN API
# ==========================
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and Password are required"
        }), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return jsonify({
            "message": "User not found"
        }), 404

    if bcrypt.check_password_hash(user[2], password):
        return jsonify({
            "message": "Login successful",
            "user_id": user[0],
            "username": user[1]
        }), 200

    return jsonify({
        "message": "Invalid password"
    }), 401


# ==========================
# ADD TO FAVORITES
# ==========================
@app.route("/favorites", methods=["POST"])
def add_favorite():

    data = request.get_json()

    user_id = data.get("user_id")
    movie_id = data.get("movie_id")
    movie_title = data.get("movie_title")

    if not user_id or not movie_id or not movie_title:
        return jsonify({
            "message": "All fields are required"
        }), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO favorites(user_id, movie_id, movie_title)
        VALUES (?, ?, ?)
        """,
        (user_id, movie_id, movie_title)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Movie added to favorites"
    }), 201


# ==========================
# VIEW FAVORITES
# ==========================
@app.route("/favorites/<int:user_id>", methods=["GET"])
def view_favorites(user_id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT movie_id, movie_title
        FROM favorites
        WHERE user_id=?
        """,
        (user_id,)
    )

    favorites = cursor.fetchall()

    conn.close()

    data = []

    for movie in favorites:
        data.append({
            "movie_id": movie[0],
            "movie_title": movie[1]
        })

    return jsonify(data)

# ==========================
# REMOVE FAVORITE
# ==========================
@app.route("/favorites", methods=["DELETE"])
def remove_favorite():

    data = request.get_json()

    user_id = data.get("user_id")
    movie_id = data.get("movie_id")

    if not user_id or not movie_id:
        return jsonify({
            "message": "User ID and Movie ID are required"
        }), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM favorites
        WHERE user_id=? AND movie_id=?
        """,
        (user_id, movie_id)
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({
            "message": "Favorite movie not found"
        }), 404

    conn.close()

    return jsonify({
        "message": "Movie removed from favorites"
    }), 200


# ==========================
# RECOMMENDATION API
# ==========================
@app.route("/recommend", methods=["GET"])
def get_recommendations():

    movie = request.args.get("movie")

    if not movie:
        return jsonify({"error": "Movie name is required"}), 400

    result = recommend(movie)

    for movie_data in result:

        try:
            details = get_movie_details(movie_data["title"])

            print("Movie:", movie_data["title"])
            print("TMDB Response:", details)

            if details:
                movie_data["rating"] = details["rating"]
                movie_data["poster"] = details["poster"]
                movie_data["overview"] = details["overview"]
                movie_data["release_date"] = details["release_date"]

        except Exception as e:
            print("TMDB Error:", e)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)