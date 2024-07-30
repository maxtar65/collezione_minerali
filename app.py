from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from models import db, Collezione, Localita, Specie, SistemaXX, migrate_sistema_xx
from forms import CollezioneForm, LocalitaForm, SearchForm, SpecieForm
from settings import DATABASE_PATH
from sqlalchemy import func, or_, event
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import unicodedata

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'
db.init_app(app)

# migrate = Migrate(app, db)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# @app.cli.command("migrate-sistema-xx")
# def migrate_sistema_xx_command():
#     """Migra i dati del sistema cristallino alla nuova tabella."""
#     migrate_sistema_xx()
#     print("Migrazione dei dati del sistema cristallino completata.")

def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# Registra la funzione con SQLite
def sqlite_unaccent(text):
    return normalize_text(text)

# Registrazione della funzione unaccent
with app.app_context():
    event.listen(db.engine, 'connect', lambda conn, rec: conn.create_function('unaccent', 1, sqlite_unaccent))

@app.context_processor
def inject_specie_valide():
    specie_valide_count = db.session.query(func.count(func.distinct(Collezione.specie_id))).filter(Collezione.specie_id.isnot(None)).scalar()
    return {'specie_valide': specie_valide_count}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/collezione', methods=['GET'])
def collezione():
    page = request.args.get('page', 1, type=int)
    specie_search = request.args.get('specie-search', '')
    localita_search = request.args.get('localita-search', '')

    query = Collezione.query

    if specie_search:
        query = query.filter(Collezione.specie_nome.ilike(f'%{specie_search}%'))
    
    if localita_search:
        query = query.filter(Collezione.cod_loc.ilike(f'%{localita_search}%'))

    # Paginazione
    pagination = query.order_by(Collezione.codice.desc()).paginate(page=page, per_page=10, error_out=False)
    items = pagination.items

    # Calcolo delle statistiche
    total_campioni = query.count()
    specie_valide = db.session.query(func.count(func.distinct(Collezione.specie_id))).filter(Collezione.specie_id.isnot(None)).scalar()
    specie_non_valide = db.session.query(func.count(func.distinct(Collezione.specie_nome))).filter(Collezione.specie_id.is_(None)).scalar()

    return render_template('collezione.html', 
                           items=items, 
                           pagination=pagination,
                           total_campioni=total_campioni,
                           specie_valide=specie_valide,
                           specie_non_valide=specie_non_valide,
                           specie_search=specie_search,
                           localita_search=localita_search)

@app.route('/localita')
def localita():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Numero di località per pagina

    pagination = Localita.query.order_by(Localita.cava_min).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    total_localita = Localita.query.count()
    localita_con_campioni = db.session.query(Localita.id).join(Collezione).group_by(Localita.id).count()

    return render_template('localita.html', 
                           items=items, 
                           pagination=pagination,
                           total_localita=total_localita,
                           localita_con_campioni=localita_con_campioni)

@app.route('/specie')
def specie():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = 15

    query = db.session.query(Specie, func.count(Collezione.id).label('campioni_count'))\
        .outerjoin(Collezione)\
        .group_by(Specie.id)

    if search:
        search_filter = or_(
            Specie.specie.ilike(f'%{search}%'),
            Specie.formula.ilike(f'%{search}%'),
            Specie.sistema_xx.ilike(f'%{search}%'),
            Specie.status.ilike(f'%{search}%'),
            Specie.sottogruppo.ilike(f'%{search}%'),
            Specie.gruppo.ilike(f'%{search}%'),
            Specie.supergruppo.ilike(f'%{search}%'),
            Specie.famiglia.ilike(f'%{search}%'),
            Specie.sottoclasse.ilike(f'%{search}%'),
            Specie.classe.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    total_specie = Specie.query.count()

    # Conteggio delle specie in collezione (con almeno un campione)
    specie_in_collezione = db.session.query(
        func.count(func.distinct(Specie.id))
    ).join(Collezione).filter(Collezione.specie_id.isnot(None)).scalar()

    specie_list = pagination.items

    return render_template('specie.html', 
                           specie_list=specie_list, 
                           pagination=pagination, 
                           total_specie=total_specie, 
                           specie_in_collezione=specie_in_collezione,
                           search=search)

# Nuove rotte per la creazione di nuovi record
@app.route('/collezione/new', methods=['GET', 'POST'])
def new_collezione():
    form = CollezioneForm()
    
    if request.method == 'GET':
        form.codice.data = Collezione.get_next_codice()
    
    if form.validate_on_submit():
        collezione = Collezione()
        form.populate_obj(collezione)
        
        # Gestione di specie valida o non valida
        if form.specie_non_valida.data:
            # Se è stata inserita una specie non valida, non associare specie_id
            collezione.specie_id = None
            collezione.specie_nome = form.specie_non_valida.data
            collezione.specie_non_valida = form.specie_non_valida.data
        else:
            # Cerca la specie valida nel database
            specie = Specie.query.get(form.specie.data)
            if specie:
                collezione.specie_id = specie.id
                collezione.specie_nome = specie.specie
        
        db.session.add(collezione)
        db.session.commit()
        flash('Nuovo campione aggiunto con successo!', 'success')
        return redirect(url_for('collezione'))
    
    return render_template('collezione_form.html', form=form, title="Nuovo Campione")

@app.route('/localita/new', methods=['GET', 'POST'])
def new_localita():
    form = LocalitaForm()
    if form.validate_on_submit():
        localita = Localita()
        form.populate_obj(localita)
        try:
            db.session.add(localita)
            db.session.commit()
            flash('Nuova località aggiunta con successo!', 'success')
            return redirect(url_for('localita'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    return render_template('localita_form.html', form=form, title="Nuova Località")

@app.route('/specie/new', methods=['GET', 'POST'])
def new_specie():
    form = SpecieForm()
    if form.validate_on_submit():
        specie = Specie()
        form.populate_obj(specie)
        specie.sistema_xx_rel = SistemaXX.query.get(form.sistema_xx.data)
        db.session.add(specie)
        db.session.commit()
        flash('Nuova specie aggiunta con successo!', 'success')
        return redirect(url_for('specie'))
    return render_template('specie_form.html', form=form, title="Nuova Specie")

# Rotte per la modifica dei record esistenti
@app.route('/collezione/edit/<int:id>', methods=['GET', 'POST'])
def edit_collezione(id):
    collezione = Collezione.query.get_or_404(id)
    form = CollezioneForm(obj=collezione)
    
    if request.method == 'GET':
        form.specie.data = collezione.specie_id
    
    if form.validate_on_submit():
        form.populate_obj(collezione)
        specie = Specie.query.get(form.specie.data)
        collezione.specie_id = specie.id
        collezione.specie_nome = specie.specie
        db.session.commit()
        flash('Campione aggiornato con successo!', 'success')
        return redirect(url_for('collezione'))
    
    return render_template('collezione_form.html', form=form, title="Modifica Campione")

@app.route('/localita/edit/<int:id>', methods=['GET', 'POST'])
def edit_localita(id):
    localita = Localita.query.get_or_404(id)
    form = LocalitaForm(obj=localita)
    if form.validate_on_submit():
        form.populate_obj(localita)
        try:
            db.session.commit()
            flash('Località aggiornata con successo!', 'success')
            return redirect(url_for('localita'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    return render_template('localita_form.html', form=form, title="Modifica Località")

@app.route('/specie/edit/<int:id>', methods=['GET', 'POST'])
def edit_specie(id):
    specie = Specie.query.get_or_404(id)
    form = SpecieForm(obj=specie)
    form.id.data = specie.id  # Imposta esplicitamente l'id nel form
    if form.validate_on_submit():
        form.populate_obj(specie)
        db.session.commit()
        flash('Specie aggiornata con successo!', 'success')
        return redirect(url_for('specie'))
    return render_template('specie_form.html', form=form, title="Modifica Specie")

@app.route('/collezione/delete/<int:id>', methods=['POST'])
def delete_collezione(id):
    collezione = Collezione.query.get_or_404(id)
    db.session.delete(collezione)
    db.session.commit()
    flash('Campione eliminato con successo!', 'success')
    return redirect(url_for('collezione'))

@app.route('/api/specie/autocomplete')
def specie_autocomplete():
    query = request.args.get('query', '')
    specie = Specie.query.filter(func.lower(func.unaccent(Specie.specie)).ilike(f'%{normalize_text(query).lower()}%')).all()
    results = [{'id': s.id, 'name': s.specie} for s in specie]
    return jsonify(results)

@app.route('/api/localita/autocomplete')
def localita_autocomplete():
    query = request.args.get('query', '')
    localita = Localita.query.filter(func.lower(func.unaccent(Localita.cava_min)).ilike(f'%{normalize_text(query).lower()}%')).all()
    results = [{'id': l.id, 'name': l.cava_min} for l in localita]
    return jsonify(results)

@app.route('/api/specie')
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_specie():
    query = request.args.get('query', '')
    specie_list = Specie.query.filter(func.lower(func.unaccent(Specie.specie)).ilike(f'%{normalize_text(query).lower()}%')).all()
    results = [{'id': specie.id, 'name': specie.specie} for specie in specie_list]
    return jsonify(results)

@app.route('/api/localita')
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_localita():
    query = request.args.get('query', '')
    localita_list = Localita.query.filter(Localita.nome.ilike(f'%{query}%')).all()
    results = [{'id': localita.id, 'name': localita.nome} for localita in localita_list]
    return jsonify(results)

@app.route('/tavola_periodica')
def tavola_periodica():
    return render_template('tavola_periodica.html')

if __name__ == '__main__':
    app.run(debug=True)
