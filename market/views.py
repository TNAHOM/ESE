from flask import render_template, redirect, url_for, flash, request, Blueprint
from market import app, db
from market.models import User
from market.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
import psycopg2, psycopg2.extras
import uuid

views = Blueprint('views', __name__)

def connectionToDB():
	try:
		return psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
	except:
		print('Cant connect to the DB')

@views.route('/admin')
@login_required
def admin():
	return render_template('admin.html')

@views.route('/')
@login_required
def school():
	return render_template('home.html')

@views.route('/market-place', methods=['GET', 'POST'])
@login_required
def market():
	conn = connectionToDB()
	cur = conn.cursor()
	cur_user = conn.cursor()
	cur_exist = conn.cursor()
	try:
		cur.execute('SELECT * FROM base_exam')
		cur_user.execute('SELECT * FROM base_user')
		
		result = cur.fetchall()
		result_user = cur_user.fetchall()
		insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY) VALUES (%s,%s,%s,%s,%s)"""
		
		if request.method=='POST':
			name = request.form.get('name')
			score = request.form.get('score')
			exam_id = request.form.get('exam_id')
			for data in result_user:
				if data[10]==name:
					my_uuid = uuid.UUID(data[9])
					cur_exist.execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s", (exam_id, my_uuid))
					does_exist = cur_exist.fetchone()
					
					if does_exist is None:
						new_uuid = uuid.uuid4()
						insert_record = (new_uuid, score, data[9], exam_id, 'true')
						cur.execute(insert_data_from, insert_record)
						conn.commit()
						
						return redirect(url_for('views.market')), flash(f'Successfully saved :) for {name}', category='success')
					elif does_exist:
						return redirect(url_for('views.market')), flash(f'Data Already Saved', category='danger')

	except Exception as er:
		return er
	
	finally:
		cur.close()
		cur_user.close()
	
	return render_template('market.html', rd=result, rd_user=result_user)

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
			
	if form.errors != {}:
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
			print(form.errors)
			flash('Username or password doesnt match! Please try again', category='danger')
		
	return render_template('login.html', form=form)

@views.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out', category='info')
	return redirect(url_for('views.login'))






