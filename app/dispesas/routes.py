from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models.dispesas import DespesaSimples
from datetime import datetime, date



dispesas_bp = Blueprint('despesas', __name__, url_prefix='/despesas-simples')

@dispesas_bp.route('/')
@login_required
def listar():
    """Lista todas as despesas simples"""
    loja_id = session.get('loja_id')
    despesas = DespesaSimples.query.filter(DespesaSimples.loja_id == loja_id).order_by(DespesaSimples.data_despesa.desc()).all()
    total = sum(d.valor for d in despesas)
    return render_template('despesas/lista.html', despesas=despesas, total=total, now=datetime.now())


@dispesas_bp.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    """Adiciona uma nova despesa"""
    descricao = request.form.get('descricao', '').strip()
    valor = request.form.get('valor', 0, type=float)
    data_despesa = request.form.get('data_despesa')
    observacao = request.form.get('observacao', '').strip()
    
    if not descricao:
        flash('Descrição é obrigatória!', 'danger')
        return redirect(url_for('despesas_simples.listar'))
    
    if valor <= 0:
        flash('Valor deve ser maior que zero!', 'danger')
        return redirect(url_for('despesas_simples.listar'))
    
    try:
        if data_despesa:
            data_despesa = datetime.strptime(data_despesa, '%Y-%m-%d').date()
        else:
            data_despesa = date.today()
        
        despesa = DespesaSimples(
            descricao=descricao,
            valor=valor,
            data_despesa=data_despesa,
            observacao=observacao,
            loja_id=session.get('loja_id')
        )
        
        db.session.add(despesa)
        db.session.commit()
        
        flash('✅ Despesa adicionada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar despesa: {str(e)}', 'danger')
    
    return redirect(url_for('despesas.listar'))


@dispesas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Exclui uma despesa"""
    despesa = DespesaSimples.query.get_or_404(id)

    loja_id = session.get('loja_id')
    
    # Verificar se o usuário tem permissão
    if despesa.loja_id != loja_id and not current_user.is_owner:
        flash('Você não tem permissão para excluir esta despesa!', 'danger')
        return redirect(url_for('despesas.listar'))
    
    db.session.delete(despesa)
    db.session.commit()
    
    flash('✅ Despesa excluída!', 'success')
    return redirect(url_for('despesas.listar'))


@dispesas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita uma despesa existente"""
    despesa = DespesaSimples.query.get_or_404(id)
    loja_id = session.get('loja_id')

    
    # Verificar permissão
    if despesa.loja_id != loja_id and not current_user.is_owner:
        flash('Você não tem permissão para editar esta despesa!', 'danger')
        return redirect(url_for('despesas_simples.listar'))
    
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', 0, type=float)
        data_despesa = request.form.get('data_despesa')
        observacao = request.form.get('observacao', '').strip()
        
        if not descricao:
            flash('Descrição é obrigatória!', 'danger')
            return render_template('despesas/editar.html', despesa=despesa)
        
        if valor <= 0:
            flash('Valor deve ser maior que zero!', 'danger')
            return render_template('despesas/editar.html', despesa=despesa)
        
        try:
            despesa.descricao = descricao
            despesa.valor = valor
            despesa.observacao = observacao
            if data_despesa:
                despesa.data_despesa = datetime.strptime(data_despesa, '%Y-%m-%d').date()
            
            db.session.commit()
            flash('✅ Despesa atualizada!', 'success')
            return redirect(url_for('despesas_simples.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
    
    return render_template('despesas/editar.html', despesa=despesa)


@dispesas_bp.route('/total-mes')
@login_required
def total_mes():
    """Retorna o total de despesas do mês atual (API)"""
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    
    total = db.session.query(db.func.sum(DespesaSimples.valor)).filter(
        DespesaSimples.data_despesa >= inicio_mes,
        DespesaSimples.data_despesa <= hoje
    ).scalar() or 0
    
    return jsonify({
        'total': float(total),
        'mes': hoje.strftime('%B/%Y'),
        'quantidade': DespesaSimples.query.filter(
            DespesaSimples.data_despesa >= inicio_mes,
            DespesaSimples.data_despesa <= hoje
        ).count()
    })

