from flask import render_template, redirect, url_for, flash, session, Blueprint, request
from main.models import User
from main.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from . import db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def school():
	return render_template('home.html')

@views.route('/admin')
@login_required
def admin():
	return render_template('admin.html')


@views.route('/disabled')
def disabled():
	# LIVE url -> process_live.check_shape
	flash('This option is temporarily disabled', category='info')
	return render_template('home.html')


@views.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		if form:
			new_user = User(username=form.username.data, email=form.email.data,
				password=form.password.data, role='School'
			)
			db.session.add(new_user)
			db.session.commit()
			
			flash(f'Account created successfully!! {new_user.username}', category='success')
			return redirect(url_for(f'views.{(current_user.role).lower()}'))
		else:
			print('error')
	
	if form.errors!={}:
		for err_msg in form.errors.values():
			flash(f'There was an error creating a user: {err_msg}')
	
	return render_template('register.html', form=form)

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
			print(form.errors, 'error')
			flash('Username or password doesnt match! Please try again', category='danger')

	return render_template('login.html', form=form)

@views.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out', category='info')
	return redirect(url_for('views.login'))
