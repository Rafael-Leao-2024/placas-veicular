# maraca a venda de id 21 ativo == false
from app import create_app, db
from app.models.pagamento import Pagamento
from app.models.venda import Venda
from app.models.item_venda import ItemVenda


app = create_app()

with app.app_context():
    pg = Pagamento.query.get(1)
    # colocar pago em id 2
    pg.status = "pago"
    db.session.commit()
