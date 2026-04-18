from app import db

class Loja(db.Model):
    __tablename__ = 'lojas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relationships
    vendedores = db.relationship('Vendedor', backref='loja', lazy=True)
    vendas = db.relationship('Venda', backref='loja', lazy=True)
    
    def __repr__(self):
        return f'<Loja {self.nome}>'