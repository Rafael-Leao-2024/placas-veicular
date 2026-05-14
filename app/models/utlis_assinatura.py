from datetime import datetime, timedelta
from app.models.assinatura import Assinatura
from app import db

def criar_ou_obter_assinatura(loja_id):
    """Cria assinatura padrão se a loja ainda não tiver uma"""
    assinatura = Assinatura.query.filter_by(loja_id=loja_id, ativo=True).first()
    
    if assinatura:
        return assinatura
    
    # Cria a assinatura padrão
    assinatura = Assinatura(
        loja_id=loja_id,
        nome_plano="Padrão",
        valor_mensal=149.99,
        data_inicio=datetime.utcnow() - timedelta(hours=3),
        ativo=True
    )
    
    db.session.add(assinatura)
    db.session.commit()
    return assinatura
