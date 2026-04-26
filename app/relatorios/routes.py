from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    session,
    Response,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
from app import db
from app.models.venda import Venda
from datetime import date, datetime, timedelta
import csv
from io import StringIO
from sqlalchemy import func

relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.route("/diario")
@login_required
def diario():
    loja_id = session.get("loja_id")
    if not loja_id:
        return redirect(url_for("loja.selecionar"))

    data_ref = request.args.get("data")
    if data_ref:
        data_ref = datetime.strptime(data_ref, "%Y-%m-%d").date()
    else:
        data_ref = date.today()

    vendas = (
        Venda.query.filter_by(loja_id=loja_id, ativo=True)
        .filter(func.date(Venda.data) == data_ref)
        .order_by(Venda.created_at.desc())
        .all()
    )

    total_vendas = sum(v.total for v in vendas)
    total_recebido = sum(v.total for v in vendas if v.pago)
    total_devendo = sum(
        v.total for v in vendas if not v.pago and v.forma_pagamento == "fiado"
    )

    return render_template(
        "relatorios/diario.html",
        vendas=vendas,
        data=data_ref,
        total_vendas=total_vendas,
        total_recebido=total_recebido,
        total_devendo=total_devendo,
    )


@relatorios_bp.route("/mensal")
@login_required
def mensal():
    loja_id = session.get("loja_id")
    if not loja_id:
        return redirect(url_for("loja.selecionar"))

    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)

    if not mes or not ano:
        hoje = date.today()
        mes = hoje.month
        ano = hoje.year

    # Calculate first and last day of month
    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    vendas = (
        Venda.query.filter(
            Venda.loja_id == loja_id,
            Venda.ativo == True,
            Venda.data >= primeiro_dia,
            Venda.data <= ultimo_dia,
        )
        .order_by(Venda.created_at.desc())
        .all()
    )

    total_vendas = sum(v.total for v in vendas)
    total_recebido = sum(v.total for v in vendas if v.pago)
    total_devendo = sum(
        v.total for v in vendas if not v.pago and v.forma_pagamento == "fiado"
    )

    return render_template(
        "relatorios/mensal.html",
        vendas=vendas,
        mes=mes,
        ano=ano,
        total_vendas=total_vendas,
        total_recebido=total_recebido,
        total_devendo=total_devendo,
        nome_mes=primeiro_dia.strftime("%B"),
    )


@relatorios_bp.route("/exportar_diario")
@login_required
def exportar_diario():
    loja_id = session.get("loja_id")
    if not loja_id:
        return redirect(url_for("loja.selecionar"))

    data_ref = request.args.get("data")
    if data_ref:
        data_ref = datetime.strptime(data_ref, "%Y-%m-%d").date()
    else:
        data_ref = date.today()

    vendas = (
        Venda.query.filter_by(loja_id=loja_id, ativo=True)
        .filter(func.date(Venda.data) == data_ref)
        .all()
    )

    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(
        ["ID", "Cliente", "Vendedor", "Total", "Forma Pagamento", "Pago", "Data"]
    )

    for venda in vendas:
        writer.writerow(
            [
                venda.id,
                venda.cliente_nome,
                venda.vendedor.user.name,
                f"R$ {venda.total:.2f}",
                venda.forma_pagamento,
                "Sim" if venda.pago else "Não",
                venda.data.strftime("%d/%m/%Y"),
            ]
        )

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_diario_{data_ref}.csv"
        },
    )


@relatorios_bp.route("/exportar_mensal")
@login_required
def exportar_mensal():
    loja_id = session.get("loja_id")
    if not loja_id:
        return redirect(url_for("loja.selecionar"))

    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)

    if not mes or not ano:
        hoje = date.today()
        mes = hoje.month
        ano = hoje.year

    primeiro_dia = date(ano, mes, 1)
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)

    vendas = Venda.query.filter(
        Venda.loja_id == loja_id,
        Venda.ativo == True,
        Venda.data >= primeiro_dia,
        Venda.data <= ultimo_dia,
    ).all()

    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(
        ["ID", "Cliente", "Vendedor", "Total", "Forma Pagamento", "Pago", "Data"]
    )

    for venda in vendas:
        writer.writerow(
            [
                venda.id,
                venda.cliente_nome,
                venda.vendedor.user.name,
                f"R$ {venda.total:.2f}",
                venda.forma_pagamento,
                "Sim" if venda.pago else "Não",
                venda.data.strftime("%d/%m/%Y"),
            ]
        )

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename=relatorio_mensal_{primeiro_dia.strftime("%B_%Y")}.csv'
        },
    )
