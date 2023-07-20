import cv2

from evaluator import top, process_answer_1
import psycopg2, psycopg2.extras

#####################
width, height = 738, 984
width_tf, height_tf = 550, 770

questions = 41
choices = 6
choices_tf = 2

############################

num_str = {'A': 0,'B': 1,'C': 2,'D': 3,'E': 4}
num_str_tf = {'true': 1, 'false':0}

#######################
cap = cv2.VideoCapture(3)

def shape1():
	while True:
		success, img = cap.read()
		if not success:
			print('NOT SUCCESS shape')
			return None
		else:
			try:
				img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
				sliced_img0 = top.TryClass(img_rot, 0, width, height).process_img()[1]
				# cv2.imshow('live', sliced_img0)
				# cv2.waitKey(0)
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
#
# def gen(answer):
# 	while True:
# 		success, img = cap.read()
#
# 		if not success:
# 			print('NOT SUCCESS')
# 			return None
# 		else:
# 			try:
# 				sliced_img = top.TryClass(img, 1, width, height).process_img()[0]
# 				final_img = process_answer_1.General(sliced_img, answer[:40], questions, choices).func_choose()
# 				ret, buffer = cv2.imencode('.jpg', final_img[2])
# 				result = final_img[0]
# 				final_img_buffer = buffer.tobytes()
# 				incorrect_que = final_img[5]
# 				disqualified_que = final_img[4]
# 				incorrect_ans = final_img[6]
# 				return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
# 				       result, incorrect_que, incorrect_ans, disqualified_que
#
# 			except ValueError as v_error:
# 				v_error = 'No sheet detected'
# 				return v_error
# 			except IndexError as i_error:
# 				i_error = 'Put the answer sheet Appropriately'
# 				return i_error
# 			except Exception as es:
# 				print(es, 'gen exception')
# 				return 'ERROR'
#
# def gen2(answer=None):
# 	# print('HIII')
# 	while True:
# 		success, img = cap.read()
#
# 		if not success:
# 			# print('Not success')
# 			break
# 		else:
# 			try:
# 				sliced_img = top.TryClass(img, 0, width, height).process_img()[0]
# 				final_img = process_answer_1.General(sliced_img, answer[40:], questions, choices).func_choose()
#
# 				ret, buffer = cv2.imencode('.jpg', final_img[2])
# 				result = final_img[0]
# 				final_img_buffer = buffer.tobytes()
# 				incorrect_que = final_img[5]
# 				incorrect_ans = final_img[6]
# 				# print(incorrect_que, '2.incorrect_que')
# 				# print(result, 'result')
# 				return(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
# 				      result, incorrect_que, incorrect_ans
#
# 			except ValueError as v_error:
# 				v_error = 'No sheet detected'
# 				# print(v_error)
# 				return v_error
# 			except IndexError as i_error:
# 				i_error = '2, Put the answer sheet Appropriately'
# 				return i_error
#
# def gen_tf(answer):
# 	while True:
# 		success, img = cap.read()
# 		if not success:
# 			print('Not success tf')
# 			return None
# 		else:
# 			try:
# 				sliced_img = top.TryClass(img, 2, width_tf, height_tf).process_img()[0]
# 				final_img = process_answer_1.General(sliced_img, answer, 11, 2).func_tf()
#
# 				ret, buffer = cv2.imencode('.jpg', final_img[2])
# 				# result = final_img[0]
# 				final_img_buffer = buffer.tobytes()
# 				# incorrect_que = final_img[5]
# 				# incorrect_ans = final_img[6]
# 				# print(incorrect_que, '2.incorrect_que')
# 				# print(result, 'result')
# 				return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n')
#
# 			except ValueError as v_error:
# 				v_error = 'No sheet detected'
# 				# print(v_error)
# 				return v_error
# 			except IndexError as i_error:
# 				i_error = '2, Put the answer sheet Appropriately'
# 				return i_error
#
# def qrcode_reader():
# 	while True:
# 		success, img = cap.read()
# 		if not success:
# 			print('qrcode not success')
# 			return None
# 		else:
# 			identifier = process_answer_1.General(img).qrcode_reader()
# 			# print(identifier, '-------------------')
# 			return identifier
#
# def ans_num(ans):
# 	answer_list = []
# 	for x in ans:
# 		for z, y in num_str.items():
# 			if x == z:
# 				answer_list.append(y)
# 	return answer_list
#
# def ans_num_tf(ans):
# 	answer_list = []
# 	for x in ans:
# 		for z, y in num_str_tf.items():
# 			if x == z:
# 				answer_list.append(y)
# 	return answer_list
#
# def connectionToDB(unique_sub):
# 	try:
# 		conn =  psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
# 		cur = conn.cursor()
# 		cur_user = conn.cursor()
# 		cur_exist = conn.cursor()
# 		cur_exam = conn.cursor()
#
# 		cur.execute('SELECT * FROM base_exam')
# 		cur_user.execute(f'SELECT * FROM base_user')
# 		cur_exam.execute(f"SELECT * FROM base_exam WHERE id='{unique_sub}'")
# 		exam_id = cur_exam.fetchone()
#
# 		result = cur.fetchall()
# 		result_user = cur_user.fetchall()
# 		insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, FINISHED, INCORRECT_ANS) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
# 		return result, result_user, insert_data_from, cur_exist, cur, conn,cur_exam, exam_id
#
# 	except Exception as er:
# 		return er
#
# def to_list(variable):
# 	x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
# 	return x
# def tf_to_list(tf_variable):
# 	y = tf_variable.replace("'", '').replace(' ', '').replace('[', '').replace(']', '').split(',')
# 	return y
#
# def answer_lists(unique_name):
# 	if unique_name is None:
# 		return 'No Barcode Detected'
# 	else:
# 		connection = connectionToDB(unique_name)[7]
# 		# print('----------')
# 		# print(connection, 'connection')
# 		answer_list = list(to_list(connection[6]))
# 		answer_list_tf = list(tf_to_list(connection[9]))
# 		return answer_list, answer_list_tf
#
# def final_ans(qrcode):
# 	if answer_lists(qrcode) == 'No Barcode Detected':
# 		# print(answer_lists(qrcode), '999999999')
# 		return 'No Barcode Detected'
# 	else:
# 		answer_list = answer_lists(qrcode)[0]
# 		to_num = ans_num(answer_list)
#
# 		answer_list_tf = answer_lists(qrcode)[1]
# 		to_num_tf = ans_num_tf(answer_list_tf)
# 		return to_num, to_num_tf
