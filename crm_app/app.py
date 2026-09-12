from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import generate_Models
from routes import generate_Routes
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
import os


app = Flask(__name__, static_folder='dist', static_url_path='/')

CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Load configuration from config.py
app.config.from_object(DevelopmentConfig)  # Change to ProductionConfig or TestingConfig as needed

os.makedirs(os.path.join(PROJECT_ROOT, 'instance'), exist_ok=True)
db = SQLAlchemy(app)

Tickets, Notes = generate_Models(db)


with app.app_context():
    db.create_all()


generate_Routes(app, db, Tickets, Notes)

if __name__ == "__main__":
    app.run(debug=True)
