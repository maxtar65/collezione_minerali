import os

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://your_username:your_password@localhost/mineral_collection'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask configuration
DEBUG = True
SECRET_KEY = 'your_secret_key_here'

# File paths
JSON_FILE_PATH = os.path.join(BASE_DIR, 'database', 'json', 'DB_Collezione_rid.json')

# Templates and static folders
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Logging configuration
LOG_FOLDER = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_FOLDER, 'app.log')

# Ensure necessary directories exist
os.makedirs(LOG_FOLDER, exist_ok=True)