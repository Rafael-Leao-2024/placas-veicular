from app import db
from datetime import datetime


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey("lojas.id"), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("vendedores.id"), nullable=False)
    data = db.Column(db.Date, default=datetime.now().date)
    cliente_nome = db.Column(db.String(255), nullable=False)
    pago = db.Column(db.Boolean, default=False)
    forma_pagamento = db.Column(
        db.String(50), nullable=False
    )  # cartao, pix, dinheiro, fiado
    total = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    itens = db.relationship(
        "ItemVenda", backref="venda", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Venda {self.id} - {self.cliente_nome}>"
