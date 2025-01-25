import json

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

#create a dictionary with iata codes for US airports
iata_codes = {
    "Atlanta": "ATL",
    "Los Angeles": "LAX",
    "Chicago": "ORD",
    "Dallas/Fort Worth": "DFW",
    "Denver": "DEN",
    "New York City": "JFK",
    "San Francisco": "SFO",
    "Seattle": "SEA",
    "Miami": "MIA",
    "Las Vegas": "LAS"
}
@app.route('/', methods=['POST'])
def get_flight():
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
        "passengers": 2,
        "legs": [
            {"departure_airport": "sfo", "destination_airport": "yyz"},
            {"departure_airport": "yyz", "destination_airport": "sfo"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 201:
        response_data = response.json()
        carbon_kg = response_data.get("data", {}).get("attributes", {}).get("carbon_kg")
        print("Carbon footprint (kg):", carbon_kg)
        return jsonify({"footprint": carbon_kg, "from": from_iata, "to": to_iata})
    else:
        print(f"Error: {response.status_code}")
        print("Details:", response.text)


if __name__ == '__main__':
    app.run(debug=True)