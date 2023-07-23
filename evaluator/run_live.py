import base64
import uuid
from thefuzz import fuzz
import cv2
import time
from . import cloud
from evaluator import top, process_answer_1
import psycopg2, psycopg2.extras

import time

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

num_str = {'A': 0,'B': 1,'C': 2,'D': 3,'E': 4}
num_str_tf = {'true': 1, 'false':0}

#######################

def shape1(number):
  time.sleep(1)
  cap = cv2.VideoCapture(number)
  print(cap.isOpened())

  while True:
    success, img = cap.read()
    cv2.imshow('sdf', img)
    cv2.waitKey(0)
    if not success:
      print('NOT SUCCESS shape')
      return None
    else:
      print('!!!!!!!')
      try:
        # img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        sliced_img0 = top.TryClass(img, 0, width, height).process_img()[1]
        cv2.imshow('live', sliced_img0)
        cv2.waitKey(0)
        ret, buffer0 = cv2.imencode('.jpg', sliced_img0)
        final_img0 = buffer0.tobytes()
        
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img0 + b'\r\n')

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
def gen(answer, sz_num, number):
  cap = cv2.VideoCapture(int(number))
  while True:
    success, img = cap.read()
    cv2.imshow('sdf', img)
    cv2.waitKey(0)
    time.sleep(0.5)
    if not success:
      print('NOT SUCCESS')
      return None
    else:
      # try:
      #   image_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
      #   cv2.imshow('sdf', image_rot)
      #   cv2.waitKey(0)
        sliced_img = top.TryClass(img, sz_num, width, height).process_img()[0]
        cv2.imshow('sdf', sliced_img)
        cv2.waitKey(0)
        final_img = process_answer_1.General(sliced_img, answer, questions, choices).func_choose()
        ret, buffer = cv2.imencode('.jpg', final_img[2])
        result = final_img[0]
        final_img_buffer = buffer.tobytes()

        processed_image_str = base64.b64encode(buffer).decode('utf-8')
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + final_img_buffer + b'\r\n'), \
               result, processed_image_str

      # except Exception as es:
      #   print(es, 'gen exception')
      #   return 'ERROR'


def gen_code(image=None, size=None):
  try:
    sliced_img = top.TryClass(image, size, 600, 700).process_img()[0]
    cv2.imshow(f'{size} code', sliced_img)
    cv2.waitKey(0)
    answer = [0, 0, 0, 0, 0, 0, 0]
    final_img = process_answer_1.General(sliced_img, answer, question_c, choice_c).func_code()
    # cv2.imshow('ss', sliced_img)
    # cv2.waitKey(0)
    exam_code = ''
    
    for x in list(final_img):
      exam_code += str(x + 1)
    
    return int(exam_code)
  except Exception as es:
    # print(es)
    return es


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


# finally:
# 	close database

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
      # print(answer_list_match)
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
        if len(answer[0])!=questions - 1:
          difference = questions - 1 - len(answer[0])
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
