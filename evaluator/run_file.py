import base64
from thefuzz import fuzz
import cv2

from .clean_ups import multi_ans_func, ans_num_tf, ans_num_choose, to_list, to_list_tf, num_str, num_str_tf
from evaluator import top, process_answer_1, connection as conne, cloud
import psycopg2, psycopg2.extras

#####################
width, height = 738, 984
width_tf, height_tf = 660, 990

questions = 51
choices = 6

question_tf = 11
choices_tf = 2

question_m = 11
choices_m = 11

question_c = 7
choice_c = 6

############################

def gen_name(image, size):
	try:
		image_rot = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
		sliced_img = top.TryClass(image_rot, size,  1150, 800).process_particular_img()[0]
		resliced_img = cv2.resize(sliced_img, (1150, 200))

		ret, buffer = cv2.imencode('.jpg', resliced_img)
		result = buffer.tobytes()

		processed_image_str = base64.b64encode(buffer).decode('utf-8')
		analyzed_text ='cloud.text_detection4(buffer)'

		return sliced_img, result, processed_image_str, buffer, analyzed_text

	# make an error handling for connectivity issue
	except  Exception as es:
		print('ERROR', es)

def gen_file_choose(answer=None, image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, 918, 1224).process_particular_img()[0]
		final_img = process_answer_1.General(sliced_img, answer, questions, choices).func_choose()
		
		ret, buffer = cv2.imencode('.jpg', final_img[2])
		processed_image_str = base64.b64encode(buffer).decode('utf-8')
	
		score = final_img[0]
		disqualified_que = final_img[3]
		incorrect_ans= final_img[5]
		incorrect_que= final_img[4]
		return final_img[2], score, processed_image_str, final_img
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'

def gen_file_m(answer=None, image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, 660, 660).process_particular_img()[0]
		final_img = process_answer_1.General(sliced_img, answer, question_m, choices_m).func_choose()
		score = final_img[0]

		ret, buffer = cv2.imencode('.jpg', final_img[2])
		processed_image_str = base64.b64encode(buffer).decode('utf-8')
		
		return final_img[2], score, processed_image_str
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'
	
def gen_file_tf(answer=None, image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, width_tf, height_tf).process_particular_img()[0]
		final_img = process_answer_1.General(sliced_img, answer, 11, 2).func_tf()
		score = final_img[0]
		
		ret, buffer = cv2.imencode('.jpg', final_img[2])
		processed_image_str = base64.b64encode(buffer).decode('utf-8')

		return sliced_img, score, processed_image_str
	except Exception as es:
		print(es, 'gen exception')
		return 'ERROR'
	
def gen_write(image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size,  600, 1000).process_particular_img()[0]
		# cv2.imshow('ss', sliced_img)
		# cv2.waitKey(0)
		ret, buffer = cv2.imencode('.jpg', sliced_img)
		
		result = buffer.tobytes()
		processed_image_str = base64.b64encode(buffer).decode('utf-8')
		analyzed_text = cloud.text_detection4(buffer)
		
		given_ans = analyzed_text.split(' ')
		# given_ans = ['PSEUDOPODIA', 'IDENTIFICATIO', 'CELL', 'BOTANIST', 'NOONNE']
		
		return sliced_img, result, processed_image_str, buffer, given_ans
	except Exception as es:
		print(es, 'gen_write')

def gen_code(image=None, size=None):
	try:
		sliced_img = top.TryClass(image, size, 600, 700).process_particular_img()[0]
		# cv2.imshow('ss', sliced_img)
		# cv2.waitKey(0)
		answer = [0, 0, 0, 0, 0, 0, 0]
		final_img = process_answer_1.General(sliced_img, answer, question_c, choice_c).func_code()

		exam_code = ''
	
		for x in list(final_img):
			exam_code+=str(x+1)
	
		return int(exam_code)

	except Exception as es:
		print(es, 'gen_code')
		return es

def get_name(given_name, name_list):
	closest_word = ''
	student_id = ''
	highest_score = 0

	for name in name_list:
		# print(name[10], name[9],'name[10]')
		score = fuzz.ratio(given_name, name[10])
		if score > highest_score:
			highest_score = score
			closest_word = name[10]
			student_id = name[9]
	# print(highest_score)
	return closest_word, student_id

def answer_lists(exam_code_f=None, exam_code_b=None):
	try:
		if exam_code_f is not None:
			answer_list_choose = []
			answer_list_tf = []
			answer_list_match = []
			
			# connection = connectionToDB(exam_code_f=exam_code_f)[7]

			connection = conne.ConnectionToDB(exam_code_f=exam_code_f).check_exam_f()
			print(connection, 'connection')
			if connection[6] is not None:
				answer_list = list(to_list(connection[6]))
				# print(answer_list)
				answer_list_choose.extend(answer_list)
				# print(len(answer_list_choose), 'answer list choose')
			if connection[9] is not None:
				answer_list = (to_list_tf(connection[9])).split()
				answer_list_tf.extend(answer_list)
			if connection[10] is not None:
				answer_list = list(to_list(connection[10]))
				answer_list_match.extend(answer_list)
			# print(answer_list_match)
			return answer_list_choose, answer_list_tf, answer_list_match
		
		elif exam_code_b is not None:
			connection = conne.ConnectionToDB(exam_code_b=exam_code_b).check_exam_b()
			
			answer_list_fill = []
			# conn_ans_try = "['PSUEDOPODIA', 'IDENTIFICATION, ANATOMY, BIOLOGY', 'CELL', 'BOTANIST, ALGAE']"
			if connection[8] is not None:
			# if conn_ans_try is not None:
				# answer_list = (to_list_tf(connection[8]).split())
				answer_list = multi_ans_func(connection[8])
				answer_list_fill.extend(answer_list)
			print(answer_list_fill, 'list ans')
			return answer_list_fill
	except Exception as ec:
		print(ec, 'answer lists')
		return ec

def final_ans(exam_code_f=None, exam_code_b=None):
	try:
		if exam_code_f is not None:
			answer = answer_lists(exam_code_f=exam_code_f)
			total_que = 0
			if answer[0] is not None:
	
				total_que += len(answer[0])
				to_num_ch = ans_num_choose(answer[0])
				if len(answer[0])!=questions-1:
					difference = questions-1 - len(answer[0])
					# print(difference, questions , answer[0])
					new_list = [-1 for _ in range(difference)]
					to_num_ch.extend(new_list)
				# print(to_num_ch, 'num')
			
			if answer[1] is not None:
				total_que += len(answer[1])
				to_num_tf = ans_num_tf(answer[1])
				
				if len(answer[1]) != question_tf-1:
					difference = question_tf-1 - len(answer[1])
					new_list = [-1 for _ in range(difference)]
					to_num_tf.extend(new_list)
	
				# print(to_num_tf)
			if answer[2] is not None:
				total_que += len(answer[2])
				to_num_match = ans_num_choose(answer[2])
				if len(answer[2]) != question_m-1:
					difference = question_m - 1 - len(answer[2])
					# print(difference, 'differences')
					new_list = [-1 for _ in range(difference)]
					to_num_match.extend(new_list)
					
			return to_num_ch, to_num_tf, to_num_match ,answer, total_que
		
	except Exception as ec:
		print(ec, 'final answer')
		return ec