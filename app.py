from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from dicttoxml import dicttoxml

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # change if your MySQL user is different
app.config['MYSQL_PASSWORD'] = 'johnjohn123'          # enter your MySQL password
app.config['MYSQL_DB'] = 'arieljohnsql'

mysql = MySQL(app)

# Home route
@app.route('/')
def home():
    return "Welcome to the Brands REST API!"

if __name__ == '__main__':
    app.run(debug=True)