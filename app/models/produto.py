from app import db

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), nullable=True)
    descricao = db.Column(db.String(255), nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)
    estoque_inicial = db.Column(db.Integer, default=0)
    estoque_atual = db.Column(db.Integer, default=0)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relationships
    loja = db.relationship('Loja', backref='produtos')
    itens_venda = db.relationship('ItemVenda', backref='produto', lazy=True)
    
    def __repr__(self):
        return f'<Produto {self.descricao}>'