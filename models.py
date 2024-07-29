import os
import json
import chardet
import traceback
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from settings import DATA_DIR
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

db = SQLAlchemy()

def import_from_json(cls, json_file):
    if not os.path.exists(json_file):
        print(f"File non trovato: {json_file}")
        return

    def detect_encoding(file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        return chardet.detect(raw_data)['encoding']

    def parse_date(date_string):
        if date_string == '00/00/0000' or not date_string:
            return None
        try:
            return datetime.strptime(date_string.strip(), '%d/%m/%Y').date()
        except ValueError:
            print(f"Errore nel parsing della data: {date_string}")
            return None

    encoding = detect_encoding(json_file)
    print(f"Detected encoding for {json_file}: {encoding}")

    try:
        with open(json_file, 'r', encoding=encoding) as file:
            data = json.load(file)
    except UnicodeDecodeError:
        print(f"Errore nella decodifica del file {json_file}. Prova con encoding='latin-1'")
        with open(json_file, 'r', encoding='latin-1') as file:
            data = json.load(file)

    valid_columns = inspect(cls).columns.keys()
    records_processed = 0
    records_added = 0
    records_updated = 0

    for item in data:
        try:
            filtered_item = {k: v for k, v in item.items() if k in valid_columns}
            
            if 'data_ins' in filtered_item:
                filtered_item['data_ins'] = parse_date(filtered_item['data_ins'])
            if 'data_acq' in filtered_item:
                filtered_item['data_acq'] = parse_date(filtered_item['data_acq'])

            if cls.__name__ == 'Localita':
                key_field = 'cod_loc'
            elif cls.__name__ == 'Specie':
                key_field = 'specie'
            elif 'codice' in filtered_item:
                key_field = 'codice'
            else:
                key_field = next(iter(filtered_item))

            existing_record = cls.query.filter_by(**{key_field: filtered_item[key_field]}).first()

            if existing_record:
                for key, value in filtered_item.items():
                    setattr(existing_record, key, value)
                records_updated += 1
            else:
                new_record = cls(**filtered_item)
                db.session.add(new_record)
                records_added += 1

            records_processed += 1

            if records_processed % 100 == 0:
                print(f"Processed {records_processed} records for {cls.__name__}")
                db.session.commit()

        except Exception as e:
            print(f"Errore durante l'importazione dell'item: {item}")
            print(f"Errore: {e}")
            print(traceback.format_exc())

    try:
        db.session.commit()
        print(f"Importazione completata per {cls.__name__}:")
        print(f"  Records processed: {records_processed}")
        print(f"  Records added: {records_added}")
        print(f"  Records updated: {records_updated}")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Errore di integrità durante il commit per {cls.__name__}: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Errore generico durante il commit per {cls.__name__}: {e}")
        print(traceback.format_exc())

class Collezione(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    codice = db.Column(db.Integer, unique=True, nullable=False)
    posizione = db.Column(db.String(50))
    specie = db.Column(db.String(100), nullable=False)
    varieta = db.Column(db.String(100))
    alias = db.Column(db.String(100))
    associazione = db.Column(db.String(100))
    cod_loc = db.Column(db.String(30), db.ForeignKey('localita.cod_loc'))
    dimensionamento = db.Column(db.String(50))
    qualita = db.Column(db.String(10))
    data_ins = db.Column(db.Date)
    data_acq = db.Column(db.Date)
    mod_acq = db.Column(db.String(50))
    acquisito_da = db.Column(db.String(100))
    costo = db.Column(db.Float)
    luogo_acq = db.Column(db.String(50))
    scambiato_per = db.Column(db.String(50))
    note = db.Column(db.Text)
    referenza = db.Column(db.String(100))
    descrizione = db.Column(db.String(200))
    fluor_lw = db.Column(db.String(20))
    fluor_sw = db.Column(db.String(20))
    radioattivo = db.Column(db.String(20))
    tl = db.Column(db.Boolean)

    serialize_rules = ('-localita',)

    @classmethod
    def import_from_json(cls, json_file):
        import_from_json(cls, json_file)

class Localita(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    cod_loc = db.Column(db.String(100), unique=True, nullable=False)
    cava_min = db.Column(db.String(255))
    loc_monte = db.Column(db.String(255))
    valle = db.Column(db.String(50))
    comune = db.Column(db.String(50))
    distr_pref = db.Column(db.String(50))
    provincia = db.Column(db.String(50))
    regione = db.Column(db.String(50))
    dipartimento = db.Column(db.String(50))
    stato = db.Column(db.String(50))
    nazione = db.Column(db.String(100))
    note = db.Column(db.Text)
    cod_mindat = db.Column(db.Integer)

    serialize_rules = ('-collezione',)

    @classmethod
    def import_from_json(cls, json_file):
        import_from_json(cls, json_file)

class Specie(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    specie = db.Column(db.String(100), unique=True, nullable=False)
    formula = db.Column(db.String(255))
    sistema_xx = db.Column(db.String(50))
    status = db.Column(db.String(50))
    sottogruppo = db.Column(db.String(50))
    gruppo = db.Column(db.String(100))
    supergruppo = db.Column(db.String(50))
    famiglia = db.Column(db.String(50))
    sottoclasse = db.Column(db.String(100))
    classe = db.Column(db.String(100))

    @classmethod
    def import_from_json(cls, json_file):
        import_from_json(cls, json_file)

def import_all_data():
    print("Inizio importazione dati...")
    
    print("Importazione Collezione...")
    Collezione.import_from_json(os.path.join(DATA_DIR, 'DB_Collezione_luglio_2024_OK.json'))
    print(f"Numero di record in Collezione dopo l'importazione: {Collezione.query.count()}")
    
    print("Importazione Localita...")
    Localita.import_from_json(os.path.join(DATA_DIR, 'DB_Localita_luglio_2024_OK.json'))
    print(f"Numero di record in Localita dopo l'importazione: {Localita.query.count()}")
    
    print("Importazione Specie...")
    Specie.import_from_json(os.path.join(DATA_DIR, 'DB_Specie_luglio_2024_OK.json'))
    print(f"Numero di record in Specie dopo l'importazione: {Specie.query.count()}")
    
    print("Importazione dati completata.")

def create_database():
    db.create_all()