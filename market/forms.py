from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from .models import User

class RegisterForm(FlaskForm):
	
	@staticmethod
	def validate_username(self, check_username):
		user = User.query.filter_by(username=check_username.data).first()
		if user:
			raise ValidationError('Username already exist!!. Please try a different Username')
		
	@staticmethod
	def validate_email(self, check_email):
		email = User.query.filter_by(email=check_email.data).first()
		if email:
			raise ValidationError('Email already exist!!. Please try a different Email')
		
	
	username = StringField(label='User Name:', validators=[Length(min=2, max=20), DataRequired()])
	email = StringField(label='Email:', validators=[Email(), DataRequired()])
	password = PasswordField(label='Password:', validators=[Length(min=4), DataRequired()])
	password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
	submit = SubmitField(label='Create Account')
	
class LoginForm(FlaskForm):
	email = StringField(label='Email:', validators=[Email(), DataRequired()])
	password = PasswordField(label='Password:', validators=[DataRequired()])
	role = StringField(label='Role')
	submit = SubmitField(label='Sign In')
