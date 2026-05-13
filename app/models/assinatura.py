from app import db


class Assinatura(db.Model):
    __tablename__ = 'assinaturas'
    
    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id', name='fk_assinatura_loja'), nullable=False)
    nome_plano = db.Column(db.String(255), nullable=False , default='Plano Padrão')
    valor_mensal = db.Column(db.Float, nullable=False, default=149.90)
    data_inicio = db.Column(db.DateTime, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Assinatura {self.nome_plano} para Loja {self.loja_id}>'