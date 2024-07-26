from flask import Flask, render_template, request, redirect, url_for
from models import db, Mineral, init_db
from settings import DEBUG, SECRET_KEY, TEMPLATE_FOLDER, STATIC_FOLDER, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
import logging
from logging.handlers import RotatingFileHandler
from settings import LOG_FILE

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize SQLAlchemy
db.init_app(app)

# Set up logging
handler = RotatingFileHandler(LOG_FILE, maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

@app.route('/')
def index():
    minerals = Mineral.query.all()
    app.logger.info('Accessed index page')
    return render_template('index.html', minerals=minerals)

@app.route('/mineral/<int:id>')
def mineral_detail(id):
    mineral = Mineral.query.get_or_404(id)
    app.logger.info(f'Accessed detail page for mineral id {id}')
    return render_template('detail.html', mineral=mineral)

@app.route('/add', methods=['GET', 'POST'])
def add_mineral():
    if request.method == 'POST':
        mineral_data = {
            'Codice Archiviazione': request.form['code'],
            'Mineral Specie': request.form['mineral_species'],
            'Localita completa': request.form['full_location'],
            # Add other fields as necessary
        }
        
        new_mineral = Mineral.create_from_dict(mineral_data)
        db.session.add(new_mineral)
        db.session.commit()
        
        app.logger.info(f'Added new mineral: {mineral_data["Codice Archiviazione"]}')
        return redirect(url_for('index'))
    
    return render_template('add.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run()