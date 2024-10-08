from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from flask_caching import Cache
from models import db, Collezione, Localita, Specie, SistemaXX
from settings import DATABASE_PATH
from sqlalchemy import func, or_, event
import os
import unicodedata

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'

# Inizializzazione delle estensioni
db.init_app(app)
migrate = Migrate(app, db)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definizione del modello User per l'autenticazione
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Caricatore di utenti
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Classe customizzata per proteggere l'accesso ad Admin
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Configurazione di Flask-Admin con la protezione di accesso
admin = Admin(app, name='Minerali Catalog Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())

# Aggiunta dei modelli al pannello di amministrazione
admin.add_view(ModelView(Collezione, db.session))
admin.add_view(ModelView(Localita, db.session))
admin.add_view(ModelView(Specie, db.session))
admin.add_view(ModelView(SistemaXX, db.session))

# Variabile per tenere traccia della prima richiesta
is_first_request = True

@app.before_request
def create_admin_user():
    global is_first_request
    if is_first_request:
        is_first_request = False
        user = User.query.filter_by(username='admin').first()
        if not user:
            admin = User(username='admin', password='password')  # Ricorda di usare un hash sicuro per le password reali
            db.session.add(admin)
            db.session.commit()

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Login non valido. Riprova.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/collezione', methods=['GET'])
def collezione():
    page = request.args.get('page', 1, type=int)
    specie_search = request.args.get('specie-search', '')
    localita_search = request.args.get('localita-search', '')
    codice_search = request.args.get('codice-search', '')

    query = db.session.query(Collezione, Localita.loc_monte).join(Localita, Collezione.cod_loc == Localita.cod_loc)

    if specie_search:
        query = query.filter(Collezione.specie_nome.ilike(f'%{specie_search}%'))
    
    if localita_search:
        query = query.filter(Localita.cava_min.ilike(f'%{localita_search}%'))

    if codice_search:
        query = query.filter(Collezione.codice.ilike(f'%{codice_search}%'))

    # Paginazione
    pagination = query.order_by(Collezione.codice.desc()).paginate(page=page, per_page=10, error_out=False)
    items = pagination.items

    # Calcolo delle statistiche
    total_campioni = Collezione.query.count()
    specie_valide = db.session.query(func.count(func.distinct(Collezione.specie_id))).filter(Collezione.specie_id.isnot(None)).scalar()
    specie_non_valide = db.session.query(func.count(func.distinct(Collezione.specie_nome))).filter(Collezione.specie_id.is_(None)).scalar()

    return render_template('collezione.html', 
                           items=items, 
                           pagination=pagination,
                           total_campioni=total_campioni,
                           specie_valide=specie_valide,
                           specie_non_valide=specie_non_valide,
                           specie_search=specie_search,
                           localita_search=localita_search, 
                           codice_search=codice_search)

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
            collezione.specie_id = None
            collezione.specie_nome = form.specie_non_valida.data
        elif form.specie.data:
            specie = Specie.query.get(form.specie.data)
            if specie:
                collezione.specie_id = specie.id
                collezione.specie_nome = specie.specie
        else:
            # Se entrambi i campi sono vuoti, gestisci l'errore
            flash('Devi inserire una specie valida o non valida', 'error')
            return render_template('collezione_form.html', form=form, title="Nuovo Campione")
        
        # Gestione del codice località
        localita = Localita.query.filter_by(cod_loc=form.cod_loc.data).first()
        if localita:
            collezione.cod_loc = localita.cod_loc
        else:
            # Se il codice località non esiste, crea una nuova località
            nuova_localita = Localita(cod_loc=form.cod_loc.data, cava_min=form.cod_loc.data, loc_monte=form.loc_monte.data)
            db.session.add(nuova_localita)
            collezione.cod_loc = nuova_localita.cod_loc

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
    results = [{
        'id': l.cod_loc,
        'name': f"{l.cod_loc} - {l.cava_min}",
        'additionalData': {
            'loc_monte': l.loc_monte,
            'comune': l.comune,
            'provincia': l.provincia
            # Aggiungi altri campi se necessario
        }
    } for l in localita]
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

@app.route('/api/localita/monte_autocomplete')
def monte_autocomplete():
    query = request.args.get('query', '')
    monti = Localita.query.filter(func.lower(func.unaccent(Localita.loc_monte)).ilike(f'%{normalize_text(query).lower()}%')).all()
    results = [{'id': m.id, 'name': m.loc_monte} for m in monti]
    return jsonify(results)

@app.route('/api/luoghi_acquisizione')
def luoghi_acquisizione():
    # Supponendo che `Collezione` sia il modello in cui si trova `luogo_acq`
    luoghi = db.session.query(Collezione.luogo_acq).distinct().all()
    results = [luogo.luogo_acq for luogo in luoghi]
    return jsonify(results)

@app.route('/tavola_periodica')
def tavola_periodica():
    return render_template('tavola_periodica.html')

if __name__ == '__main__':
    app.run(debug=True)
