from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

@app.route('/', methods=['POST'])
def calculate_footprint():
    result = {'footprint': 5}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
