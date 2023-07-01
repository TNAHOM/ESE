from flask import render_template, redirect, url_for, flash, request, Blueprint
from evaluator import run_folder, run_file, run_textract, cloud
from flask_login import login_required
import os, cv2


process_file = Blueprint('process_file', __name__)

class AllInOneFolder:
  def __init__(self, image=None, qrcode=None):
    self.qrcode = qrcode
    self.answer_folder = run_folder.final_ans(self.qrcode)
    self.image = image
  
  def folder(self):
    gen = run_folder.gen_folder(self.answer_folder[0], self.image)
    return gen, self.answer_folder[0]
  
  def folder_2(self):
    gen = run_folder.gen_folder_2(self.answer_folder[0], self.image)
    return gen, self.answer_folder[0]


@process_file.route('/evaluate-exam', methods=['GET', 'POST'])
@login_required
def upload_file():
  if request.method=='POST':
    directory = request.form.get('file')
    if directory[-3:] == ('jpg' or 'png' or 'jpeg'):
      img = cv2.imread(directory)
      qrcode = run_file.qrcode_reader(img)
      print(qrcode, 'qrcode')
      if qrcode is not None:
        # exam id
        id_qrcode = qrcode[7:43]
        # front page or back page
        position = qrcode[48:-2]
        student_name = run_file.gen_name(img, 2)[4]
        # student_name = 'saron tamirat kebede'
        print(student_name, 'analyzed name')

        to_db = run_file.connectionToDB(unique_sub=id_qrcode)
        get_name = run_file.get_name(student_name, to_db[1])
        print(get_name, 'get_name')
        to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
          (id_qrcode, get_name[1]))
        does_exist = to_db[3].fetchone()
      
        if does_exist is None:
          if position == 'front':
            # print(run_file.gen_write(img, 0)[3])
            # ret, buffer = cv2.imencode('.jpg', img)
            # analyzed_text = cloud.text_detection(response)
            # print(analyzed_text, 'analyzed')
            
            final_answer = run_file.final_ans(id_qrcode)
            
            all_together_0 = run_file.gen_file_choose(final_answer[0], img, 1)
            all_together_1 = run_file.gen_file_choose(final_answer[0], img, 0)
            all_together_m = run_file.gen_file_m(final_answer[2], img, 3)
            all_together_tf = run_file.gen_file_tf(final_answer[1], img, 4)
            
            incorrect_ans = []
            incorrect_que = []
            disqualified_ans = []
            disqualified_que = []
            
            display_img = []
            score = 0
            total_que = final_answer[4]
            if final_answer[3][0] is not None:
              # number of choose < 50
              if len(final_answer[3][0]) <= 50:
                display_img.append(all_together_0[2])
                score+=all_together_0[1]
                incorrect_ans.extend(all_together_0[3][5])
                incorrect_que.extend(all_together_0[3][4])
                disqualified_que.extend(all_together_0[3][3])
                disqualified_ans.append(all_together_0[3][6])

              else:
                display_img.append(all_together_0[2])
                score+=all_together_0[1]
                incorrect_ans.extend(all_together_0[3][5])
                incorrect_que.extend(all_together_0[3][4])
                disqualified_que.extend(all_together_0[3][3])
                disqualified_ans.append(all_together_0[3][6])
                
                display_img.append(all_together_1[2])
                score+=all_together_1[1]
                incorrect_ans.extend(all_together_1[3][5])
                incorrect_que.extend([x+50 for x in all_together_1[3][4]])
                disqualified_que.extend([x+50 for x in all_together_1[3][3]])
                disqualified_ans.append(all_together_1[3][6])
  
            if final_answer[1] is not None:
              display_img.append(all_together_tf[2])
              score += all_together_tf[1]
              
            if final_answer[2] is not None:
              display_img.append(all_together_m[2])
              score += all_together_m[1]
            
            # run_file.upload_result(id_qrcode, score, get_name[1], 'true', datetime.date.today(),
            #   str(incorrect_ans), str(incorrect_que), str(disqualified_que))
            
            return render_template('upload file.html', name=get_name[0],display=position, img_list=display_img, score=score, total_que=total_que)

          elif position == 'back':
            response = run_file.gen_write(img, 1)
            analyzed_text = response[4]
            ans_list_2 = run_file.connectionToDB(id_qrcode)[7][8]
            print(ans_list_2, type(ans_list_2))

            ans_list = ['PSEUDOPODIA', 'IDENTIFICATION', 'EXPLANATION', 'CELL', 'FISH']
            score = 0
            for x in analyzed_text:
              result = cloud.similarity_test(x, ans_list)
              print(result[1])
              if result[1] >= 70:
                score += 1
            display = 'back'
            return render_template('upload file.html', name=get_name[0] ,display=display, img=response[2], ans=ans_list, score=score,)
        else:
          flash(f'{get_name[0]} already have taken this exam', category='success')
          return redirect(url_for('views.school'))
        
      else:
        flash('No barcode detected', category='danger')
        return redirect(url_for('views.school'))
    
    else:
      flash('Their is no image detected with the extension *.jpg, *.png, *.jpeg', category='danger')
      return redirect(url_for('process_file.upload_file'))
  elif request.method == 'GET':
      display = False
      return render_template('upload file.html', display=display)

############  USE FOLDER ############
@process_file.route('/evaluate_folder', methods=['POST', 'GET'])
@login_required
def upload_folder():
  scores = []
  names = []
  num_saved = 0
  num_existed = 0

  existed = {}
  new_result = {}
  if request.method=='POST':
    display = True

    directorate = request.form.get('file')
    for x in os.listdir(directorate):
      # print(x, x[:-4])
      img = cv2.imread(directorate + '\\' + x)
      qrcode = run_folder.qrcode_reader(img)
      
      if qrcode is not None:
        id_qrcode = qrcode[7:43]
        position = qrcode[48:-2]
        student_name = x[:-4]

        to_db = run_file.connectionToDB(unique_sub=id_qrcode)
        get_name = run_file.get_name(student_name, to_db[1])
        to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
          (id_qrcode, get_name[1]))
        does_exist = to_db[3].fetchone()
        # print(does_exist, 'does_exist')

        score = 0
        if does_exist is None:
          if position == 'front':
            final_answer = run_file.final_ans(id_qrcode)
            all_together_0 = run_file.gen_file_choose(final_answer[0], img, 1)
            all_together_1 = run_file.gen_file_choose(final_answer[0], img, 0)
            all_together_m = run_file.gen_file_m(final_answer[2], img, 2)
            all_together_tf = run_file.gen_file_tf(final_answer[1], img, 3)
  
            incorrect_ans = []
            incorrect_que = []
            disqualified_ans = []
            disqualified_que = []
  
            display_img = []
            total_que = final_answer[4]
            if final_answer[3][0] is not None:
              # number of choose < 50
              if len(final_answer[3][0]) <= 50:
                display_img.append(all_together_0[2])
                score += all_together_0[1]
                incorrect_ans.extend(all_together_0[3][5])
                incorrect_que.extend(all_together_0[3][4])
                disqualified_que.extend(all_together_0[3][3])
                disqualified_ans.append(all_together_0[3][6])
    
              else:
                display_img.append(all_together_0[2])
                score += all_together_0[1]
                incorrect_ans.extend(all_together_0[3][5])
                incorrect_que.extend(all_together_0[3][4])
                disqualified_que.extend(all_together_0[3][3])
                disqualified_ans.append(all_together_0[3][6])
      
                display_img.append(all_together_1[2])
                score += all_together_1[1]
                incorrect_ans.extend(all_together_1[3][5])
                incorrect_que.extend([x + 50 for x in all_together_1[3][4]])
                disqualified_que.extend([x + 50 for x in all_together_1[3][3]])
                disqualified_ans.append(all_together_1[3][6])
  
            if final_answer[1] is not None:
              display_img.append(all_together_tf[2])
              score += all_together_tf[1]
  
            if final_answer[2] is not None:
              display_img.append(all_together_m[2])
              score += all_together_m[1]
            print(score, student_name)
            scores.append(score)
            names.append(student_name)
            num_saved+=1
            new_result.update({student_name: score})
        else:
          num_existed+=1
          existed.update({student_name: score})
    print(num_saved, num_existed)
    flash(f'{num_saved} Has been saved', category='success')
    flash(f'{num_existed} Has already been registered', category='danger')
    return render_template('evaluation description.html', display=display, score=scores, new_result=new_result,
      existed=existed)
        # all_in_one = AllInOneFolder(img, qrcode)
        # # [:-4] for excluding .jpg
        # to_db = run_folder.connectionToDB(qrcode)
        # score = all_in_one.folder()[0][1] + all_in_one.folder_2()[0][1]
        # incorrect_ans = str(all_in_one.folder()[0][3] + all_in_one.folder_2()[0][3])
        # incorrect_que = str(all_in_one.folder()[0][2] + ([x+40 for x in all_in_one.folder_2()[0][2]]))
        # # print(incorrect_que, incorrect_ans)
        #
        # for user in to_db[1]:
        #   if user[10] == student_name and user[12] == 'Student':
        #     # print(student_name, user[10])
        #     new_uuid = uuid.uuid4()
        #     my_uuid = uuid.UUID(user[9])
        #     to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
        #       (qrcode, my_uuid))
        #     does_exist = to_db[3].fetchone()
        #     # print(does_exist)
        #     if does_exist is None:
        #       insert_record = (new_uuid, score, user[9], qrcode, 'true', datetime.date.today(), incorrect_ans, incorrect_que)
        #       # to_db[4].execute(to_db[2], insert_record)
        #       # to_db[5].commit()
        #       names.append(user[10])
        #       scores.append(score)
        #       num_saved += 1
        #       new_result.update({user[10]: score})
        #
        #     elif does_exist:
        #       num_existed+=1
        #
        #       existed.update({user[10]:score})
        #       print(f'data already existed of {user}')
        #     else:
        #       print('Dont know the error')
        #   else:
        #     print('User Doesn/"t exist')
        # # print(new_result)
        # flash(f'{num_saved} Has been saved', category='success')
        # flash(f'{num_existed} Has already been registered', category='danger')
        #
        # return render_template('evaluation description.html', display=display, score=scores, new_result=new_result,
        #    existed=existed)
    
  
  elif request.method == 'GET':
    display = False
    return render_template('upload folder.html', display=display, score='score', name='stu', names='(len(11))')
