from app import db

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relationships
    vendas = db.relationship('Venda', backref='vendedor', lazy=True)
    
    def __repr__(self):
        return f'<Vendedor user_id={self.user_id} loja_id={self.loja_id}>'