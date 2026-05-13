from app import db
from datetime import datetime

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    assinatura_id = db.Column(db.Integer, db.ForeignKey('assinaturas.id', name='fk_pagamento_assinatura'), nullable=False)
    
    # Dados da InfinitePay
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)   # ID da transação
    invoice_slug = db.Column(db.String(100), unique=True, nullable=True)
    order_nsu = db.Column(db.String(100))
    transaction_nsu = db.Column(db.String(100))
    
    amount = db.Column(db.Integer)                    # valor cobrado em centavos
    paid_amount = db.Column(db.Integer)               # valor realmente pago
    capture_method = db.Column(db.String(50))         # pix, credit_card, etc.
    installments = db.Column(db.Integer, default=1)
    
    receipt_url = db.Column(db.String(500))
    status = db.Column(db.String(30), default='pending')   # pending, approved, failed, etc.
    
    payment_url = db.Column(db.String(500))           # link do checkout que geramos
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Pagamento {self.id} - Pedido {self.order_nsu} - {self.status}>'