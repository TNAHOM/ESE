from flask import render_template, redirect, url_for, flash, request, Blueprint
from main.models import User
from main.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def school():
	return render_template('home.html')

@views.route('/disabled')
def disabled():
	# LIVE url -> process_live.check_shape
	flash('This option is temporarily disabled', category='info')
	return render_template('home.html')

@views.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		attempted_user = User.query.filter_by(email=form.email.data).first()
		if attempted_user and attempted_user.check_password(
			attempted_password=form.password.data
		):
			login_user(attempted_user)
			flash(f'You have successfully Logged in as: {attempted_user.username}', category='success')
			return redirect(url_for(f'views.{current_user.role.lower()}'))
		else:
			print(form.errors, 'ddddd')
			flash('Username or password doesnt match! Please try again', category='danger')
			
		
	return render_template('login.html', form=form)

@views.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out', category='info')
	return redirect(url_for('views.login'))
