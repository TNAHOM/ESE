import datetime

from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from evaluator import run2, run3
from flask_login import login_required
import uuid
import os
import cv2


process = Blueprint('process', __name__)

class AllInOne:
	def __init__(self):
		self.answersheet = run2.qrcode_reader()
		self.answer = run2.final_ans(self.answersheet)

		self.answersheet_folder = run3.qrcode_reader()
		self.answer_folder = run3.final_ans(self.answersheet_folder)
		# print(run3.gen_folder(self.answer_folder[0])[1], self.answersheet_folder)
	def first_choose(self):
		gen = run2.gen(self.answer[0])
		return gen, self.answer[0]
	
	def second_choose(self):
		gen = run2.gen2(self.answer[0])
		return gen, self.answer[0]

	@staticmethod
	def check_shape():
		gen = run2.shape1()
		return gen
	
	def true_false(self):
		gen = run2.gen_tf(self.answer[1])
		return gen, self.answer[1]
	
	def folder(self):
		gen = run3.gen_folder(self.answer_folder[0])
		return gen, self.answer_folder[0]
	
	def folder_2(self):
		gen = run3.gen_folder_2(self.answer_folder[0])
		return gen, self.answer_folder[0]

############ LIVE CAM ############

@process.route('/streams')
def process_img_1():
	all_in_one = AllInOne().first_choose()[0]
	if all_in_one[1] =='No Barcode Detected' or None:
		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
	else:
		img = all_in_one[0]
		return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/streams2')
def process_img_2():
	all_in_one = AllInOne().second_choose()[0]
	if all_in_one[1]=='No Barcode Detected' or None:
		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
	else:
		img = all_in_one[0]
		return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')
	
@process.route('/streams3')
def process_img_tf():
	all_in_one = AllInOne().true_false()
	if all_in_one[1]=='No Barcode Detected' or None:
		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
	else:
		img = all_in_one[0]
		return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/streams4')
def shape():
	gen = run2.shape1()
	return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/check')
def check_shape():
	all_in_one = AllInOne()

	if all_in_one.check_shape() == 'No sheet detected':
		flash('No sheet detected', category='danger')
		return redirect(url_for('views.school'))
	elif all_in_one.answersheet is None:
		flash('Difficulty on reading Qrcode', category='danger')
		return redirect(url_for('views.school'))
	
	elif any(all_in_one.first_choose() or all_in_one.second_choose()) == 'Put the answer sheet Appropriately':
		print(all_in_one.first_choose() or all_in_one.second_choose())
		return redirect(url_for('views.school')), flash(all_in_one.first_choose() or all_in_one.second_choose(), category='danger')
	else:
		return render_template('check_shape.html')

@process.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
	try:
		all_in_one = AllInOne()
		parameters_list = [
			all_in_one.first_choose()[0][3], all_in_one.second_choose()[0][3],
			all_in_one.first_choose()[0][2], all_in_one.second_choose()[0][2],
		]
		parameters_int = [all_in_one.first_choose()[0][1], all_in_one.second_choose()[0][1]]
		# print(all_in_one.first_choose()[0], all_in_one.second_choose()[0], 'kokokt')
		# print(list(x for x in parameters_list), 'list')
		# print(list(x for x in parameters_list), 'list')
		# print(list(x for x in parameters_int), 'int')
		
		if all(type(x) == list for x in parameters_list) and all(type(x) == int for x in parameters_int):
			# USED LIST COMPREHENSION BECAUSE THE INDEX/QUESTIONS WHERE UPTO 40
			print(all_in_one.first_choose()[0][2], all_in_one.second_choose()[0][2], 'WRONG2')
			wrong_que = all_in_one.first_choose()[0][2] + [i + 40 for i in all_in_one.second_choose()[0][2]]
			# print(wrong_que, 'wrong_que')
			wrong_ans = all_in_one.first_choose()[0][3] + all_in_one.first_choose()[0][3]
			# print(wrong_ans, 'wrong_ans')
			print(parameters_int[0], parameters_int[1])
			score = parameters_int[0] + parameters_int[1]
			qr_code = all_in_one.answersheet
			# print(qr_code)
			to_db = run2.connectionToDB(qr_code)
			# print(len(to_db[1]))
			# for x in to_db[7]:
				# for y in x:
				# 	print(x[9])
				# 	print('-------')
			if request.method=='POST':
				name = request.form.get('name')
				for y in range(len(to_db[1])):
					print(y, '--', to_db[1][y][10])
					data = to_db[1][y]
					if data[10]==name:
						my_uuid = uuid.UUID(data[9])
						to_db[6].execute(f"SELECT * FROM base_exam WHERE unique_name='{qr_code}'")
						# exam_id = to_db[6].fetchone()
						# print(exam_id, '+++++++')
						to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
							(qr_code, my_uuid))
						does_exist = to_db[3].fetchone()
						
						if does_exist is None:
							new_uuid = uuid.uuid4()
							insert_record = (new_uuid, score, data[9], qr_code, 'true', datetime.date.today(), str(wrong_ans))
							to_db[4].execute(to_db[2], insert_record)
							to_db[5].commit()
							
							return redirect(url_for('views.school')), flash(f'Successfully saved :) for {name}', category='success')
						elif does_exist:
							return redirect(url_for('views.school')), flash(f'Data Already Saved', category='danger')
					else:
						flash(f'Name does not exist', category='danger')
		else:
			return redirect(url_for('views.school')), flash('Somthing is wrong please', category='danger')
	except Exception as ex:
		print(ex, 'lioliolio')
		return redirect(url_for('process.check_shape')), flash('Please try again ot try to adjust the paper', category='danger')
	
	return render_template('evaluate.html', score=score)