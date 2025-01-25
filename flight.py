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

@app.route('/', methods=['POST'])
def calculate_footprint():
    from_location = request.form.get('from')
    to_location = request.form.get('to')
    result = {'footprint': 5, 'to': to_location, 'from': from_location}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
