import json
import os
import chardet
from datetime import datetime
import traceback
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from models import db, Collezione, Localita, Specie
from app import app

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

def import_from_json(cls, json_file):
    if not os.path.exists(json_file):
        print(f"File non trovato: {json_file}")
        return

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
    invalid_species = 0

    for item in data:
        try:
            filtered_item = {k: v for k, v in item.items() if k in valid_columns or k == 'specie'}
            
            if 'data_ins' in filtered_item:
                filtered_item['data_ins'] = parse_date(filtered_item['data_ins'])
            if 'data_acq' in filtered_item:
                filtered_item['data_acq'] = parse_date(filtered_item['data_acq'])

            if cls.__name__ == 'Collezione':
                # Gestione speciale per Collezione
                specie_nome = filtered_item.pop('specie', None)
                if specie_nome:
                    specie = Specie.query.filter_by(specie=specie_nome).first()
                    if specie:
                        filtered_item['specie_id'] = specie.id
                        filtered_item['specie_nome'] = specie.specie
                    else:
                        print(f"Specie non valida trovata: {specie_nome}")
                        filtered_item['specie_id'] = None
                        filtered_item['specie_nome'] = specie_nome
                        filtered_item['specie_non_valida'] = specie_nome
                        invalid_species += 1
                key_field = 'codice'
            elif cls.__name__ == 'Localita':
                key_field = 'cod_loc'
            elif cls.__name__ == 'Specie':
                key_field = 'specie'
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
        if cls.__name__ == 'Collezione':
            print(f"  Invalid species found: {invalid_species}")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Errore di integrità durante il commit per {cls.__name__}: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Errore generico durante il commit per {cls.__name__}: {e}")
        print(traceback.format_exc())

def import_all_data(data_dir):
    print("Inizio importazione dati...")
    
    print("Importazione Specie...")
    import_from_json(Specie, os.path.join(data_dir, 'DB_Specie_luglio_2024_OK.json'))
    print(f"Numero di record in Specie dopo l'importazione: {Specie.query.count()}")
    
    print("Importazione Localita...")
    import_from_json(Localita, os.path.join(data_dir, 'DB_Localita_luglio_2024_OK.json'))
    print(f"Numero di record in Localita dopo l'importazione: {Localita.query.count()}")
    
    print("Importazione Collezione...")
    import_from_json(Collezione, os.path.join(data_dir, 'DB_Collezione_luglio_2024_OK.json'))
    print(f"Numero di record in Collezione dopo l'importazione: {Collezione.query.count()}")
    
    print("Importazione dati completata.")

if __name__ == "__main__":
    with app.app_context():
        import_all_data('path/to/your/data/directory')