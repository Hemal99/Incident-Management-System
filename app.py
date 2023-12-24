from flask import Flask, jsonify

app = Flask(__name__)

# Define a route for the root endpoint
@app.route('/')
def hello():
    return jsonify(message='Hello, this is your Flask API!')

# Define a route for a custom endpoint
@app.route('/api/get-data')
def greet(name):
    return jsonify(message=f'Hello, {name}!')

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)
