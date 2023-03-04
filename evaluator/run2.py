import cv2

from evaluator import top, process_answer_1
import psycopg2, psycopg2.extras

#####################
# path = 'C:\Users\Nahom tamirat.DESKTOP-O0JRFDT\Desktop\PROJECT\Flask\prototype_1\website\static\img\bn (2).jpg'
width, height = 738, 984
width_tf, height_tf = 550, 770

questions = 41
choices = 6
choices_tf = 2

############################

num_str = {'A': 0,'B': 1,'C': 2,'D': 3,'E': 4}

#######################
cap = cv2.VideoCapture(1)

def shape1():
	while True:
		success, img = cap.read()

		if not success:
			print('NOT SUCCESS shape')
			return None
		else:
			try:
				sliced_img0 = top.TryClass(img, 0, 1200, 900).process_img()[1]
				ret, buffer0 = cv2.imencode('.jpg', sliced_img0)
				final_img0 = buffer0.tobytes()
				
				return (b'--frame\r\n'
				       b'Content-Type: image/jpeg\r\n\r\n' + final_img0 + b'\r\n')
				      
			except ValueError as v_error:
				v_error = 'No sheet detected'
				return v_error
			except IndexError as i_error:
				i_error = 'Put the answer sheet Appropriately'
				return i_error
			except Exception as es:
				print(es, 'gen exception')
				return 'ERROR'

def gen(answer):
	while True:
		success, img = cap.read()
		
		if not success:
			print('NOT SUCCESS')
			return None
		else:
			try:
				sliced_img = top.TryClass(img, 1, width, height).process_img()[0]
				final_img = process_answer_1.General(sliced_img, answer[:40], questions, choices).func_choose()
				ret, buffer = cv2.imencode('.jpg', final_img[2])
				result = final_img[0]
				final_img_buffer = buffer.tobytes()
				incorrect_que = final_img[5]
				incorrect_ans = final_img[6]
				# print(incorrect_que, '1.incorrect_que')
				# print(incorrect_ans, 'incorrect_ans')
				return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
				       result, incorrect_que, incorrect_ans
			
			except ValueError as v_error:
				v_error = 'No sheet detected'
				return v_error
			except IndexError as i_error:
				i_error = 'Put the answer sheet Appropriately'
				return i_error
			except Exception as es:
				print(es, 'gen exception')
				return 'ERROR'

def gen2(answer=None):
	while True:
		success, img = cap.read()

		if not success:
			# print('Not success')
			break
		else:
			try:
				sliced_img = top.TryClass(img, 0, width, height).process_img()[0]
				final_img = process_answer_1.General(sliced_img, answer[40:], questions, choices).func_choose()

				ret, buffer = cv2.imencode('.jpg', final_img[2])
				result = final_img[0]
				final_img_buffer = buffer.tobytes()
				incorrect_que = final_img[5]
				incorrect_ans = final_img[6]
				# print(incorrect_que, '2.incorrect_que')
				# print(incorrect_ans, 'incorrect_ans')
				return(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
				      result, incorrect_que, incorrect_ans

			except ValueError as v_error:
				v_error = 'No sheet detected'
				# print(v_error)
				return v_error
			except IndexError as i_error:
				i_error = '2, Put the answer sheet Appropriately'
				return i_error
#
def qrcode_reader():
	while True:
		success, img = cap.read()
		if not success:
			print('qrcode not success')
			return None
		else:
			identifier = process_answer_1.General(img).qrcode_reader()
			# print(identifier, '-------------------')
			return identifier
			
def ans_num(ans):
	answer_list = []
	for x in ans:
		for z, y in num_str.items():
			if x == z:
				answer_list.append(y)
	return answer_list

def connectionToDB(unique_sub):
	try:
		conn =  psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
		cur = conn.cursor()
		cur_user = conn.cursor()
		cur_exist = conn.cursor()
		cur_exam = conn.cursor()

		cur.execute('SELECT * FROM base_exam')
		cur_user.execute(f'SELECT * FROM base_user')
		cur_exam.execute(f"SELECT * FROM base_exam WHERE id='{unique_sub}'")
		exam_id = cur_exam.fetchone()

		result = cur.fetchall()
		result_user = cur_user.fetchall()
		insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, FINISHED, INCORRECT_ANS) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
		return result, result_user, insert_data_from, cur_exist, cur, conn,cur_exam, exam_id

	except Exception as er:
		return er
#
def to_list(variable):
	x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
	return x
#
def answer_lists(unique_name):
	if unique_name is None:
		return 'No Barcode Detected'
	else:
		# print(unique_name, '000000000000000000000')
		# print(connectionToDB(unique_name))
		connection = connectionToDB(unique_name)[7]
		# print(connection, 'connection')
		# print(connection)
		answer_list = list(to_list(connection[6]))
		# print(answer_list, 'answer_list')
		return answer_list
#
def final_ans(qrcode):
	if answer_lists(qrcode) == 'No Barcode Detected':
		# print(answer_lists(qrcode), '999999999')
		return 'No Barcode Detected'
	else:
		answer_list = answer_lists(qrcode)
		# print(len(answer_list))
		to_num = ans_num(answer_list)
		# print(to_num, '$$$$$$$$$$$$$$$$$$$$$$$')
		return to_num
