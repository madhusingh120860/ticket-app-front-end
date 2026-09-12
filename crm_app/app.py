from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import generate_Models
from routes import generate_Routes
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
import os


app = Flask(__name__, static_folder='dist', static_url_path='/')

CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# 1. Establish the absolute project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# 2. Force create the instance folder right inside crm_app/
INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

# 3. Load configurations dynamically based on environment
if os.environ.get('RENDER'):
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# 4. OVERRIDE: Guarantee the database path maps perfectly to our created directory
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    f"sqlite:///{os.path.join(INSTANCE_PATH, 'app.db')}"
)

# Initialize database safely now
db = SQLAlchemy(app)

Tickets, Notes = generate_Models(db)

with app.app_context():
    db.create_all()

generate_Routes(app, db, Tickets, Notes)

if __name__ == "__main__":
    app.run(debug=True)
