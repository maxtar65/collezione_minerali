import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'db.sqlite3')
# dati esistenti da importare
DATA_DIR = os.path.join(BASE_DIR, 'data')