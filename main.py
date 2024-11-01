
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api')
def hello_world():
    return "<h1>Hello, Welcome to VLESIM FBS!</h1>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
