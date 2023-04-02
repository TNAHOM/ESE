import datetime

from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from evaluator import run2, run3
from flask_login import login_required
import uuid
import os
import cv2
import psycopg2

process_folder = Blueprint('process_folder', __name__)


class AllInOneFolder:
	def __init__(self, image=None, qrcode=None):
		self.qrcode = qrcode
		# self.answersheet_folder = run3.qrcode_reader()
		# self.answer_folder = run3.final_ans(self.answersheet_folder)
		self.answer_folder = run3.final_ans(self.qrcode)
		self.image = image
	
	def folder(self):
		gen = run3.gen_folder(self.answer_folder[0], self.image)
		return gen, self.answer_folder[0]
	
	def folder_2(self):
		gen = run3.gen_folder_2(self.answer_folder[0], self.image)
		return gen, self.answer_folder[0]


############  USE FOLDER ############
# @process_folder.route('/streams6')
# def process_img_folder_2():
# 	all_in_one = AllInOneFolder().folder_2()
# 	if all_in_one[1] =='No Barcode Detected' or None:
# 		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
# 	else:
# 		img = all_in_one[0][0]
# 		return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')
#
# @process_folder.route('/streams5')
# def process_img_folder():
# 	all_in_one = AllInOneFolder().folder()
# 	if all_in_one[1] =='No Barcode Detected' or None:
# 		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
# 	else:
# 		img = all_in_one[0][0]
# 		return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')

@process_folder.route('/use_folder', methods=['POST', 'GET'])
def upload_folder():
	scores = []
	names = []
	
	if request.method=='POST':
		display = True
		
		directorate = request.form.get('file')
		for x in os.listdir(directorate):
			# print(x, x[:-4])
			img = cv2.imread(directorate + '\\' + x)
			qrcode = run3.qrcode_reader(img)
			print(qrcode, x)
			all_in_one = AllInOneFolder(img, qrcode)
			# [:-4] for excluding .jpg
			to_db = run2.connectionToDB(qrcode)
			names.append(x[:-4])
			score = all_in_one.folder()[0][1] + all_in_one.folder_2()[0][1]
			scores.append(score)
			
			for y in range(len(to_db[1])):
				data = to_db[1][y]
				name = data[10]
				if type(names) is list:
					# for name in names:
					if data[10] in names:
						my_uuid = uuid.UUID(data[9])
						wrong_ans = 'placeholder'
						new_uuid = uuid.uuid4()
						to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
							(qrcode, my_uuid))
						does_exist = to_db[3].fetchone()
						# print(does_exist, 'exist')
						if does_exist is None:
							qrcode2 = run3.qrcode_reader(img)
							insert_record = (new_uuid, score, data[9], qrcode, 'true', datetime.date.today(), str(wrong_ans))
							to_db[4].execute(to_db[2], insert_record)
							to_db[5].commit()
							print(name, score, qrcode2)

							flash(f'Successfully saved :) for {name}', category='success')
							# print(name, 'Successfully saved :)')
						elif does_exist:
							# print(name, 'data already saved')
							flash(f'Data Already Saved', category='danger')
					
					elif data[10] != names:
						# # print(name, 'Name does not exist')
						# flash(f'Name does not exist', category='danger')
						continue
					else:
						print('DONT KNOW THE ERROR')
		# print(names, scores, new_uuid)
		
		return redirect(url_for('views.school'))

	else:
		display = False
	return render_template('upload folder.html', display=display, score=scores, name=names, names=range(len(names)))
