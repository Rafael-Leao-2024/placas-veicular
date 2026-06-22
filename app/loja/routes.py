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

        # ==========================
        # SELECIONAR LOJA
        # ==========================
        if action == 'selecionar':
            loja_id = request.form.get('loja_id')

            if not loja_id:
                flash('Loja inválida.', 'error')
                return redirect(url_for('loja.selecionar'))

            loja = db.session.get(Loja, int(loja_id))

            if not loja or not loja.ativo:
                flash('Loja não encontrada ou inativa.', 'error')
                return redirect(url_for('loja.selecionar'))

            # Procura se o usuário já é vendedor desta loja
            vendedor = Vendedor.query.filter_by(
                user_id=current_user.id,
                loja_id=loja.id
            ).first()

            # Se não existir, cria apenas uma vez
            if not vendedor:
                vendedor = Vendedor(
                    user_id=current_user.id,
                    loja_id=loja.id,
                    ativo=True
                )
                db.session.add(vendedor)
                db.session.commit()

            # Se existir mas estiver inativo, reativa
            elif not vendedor.ativo:
                vendedor.ativo = True
                db.session.commit()

            session['loja_id'] = loja.id
            session['loja_nome'] = loja.nome

            flash(f'Loja {loja.nome} selecionada com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        # ==========================
        # CRIAR LOJA
        # ==========================
        elif action == 'criar':

            if not current_user.is_admin:
                flash('Apenas administradores podem criar novas lojas.', 'error')
                return redirect(url_for('loja.selecionar'))

            nome_loja = request.form.get('nome_loja', '').strip()

            if not nome_loja:
                flash('Informe o nome da loja.', 'error')
                return redirect(url_for('loja.selecionar'))

            # Evita criar lojas duplicadas
            loja_existente = Loja.query.filter_by(nome=nome_loja).first()

            if loja_existente:
                flash('Já existe uma loja com esse nome.', 'warning')
                return redirect(url_for('loja.selecionar'))

            nova_loja = Loja(
                nome=nome_loja,
                ativo=True
            )

            db.session.add(nova_loja)
            db.session.commit()

            # Verifica se já existe vínculo do usuário com a loja
            vendedor = Vendedor.query.filter_by(
                user_id=current_user.id,
                loja_id=nova_loja.id
            ).first()

            # Só cria se não existir
            if not vendedor:
                vendedor = Vendedor(
                    user_id=current_user.id,
                    loja_id=nova_loja.id,
                    ativo=True
                )
                db.session.add(vendedor)
                db.session.commit()

            session['loja_id'] = nova_loja.id
            session['loja_nome'] = nova_loja.nome

            flash(f'Loja {nome_loja} criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))

    # ==========================
    # LISTAGEM DE LOJAS
    # ==========================
    if current_user.is_admin:
        lojas_disponiveis = Loja.query.filter_by(
            ativo=True
        ).order_by(Loja.nome).all()
    else:
        lojas_disponiveis = (
            Loja.query
            .join(Vendedor, Vendedor.loja_id == Loja.id)
            .filter(
                Loja.ativo == True,
                Vendedor.user_id == current_user.id,
                Vendedor.ativo == True
            )
            .order_by(Loja.nome)
            .all()
        )

    return render_template(
        'loja/selecionar.html',
        lojas=lojas_disponiveis
    )