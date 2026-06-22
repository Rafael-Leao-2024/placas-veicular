from app import create_app
from app.models.loja import db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        user.is_admin = False
    db.session.commit()

    print(user.is_admin)
