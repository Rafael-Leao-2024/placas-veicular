from app.models.utlis_assinatura import criar_ou_obter_assinatura
from app.models.pagamento import Pagamento
from flask import session, redirect, url_for, flash
from app import agora_brasil, meses_pt, db

def verificar_assinatura(loja_id):
    assinatura = criar_ou_obter_assinatura(int(loja_id))

    # pegar Pagamento do mês atual
    hoje = agora_brasil()
    ano = hoje.strftime("%Y")

    order_nsu = f"Assinatura {meses_pt.get((agora_brasil().month)-1, 'Dezembro').title()} / {ano}{int(loja_id)}"
    pagamento = Pagamento.query.filter_by(
        assinatura_id=assinatura.id, order_nsu=order_nsu
    ).first()

    if not pagamento:  # Se não existe pagamento para o mês atual E estamos no dia 2, 3, 4 ou 22
        # Se não existe pagamento para o mês atual, cria um novo com status pendente
        pagamento = Pagamento(
            assinatura_id=assinatura.id,
            order_nsu=order_nsu,
            amount=assinatura.valor_mensal, # mes atual valor fixo mensal 
            status="pendente",
            data_criacao=agora_brasil(),
        )
        db.session.add(pagamento)
        db.session.commit()
        db.session.flush()
    # Execute se a data for dia 2 e se o pagamento do mês atual estiver pendente

    if hoje.day in [2, 3, 4, 5, 6, 7]:
        if pagamento.status == "pendente":
            flash(
                "Sua assinatura está pendente. Por favor, finalize o pagamento para continuar.",
                "warning",
            )
            print('Assinatura pendente')
            return True
    return False