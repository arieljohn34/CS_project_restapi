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
# Get all brands (JSON or XML)
@app.route('/brands', methods=['GET'])
def get_brands():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM brands")
    rows = cursor.fetchall()
    cursor.close()

    # Convert rows to list of dictionaries
    brands_list = []
    for row in rows:
        brands_list.append({
            'id': row[0],
            'brand_name': row[1],
            'model': row[2],
            'description': row[3]
        })

    # Check for output format
    fmt = request.args.get('format', 'json')
    if fmt.lower() == 'xml':
        xml_data = dicttoxml(brands_list, custom_root='brands', attr_type=False)
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        return response
    else:
        return jsonify(brands_list)



if __name__ == '__main__':
    app.run(debug=True)
