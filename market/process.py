from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
import cv2
from evaluator import run2
from flask_login import login_required
import uuid

process = Blueprint('process', __name__)

camera = cv2.VideoCapture(3)

answer = run2.final_ans()
# print(answer, 'answer0.0')

@process.route('/stream')
def process_img_1():
	# answersheet = run2.qrcode_reader()
	# gen = run2.gen()
	# print(gen, 'gen')
	print(answer, 'answers')
	if answer == 'No Barcode Detected':
		print(answer, 'answer2')
		return flash(answer, category='error')
	
	else:
		print('if passed else')
		# answer = run2.ans_num(answer2)
		gen = run2.gen(answer)
		# print(gen)
		if gen=='No sheet detected':
			return gen
		
		else:
			return Response(run2.gen(answer)[0], mimetype='multipart/x-mixed-replace; boundary=frame')


@process.route('/streams2')
def process_img_2():
	# answersheet = run2.qrcode_reader()
	# gen = run2.gen()
	# print(gen, 'gen')
	# print(answer, 'answers')
	if answer=='No Barcode Detected':
		# print(answer, 'answer2')
		return flash(answer, category='error')
	
	else:
		# print('if passed else')
		gen = run2.gen2(answer)
		# print(gen)
		if gen=='No sheet detected':
			return gen
		
		else:
			return Response(gen[0], mimetype='multipart/x-mixed-replace; boundary=frame')


@process.route('/streams3')
def shape():
	gen = run2.shape1()
	return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/check')
def check_shape():
	return render_template('check_shape.html')
@process.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
	answersheet = run2.qrcode_reader()
	# print(answersheet, '8888888')
	# print(answer, 'answerev')
	if answer=='No barcode is detected':
		# print(answersheet, 'answersheet2')
		flash(answer, category='danger')
		display = 'false'
		score = 'None'
	else:
		# answers = run2.ans_num()
		# print(run2.gen(answer)[1], '111111111111111111')
		score = run2.gen(answer)[1] + run2.gen2(answer)[1]
		# score = 21
		# print(score, 'score')
		display = 'true'
		to_db = run2.connectionToDB()
		if request.method == 'POST':
			name = request.form.get('name')
			for data in to_db[1]:
				if data[10] == name:
					my_uuid = uuid.UUID(data[9])
					to_db[6].execute(f"SELECT * FROM base_exam WHERE unique_name='{answersheet}'")
					exam_id = to_db[6].fetchone()
					# print(exam_id, '+++++++')
					to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s", ('b05cad80-419d-4912-ab97-5eba7a40e924', my_uuid))
					does_exist = to_db[3].fetchone()
					
					if does_exist is None:
						new_uuid = uuid.uuid4()
						insert_record = (new_uuid, score, data[9], 'b05cad80-419d-4912-ab97-5eba7a40e924', 'true')
						to_db[4].execute(to_db[2], insert_record)
						to_db[5].commit()
						
						return redirect(url_for('views.school')), flash(f'Successfully saved :) for {name}', category='success')
					elif does_exist:
						return redirect(url_for('views.school')), flash(f'Data Already Saved', category='danger')
				else:
					return redirect(url_for('views.school')), flash(f'Name does not exist', category='danger')
	# print(display)
	return render_template('evaluate.html', display=display, score=score)

