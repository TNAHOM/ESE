from flask import render_template, redirect, url_for, flash, request, Blueprint
from evaluator import run_folder, run_file, cloud
from flask_login import login_required, current_user
import os, cv2
import datetime


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
  try:
    if request.method=='POST':
      directory = request.form.get('file')
      file_name = request.files['file'].filename
      
      full_path = directory+'\\'+file_name
      if file_name[-4:] == 'jpeg':
        img = cv2.imread(full_path)
        exam_code = run_file.gen_code(img, 4)

        # 2 == BACK
        if type(exam_code) == IndexError:
          exam_code = run_file.gen_code(img, 2)
          if int(str(exam_code)[-1])==2:
            to_db = run_file.connectionToDB(exam_code_b=exam_code)
            if to_db[7] is not None:
              # print(to_db[7])
              student_name = run_file.gen_name(img, 1)

              # student_name[4] == converts img to text
              get_name = run_file.get_name(student_name[4], to_db[1])
              print(get_name, 'get_name')
              to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
                (to_db[7][0], get_name[1]))
              does_exist = to_db[3].fetchone()
  
              # use answer_list instead of final_answer b/c there is no preprocessing that will happen unlike t/f and choose
              final_answer = run_file.answer_lists(exam_code_b=exam_code)
              response = run_file.gen_write(img, 0)
              analyzed_text = response[4]
              
              score = 0
              for x in analyzed_text:
                result = cloud.similarity_test(x, final_answer)
                # print(result[1])
                if result[1] >= 70:
                  score += 1
              display = 'back'

              if does_exist is None:
                run_file.upload_result(score, get_name[1], to_db[7][0], 'true', datetime.date.today(), exam_code_b=exam_code)
                flash(f'{get_name[0]} exam has been registered successfully', category='success')
              else:
                to_db[3].execute(
                  "SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_B=%s",
                  (to_db[7][0], get_name[1], exam_code,))
                does_exist_f = to_db[3].fetchone()
  
                if does_exist_f is None:
                  to_db[3].execute(
                    "UPDATE base_score SET SCORE_EXAM_CODE_B=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
                    (exam_code, score, to_db[7][0], get_name[1],))
                  to_db[5].commit()
    
                  flash(f'{get_name[0]} exam has been updated', category='danger')
                else:
                  flash(f'{get_name[0]} exam has already been saved', category='danger')

            return render_template('show result.html', name=get_name[0] ,display=display, img=response[2], ans=final_answer, score=score,)
  
        # 1 == FRONT
        elif int(str(exam_code)[-1]) == 1:
          to_db = run_file.connectionToDB(exam_code_f=exam_code)
          if to_db[7] is not None:
            # print(to_db[7])
            student_name = run_file.gen_name(img, 2)

            # student_name[4] == converts img to text
            get_name = run_file.get_name(student_name[4], to_db[1])
            print(get_name, 'get_name')
            to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
              (to_db[7][0], get_name[1]))
            does_exist = to_db[3].fetchone()

            final_answer = run_file.final_ans(exam_code)
    
            all_together_0 = run_file.gen_file_choose(final_answer[0], img, 1)
            all_together_1 = run_file.gen_file_choose(final_answer[0], img, 0)
            all_together_m = run_file.gen_file_m(final_answer[2], img, 3)
            all_together_tf = run_file.gen_file_tf(final_answer[1], img, 5)
    
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
      
            if does_exist is None:
              run_file.upload_result(score, get_name[1], to_db[7][0], 'true', datetime.date.today(),
                str(incorrect_ans), str(incorrect_que), str(disqualified_que), exam_code_f=exam_code)
              flash(f'{get_name[0]} exam has been registered successfully', category='success')
            
            else:
              to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_F=%s",
                (to_db[7][0], get_name[1], exam_code,))
              does_exist_f = to_db[3].fetchone()
              
              if does_exist_f is None:
                to_db[3].execute("UPDATE base_score SET SCORE_EXAM_CODE_F=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
                  (exam_code, score,to_db[7][0], get_name[1],))
                to_db[5].commit()
               
                flash(f'{get_name[0]} exam has been updated', category='danger')
              else:
                flash(f'{get_name[0]} exam has already been saved', category='danger')
    
            return render_template('show result.html', name=get_name[0], display='front', img_list=display_img,
              score=score, total_que=total_que)
      
      else:
        flash('Their is no image detected with the extension *.jpg, *.png, *.jpeg', category='danger')
        return redirect(url_for('process_file.upload_file'))
    elif request.method == 'GET':
      
      return render_template('upload file.html')
  except Exception as ec:
    print(ec, 'ec')
    flash(f'Error: {ec}', category='danger')
    return redirect(url_for('process_file.upload_file'))


############  USE FOLDER ############
@process_file.route('/evaluate_folder', methods=['POST', 'GET'])
@login_required
def upload_folder():
  scores = []
  names = []
  num_saved = 0
  num_existed = 0
  
  invalid_img = []

  existed = {}
  new_result = {}
  if request.method=='POST':
    display = True

    directorate = request.form.get('file')
    for single_file in os.listdir(directorate):
      print(single_file)
      img = cv2.imread(directorate + '\\' + single_file)
      exam_code = run_file.gen_code(img, 4)
      # print(exam_code, 'exam_code')

      # 2 == BACK
      if type(exam_code)==IndexError:
        exam_code = run_file.gen_code(img, 2)
        # print(exam_code, 'exam_code')
        if type(exam_code)==int and  int(str(exam_code)[-1])==2:
          to_db = run_file.connectionToDB(exam_code_b=exam_code)
          
          if to_db[7] is not None:
            student_name = run_file.gen_name(img, 1)

            # student_name[4] == converts img to text
            get_name = run_file.get_name(student_name[4], to_db[1])
            # print(get_name, '!!!')
            to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
              (to_db[7][0], get_name[1]))
            does_exist = to_db[3].fetchone()
            # use answer_list instead of final_answer b/c there is no preprocessing that will happen unlike t/f and choose
            final_answer = run_file.answer_lists(exam_code_b=exam_code)
            response = run_file.gen_write(img, 0)
            analyzed_text = response[4]
  
            score = 0
            for x in analyzed_text:
              result = cloud.similarity_test(x, final_answer)
              # print(result[1])
              if result[1] >= 70:
                score += 1
            display = 'back'
            
            # If it doesn't exist with student name and subject id
            if does_exist is None:
              run_file.upload_result(score, get_name[1], to_db[7][0], 'true', datetime.date.today(),
                exam_code_b=exam_code)
              flash(f'{get_name[0]} exam has been registered successfully', category='success')
              new_result.update({get_name[0]:score})
              num_saved+=1

            # If it exists with student name and subject id then
            else:
              to_db[3].execute(
                "SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_B=%s",
                (to_db[7][0], get_name[1], exam_code,))
              does_exist_f = to_db[3].fetchone()
              
              # If the front is registered
              if does_exist_f is None:
                to_db[3].execute(
                  "UPDATE base_score SET SCORE_EXAM_CODE_B=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
                  (exam_code, score, to_db[7][0], get_name[1],))
                to_db[5].commit()
                # print(f'Exam updated')
                num_saved+=1
                new_result.update({get_name[0]:score})
              else:
                # print(f'Exam already been saved: {single_file}')
                num_existed+=1
                existed.update({get_name[0]:score})

          else:
            print(f'The image is not recognized or exam code is invalid: file name {single_file}')
            invalid_img.append(single_file)
            
      #  Front
      elif type(exam_code)==int and int(str(exam_code)[-1])==1:
        print('ffffffffffffff')
        to_db = run_file.connectionToDB(exam_code_f=exam_code)
        if to_db[7] is not None:
          # print(to_db[7])
          student_name = run_file.gen_name(img, 2)

          # student_name[4] == converts img to text
          get_name = run_file.get_name(student_name[4], to_db[1])
          print(get_name, 'get_name')
          to_db[3].execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
            (to_db[7][0], get_name[1]))
          does_exist = to_db[3].fetchone()
  
          final_answer = run_file.final_ans(exam_code)
  
          all_together_0 = run_file.gen_file_choose(final_answer[0], img, 1)
          all_together_1 = run_file.gen_file_choose(final_answer[0], img, 0)
          all_together_m = run_file.gen_file_m(final_answer[2], img, 3)
          all_together_tf = run_file.gen_file_tf(final_answer[1], img, 5)
  
          incorrect_ans = []
          incorrect_que = []
          disqualified_ans = []
          disqualified_que = []
  
          score = 0
          if final_answer[3][0] is not None:
            # number of choose < 50
            if len(final_answer[3][0]) <= 50:
              score += all_together_0[1]
              incorrect_ans.extend(all_together_0[3][5])
              incorrect_que.extend(all_together_0[3][4])
              disqualified_que.extend(all_together_0[3][3])
              disqualified_ans.append(all_together_0[3][6])
  
            else:
              score += all_together_0[1]
              incorrect_ans.extend(all_together_0[3][5])
              incorrect_que.extend(all_together_0[3][4])
              disqualified_que.extend(all_together_0[3][3])
              disqualified_ans.append(all_together_0[3][6])
  
              score += all_together_1[1]
              incorrect_ans.extend(all_together_1[3][5])
              incorrect_que.extend([x + 50 for x in all_together_1[3][4]])
              disqualified_que.extend([x + 50 for x in all_together_1[3][3]])
              disqualified_ans.append(all_together_1[3][6])

          if final_answer[1] is not None:
            score += all_together_tf[1]
  
          if final_answer[2] is not None:
            score += all_together_m[1]
  
          if does_exist is None:
            run_file.upload_result(score, get_name[1], to_db[7][0], 'true', datetime.date.today(),
              str(incorrect_ans), str(incorrect_que), str(disqualified_que), exam_code_f=exam_code)
            # flash(f'{get_name[0]} exam has been registered successfully', category='success')
            num_existed+=1
            new_result.update({get_name[0]:score})
            print(new_result, 'new')
          else:
            to_db[3].execute(
              "SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_F=%s",
              (to_db[7][0], get_name[1], exam_code,))
            does_exist_b = to_db[3].fetchone()
            print(does_exist_b, 'does_b')
            # If back exists or if the fill in the database
            if does_exist_b is None:
              to_db[3].execute(
                "UPDATE base_score SET SCORE_EXAM_CODE_F=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
                (exam_code, score, to_db[7][0], get_name[1],))
              to_db[5].commit()
              num_saved += 1
              new_result.update({get_name[0]: score})
            else:
              # flash(f'{get_name[0]} exam has already been saved', category='danger')
              print('back doesnt exist', get_name[0], score)
              num_existed+=1
              print(existed, 'value')
              if get_name[0] in existed:
                print('existed', '--------')
                print(existed.values(), 'value')
                existed[get_name[0]] = [existed.values()]
                existed[get_name[0]].append(score)
                print()
              existed.__setitem__(get_name[0], score)
              existed |= {get_name[0]:score}
              # existed.update({get_name[0]:score})
              print(existed, 'existed')
              
    print(new_result, existed, 'existed', 'saved')
    flash(f'{num_saved} Has been saved', category='success')
    flash(f'{num_existed} Has already been registered', category='danger')
    return render_template('evaluation description.html', display=display, score=scores, new_result=new_result,
      existed=existed)
    
  
  elif request.method == 'GET':
    display = False
    return render_template('upload folder.html', display=display, score='score', name='stu', names='(len(11))')
