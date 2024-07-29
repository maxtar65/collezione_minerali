from flask import Flask, render_template, jsonify
from models import db, Collezione, Localita, Specie, create_database, import_all_data
from settings import DATABASE_PATH

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/collezione')
def collezione():
    items = Collezione.query.all()
    return render_template('collezione.html', items=items)

@app.route('/localita')
def localita():
    items = Localita.query.all()
    return render_template('localita.html', items=items)

@app.route('/specie')
def specie():
    items = Specie.query.all()
    return render_template('specie.html', items=items)

# API routes
@app.route('/api/collezione')
def api_collezione():
    items = Collezione.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/localita')
def api_localita():
    items = Localita.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/specie')
def api_specie():
    items = Specie.query.all()
    return jsonify([item.to_dict() for item in items])

if __name__ == '__main__':
    with app.app_context():
        create_database()
        import_all_data()
    app.run(debug=True)