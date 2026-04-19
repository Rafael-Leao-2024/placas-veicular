from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from app import db
from app.models.loja import Loja
from app.models.vendedor import Vendedor

loja_bp = Blueprint('loja', __name__)

@loja_bp.route('/selecionar', methods=['GET', 'POST'])
@login_required
def selecionar():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'selecionar':
            loja_id = request.form.get('loja_id')
            loja = Loja.query.get(loja_id)
            
            if loja and loja.ativo:
                # Check if user is a seller in this store
                vendedor = Vendedor.query.filter_by(
                    user_id=current_user.id,
                    loja_id=loja_id,
                    ativo=True
                ).first()
                if vendedor:
                    session['loja_id'] = loja.id
                    session['loja_nome'] = loja.nome
                    flash(f'Loja {loja.nome} selecionada com sucesso!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    # Criar um vendedor ativo para o usuário nessa loja
                    novo_vendedor = Vendedor(user_id=current_user.id, loja_id=loja.id, ativo=True)
                    db.session.add(novo_vendedor)
                    db.session.commit()
                    session['loja_id'] = loja.id
                    session['loja_nome'] = loja.nome
                    flash(f'Você foi adicionado como vendedor da loja {loja.nome} e selecionou a loja com sucesso!', 'success')
                    return redirect(url_for('dashboard'))
                
                
        elif action == 'criar':
            if not current_user.is_admin:
                flash('Apenas administradores podem criar novas lojas.', 'error')
                return redirect(url_for('loja.selecionar'))
            
            nome_loja = request.form.get('nome_loja')
            
            if nome_loja:
                nova_loja = Loja(nome=nome_loja, ativo=True)
                db.session.add(nova_loja)
                db.session.commit()
                db.session.refresh(nova_loja)  # Refresh to get the new loja ID
                
                # pegar o vendedor
                vendedor = Vendedor.query.filter_by(user_id=current_user.id, loja_id=nova_loja.id).first()
                
                if not vendedor:
                    vendedor = Vendedor(user_id=current_user.id, loja_id=nova_loja.id, ativo=True)
                    db.session.add(vendedor)
                    db.session.commit()
                    flash('Você foi adicionado como vendedor da nova loja.', 'success')
                    return redirect(url_for('dashboard'))                             
                
                flash(f'Loja {nome_loja} criada com sucesso!', 'success')
                session['loja_id'] = nova_loja.id
                session['loja_nome'] = nova_loja.nome
                return redirect(url_for('dashboard'))
    
    if current_user.is_admin:
        # lojas_disponiveis = Loja.query.filter_by(ativo=True).join(Vendedor).filter(Vendedor.user_id == current_user.id).all()
        lojas_disponiveis = Loja.query.filter_by(ativo=True).all()
    return render_template('loja/selecionar.html', lojas=lojas_disponiveis)