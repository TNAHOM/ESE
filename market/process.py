import datetime

from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from evaluator import run2
from flask_login import login_required
import uuid

process = Blueprint('process', __name__)


# USE gen = runs2. HERE
# answersheet = run2.qrcode_reader()
# answer = run2.final_ans(answersheet)

@process.route('/stream')
def process_img_1():
	answersheet = run2.qrcode_reader()
	answer = run2.final_ans(answersheet)
	
	if answer == 'No Barcode Detected' or None:
		# print(answer, 'answer2')
		return redirect(url_for('views.school')), flash(f'no bar', category='danger')
	else:
		print(len(answer))
		# print('if passed else')
		# answer = run2.ans_num(answer2)
		gen = run2.gen(answer)
		# print(gen)
		if gen=='No sheet detected':
			return gen
		else:
			return Response(run2.gen(answer)[0], mimetype='multipart/x-mixed-replace; boundary=frame')


@process.route('/streams2')
def process_img_2():
	answersheet = run2.qrcode_reader()
	answer = run2.final_ans(answersheet)
	# gen = run2.gen()
	# print(gen, 'gen')
	# print(answer, 'answers')
	if answer=='No Barcode Detected' or None:
		# print(answer, 'answer2')
		return redirect(url_for('views.school')), flash(f'no bar', category='danger')

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
	# print(gen)
	return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/check')
def check_shape():
	return render_template('check_shape.html')

@process.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
	answersheet = run2.qrcode_reader()
	# print(answer, 'answer')
	
	if answersheet=='No barcode is detected':
		flash(answersheet, category='danger')
		display = 'false'
		score = 'None'
	else:
		answer = run2.final_ans(answersheet)
		# USED LIST COMPREHENSION BECAUSE THE INDEX/QUESTIONS WHERE UPTO 40
		wrong_que = run2.gen(answer)[2] + [i+40 for i in run2.gen2(answer)[2]]
		# print(wrong_que, 'wrong_que')
		wrong_ans = run2.gen(answer)[3] + run2.gen2(answer)[3]
		# print(wrong_ans, 'wrong_ans')
		score = run2.gen(answer)[1] + run2.gen2(answer)[1]
		print(score, 'score')
		display = 'true'
		to_db = run2.connectionToDB(answersheet)
		print(len(to_db[1]))
		if request.method == 'POST':
			name = request.form.get('name')
			for y in range(len(to_db[1])):
				print(y,'--', to_db[1][y][10])
				data = to_db[1][y]
				if data[10] == name:
					my_uuid = uuid.UUID(data[9])
					to_db[6].execute(f"SELECT * FROM base_exam WHERE unique_name='{answersheet}'")
					# exam_id = to_db[6].fetchone()
					# print(exam_id, '+++++++')
					to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s", (answersheet, my_uuid))
					does_exist = to_db[3].fetchone()

					if does_exist is None:
						new_uuid = uuid.uuid4()
						# 'b05cad80-419d-4912-ab97-5eba7a40e924'
						insert_record = (new_uuid, score, data[9], answersheet, 'true', datetime.date.today(), str(wrong_ans))
						to_db[4].execute(to_db[2], insert_record)
						to_db[5].commit()

						return redirect(url_for('views.school')), flash(f'Successfully saved :) for {name}', category='success')
					elif does_exist:
						return redirect(url_for('views.school')), flash(f'Data Already Saved', category='danger')
				else:
					flash(f'Name does not exist', category='danger')
	# print(display)
	return render_template('evaluate.html', score=score)

