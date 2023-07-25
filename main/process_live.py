import datetime

import cv2
from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from evaluator import run_live, run_folder
from flask_login import login_required
import uuid

process = Blueprint('process_live', __name__)

@process.route('/streams4')
def shape():
  number = int(request.args.get('number', 1))  # default to 1 if no number is provided
  gen = run_live.shape1(number)
  return Response(gen[0], mimetype='multipart/x-mixed-replace; boundary=frame')

@process.route('/check', methods=['GET', 'POST'])
def check_shape():
  if request.method == 'POST':
    selected_number = int(request.form.get('number', 1))  # default to 1 if no number is provided
    display = 'true'
    return render_template('check_shape.html', display=display, selected_number=selected_number)
  else:
    display = 'false'
    return render_template('check_shape.html', display=display)

@process.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
    selected_number = request.args.get('number')
    exam_code = run_live.exam_code(4, selected_number)
    print(exam_code)
    final_answer = run_live.final_ans(133441)

    # Get img once instead of multiple times
    choose1 = run_live.choose(final_answer[0], 1, selected_number)
    choose2 = run_live.choose(final_answer[0], 0, selected_number)

    tf = run_live.tf(final_answer[1], 5, selected_number)
    matching = run_live.matching(final_answer[2], 3, selected_number)

   # except Exception as ex:
  #   print(ex, 'lioliolio')
  #   return redirect(url_for('process_live.check_shape')), flash('Please try again ot try to adjust the paper', category='danger')

    return render_template('evaluate.html', score='score', img=choose1[2], img2=choose2[2], img_tf=tf[2], img_match=matching[2])

# @process.route('/streams4')
# def shape():
#   number = int(request.args.get('number', 1))  # default to 1 if no number is provided
#   gen = run_live.shape1(number)
#   return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')
#
# @process.route('/check', methods=['GET', 'POST'])
# def check_shape():
#   all_in_one = AllInOne()
#   if request.method == 'POST':
#     selected_number = int(request.form.get('number', 1))  # default to 1 if no number is provided
#     print(selected_number)
#     display = 'true'
#
#     return redirect(url_for('process_live.shape', number=selected_number))
#
#   else:
#     display = 'false'
#     return render_template('check_shape.html', display=display)