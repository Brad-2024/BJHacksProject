import json

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import requests
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

app.secret_key = 'your_secret_key' # Secret key for sessions
app.config['SESSION_TYPE'] = 'filesystem' # Session configuration
Session(app)

API_KEY = "P6h8GSVpyg3mu8Ix1IfjQ"
url = "https://www.carboninterface.com/api/v1/estimates"

# Headers for authentication
headers = {
    "Authorization": "Bearer P6h8GSVpyg3mu8Ix1IfjQ",
    "Content-Type": "application/json"
}

#create a dictionary with iata codes for US airports
iata_codes = {
    "": "empty",
    "Atlanta": "atl",
    "Los Angeles": "lax",
    "Chicago": "ord",
    "Dallas/Fort Worth": "dfw",
    "Denver": "den",
    "New York City": "jfk",
    "San Francisco": "sfo",
    "Seattle": "sea",
    "Miami": "mia",
    "Las Vegas": "las"
}

# Helper function to check if the username exists in the database
def user_exists(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Helper function to add a new user to the database
def add_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    # Login route to authenticate user
    username = request.json.get('username')
    if username:
        if not user_exists(username):  # Check if username is already in the database
            add_user(username)  # Add new user if not present
        session['username'] = username  # Store username in session
        return jsonify({"message": "Login successful", "username": username}), 200
    return jsonify({"error": "Invalid username"}), 400

@app.route('/check-login', methods=['GET'])
def check_login():
    # Route to check if the user is logged in
    if 'username' in session:
        return jsonify({"logged_in": True, "username": session['username']}), 200
    return jsonify({"logged_in": False}), 401

@app.route('/', methods=['POST'])
def get_flight():
    if 'username' not in session:
        return jsonify({"error": "Not authenticated, please log in"}), 401  # Check if the user is logged in
    from_location = request.form.get('from')
    to_location = request.form.get('to')
    return get_iata(from_location, to_location)

def get_iata(from_location, to_location):

    # Placeholder function to get IATA codes
    from_iata = iata_codes.get(from_location)
    to_iata = iata_codes.get(to_location)
    return calculate_footprint(from_iata, to_iata)

def calculate_footprint(from_iata, to_iata):
    data = {
        "type": "flight",
        "passengers": 1,
        "legs": [
            {"departure_airport": f"{from_iata}", "destination_airport": f"{to_iata}"},
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Check the response
    if from_iata == "empty" or to_iata == "empty":
        return jsonify({"error": "empty"})
    elif from_iata == to_iata:
        return jsonify({"error": "same"})
    elif response.status_code == 201:
        response_data = response.json()
        carbon_kg = response_data.get("data", {}).get("attributes", {}).get("carbon_kg")
        print("Carbon footprint (kg):", carbon_kg)
        return jsonify({"footprint": carbon_kg, "from": from_iata, "to": to_iata})
    else:
        print(f"Error: {response.status_code}")
        print("Details:", response.text)


if __name__ == '__main__':
    app.run(debug=True)