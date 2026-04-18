from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.venda import Venda
from app.models.item_venda import ItemVenda
from app.models.produto import Produto
from app.models.vendedor import Vendedor
from datetime import date, datetime

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
@login_required
def index():
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    vendas = Venda.query.filter_by(loja_id=loja_id, ativo=True).order_by(Venda.created_at.desc()).all()[:100]
    return render_template('vendas/index.html', vendas=vendas)

@vendas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    if request.method == 'POST':
        cliente_nome = request.form.get('cliente_nome')
        forma_pagamento = request.form.get('forma_pagamento')
        produtos_json = request.form.get('produtos')
        
        import json
        produtos = json.loads(produtos_json)
        
        # Check stock availability
        for item in produtos:
            produto = Produto.query.get(item['produto_id'])
            if produto.estoque_atual < item['quantidade']:
                flash(f'Estoque insuficiente para o produto {produto.descricao}.', 'error')
                return redirect(url_for('vendas.nova'))
        
        # Get seller
        vendedor = Vendedor.query.filter_by(user_id=current_user.id, loja_id=loja_id, ativo=True).first()
        print(current_user.id, loja_id)
        if not vendedor:
            flash('Você não está registrado como vendedor nesta loja.', 'error')
            return redirect(url_for('loja.selecionar'))
        
        # Create sale
        total = sum(item['total'] for item in produtos)
        venda = Venda(
            loja_id=loja_id,
            vendedor_id=vendedor.id,
            cliente_nome=cliente_nome,
            pago=(forma_pagamento != 'fiado'),
            forma_pagamento=forma_pagamento,
            total=total,
            ativo=True
        )
        db.session.add(venda)
        db.session.flush()
        
        # Create sale items and update stock
        for item in produtos:
            produto = Produto.query.get(item['produto_id'])
            item_venda = ItemVenda(
                venda_id=venda.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                preco_unitario=produto.preco_venda,
                total_item=item['total']
            )
            db.session.add(item_venda)
            
            # Update stock
            produto.estoque_atual -= item['quantidade']
        
        db.session.commit()
        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('vendas.index'))
    
    produtos = Produto.query.filter_by(loja_id=loja_id, ativo=True).all()
    produtos_disponiveis = [produto for produto in produtos if produto.estoque_atual > 0]
    return render_template('vendas/nova.html', produtos=produtos_disponiveis)

@vendas_bp.route('/<int:venda_id>/marcar_pago')
@login_required
def marcar_pago(venda_id):
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    venda = Venda.query.get_or_404(venda_id)
    
    if venda.loja_id != int(loja_id):
        flash('Você não tem permissão para alterar esta venda.', 'error')
        return redirect(url_for('vendas.index'))
    
    venda.pago = True
    db.session.commit()
    
    flash('Venda marcada como paga com sucesso!', 'success')
    return redirect(url_for('vendas.index'))

@vendas_bp.route('/<int:venda_id>/excluir')
@login_required
def excluir(venda_id):
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    venda = Venda.query.get_or_404(venda_id)
    
    if venda.loja_id != int(loja_id):
        flash('Você não tem permissão para excluir esta venda.', 'error')
        return redirect(url_for('vendas.index'))
    
    # Return items to stock
    for item in venda.itens:
        produto = Produto.query.get(item.produto_id)
        produto.estoque_atual += item.quantidade
    
    venda.ativo = False
    db.session.commit()
    
    flash('Venda excluída com sucesso!', 'success')
    return redirect(url_for('vendas.index'))

@vendas_bp.route('/devolvendo')
@login_required
def devendo():
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    # Get all unpaid credit sales
    vendas_devendo = Venda.query.filter_by(
        loja_id=loja_id,
        ativo=True,
        pago=False,
        forma_pagamento='fiado'
    ).all()
    
    # Group by customer
    clientes = {}
    for venda in vendas_devendo:
        if venda.cliente_nome not in clientes:
            clientes[venda.cliente_nome] = {
                'total': 0,
                'vendas': []
            }
        clientes[venda.cliente_nome]['total'] += venda.total
        clientes[venda.cliente_nome]['vendas'].append(venda)
    
    return render_template('devendo.html', clientes=clientes)


# editar venda - permitir editar apenas vendas do dia e do usuario logado
@vendas_bp.route('/<int:venda_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(venda_id):
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    venda = Venda.query.get_or_404(venda_id)
    
    if venda.loja_id != int(loja_id):
        flash('Você não tem permissão para editar esta venda.', 'error')
        return redirect(url_for('vendas.index'))
    
    if venda.data != date.today():
        flash('Só é permitido editar vendas do dia.', 'error')
        return redirect(url_for('vendas.index'))
    
    if request.method == 'POST':
        cliente_nome = request.form.get('cliente_nome')
        forma_pagamento = request.form.get('forma_pagamento')
        total_venda = float(request.form.get('total'))
        
        venda.cliente_nome = cliente_nome
        venda.forma_pagamento = forma_pagamento
        venda.pago = (forma_pagamento != 'fiado')
        venda.total = total_venda
                      

        db.session.commit()
        flash('Venda atualizada com sucesso!', 'success')
        return redirect(url_for('vendas.index'))
    produtos = Produto.query.filter_by(loja_id=loja_id, ativo=True).all()
    produtos_disponiveis = [produto for produto in produtos if produto.estoque_atual > 0] 
    return render_template('vendas/editar.html', venda=venda, produtos=produtos_disponiveis)