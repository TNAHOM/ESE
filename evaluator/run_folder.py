import cv2
import os

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
num_str_tf = {'true': 1, 'false': 0}

#######################
def gen_folder(answer=None, image=None):
	try:
		sliced_img = top.TryClass(image, 1, width, height).process_img_folder()[0]
		final_img = process_answer_1.General(sliced_img, answer[:40], questions, choices).func_choose()

		ret, buffer = cv2.imencode('.jpg', final_img[2])
		result = final_img[0]
		# print(result, 'gen folder')
		final_img_buffer = buffer.tobytes()
		
		wrong_ans = final_img[6]
		wrong_que = final_img[5]

		return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
		       result, wrong_que, wrong_ans
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'
	
def gen_folder_2(answer=None, image=None):
	try:
		sliced_img = top.TryClass(image, 0, width, height).process_img_folder()[0]
		# print(len(answer[40:]))
		final_img = process_answer_1.General(sliced_img, answer[40:], questions, choices).func_choose()

		ret, buffer = cv2.imencode('.jpg', final_img[2])
		result = final_img[0]
		# print(result, 'gen folder2')
		final_img_buffer = buffer.tobytes()
		
		wrong_ans = final_img[6]
		wrong_que = final_img[5]
	
		return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
		       result, wrong_que, wrong_ans
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'

def qrcode_reader(image=None):
	identifier = process_answer_1.General(image).qrcode_reader()
	# print(identifier, '-------------------')
	return identifier

def ans_num(ans):
	answer_list = []
	for x in ans:
		for z, y in num_str.items():
			if x==z:
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
		insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, FINISHED, INCORRECT_ANS, INCORRECT_ANS_NUM) VALUES (%s,%s,%s,%s,%s,%s,%s, %s)"""
		return result, result_user, insert_data_from, cur_exist, cur, conn, cur_exam, exam_id
	except Exception as er:
		print(er)
		return er
	# finally:
	# 	close database


def to_list(variable):
	x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
	return x

def answer_lists(unique_name):
	if unique_name is None:
		return 'No Barcode Detected'
	else:
		connection = connectionToDB(unique_name)[7]
		# print('----------')
		# print(connection, 'connection')
		answer_list = list(to_list(connection[6]))
		return answer_list, 'answer_list_tf'


def final_ans(qrcode):
	if answer_lists(qrcode)=='No Barcode Detected':
		# print(answer_lists(qrcode), '999999999')
		return 'No Barcode Detected'
	else:
		answer_list = answer_lists(qrcode)[0]
		to_num = ans_num(answer_list)
		
		answer_list_tf = answer_lists(qrcode)[1]
		'to_num_tf = ans_num_tf(answer_list_tf)'
		return to_num, 'to_num_tf'
