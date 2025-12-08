from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from dicttoxml import dicttoxml
import pytest
from unittest.mock import patch, MagicMock

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
            'Phone': row[1],
            'Desktop': row[2],
            'Laptop': row[3]
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

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.mysql.connection')
def test_get_brands_json_default_format(mock_mysql_conn, client):
    """Test GET /brands returns JSON format by default"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, 'Apple', 'iOS', 'macOS'),
        (2, 'Samsung', 'Android', 'Windows')
    ]
    
    response = client.get('/brands')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['id'] == 1
    assert data[0]['Phone'] == 'Apple'
    assert data[1]['Desktop'] == 'Android'
    mock_cursor.close.assert_called_once()

@patch('app.mysql.connection')
def test_get_brands_xml_format(mock_mysql_conn, client):
    """Test GET /brands?format=xml returns XML response"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'iOS', 'macOS')]
    
    response = client.get('/brands?format=xml')
    assert response.status_code == 200
    assert response.content_type == 'application/xml'
    assert b'<brands>' in response.data
    assert b'</brands>' in response.data
    mock_cursor.close.assert_called_once()

@patch('app.mysql.connection')
def test_get_brands_empty_list(mock_mysql_conn, client):
    """Test GET /brands returns empty list when no brands exist"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    
    response = client.get('/brands')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []
    assert isinstance(data, list)

@patch('app.mysql.connection')
def test_get_brands_case_insensitive_xml(mock_mysql_conn, client):
    """Test format parameter is case-insensitive"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'iOS', 'macOS')]
    
    for fmt in ['XML', 'Xml', 'xML']:
        response = client.get(f'/brands?format={fmt}')
        assert response.status_code == 200
        assert response.content_type == 'application/xml'

@patch('app.mysql.connection')
def test_get_brands_invalid_format_defaults_json(mock_mysql_conn, client):
    """Test invalid format parameter defaults to JSON"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'iOS', 'macOS')]
    
    response = client.get('/brands?format=pdf')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

@patch('app.mysql.connection')
def test_get_brands_multiple_rows(mock_mysql_conn, client):
    """Test GET /brands with multiple brand entries"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, 'Apple', 'iOS', 'macOS'),
        (2, 'Samsung', 'Android', 'Windows'),
        (3, 'Google', 'Android', 'ChromeOS'),
        (4, 'Microsoft', 'Windows Phone', 'Windows')
    ]
    
    response = client.get('/brands')
    data = response.get_json()
    assert len(data) == 4
    assert data[2]['Phone'] == 'Google'
    assert data[3]['id'] == 4

@patch('app.mysql.connection')
def test_get_brands_cursor_operations(mock_mysql_conn, client):
    """Test that cursor is properly opened and closed"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    
    client.get('/brands')
    mock_mysql_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM brands")
    mock_cursor.close.assert_called_once()

@patch('app.mysql.connection')
def test_get_brands_data_mapping(mock_mysql_conn, client):
    """Test that database rows are correctly mapped to JSON keys"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(5, 'TestBrand', 'TestPhone', 'TestLaptop')]
    
    response = client.get('/brands')
    data = response.get_json()
    assert data[0]['id'] == 5
    assert data[0]['Phone'] == 'TestPhone'
    assert data[0]['Desktop'] == 'TestPhone'
    assert data[0]['Laptop'] == 'TestLaptop'

@patch('app.mysql.connection')
def test_get_brands_xml_contains_all_fields(mock_mysql_conn, client):
    """Test XML response contains all required fields"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'iOS', 'macOS')]
    
    response = client.get('/brands?format=xml')
    assert b'id' in response.data
    assert b'Phone' in response.data
    assert b'Desktop' in response.data
    assert b'Laptop' in response.data

@patch('app.mysql.connection')
def test_get_brands_no_format_parameter(mock_mysql_conn, client):
    """Test GET /brands without format parameter uses JSON"""
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'iOS', 'macOS')]
    
    response = client.get('/brands')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
