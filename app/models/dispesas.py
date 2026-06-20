from datetime import datetime
from app import db

class DespesaSimples(db.Model):
    __tablename__ = 'despesas_simples'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_despesa = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.String(500))
    
    # Quem registrou
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    loja = db.relationship('Loja', backref='despesas_simples')