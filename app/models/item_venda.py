from app import db

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'
    
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    total_item = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ItemVenda venda_id={self.venda_id} produto_id={self.produto_id}>'