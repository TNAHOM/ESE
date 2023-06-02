import datetime

from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from evaluator import run_folder, run_file
from flask_login import login_required, current_user
import uuid
import os
import cv2
# from . import views

process_file = Blueprint('process_file', __name__)

class AllInOneFolder:
	def __init__(self, image=None, qrcode=None):
		self.qrcode = qrcode
		self.answer_folder = run_folder.final_ans(self.qrcode)
		self.image = image
	
	def folder(self):
		gen = run_folder.gen_folder(self.answer_folder[0], self.image)
		return gen, self.answer_folder[0]
	
	def folder_2(self):
		gen = run_folder.gen_folder_2(self.answer_folder[0], self.image)
		return gen, self.answer_folder[0]

@process_file.route('/streams6', methods=['GET', 'POST'])
@login_required
def upload_file():
	if request.method=='POST':
		directory = request.form.get('file')
		if directory[-3:] == ('jpg' or 'png' or 'jpeg'):
			img = cv2.imread(directory)
			qrcode = run_file.qrcode_reader(img)
			print(qrcode, type(qrcode))
			id_qrcode = qrcode[7:43]
 
			if qrcode[-7:-2] =='front':
				final_answer = run_file.final_ans(id_qrcode, email=current_user.email)
				all_together_0 = run_file.gen_file_choose(final_answer[0], img, 0)
				all_together_1 = run_file.gen_file_choose(final_answer[0], img, 1)
				# all_together_tf = run_file.gen_file_tf(final_answer[1], img, 2)
		
				if final_answer =='No Barcode Detected' or None:
					flash('No barcode detected', category='danger')
					return redirect(url_for('views.school'))
				else:
					# bind_img = run_file.bind_img(all_together_0[0], all_together_1[0], all_together_tf[0])
					bind_img = run_file.bind_img(all_together_0[0], all_together_1[0])

					return Response(bind_img, mimetype='multipart/x-mixed-replace; boundary=frame')
			else:
				final_answer_fill = run_file.final_ans(qrcode, email=current_user.email)
				fill_img = run_file.gen_write(final_answer_fill[0])
		else:
			flash('Their is no image detected with the extension *.jpg, *.png, *.jpeg', category='danger')
			return redirect(url_for('process_file.upload_file'))
	elif request.method == 'GET':
			display = False
			return render_template('upload file.html', display=display)

############  USE FOLDER ############
@process_file.route('/evaluate_folder', methods=['POST', 'GET'])
@login_required
def upload_folder():
	scores = []
	names = []
	num_saved = 0
	num_existed = 0

	existed = {}
	new_result = {}
	if request.method=='POST':
		display = True

		directorate = request.form.get('file')
		for x in os.listdir(directorate):
			# print(x, x[:-4])
			user_name = x[:-4]
			img = cv2.imread(directorate + '\\' + x)
			qrcode = run_folder.qrcode_reader(img)
			all_in_one = AllInOneFolder(img, qrcode)
			# [:-4] for excluding .jpg
			to_db = run_folder.connectionToDB(qrcode)
			score = all_in_one.folder()[0][1] + all_in_one.folder_2()[0][1]
			wrong_ans = str(all_in_one.folder()[0][3] + all_in_one.folder_2()[0][3])
			wrong_que = str(all_in_one.folder()[0][2] + ([x+40 for x in all_in_one.folder_2()[0][2]]))
			# print(wrong_que, wrong_ans)

			for user in to_db[1]:
				if user[10] == user_name and user[12] == 'Student':
					# print(user_name, user[10])
					new_uuid = uuid.uuid4()
					my_uuid = uuid.UUID(user[9])
					to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
						(qrcode, my_uuid))
					does_exist = to_db[3].fetchone()
					# print(does_exist)
					if does_exist is None:
						insert_record = (new_uuid, score, user[9], qrcode, 'true', datetime.date.today(), wrong_ans, wrong_que)
						to_db[4].execute(to_db[2], insert_record)
						to_db[5].commit()
						names.append(user[10])
						scores.append(score)
						num_saved += 1
						new_result.update({user[10]: score})

					elif does_exist:
						num_existed+=1
						
						existed.update({user[10]:score})
						print(f'data already existed of {user}')
					else:
						print('Dont know the error')
				else:
					print('User Doesn/"t exist')
		print(new_result)
		flash(f'{num_saved} Has been saved', category='success')
		flash(f'{num_existed} Has already been registered', category='danger')

		return render_template('evaluation description.html', display=display, score=scores, new_result=new_result,
			 existed=existed)
	
	
	elif request.method == 'GET':
		display = False
		return render_template('upload folder.html', display=display, score=scores, name=names, names=range(len(names)))
