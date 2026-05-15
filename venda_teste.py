# # maraca a venda de id 21 ativo == false
# from app import create_app, db
# from app.models.pagamento import Pagamento
# from app.models.venda import Venda
# from app.models.item_venda import ItemVenda


# app = create_app()

# with app.app_context():
#     # deletar todos pagamentos
#     Pagamento.query.delete()
#     db.session.commit()