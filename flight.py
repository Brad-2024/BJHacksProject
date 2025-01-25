import json
import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins
API_KEY = "P6h8GSVpyg3mu8Ix1IfjQ"
url = "https://www.carboninterface.com/api/v1/estimates"

# Headers for authentication
headers = {
    "Authorization": "Bearer P6h8GSVpyg3mu8Ix1IfjQ",
    "Content-Type": "application/json"
}

# create a dictionary with iata codes for US airports
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


def get_db_connection():
    conn = sqlite3.connect('identifier.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Parse JSON from the request
    username = data.get('username')  # Get username from the JSON

    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    conn = get_db_connection()
    try:
        # Query the database for the username
        user = conn.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
    finally:
        conn.close()

    if user:
        # If the user exists, return success
        return jsonify({'success': True, 'username': username}), 200
    else:
        # If the user does not exist, return an error
        return jsonify({'success': False, 'message': 'Invalid username'}), 401


@app.route('/', methods=['POST'])
def get_flight():
    from_location = request.form.get('from')
    to_location = request.form.get('to')
    username = request.form.get('username')

    # Check for missing or empty inputs
    if not from_location or not to_location:
        return jsonify({"error": "empty"}), 400

    # Call get_iata to process inputs
    return get_iata(from_location, to_location, username)


def get_iata(from_location, to_location, username):
    # Placeholder function to get IATA codes
    from_iata = iata_codes.get(from_location)
    to_iata = iata_codes.get(to_location)
    return calculate_footprint(from_iata, to_iata, username)


def calculate_footprint(from_iata, to_iata, username):
    data = {
        "type": "flight",
        "passengers": 1,
        "legs": [
            {"departure_airport": f"{from_iata}", "destination_airport": f"{to_iata}"},
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    print(f"from_iata: {from_iata}, to_iata: {to_iata}")
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


@app.route('/account-info', methods=['POST'])
def account_info():
    # Extract username from the JSON payload
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    # Connect to the database
    try:
        conn = get_db_connection()
        user_data = conn.execute(
            'SELECT total_carbon, num_flights FROM Users WHERE username = ?',
            (username,)
        ).fetchone()

        if user_data is None:
            return jsonify({'error': 'User not found'}), 404

        total_carbon = user_data['total_carbon']
        total_carbon = round(total_carbon, 2)
        num_flights = user_data['num_flights']
        print(total_carbon, num_flights)
        return jsonify({
            'carbon_total': total_carbon,
            'flight_total': num_flights
        }), 200
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)