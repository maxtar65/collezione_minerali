import json
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from settings import JSON_FILE_PATH

db = SQLAlchemy()

class Mineral(db.Model):
    __tablename__ = 'minerals'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    position = db.Column(db.String(255))
    mineral_species = db.Column(db.String(255))
    variety = db.Column(db.String(255))
    alias = db.Column(db.String(255))
    association = db.Column(db.String(255))
    short_location = db.Column(db.String(255))
    full_location = db.Column(db.Text)
    sizing = db.Column(db.String(50))
    dimensions = db.Column(db.String(255))
    quality = db.Column(db.String(2))
    insert_date = db.Column(db.Date)
    acquisition_date = db.Column(db.Date)
    acquisition_method = db.Column(db.String(255))
    acquired_from = db.Column(db.String(255))
    cost = db.Column(db.Numeric(10, 2))
    exchanged_for = db.Column(db.Text)
    fluorescence_lw = db.Column(db.String(50))
    fluorescence_sw = db.Column(db.String(50))
    radioactive = db.Column(db.String(50))
    notes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Mineral, self).__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def create_from_dict(cls, data):
        return cls(
            code=data.get('Codice Archiviazione'),
            position=data.get('Posizione'),
            mineral_species=data.get('Mineral Specie'),
            variety=data.get('Varieta'),
            alias=data.get('Alias'),
            association=data.get('Associazione'),
            short_location=data.get('Loc. Breve'),
            full_location=data.get('Localita completa'),
            sizing=data.get('Dimensionamento'),
            dimensions=data.get('Dimensioni'),
            quality=data.get('Qualita'),
            insert_date=datetime.strptime(data.get('Data inserimento'), '%d/%m/%Y').date() if data.get('Data inserimento') else None,
            acquisition_date=datetime.strptime(data.get('Data di acquisizione'), '%d/%m/%Y').date() if data.get('Data di acquisizione') else None,
            acquisition_method=data.get('Modalita di acquisizione'),
            acquired_from=data.get('Da/Con'),
            cost=data.get('Costo'),
            exchanged_for=data.get('Scambiato per'),
            fluorescence_lw=data.get('FluorescenzaLW'),
            fluorescence_sw=data.get('FluorescenzaSW'),
            radioactive=data.get('Radioattivo'),
            notes=data.get('Libero01')
        )

def import_json_data():
    if not os.path.exists(JSON_FILE_PATH):
        print(f"Errore: Il file JSON non è stato trovato in {JSON_FILE_PATH}")
        return

    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            minerals_data = json.load(file)
    except json.JSONDecodeError:
        print(f"Errore: Il file {JSON_FILE_PATH} non è un JSON valido")
        return
    except Exception as e:
        print(f"Errore durante la lettura del file JSON: {str(e)}")
        return

    for mineral_data in minerals_data:
        mineral = Mineral.create_from_dict(mineral_data)
        db.session.add(mineral)

    try:
        db.session.commit()
        print(f"Importati con successo {len(minerals_data)} minerali dal file JSON")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante il salvataggio dei dati nel database: {str(e)}")

# This function can be called after the app is initialized to import the data
def init_db():
    db.create_all()
    if Mineral.query.count() == 0:
        import_json_data()