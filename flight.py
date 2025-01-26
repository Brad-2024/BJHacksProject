import json
import random
import sqlite3
import os
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
        if user:
            # If the user exists, return success
            return jsonify({'success': True, 'username': username}), 200
        else:
            # If the user does not exist, create an account for the user
            conn.execute(
                'INSERT INTO Users (username, num_flights, total_carbon) VALUES (?, ?, ?)',
                (username, 0, 0.0)
            )
            conn.commit()
            return jsonify({'success': True, 'username': username, 'message': 'New account created!'}), 201
    finally:
        conn.close()

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

@app.route('/add_to_profile', methods=['POST'])
def add_to_profile():
    # Parse JSON data from the request
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid or missing JSON payload'}), 400

    username = data.get('username')
    flightFootprint = data.get('flightFootprint')
    from_airport = data.get('from')
    to_airport = data.get('to')

    if not username or flightFootprint is None or not from_airport or not to_airport:
        return jsonify({'error': 'Missing required data'}), 400

    try:
        # Convert flightFootprint to float
        flightFootprint = float(flightFootprint)
    except ValueError:
        return jsonify({'error': 'Invalid flightFootprint value'}), 400

    # Update the database
    conn = get_db_connection()
    try:
        # Update user's total carbon footprint and flight count
        result = conn.execute(
            '''
            UPDATE Users 
            SET total_carbon = total_carbon + ?, 
                num_flights = num_flights + 1 
            WHERE username = ?
            ''',
            (flightFootprint, username)
        )
        conn.commit()



        # Check if the update affected any rows
        if result.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404

        # Handle the JSON file for flight history
        json_file_path = f"user_history/{username}_flight_history.json"

        # generate a random number for the flight id and make sure it is unique
        flight_id = random.randint(100000, 999999)
        while os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                flight_history = json.load(file)
                existing_ids = {flight['id'] for flight in flight_history}
                if flight_id not in existing_ids:
                    break
                flight_id = random.randint(100000, 999999)
        # Backwards convert from iata codes to city names
        from_airport = list(iata_codes.keys())[list(iata_codes.values()).index(from_airport)]
        to_airport = list(iata_codes.keys())[list(iata_codes.values()).index(to_airport)]
        # Create or update the JSON file
        flight_data = {
            "name": from_airport + " to " + to_airport,
            "id": flight_id,
            "from": from_airport,
            "to": to_airport,
            "carbon_footprint": flightFootprint
        }

        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                flight_history = json.load(file)
        else:
            flight_history = []

        flight_history.append(flight_data)

        with open(json_file_path, 'w') as file:
            json.dump(flight_history, file, indent=4)

        return jsonify({'success': True, 'message': 'Profile updated and flight history saved!'}), 200

    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/get_flight_history', methods=['POST'])
def get_flight_history():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    # Construct the path to the user's flight history JSON file
    json_file_path = f"user_history/{username}_flight_history.json"

    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                flight_history = json.load(file)
            return jsonify(flight_history), 200
        else:
            return jsonify({'error': 'Flight history not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to read flight history', 'message': str(e)}), 500


@app.route('/delete_flight', methods=['POST'])
def delete_flight():
    data = request.get_json()
    username = data.get('username')
    flight_id = data.get('id')

    if not username or not flight_id:
        return jsonify({'error': 'Missing required data'}), 400

    # Path to the user's flight history JSON file
    json_file_path = f"user_history/{username}_flight_history.json"

    try:
        if not os.path.exists(json_file_path):
            return jsonify({'error': 'Flight history not found'}), 404

        # Load the flight history
        with open(json_file_path, 'r') as file:
            flight_history = json.load(file)

        # Find and remove the flight by ID
        flight_to_delete = next((flight for flight in flight_history if flight['id'] == flight_id), None)

        if not flight_to_delete:
            return jsonify({'error': 'Flight not found'}), 404

        # Remove the flight from the list
        flight_history = [flight for flight in flight_history if flight['id'] != flight_id]

        # Save the updated flight history back to the file
        with open(json_file_path, 'w') as file:
            json.dump(flight_history, file, indent=4)

        # Update the database
        carbon_to_deduct = flight_to_delete['carbon_footprint']

        conn = get_db_connection()
        try:
            # Retrieve the current values from the database
            user_data = conn.execute(
                'SELECT total_carbon, num_flights FROM Users WHERE username = ?',
                (username,)
            ).fetchone()

            if not user_data:
                return jsonify({'error': 'User not found'}), 404

            # Calculate the new values
            total_carbon = max(0, user_data['total_carbon'] - carbon_to_deduct)  # Ensure carbon does not go negative
            num_flights = max(0, user_data['num_flights'] - 1)  # Ensure flights do not go negative

            # Update the database
            conn.execute(
                'UPDATE Users SET total_carbon = ?, num_flights = ? WHERE username = ?',
                (total_carbon, num_flights, username)
            )
            conn.commit()

        finally:
            conn.close()

        return jsonify({'success': True, 'message': 'Flight deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to delete flight', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)