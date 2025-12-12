Project Overview

This project implements a Flask-based REST API with MySQL integration, JWT authentication, and structured Python modules. The system provides secure user authentication and a public CRUD API, with consistent HTTP responses to support debugging and integration.


1. Database Setup

The project begins with creating a MySQL database. Defining the schema early ensures clarity on the required tables and relationships. This structure serves as the foundation for the application’s modules and API endpoints.


2. Project Structure and Module Organization

A structured folder layout was created for:
Python modules
API blueprints
Utility functions
Configuration files


3. Virtual Environment Setup

A Python virtual environment (venv) was created to isolate dependencies.
All packages are installed from requirements.txt, ensuring consistency across development environments:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt



4. JWT Authentication API

A dedicated JWT authentication API was implemented to manage:
User login
Token creation
Token validation
Secure access to protected routes


5. Public CRUD API

A separate public API was created to perform CRUD operations.
This API interacts with the MySQL database using Flask-MySQLdb and follows standard REST principles.



6. HTTP Response Handling

Custom HTTP responses were developed to ensure that API interactions return clear status codes (200–400 range).
These responses help with:
Debugging
Client-side integration
Ensuring predictable behavior for each reques





