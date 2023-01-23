from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
import cv2
from evaluator import run2
from flask_login import login_required
import uuid

process = Blueprint('process', __name__)

camera = cv2.VideoCapture(3)


@process.route('/stream')
def process_img_1():
	answer = run2.final_ans()
	# answersheet = run2.qrcode_reader()
	print(answer, 'answers')
	if answer == 'No Barcode Detected' or None:
		return flash(answer, category='error')
	else:
		print('if passed else')
		# answer = run2.ans_num(answer2)
		if run2.gen(answer)=='No sheet detected':
			return run2.gen(answer)
		else:
			return Response(run2.gen(answer)[0], mimetype='multipart/x-mixed-replace; boundary=frame')


@process.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
	answersheet = run2.qrcode_reader()
	
	if answersheet=='No barcode is detected' or 'Please place the sheet properly':
		flash(answersheet, category='danger')
		display = 'false'
		score = None
	
	else:
		# answers = run2.ans_num()
		print(run2.gen(), '111111111111111111')
		# score = run2.gen(answer)[1]
		score = 21
		print(score, 'score')
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
						
						return redirect(url_for('process.evaluate')), flash(f'Successfully saved :) for {name}', category='success')
					elif does_exist:
						return redirect(url_for('process.evaluate')), flash(f'Data Already Saved', category='danger')
	
	# print(display)
	return render_template('evaluate.html', display=display, score=score)

