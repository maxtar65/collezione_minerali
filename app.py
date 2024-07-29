from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Collezione, Localita, Specie
from forms import CollezioneForm, LocalitaForm, SearchForm, SpecieForm
from settings import DATABASE_PATH
from sqlalchemy import or_
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/collezione', methods=['GET', 'POST'])
def collezione():
    search_form = SearchForm(request.form)
    query = Collezione.query

    if request.method == 'POST' and search_form.validate():
        search_term = search_form.search.data
        query = query.filter(or_(
            Collezione.codice.ilike(f'%{search_term}%'),
            Collezione.specie_nome.ilike(f'%{search_term}%'),
            Collezione.varieta.ilike(f'%{search_term}%'),
            Collezione.cod_loc.ilike(f'%{search_term}%'),
            Collezione.qualita.ilike(f'%{search_term}%'),
            # Aggiungi qui altri campi su cui vuoi effettuare la ricerca
        ))

    items = query.all()
    return render_template('collezione.html', items=items, search_form=search_form)

@app.route('/localita')
def localita():
    items = Localita.query.all()
    return render_template('localita.html', items=items)

@app.route('/specie')
def specie():
    specie_list = Specie.query.all()
    return render_template('specie.html', specie_list=specie_list)

# Nuove rotte per la creazione di nuovi record
@app.route('/collezione/new', methods=['GET', 'POST'])
def new_collezione():
    form = CollezioneForm()
    if form.validate_on_submit():
        collezione = Collezione()
        form.populate_obj(collezione)
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
        db.session.add(localita)
        db.session.commit()
        flash('Nuova località aggiunta con successo!', 'success')
        return redirect(url_for('localita'))
    return render_template('localita_form.html', form=form, title="Nuova Località")

@app.route('/specie/new', methods=['GET', 'POST'])
def new_specie():
    form = SpecieForm()
    if form.validate_on_submit():
        specie = Specie()
        form.populate_obj(specie)
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
        db.session.commit()
        flash('Località aggiornata con successo!', 'success')
        return redirect(url_for('localita'))
    return render_template('localita_form.html', form=form, title="Modifica Località")

@app.route('/specie/edit/<int:id>', methods=['GET', 'POST'])
def edit_specie(id):
    specie = Specie.query.get_or_404(id)
    form = SpecieForm(obj=specie)
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

if __name__ == '__main__':
    app.run(debug=True)