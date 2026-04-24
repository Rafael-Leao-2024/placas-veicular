from flask import Flask, redirect, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import models
    from app.models.user import User
    from app.models.loja import Loja
    from app.models.vendedor import Vendedor
    from app.models.produto import Produto
    from app.models.venda import Venda
    from app.models.item_venda import ItemVenda
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.loja.routes import loja_bp
    from app.estoque.routes import estoque_bp
    from app.vendas.routes import vendas_bp
    from app.relatorios.routes import relatorios_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(loja_bp, url_prefix='/loja')
    app.register_blueprint(estoque_bp, url_prefix='/estoque')
    app.register_blueprint(vendas_bp, url_prefix='/vendas')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Check if user has selected a store
        if not session.get('loja_id'):
            return redirect(url_for('loja.selecionar'))
        
        return redirect(url_for('dashboard'))
    
    @app.route('/dashboard')
    def dashboard():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not session.get('loja_id'):
            return redirect(url_for('loja.selecionar'))
        
        from app.models.venda import Venda
        from datetime import datetime
        
        loja_id = session.get('loja_id')
        today = datetime.now().date()
        # pegar vendas do dia do usuario logado e do loja do usuario logado
        
        vendas = Venda.query.filter_by(loja_id=loja_id).filter(Venda.data == today).all()
        print(vendas)
        vendas = [venda for venda in vendas if venda.ativo == True]
        print(vendas)

        total_vendas = len(vendas)
        total_recebido = sum(venda.total for venda in vendas if venda.pago == True)
        total_devendo = sum(venda.total for venda in vendas if venda.forma_pagamento.lower() == 'fiado' and venda.pago == False or venda.forma_pagamento.lower() == 'cartão' and venda.pago == False)
        
        return render_template('dashboard.html',
                             total_vendas=total_vendas,
                             total_recebido=total_recebido,
                             total_devendo=total_devendo,
                             )
    
    @login_manager.user_loader
    def load_user(id):
        from app.models.user import User
        return User.query.get(int(id))
    
    return app