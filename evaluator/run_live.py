import base64
import uuid

import cv2
from thefuzz import fuzz

from evaluator import top, process_answer_1
import psycopg2, psycopg2.extras

#####################
width, height = 306*3, 306*4
width_tf, height_tf = 550, 770

question = 51
choice = 6

question_tf = 11
choice_tf = 2

question_m = 11
choice_m = 11

question_c = 7
choice_c = 6

############################

num_str = {'A': 0,'B': 1,'C': 2,'D': 3,'E': 4,'F':5, 'G':6,'H':7,'I':8,'J':9}
num_str_tf = {'T': 1, 'F':0}

#######################

def shape1(number):
  cap = cv2.VideoCapture(number)
  print(cap.isOpened())
  
  if not cap.isOpened():
    print(f"Error: Unable to open camera source {number}.")
    return
  
  try:
    while True:
      success, img = cap.read()
      # cv2.imshow('sdf', img)
      # cv2.waitKey(0)
      if not success:
        print(f"Error: Unable to read frame from camera source {number}.")
        break
      
      try:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img0 = top.TryClass(img_rot, 0, width, height).process_img()[1]
        # cv2.imshow('live', sliced_img0)
        # cv2.waitKey(0)
        ret, buffer0 = cv2.imencode('.jpg', sliced_img0)
        final_img0 = buffer0.tobytes()
        
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img0 + b'\r\n'), img_rot
      
      except ValueError as v_error:
        print(v_error, 'v_error-SHAPE')
        v_error = 'No sheet detected'
        return v_error
      except IndexError as i_error:
        i_error = 'Put the answer sheet Appropriately'
        return i_error
      except Exception as es:
        print(es, 'gen exception')
        return 'ERROR'
  finally:
    print('Finally')
    cap.release()
    cv2.destroyAllWindows()

def choose(answer, sz_num, camera):
  cap = cv2.VideoCapture(int(camera))
  
  try:
    while True:
      success, img = cap.read()
      
      if not success:
        print(f"Error: Unable to read frame from camera source {camera}.")
        break
        
      try:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img = top.TryClass(img_rot, sz_num, width, height).process_img()[0]
        # cv2.imshow('final_img', sliced_img)
        # cv2.waitKey(0)
        final_img = process_answer_1.General(sliced_img, answer, question, choice).func_choose()
        # cv2.imshow('final_img', final_img[2])
        # cv2.waitKey(0)
        ret, buffer = cv2.imencode('.jpg', final_img[2])
        result = final_img[0]
        final_img_buffer = buffer.tobytes()
        
        processed_image_str = base64.b64encode(buffer).decode('utf-8')
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
               result, processed_image_str, img
      
      except ValueError as v_error:
        print(v_error, 'v_error')
        v_error = 'No sheet detected'
        return v_error
      except IndexError as i_error:
        print(i_error, 'IndexError')
        i_error = 'Put the answer sheet Appropriately'
        return i_error
      except Exception as es:
        print(es, 'gen exception')
        return 'ERROR'
  finally:
    cap.release()
    cv2.destroyAllWindows()


def tf(answer, sz_num, camera):
  cap = cv2.VideoCapture(int(camera))
  
  try:
    while True:
      success, img = cap.read()
      
      if not success:
        print(f"Error: Unable to read frame from camera source {camera}.")
        break
      
      try:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img = top.TryClass(img_rot, sz_num, width_tf, height_tf).process_img()[0]
        sliced_img_resize = cv2.resize(sliced_img, (374, 550))
        # cv2.imshow('final_img', sliced_img_resize)
        # cv2.waitKey(0)
        final_img = process_answer_1.General(sliced_img_resize, answer, question_tf, choice_tf).func_tf()
        # print(final_img, 'final_img')
        
        ret, buffer = cv2.imencode('.jpg', final_img[2])
        result = final_img[0]
        final_img_buffer = buffer.tobytes()
        
        processed_image_str = base64.b64encode(buffer).decode('utf-8')
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
               result, processed_image_str, img
      
      except ValueError as v_error:
        print(v_error, 'v_error')
        v_error = 'No sheet detected'
        return v_error
      except IndexError as i_error:
        print(i_error, 'IndexError')
        i_error = 'Put the answer sheet Appropriately'
        return i_error
      except Exception as es:
        print(es, 'gen exception')
        return 'ERROR'
  finally:
    cap.release()
    cv2.destroyAllWindows()


def matching(answer, sz_num, camera):
  cap = cv2.VideoCapture(int(camera))
  try:
    while True:
      success, img = cap.read()
      
      if not success:
        print(f"Error: Unable to read frame from camera source {camera}.")
        break
      
      try:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img = top.TryClass(img_rot, sz_num, width_tf, height_tf).process_img()[0]
        sliced_img_resize = cv2.resize(sliced_img, (550, 220))
        final_img = process_answer_1.General(sliced_img_resize, answer, question_m, choice_m).func_tf()
        
        # cv2.imshow('final_img', final_img[2])
        # cv2.waitKey(0)
        ret, buffer = cv2.imencode('.jpg', final_img[2])
        result = final_img[0]
        final_img_buffer = buffer.tobytes()
        
        processed_image_str = base64.b64encode(buffer).decode('utf-8')
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
               result, processed_image_str, img
      
      except ValueError as v_error:
        print(v_error, 'v_error-M')
        v_error = 'No sheet detected'
        return v_error
      except IndexError as i_error:
        print(i_error, 'IndexError-M')
        i_error = 'Put the answer sheet Appropriately'
        return i_error
      except Exception as es:
        print(es, 'gen exception-M')
        return 'ERROR'
  finally:
    cap.release()
    cv2.destroyAllWindows()


def exam_code(sz_num, camera):
  cap = cv2.VideoCapture(int(camera))
  try:
    while True:
      success, img = cap.read()
      
      if not success:
        print(f"Error: Unable to read frame from camera source {camera}.")
        break
      
      try:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img = top.TryClass(img_rot, sz_num, 600, 700).process_img()[0]
        # sliced_img_resize = cv2.resize(sliced_img, (53*6, 23*7))
        # cv2.imshow('final_img', sliced_img)
        # cv2.waitKey(0)
        answer = [0, 0, 0, 0, 0, 0, 0]
        final_img = process_answer_1.General(sliced_img, answer, question_c, choice_c).func_code()
        # print(final_img, 'final_img')
        
        exam_code = ''
        for x in list(final_img):
          exam_code += str(x + 1)

        return int(exam_code)
      
      except ValueError as v_error:
        print(v_error, 'v_error-CODE')
        v_error = 'No sheet detected'
        return v_error
      except IndexError as i_error:
        print(i_error, 'IndexError-CODE')
        i_error = 'Put the answer sheet Appropriately'
        return i_error
      except Exception as es:
        print(es, 'gen exception-CODE')
        return 'ERROR'
  finally:
    cap.release()
    cv2.destroyAllWindows()


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
      if x==z:
        answer_list.append(y)
  return answer_list

def connectionToDB(school=None, exam_code_f=None, exam_code_b=None):
  try:
    conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
    cur = conn.cursor()
    cur_user = conn.cursor()
    cur_exist = conn.cursor()
    cur_exam = conn.cursor()
    
    cur.execute('SELECT * FROM base_exam')
    cur_user.execute(f"SELECT * FROM base_user WHERE role='Student'")
    
    if exam_code_f is not None:
      cur_exam.execute(f"SELECT * FROM base_exam WHERE exam_code_f='{exam_code_f}'")
      insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, SCORE_EXAM_CODE_F, FINISHED, INCORRECT_ANS, INCORRECT_ANS_NUM, DISQUALIFIED_ANS, DISQUALIFIED_ANS_NUM) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    
    elif exam_code_b is not None:
      cur_exam.execute(f"SELECT * FROM base_exam WHERE exam_code_b='{exam_code_b}'")
      insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, SCORE_EXAM_CODE_B, FINISHED, INCORRECT_ANS, INCORRECT_ANS_NUM, DISQUALIFIED_ANS, DISQUALIFIED_ANS_NUM) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    
    exam_id = cur_exam.fetchone()
    # print('exam_id')
    # print(exam_id, 'id')
    result = cur.fetchall()
    result_user = cur_user.fetchall()
    return result, result_user, insert_data_from, cur_exist, cur, conn, cur_exam, exam_id
  except Exception as er:
    print(f'connectionToDB ec')
    return er


def upload_result(score=None, student_id=None, id_qrcode=None, display=None, date=None, wrong_ans=None, wrong_que=None,
                  disqualified_que=None, exam_code_f=None, exam_code_b=None):
  new_uuid = uuid.uuid4()
  if exam_code_f is not None:
    to_db = connectionToDB(exam_code_f=exam_code_f)
    insert_record = (
      new_uuid, score, student_id, id_qrcode, display, exam_code_f, date, wrong_ans, wrong_que, disqualified_que,
      disqualified_que)
  
  elif exam_code_b is not None:
    to_db = connectionToDB(exam_code_b=exam_code_b)
    insert_record = (
      new_uuid, score, student_id, id_qrcode, display, exam_code_b, date, wrong_ans, wrong_que, disqualified_que,
      disqualified_que)
  
  # print(len(to_db), 'len')
  to_db[4].execute(to_db[2], insert_record)
  to_db[5].commit()


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


def to_list(variable):
  x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
  return x


def to_list_tf(variable):
  x = variable.replace(',', '').replace("'", '').replace('[', '').replace(']', '')
  return x


def answer_lists(exam_code_f=None, exam_code_b=None):
  try:
    if exam_code_f is not None:
      answer_list_choose = []
      answer_list_tf = []
      answer_list_match = []
      
      connection = connectionToDB(exam_code_f=exam_code_f)[7]
      # print(connection, 'connection')
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
      return answer_list_choose, answer_list_tf, answer_list_match
    
    elif exam_code_b is not None:
      connection = connectionToDB(exam_code_b=exam_code_b)[7]
      answer_list_fill = []
      if connection[8] is not None:
        answer_list = (to_list_tf(connection[8]).split())
        answer_list_fill.extend(answer_list)
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
        if len(answer[0])!=question - 1:
          difference = question - 1 - len(answer[0])
          # print(difference, questions , answer[0])
          new_list = [-1 for _ in range(difference)]
          to_num_ch.extend(new_list)
      # print(to_num_ch, 'num')
      
      if answer[1] is not None:
        total_que += len(answer[1])
        to_num_tf = ans_num_tf(answer[1])
        
        if len(answer[1])!=question_tf - 1:
          difference = question_tf - 1 - len(answer[1])
          new_list = [-1 for _ in range(difference)]
          to_num_tf.extend(new_list)
      
      # print(to_num_tf)
      if answer[2] is not None:
        total_que += len(answer[2])
        to_num_match = ans_num_choose(answer[2])
        if len(answer[2])!=question_m - 1:
          difference = question_m - 1 - len(answer[2])
          # print(difference, 'differences')
          new_list = [-1 for _ in range(difference)]
          to_num_match.extend(new_list)
      
      return to_num_ch, to_num_tf, to_num_match, answer, total_que
  
  except Exception as ec:
    print(ec, 'final answer')
    return ec