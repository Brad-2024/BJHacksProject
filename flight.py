from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins
API_KEY = "QRwlkKzlY2x5TIXL1VPww"
BASE_URL = "https://www.carboninterface.com/api/v1"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
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

    # Add API funtionality here

    result = {'footprint': 5, 'to': to_iata, 'from': from_iata}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
