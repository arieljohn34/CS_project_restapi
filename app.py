from flask import Flask, request, render_template, redirect, url_for, jsonify, Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# -------------------------
# MySQL Configuration
# -------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'johnjohn123'
app.config['MYSQL_DB'] = 'arieljohnsql'
mysql = MySQL(app)

# -------------------------
# JWT Configuration
# -------------------------
app.config["JWT_SECRET_KEY"] = "jwtsecretkey123"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# -------------------------
# Home route
# -------------------------
@app.route("/")
def home():
    return redirect(url_for('login'))

# -------------------------
# Registration
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "user")

        if not email or not password:
            return jsonify({"error": "Email and Password are required"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE email=%s", (email,))
        exists = cursor.fetchone()

        if exists:
            cursor.close()
            return jsonify({"error": "Account already exists"}), 409

        hashed_password = generate_password_hash(password)
        access_token = create_access_token(identity={"email": email, "role": role})

        cursor.execute(
            "INSERT INTO accounts (email, password, role, jwt_token) VALUES (%s, %s, %s, %s)",
            (email, hashed_password, role, access_token)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Account created successfully!", "access_token": access_token}), 201

    return render_template("register.html")

# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return jsonify({"error": "Email and Password are required"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE email=%s", (email,))
        account = cursor.fetchone()
        cursor.close()

        if account and check_password_hash(account["password"], password):
            access_token = create_access_token(identity={"email": account["email"], "role": account["role"]})

            # Store token in database
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE accounts SET jwt_token=%s WHERE email=%s", (access_token, email))
            mysql.connection.commit()
            cursor.close()

            # Redirect to dashboard
            return redirect(url_for('dashboard'))

        return jsonify({"error": "Invalid credentials"}), 401

    return render_template("login.html")

# -------------------------
# Dashboard (JWT Protected)
# -------------------------
@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    identity = get_jwt_identity()
    return jsonify({"message": f"Welcome {identity['email']}! Your role is {identity['role']}."})

# -------------------------
# Logout
# -------------------------
@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "You have been logged out. Discard your token on the client side."})

# -------------------------
# Brands Blueprint
# -------------------------
brands_bp = Blueprint('brands', __name__, url_prefix='/api/brands')

@brands_bp.route("", methods=["GET"])
def get_brands():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM brands")
    brands = cursor.fetchall()
    cursor.close()
    return jsonify(brands), 200

@brands_bp.route("/<int:id>", methods=["GET"])
def get_brand(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM brands WHERE idbrands=%s", (id,))
    brand = cursor.fetchone()
    cursor.close()
    if not brand:
        return jsonify({"error": "Brand not found"}), 404
    return jsonify(brand), 200

@brands_bp.route("", methods=["POST"])
def create_brand():
    data = request.get_json()
    phone = data.get("Phone")
    desktop = data.get("Desktop")
    laptop = data.get("Laptop")

    if not any([phone, desktop, laptop]):
        return jsonify({"error": "At least one field is required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO brands (Phone, Desktop, Laptop) VALUES (%s, %s, %s)", (phone, desktop, laptop))
    mysql.connection.commit()
    brand_id = cursor.lastrowid
    cursor.close()
    return jsonify({"message": "Brand created", "id": brand_id}), 201

@brands_bp.route("/<int:id>", methods=["PUT"])
def update_brand(id):
    data = request.get_json()
    phone = data.get("Phone")
    desktop = data.get("Desktop")
    laptop = data.get("Laptop")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM brands WHERE idbrands=%s", (id,))
    brand = cursor.fetchone()
    if not brand:
        cursor.close()
        return jsonify({"error": "Brand not found"}), 404

    cursor.execute("UPDATE brands SET Phone=%s, Desktop=%s, Laptop=%s WHERE idbrands=%s", (phone, desktop, laptop, id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Brand updated"}), 200

@brands_bp.route("/<int:id>", methods=["DELETE"])
def delete_brand(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM brands WHERE idbrands=%s", (id,))
    brand = cursor.fetchone()
    if not brand:
        cursor.close()
        return jsonify({"error": "Brand not found"}), 404

    cursor.execute("DELETE FROM brands WHERE idbrands=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Brand deleted"}), 200

@brands_bp.route("/search", methods=["GET"])
def search_brands():
    phone = request.args.get("phone")
    desktop = request.args.get("desktop")
    laptop = request.args.get("laptop")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = "SELECT * FROM brands WHERE 1=1"
    params = []

    if phone:
        query += " AND Phone LIKE %s"
        params.append(f"%{phone}%")

    if desktop:
        query += " AND Desktop LIKE %s"
        params.append(f"%{desktop}%")

    if laptop:
        query += " AND Laptop LIKE %s"
        params.append(f"%{laptop}%")

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()

    return jsonify(results), 200


# Register blueprint
app.register_blueprint(brands_bp)

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
