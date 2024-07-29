from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, DateField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional
from models import Specie, SistemaXX

class CollezioneForm(FlaskForm):
    codice = IntegerField('Codice', validators=[DataRequired()])
    posizione = StringField('Posizione')
    # specie = StringField('Specie', validators=[DataRequired()])
    specie = SelectField('Specie', coerce=int, validators=[DataRequired()])
    varieta = StringField('Varietà')
    alias = StringField('Alias')
    associazione = StringField('Associazione')
    cod_loc = StringField('Codice Località')
    dimensionamento = StringField('Dimensionamento')
    qualita = StringField('Qualità')
    data_ins = DateField('Data Inserimento', format='%Y-%m-%d', validators=[Optional()])
    data_acq = DateField('Data Acquisizione', format='%Y-%m-%d', validators=[Optional()])
    mod_acq = StringField('Modalità Acquisizione')
    acquisito_da = StringField('Acquisito Da')
    costo = FloatField('Costo', validators=[Optional()])
    luogo_acq = StringField('Luogo Acquisizione')
    scambiato_per = StringField('Scambiato Per')
    note = TextAreaField('Note')
    referenza = StringField('Referenza')
    descrizione = TextAreaField('Descrizione')
    fluor_lw = StringField('Fluorescenza LW')
    fluor_sw = StringField('Fluorescenza SW')
    radioattivo = StringField('Radioattivo')
    tl = BooleanField('TL')

    def __init__(self, *args, **kwargs):
        super(CollezioneForm, self).__init__(*args, **kwargs)
        self.specie.choices = [(s.id, s.specie) for s in Specie.query.order_by(Specie.specie).all()]

class LocalitaForm(FlaskForm):
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
    specie = StringField('Specie', validators=[DataRequired()])
    formula = StringField('Formula')
    sistema_xx = SelectField('Sistema Cristallino', coerce=int)
    status = StringField('Status')
    sottogruppo = StringField('Sottogruppo')
    gruppo = StringField('Gruppo')
    supergruppo = StringField('Supergruppo')
    famiglia = StringField('Famiglia')
    sottoclasse = StringField('Sottoclasse')
    classe = StringField('Classe')
    submit = SubmitField('Salva')

    def __init__(self, *args, **kwargs):
        super(SpecieForm, self).__init__(*args, **kwargs)
        self.sistema_xx.choices = [(s.id, s.nome) for s in SistemaXX.query.order_by(SistemaXX.nome).all()]

class SearchForm(FlaskForm):
    specie = StringField('Specie')
    localita = StringField('Località')
    submit = SubmitField('Cerca')