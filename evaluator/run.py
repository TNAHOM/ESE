import cv2
from evaluator import top, process_answer_1


#####################
path = "MAIN/NT (1).jpg"
width, height = 738, 984
width_tf, height_tf = 550, 770

questions = 41
questions_fill = 10
questions_tf = 11
choices = 6
choices_tf = 2

############################
answer1 = [
	0, 1, 2, 3, 4, 0, 0, 1, 1, 2,
	2, 3, 4, 4, 3, 3, 2, 2, 1, 1,
	0, 0, 1, 2, 2, 2, 3, 3, 4, 4,
	3, 3, 2, 2, 1, 1, 0, 0, 1, 1
]
answer2 = [
	0, 1, 2, 3, 4, 0, 1, 2, 3, 4,
	0, 1, 2, 3, 4, 0, 1, 2, 3, 4,
	0, 1, 2, 3, 4, 0, 1, 2, 3, 4,
	0, 1, 2, 3, 4, 0, 1, 2, 3, 4
]

#######################
cap = cv2.VideoCapture(2)
cap.set(10, 120)


def gen(answer=None):
	while True:
		success, img = cap.read()
		
		if not success:
			print('Not success')
		else:
			try:
				sliced_img = top.TryClass(img, 0, width, height).process_img()
				final_img = process_answer_1.General(sliced_img, answer, questions, choices).func_choose()
		
				sliced_img2 = top.TryClass(img, 1, width, height).process_img()
				final_img2 = process_answer_1.General(sliced_img2, answer, questions, choices).func_choose()
		
				ret, buffer = cv2.imencode('.jpg', final_img[2])
				result = final_img[0]
				final_img = buffer.tobytes()
			
				ret, buffer = cv2.imencode('.jpg', final_img2[2])
				result2 = final_img2[0]
				final_img2 = buffer.tobytes()
				return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img + b'\r\n'), (
						b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img2 + b'\r\n'), int(result+result2)
			
			except ValueError as v_error:
				v_error = 'No sheet detected'
				return v_error
			except IndexError as i_error:
				i_error = 'Put the answer sheet Appropriately'
				return i_error
			# except TypeError as t_error:
			# 	print('------------------------------------------')
			# 	print(t_error)
			# 	t_error = 'Make the both choose box visible'
			# 	return t_error