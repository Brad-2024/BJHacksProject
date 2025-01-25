from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

@app.route('/', methods=['POST'])
def calculate_footprint():
    from_location = request.form.get('from')
    to_location = request.form.get('to')
    result = {'footprint': 5, 'to': to_location, 'from': from_location}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
