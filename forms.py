from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, FloatField, DateField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional
from models import Localita, Specie, SistemaXX

class CollezioneForm(FlaskForm):
    codice = IntegerField('Codice campione', validators=[DataRequired()])
    specie = SelectField('Specie', validators=[Optional()], choices=[])
    specie_non_valida = StringField('Specie non valida', validators=[Optional()])
    varieta = StringField('Varietà mineralogica')
    posizione = StringField('Codice archivio')
    alias = StringField('Altro nome')
    associazione = StringField('Associazione con')
    cod_loc = SelectField('Codice località', validators=[DataRequired()], choices=[])
    loc_monte = SelectField('Località', validators=[DataRequired()], choices=[])
    dimensionamento = SelectField('Dimensioni campione', choices=[
        ('Non definito', 'Non definito'),
        ('Micro', 'Micro'),
        ('Thumbnail', 'Thumbnail'),
        ('Miniature', 'Miniature'),
        ('Cabinet', 'Cabinet'),
        ('Tipo 1', 'Tipo 1'),
        ('Tipo 4', 'Tipo 4'),
        ('Tipo 32h', 'Tipo 32h')
    ])
    qualita = SelectField('Qualità', choices=[
        ('non valutato', 'non valutato'),
        ('AA', 'AA - pezzo notevole'),
        ('A', 'A - cristalli visibili'),
        ('B', 'B - sferule, aggregati'),
        ('C', 'C - campione massivo')        
    ])
    data_ins = DateField('Data inserimento', format='%Y-%m-%d', validators=[Optional()])
    data_acq = DateField('Data acquisizione', format='%Y-%m-%d', validators=[Optional()])
    mod_acq = SelectField('Modalità acquisizione', choices=[
        ('Non specificato', 'Non specificato'),
        ('Asta Ebay', 'Asta Ebay'),
        ('Raccolto personalmente', 'Raccolto personalmente'),
        ('Scambiato', 'Scambiato'),
        ('Acquistato', 'Acquistato'),
        ('Donato', 'Donato'),
        ('Ex analisi', 'Ex analisi')
    ])
    acquisito_da = StringField('Acquisito da')
    costo = FloatField('Costo', validators=[Optional()])
    luogo_acq = StringField('Luogo acquisizione')
    scambiato_per = StringField('Scambiato per')
    note = StringField('Note')
    referenza = StringField('Referenza')
    descrizione = StringField('Descrizione')
    fluor_lw = StringField('Fluorescenza LW')
    fluor_sw = StringField('Fluorescenza SW')
    radioattivo = StringField('Radioattivo')
    tl = BooleanField('Type Locality')

    def __init__(self, *args, **kwargs):
        super(CollezioneForm, self).__init__(*args, **kwargs)
        self.specie.choices = [('', 'Seleziona una specie')] + [(str(s.id), s.specie) for s in Specie.query.all()]
        self.cod_loc.choices = [('', 'Seleziona una località')] + [(l.cod_loc, f"{l.cod_loc} - {l.cava_min}") for l in Localita.query.all()]
        self.loc_monte.choices = [('', 'Seleziona un monte')] + [(l.loc_monte, l.loc_monte) for l in Localita.query.distinct(Localita.loc_monte).all()]

class LocalitaForm(FlaskForm):
    id = HiddenField('ID')
    cod_loc = StringField('Codice Località', validators=[DataRequired()])
    cava_min = StringField('Cava/Miniera')
    loc_monte = StringField('Località/Monte')
    valle = StringField('Valle')
    comune = StringField('Comune')
    distr_pref = StringField('Distretto/Prefettura')
    provincia = StringField('Provincia')
    regione = StringField('Regione')
    dipartimento = StringField('Dipartimento')
    stato = StringField('Stato')
    nazione = StringField('Nazione')
    note = TextAreaField('Note')
    cod_mindat = IntegerField('Codice Mindat', validators=[Optional()])
    submit = SubmitField('Salva')

class SpecieForm(FlaskForm):
    id = HiddenField('ID')
    specie = StringField('Specie', validators=[DataRequired()])
    formula = StringField('Formula')
    sistema_xx = SelectField('Sistema Cristallino', choices=[
        ('', 'Seleziona...'),
        ('Cubico', 'Cubico'),
        ('Tetragonale', 'Tetragonale'),
        ('Ortorombico', 'Ortorombico'),
        ('Monoclino', 'Monoclino'),
        ('Triclino', 'Triclino'),
        ('Esagonale', 'Esagonale'),
        ('Trigonale', 'Trigonale')
    ])
    status = StringField('Status')
    sottogruppo = StringField('Sottogruppo')
    gruppo = StringField('Gruppo')
    supergruppo = StringField('Supergruppo')
    famiglia = StringField('Famiglia')
    sottoclasse = StringField('Sottoclasse')
    classe = StringField('Classe')

class SearchForm(FlaskForm):
    specie = StringField('Specie')
    localita = StringField('Località')
    submit = SubmitField('Cerca')