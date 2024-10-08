from flask import render_template, redirect, url_for, flash, request, Blueprint
from evaluator import run_folder, run_file, cloud, connection
from flask_login import login_required, current_user
import os, cv2
from io import BytesIO


process_file = Blueprint('process_file', __name__)
@process_file.route('/evaluate-exam', methods=['GET', 'POST'])
@login_required
def upload_file():
  # try:
    if request.method=='POST':
      directory = request.form.get('file')
      student_id = request.form.get('student_id')
      file_name = request.files['file'].filename
      upload_file = request.files['file']
      full_path = directory+'\\'+file_name
    
      if file_name[-4:] == 'jpeg' or '.jpg' or '.png':
        img = cv2.imread(full_path)
        exam_code = run_file.gen_code(img, 4)

        # 2 == BACK
        if type(exam_code) == IndexError:
          exam_code = run_file.gen_code(img, 2)
          if int(str(exam_code)[-1])==2:
            exam_b = connection.ConnectionToDB(exam_code_b=exam_code)
            check_exam_b = exam_b.check_exam_b()
            if check_exam_b is not None:
              student_name = connection.ConnectionToDB().get_student_id(student_id)
              exam_name = f"{student_name[10]} {check_exam_b[4]} -B"
              school_folder_id = cloud.search_file(current_user.email)
              
              if student_name is not None:
                exam_exist = connection.ConnectionToDB(name_id=student_name[9]).exam_exist(check_exam_b[0])
  
                # use answer_list instead of final_answer b/c there is no preprocessing that will happen unlike t/f and choose
                final_answer = run_file.answer_lists(exam_code_b=exam_code)
                response = run_file.gen_write(img, 0)
                analyzed_text = response[4]
  
                result = cloud.similarity_test(analyzed_text, final_answer)
  
                display = 'back'
  
                if exam_exist is None:
                  connection.ConnectionToDB(exam_code_b=exam_code).upload_result(result[1], student_name[9], check_exam_b[0])

                  # UPLOAD EXAM IMAGE TO GOOGLE DRIVE
                  cloud.upload_exam(full_path, exam_name, upload_file, school_folder_id[1])
                  
                  flash(f'{student_name[10]} exam has been registered successfully', category='success')
                  
                else:
                  get_exam_b = connection.ConnectionToDB(name_id=student_name[9], exam_code_b=exam_code, name=student_name[10])
                  run = get_exam_b.get_exam_b(result[1], check_exam_b, full_path, exam_name, upload_file, school_folder_id[1])
    
                  flash(run, category='danger')
                return render_template('show result.html', name=student_name[10], display=display, img=response[2],
                  ans=result[0], score=result[1], )

              else:
                flash("Student Id doesn'\nt exist.Please try again!!", category='danger')
                return redirect(url_for('process_file.upload_file'))
            elif check_exam_b is None:
              flash('Exam id doesnt exist', category='danger')
              return redirect(url_for('process_file.upload_file'))
            
        # 1 == FRONT
        elif int(str(exam_code)[-1]) == 1:
          check_exam_f = connection.ConnectionToDB(exam_code_f=exam_code).check_exam_f()
  
          if check_exam_f is not None:
            student_name = connection.ConnectionToDB().get_student_id(student_id)
            if student_name is not None:
              exam_exist = connection.ConnectionToDB(name_id=student_name[9]).exam_exist(check_exam_f[0])
  
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

                exam_name = f"{student_name[10]} {check_exam_f[4]} -F"
                school_folder_id = cloud.search_file(current_user.email)

                if exam_exist is None:
                  connection.ConnectionToDB(exam_code_f=exam_code).upload_result(int(score), student_name[9], check_exam_f[0],
                    str(incorrect_ans), str(incorrect_que), str(disqualified_ans[0]), str(disqualified_que))

                  # UPLOAD EXAM IMAGE TO GOOGLE DRIVE
                  cloud.upload_exam(full_path, exam_name, upload_file, school_folder_id[1])
                  
                  flash(f'{student_name[10]} exam has been registered successfully', category='success')

                else:
                  get_exam_f = connection.ConnectionToDB(name_id=student_name[9], exam_code_f=exam_code, name=student_name[10])
                  run = get_exam_f.get_exam_f(score, check_exam_f, full_path, exam_name, upload_file, school_folder_id[1])
    
                  flash(run, category='danger')
  
                return render_template('show result.html', name=student_name[10], display='front', img_list=display_img,
                  score=score, total_que=total_que)
            
            else:
              flash("Student Id doesn'\nt exist.Please try again!!", category='danger')
              return redirect(url_for('process_file.upload_file'))

          elif check_exam_f is None:
            flash('Exam id doesnt exist', category='danger')
            return redirect(url_for('process_file.upload_file'))
      
      else:
        flash('Their is no image detected with the extension *.jpg, *.png, *.jpeg', category='danger')
        return redirect(url_for('process_file.upload_file'))
    elif request.method == 'GET':
      return render_template('upload file.html')
  # except Exception as ec:
  #   print(ec, 'ec')
  #   flash(f'Error: {ec}', category='danger')
  #   return redirect(url_for('process_file.upload_file'))

