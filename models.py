import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import func

db = SQLAlchemy()

class SistemaXX(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    specie = db.relationship('Specie', back_populates='sistema_xx_rel')

    def __repr__(self):
        return self.nome

class Collezione(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    codice = db.Column(db.Integer, unique=True, nullable=False)
    posizione = db.Column(db.String(50))
    specie_id = db.Column(db.Integer, db.ForeignKey('specie.id', name='fk_collezione_specie'), nullable=True)
    specie_nome = db.Column(db.String(100))
    specie_non_valida = db.Column(db.String(100))
    varieta = db.Column(db.String(100))
    alias = db.Column(db.String(100))
    associazione = db.Column(db.String(100))
    cod_loc = db.Column(db.String(30), db.ForeignKey('localita.cod_loc', name='fk_collezione_localita'))
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

    specie_rel = db.relationship('Specie', back_populates='campioni')
    serialize_rules = ('-localita', '-specie_rel')

    def to_dict(self):
        return {
            'id': self.id,
            'codice': self.codice,
            'specie': self.specie_nome or self.specie_non_valida,
            'varieta': self.varieta,
            'cod_loc': self.cod_loc,
            'qualita': self.qualita
        }
    
    @staticmethod
    def get_next_codice():
        max_codice = db.session.query(func.max(Collezione.codice)).scalar()
        return (max_codice or 0) + 1

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

    collezione = db.relationship('Collezione', backref='localita', lazy='dynamic')
    serialize_rules = ('-collezione',)

class Specie(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    specie = db.Column(db.String(100), unique=True, nullable=False)
    formula = db.Column(db.String(255))
    sistema_xx = db.Column(db.String(50))  # Manteniamo temporaneamente questa colonna
    sistema_xx_id = db.Column(db.Integer, db.ForeignKey('sistema_xx.id', name='fk_specie_sistema_xx'))
    status = db.Column(db.String(50))
    sottogruppo = db.Column(db.String(50))
    gruppo = db.Column(db.String(100))
    supergruppo = db.Column(db.String(50))
    famiglia = db.Column(db.String(50))
    sottoclasse = db.Column(db.String(100))
    classe = db.Column(db.String(100))

    sistema_xx_rel = db.relationship('SistemaXX', back_populates='specie')
    campioni = db.relationship('Collezione', back_populates='specie_rel', lazy='dynamic')
    serialize_rules = ('-campioni', '-sistema_xx_rel')

    def to_dict(self):
        return {
            'id': self.id,
            'specie': self.specie,
            'formula': self.formula,
            'sistema_xx': self.sistema_xx_rel.nome if self.sistema_xx_rel else self.sistema_xx,
            'status': self.status,
            'sottogruppo': self.sottogruppo,
            'gruppo': self.gruppo,
            'supergruppo': self.supergruppo,
            'famiglia': self.famiglia,
            'sottoclasse': self.sottoclasse,
            'classe': self.classe
        }
    
    @property
    def formatted_formula(self):
        if self.formula:
            return self.formattazione_formula(self.formula)
        return ""

    @staticmethod
    def formattazione_formula(formula):
        # Formatta le valenze e le cariche come apici
        formula = re.sub(r'(\d+)([+-])', r'<sup>\1\2</sup>', formula)
        # Formatta i numeri di atomi come pedici
        formula = re.sub(r'(?<!<sup>)(?<!·)(\d+)(?!<)', r'<sub>\1</sub>', formula)
        return formula

def migrate_sistema_xx():
    # Crea nuove istanze di SistemaXX dai dati esistenti
    sistemi_unici = db.session.query(Specie.sistema_xx).distinct().all()
    for (sistema,) in sistemi_unici:
        if sistema:
            esistente = SistemaXX.query.filter_by(nome=sistema).first()
            if not esistente:
                nuovo_sistema = SistemaXX(nome=sistema)
                db.session.add(nuovo_sistema)
    db.session.commit()
    
    # Aggiorna le relazioni nelle specie esistenti
    for specie in Specie.query.all():
        if specie.sistema_xx:
            sistema = SistemaXX.query.filter_by(nome=specie.sistema_xx).first()
            if sistema:
                specie.sistema_xx_id = sistema.id
    
    db.session.commit()
    print("Migrazione dei dati del sistema cristallino completata.")

def create_database():
    db.create_all()
    migrate_sistema_xx()