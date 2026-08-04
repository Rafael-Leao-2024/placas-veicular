from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import extract, func
from app import db
from app.models.utlis_assinatura import criar_ou_obter_assinatura
from app.models.pagamento import Pagamento
from app.models.venda import Venda

assinatura_bp = Blueprint("assinatura", __name__, url_prefix="/assinatura")


@assinatura_bp.route("/minha-assinatura")
@login_required
def minha_assinatura():
    hoje = datetime.utcnow() - timedelta(hours=3)
    # === CRIA A ASSINATURA SE NÃO EXISTIR ===

    loja_id = session.get("loja_id")

    assinatura = criar_ou_obter_assinatura(int(loja_id))
    # Busca todos os pedidos do usuário agrupados por mês/ano
    pedidos_por_mes = (
        db.session.query(
            extract("year", Venda.data).label("ano"),
            extract("month", Venda.data).label("mes"),
            func.count(Venda.id).label("quantidade"),
        )
        .filter(Venda.loja_id == int(loja_id), Venda.ativo == True)
        .group_by(
            extract("year", Venda.data), extract("month", Venda.data)
        )
        .order_by(
            extract("year", Venda.data).desc(),
            extract("month", Venda.data).desc(),
        )
        .all()
    )

    print('pedido dos meses', pedidos_por_mes)

    historico = []
    total_acumulado = 0.0

    meses_pt = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }

    for item in pedidos_por_mes:
        ano = int(item.ano)
        mes = int(item.mes)
        quantidade = int(item.quantidade)

        valor_variavel = round(
            quantidade * 0, 2
        )  # usa o valor da assinatura
        total_mes = assinatura.valor_mensal

        nome_mes = f"{meses_pt.get(mes, 'Mês')} / {ano}"
        print(f"Assinatura {nome_mes}{int(loja_id)}")

        atual = ano == hoje.year and mes == hoje.month

        pagamento = Pagamento.query.filter(
            (Pagamento.order_nsu == f"Assinatura {nome_mes}{int(loja_id)}") &
            (Pagamento.assinatura_id == assinatura.id)
        ).first()

        is_pago = False
        if pagamento:
            is_pago = True if pagamento.status == "pago" else False
        historico.append(
            {
                "mes_ano": nome_mes,
                "quantidade_pedidos": quantidade,
                "valor_variavel": valor_variavel,
                "total": total_mes,
                "atual": atual,
                "pago": is_pago,  # ainda temporário
                "produto": f"Assinatura {nome_mes}",
                "loja_id": str(int(loja_id)),
                "usuario_id": current_user.id,
            }
        )

        total_acumulado += total_mes

    # Próxima cobrança
    if hoje.day >= 2:
        proximo = (hoje.replace(day=1) + timedelta(days=32)).replace(day=2)
    else:
        proximo = hoje.replace(day=2)

    data_proxima_cobranca = proximo.strftime("%d/%m/%Y")

    return render_template(
        "assinatura/minha_assinatura.html",
        historico=historico,
        total_acumulado=round(total_acumulado, 2),
        data_proxima_cobranca=data_proxima_cobranca,
        assinatura=assinatura,  # ← pode passar para o template se quiser
    )


# api de pagamento
@assinatura_bp.route("/criar-pagamento", methods=["POST"])
@login_required
def criar_pagamento():
    items = request.get_json()
    print(items)
    loja_id = session.get("loja_id")
    assinatura = criar_ou_obter_assinatura(int(loja_id))
    orden_nsu = items[0].get("produto") + str(assinatura.loja_id)

    pagamento = Pagamento.query.filter(
        (Pagamento.order_nsu == orden_nsu) &
        (Pagamento.assinatura_id == assinatura.id)  # aqui idealmente seria a assinatura
    ).first()

    if not pagamento:
        pagamento = Pagamento(
            assinatura_id=assinatura.id,
            order_nsu=orden_nsu,
            amount=items[0].get("total"),
            status="pendente",
            data_criacao=datetime.utcnow() - timedelta(hours=3),            
        )
        db.session.add(pagamento)
        db.session.commit()
    else:
        pagamento.amount = items[0].get("total")  # atualiza o valor do pagamento para o valor correto
        db.session.commit()

    payload = {
        "handle": "rafael-leao-da-silva-",
        "order_nsu": orden_nsu,
        "redirect_url": "https://web-production-513e8.up.railway.app/assinatura/minha-assinatura",
        "webhook_url": "https://web-production-513e8.up.railway.app/assinatura/webhook-infinitepay",
        # "customer": {
        #     "name": "Rafael Leão da Silva",
        #     "email": "rafaelampaz6@gmail.com",
        #     "phone_number": "+5581983685747",
        # },
        # "address": {
        #     "cep": "51250545",
        #     "street": "Rua das Flores",
        #     "neighborhood": "jordao baixo",
        #     "number": "195",
        #     "complement": "apos o campo",
        # },
        "items": [
            {
                "quantity": 1,
                "price": item.get("total") * 100,  # Convertendo para centavos
                "description": item.get("produto"),
            }
            for item in items
        ],
    }

    import requests

    headers = {"Content-Type": "application/json"}

    resp = requests.post(
        "https://api.infinitepay.io/invoices/public/checkout/links",
        json=payload,
        headers=headers,
    )

    resultado = resp.json()

    pagamento.amount = items[0].get("total")
    pagamento.payment_url = resultado.get("url")[:400]  # salva o link do checkout
    db.session.commit()

    if resp.status_code == 200 or resp.status_code == 201:
        return jsonify(
            {"payment_url": resultado.get("url")}
        )  # ou o campo correto que retorna o link
    else:
        return jsonify({"error": "Falha ao criar pagamento"}), 400


@assinatura_bp.route("/webhook-infinitepay", methods=["POST"])
def webhook_pagamento():
    try:
        data = request.get_json()
        order_nsu = data.get("order_nsu")

        # Busca o pagamento que já existe
        pagamento = Pagamento.query.filter(
            (Pagamento.order_nsu == str(order_nsu)) # & (Pagamento.assinatura_id == assinatura.id)  # aqui idealmente seria a assinatura    
        ).first()

        if not pagamento:
            # Opcional: criar como fallback, mas não é o ideal
            return jsonify({"status": "ignored"}), 200

        # Atualiza com os dados do webhook
        pagamento.paid_amount = data.get("paid_amount")
        pagamento.receipt_url = data.get("receipt_url")
        pagamento.transaction_nsu = data.get("transaction_nsu")
        pagamento.transaction_id = data.get("transaction_nsu")
        pagamento.invoice_slug = data.get("invoice_slug")
        pagamento.capture_method = data.get("capture_method")
        pagamento.installments = data.get("installments")
        # ... outros campos

        if data.get("receipt_url"):
            pagamento.status = "pago"  # atualiza o pedido também

        db.session.commit()

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Erro ao processar webhook:", e)
        return jsonify({"status": "erro"}), 400