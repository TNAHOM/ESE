import cv2
import numpy as np

from evaluator import top, process_answer_1
import psycopg2, psycopg2.extras

#####################
width, height = 738, 984
width_tf, height_tf = 550, 770

questions = 41
choices = 6
choices_tf = 2

############################

num_str = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
num_str_tf = {'true': 0, 'false': 1}

#######################
def gen_file_choose(answer=None, image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, 984, 1230).process_img()[0]
		final_img = process_answer_1.General(sliced_img, answer, questions, choices).func_choose()
		result = final_img[0]

		return final_img[2], result
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'
	
def gen_file_tf(answer=None, image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, width_tf, height_tf).process_img()[0]
		final_img = process_answer_1.General(sliced_img, answer, 11, 2).func_tf()
		
		result = final_img[0]
		# print(result, 'result')
		
		return final_img[2], result
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'

def qrcode_reader(image=None):
	identifier = process_answer_1.General(image).qrcode_reader()
	# print(identifier, '-------------------')
	return identifier

def ans_num_choose(ans):
	answer_list = []
	for x in ans:
		for z, y in num_str.items():
			if x==z:
				answer_list.append(y)
	return answer_list

def ans_num_tf(ans):
	answer_list = []
	for x in ans:
		for z, y in num_str_tf.items():
			if x == z:
				answer_list.append(y)
	return answer_list

def connectionToDB(unique_sub):
	try:
		conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
		cur = conn.cursor()
		cur_user = conn.cursor()
		cur_exist = conn.cursor()
		cur_exam = conn.cursor()
		
		cur.execute('SELECT * FROM base_exam')
		cur_user.execute(f"SELECT * FROM base_user WHERE role='Student'")
		cur_exam.execute(f"SELECT * FROM base_exam WHERE id='{unique_sub}'")
		exam_id = cur_exam.fetchone()

		result = cur.fetchall()
		result_user = cur_user.fetchall()
		# print(result_user, 'user')
		insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, FINISHED, INCORRECT_ANS) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
		return result, result_user, insert_data_from, cur_exist, cur, conn, cur_exam, exam_id
	except Exception as er:
		print(er)
		return er
	# finally:
	# 	close database

def to_list(variable):
	x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
	return x

def to_list_tf(variable):
	x = variable.replace(',', '').replace("'", '').replace('[', '').replace(']', '')
	return x

def answer_lists(unique_name):
	if unique_name is None:
		return 'No Barcode Detected'
	else:
		connection = connectionToDB(unique_name)[7]
	
		answer_list_choose = list(to_list(connection[6]))
		answer_list_tf = (to_list_tf(connection[9])).split()

		return answer_list_choose, answer_list_tf

def final_ans(qrcode):
	if answer_lists(qrcode)=='No Barcode Detected':
		# print(answer_lists(qrcode), '999999999')
		return 'No Barcode Detected'
	else:
		answer_list = answer_lists(qrcode)[0]
		to_num = ans_num_choose(answer_list)
		
		answer_list_tf = answer_lists(qrcode)[1]
		# print(answer_list, answer_list_tf)
		to_num_tf = ans_num_tf(answer_list_tf)
		# print(to_num_tf)
		return to_num, to_num_tf

def bind_img(img1, img2, img3):
	# Resize the images to have the same height
	height_img = min(img1.shape[0], img1.shape[0])
	# print(type(img3), type(img2))

	final_img1 = cv2.resize(img1, (int(img1.shape[1] * height_img / img1.shape[0]), height_img))
	final_img2 = cv2.resize(img2, (int(img2.shape[1] * height_img / img2.shape[0]), height_img))
	final_img3 = cv2.resize(img3, (int(img3.shape[1] * height_img / img3.shape[0]), height_img))
	
	# Horizontally concatenate the images
	result = cv2.hconcat([final_img2, final_img1, final_img3])
	
	# Convert numpy to bytes
	ret, buffer = cv2.imencode('.jpg', result)
	result = buffer.tobytes()
	return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + result + b'\r\n')
