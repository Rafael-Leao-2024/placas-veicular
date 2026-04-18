from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    vendedores = db.relationship('Vendedor', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'