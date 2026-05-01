from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from app import db
from app.models.produto import Produto
from app.models.venda import Venda
from app.models.item_venda import ItemVenda

estoque_bp = Blueprint('estoque', __name__)

@estoque_bp.route('/')
@login_required
def index():
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    produtos = Produto.query.filter_by(loja_id=loja_id, ativo=True).all()
    print('{} vendo o estoque'.format(current_user.name))
    return render_template('estoque/index.html', produtos=produtos)

@estoque_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')
        preco_venda = float(request.form.get('preco_venda'))
        estoque_inicial = int(request.form.get('estoque_inicial'))
        
        produto = Produto(
            codigo=codigo,
            descricao=descricao,
            preco_venda=preco_venda,
            estoque_inicial=estoque_inicial,
            estoque_atual=estoque_inicial,
            loja_id=loja_id,
            ativo=True
        )
        
        db.session.add(produto)
        db.session.commit()
        
        print(f"Produto Criado {produto.descricao} por {current_user.name}")
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('estoque.index'))
    
    return render_template('estoque/novo.html')

@estoque_bp.route('/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar(produto_id):
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    produto = Produto.query.get_or_404(produto_id)
    
    if int(produto.loja_id) != int(loja_id):
        flash('Você não tem permissão para editar este produto.', 'error')
        return redirect(url_for('estoque.index'))
    
    if request.method == 'POST':
        produto.codigo = request.form.get('codigo')
        produto.descricao = request.form.get('descricao')
        produto.preco_venda = float(request.form.get('preco_venda'))
        
        # Manual stock adjustment
        novo_estoque = int(request.form.get('estoque_atual'))
        if novo_estoque != produto.estoque_atual:
            antigo = produto.estoque_atual
            produto.estoque_atual = novo_estoque
        
        db.session.commit()
        print(f"{current_user.name} Produto {produto.descricao} editado valor antigo {antigo} por {novo_estoque}")
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('estoque.index'))
    
    return render_template('estoque/editar.html', produto=produto)

@estoque_bp.route('/excluir/<int:produto_id>')
@login_required
def excluir(produto_id):
    loja_id = session.get('loja_id')
    if not loja_id:
        return redirect(url_for('loja.selecionar'))
    
    produto = Produto.query.get_or_404(produto_id)
    
    if produto.loja_id != int(loja_id):
        flash('Você não tem permissão para excluir este produto.', 'error')
        return redirect(url_for('estoque.index'))
    
    # Check if product has any active sales
    has_sales = ItemVenda.query.join(Venda).filter(
        ItemVenda.produto_id == produto_id,
        Venda.ativo == True
    ).first()
    
    if has_sales:
        flash('Não é possível excluir produto com vendas associadas ou estoque não zerado.', 'error')
    else:
        produto.ativo = False
        db.session.commit()
        print(f"{current_user.name} excluiu o {produto.descricao}")
        flash('Produto excluído com sucesso!', 'success')
    
    return redirect(url_for('estoque.index'))