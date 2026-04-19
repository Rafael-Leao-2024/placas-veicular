from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.vendedor import Vendedor
from app.models.loja import Loja

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def index():
    if not current_user.is_admin:
        flash("Acesso negado. Área restrita para administradores.", "error")
        return redirect(url_for("dashboard"))
    
    vendedores = Vendedor.query.join(User).filter(User.id == Vendedor.user_id).all()
    lojas = Loja.query.filter_by(ativo=True).join(Vendedor).filter(Vendedor.user_id == current_user.id).all()  

    return render_template("admin/index.html", vendedores=vendedores, lojas=lojas)


@admin_bp.route("/toggle_vendedor/<int:vendedor_id>")
@login_required
def toggle_vendedor(vendedor_id):
    if not current_user.is_admin:
        flash("Acesso negado.", "error")
        return redirect(url_for("dashboard"))

    vendedor = Vendedor.query.get_or_404(vendedor_id)
    vendedor.ativo = not vendedor.ativo
    db.session.commit()

    status = "ativado" if vendedor.ativo else "desativado"
    flash(f"Vendedor {status} com sucesso!", "success")

    return redirect(url_for("admin.index"))


@admin_bp.route("/toggle_loja/<int:loja_id>")
@login_required
def toggle_loja(loja_id):
    if not current_user.is_admin:
        flash("Acesso negado.", "error")
        return redirect(url_for("dashboard"))

    loja = Loja.query.get_or_404(loja_id)
    loja.ativo = not loja.ativo
    db.session.commit()

    status = "ativada" if loja.ativo else "desativada"
    flash(f"Loja {status} com sucesso!", "success")

    return redirect(url_for("admin.index"))
