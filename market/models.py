from . import db, app, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer(), primary_key=True)
	username = db.Column(db.String(length=30), nullable=False, unique=True)
	email = db.Column(db.String(length=22), nullable=False, unique=True)
	password_hash = db.Column(db.String(length=128), nullable=False)
	role = db.Column(db.String(length=20), nullable=True)
	def __repr__(self):
		return f'Item {self.email}'
	
	@property
	def password(self):
		return self.password
	
	@password.setter
	def password(self, plain_password):
		self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')
		
	def check_password(self, attempted_password):
		return bcrypt.check_password_hash(self.password_hash, attempted_password)


with app.app_context():
	db.create_all()