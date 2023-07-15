import datetime
import uuid

import psycopg2


class ConnectionToDB:
	
	def __init__(self, school=None, exam_code_f=None, exam_code_b=None, score_code_f=None, score_code_b=None,
	             name_id=None, name=None):
		self.school = school
		self.exam_code_f = exam_code_f
		self.exam_code_b = exam_code_b
		self.conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')
		self.name_id = name_id
		self.name = name

		self.subject_id = ''
		
	def get_school(self):
		cur_school = self.conn.cursor()
		cur_school.execute(f"SELECT * FROM base_user WHERE email='{self.school}'")
		school_id = cur_school.fetchone()[9]
		return school_id
	
	def get_exam_f(self, score):
		cur_exam = self.conn.cursor()
		cur_exam.execute(f"SELECT * FROM base_exam WHERE exam_code_f='{self.exam_code_f}'")
		exam_id = cur_exam.fetchone()
		
		# If exam exists with the given exam code
		if exam_id is not None:
			f_exist = self.conn.cursor()
			f_exist.execute(
				"SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_F=%s",
				(exam_id[0], self.name_id, self.exam_code_f,))
			does_exist_b = f_exist.fetchone()
			
			# If front exam exist when if
			if does_exist_b is None:
				update_exam = self.conn.cursor()
				update_exam.execute(
					"UPDATE base_score SET SCORE_EXAM_CODE_F=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
					(self.exam_code_f, score, exam_id[0], self.name_id,))
				self.conn.commit()
				
				flash = f'{self.name} exam has been updated'
			else:
				flash = f'{self.name} exam has been updated'
		
		return exam_id, flash
	
	def get_exam_b(self, score):
		cur_exam = self.conn.cursor()
		cur_exam.execute(f"SELECT * FROM base_exam WHERE exam_code_b='{self.exam_code_b}'")
		exam_id = cur_exam.fetchone()
		
		if self.subject_id is '':
			self.subject_id+=exam_id[0]
			
		# If exam exists with the given exam code
		if exam_id is not None:
			b_exist = self.conn.cursor()
			b_exist.execute(
				"SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s AND SCORE_EXAM_CODE_B=%s",
				(exam_id[0], self.name_id, self.exam_code_b,))
			does_exist_f = b_exist.fetchone()
			
			# If front exam exist when if
			if does_exist_f is None:
				update_exam = self.conn.cursor()
				update_exam.execute(
					"UPDATE base_score SET SCORE_EXAM_CODE_B=%s, SCORE=SCORE + %s WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
					(self.exam_code_b, score, exam_id[0], self.name_id,))
				self.conn.commit()
				
				flash = f'{self.name} exam has been updated'
			else:
				flash = f'{self.name} exam has been updated'
		
		return  exam_id, flash
	
	def get_student(self):
		cur_user = self.conn.cursor()
		cur_user.execute(f"SELECT * FROM base_user WHERE role='Student'")
		result_user = cur_user.fetchall()
		return result_user
	
	def exam_exist(self):
		cur_exist = self.conn.cursor()
		cur_exist.execute("SELECT * FROM base_score WHERE SUBJECT_ID=%s AND STUDENT_SCORE_ID=%s",
			(self.subject_id, self.name_id))
		does_exist = cur_exist.fetchone()
		return does_exist
	
	def upload_result(self, score, student_id, wrong_ans, wrong_que, disqualified_que):
		new_uuid = uuid.uuid4()
		cur = self.conn.cursor()
		cur.execute('SELECT * FROM base_exam')
		
		if self.exam_code_f is not None:
			insert_record = (
				new_uuid, score, student_id, self.subject_id, 'true', self.exam_code_f, datetime.date.today(), wrong_ans,
				wrong_que, disqualified_que, disqualified_que
			)
			insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, SCORE_EXAM_CODE_F,
			FINISHED, INCORRECT_ANS, INCORRECT_ANS_NUM, DISQUALIFIED_ANS, DISQUALIFIED_ANS_NUM) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
			
			cur.execute(insert_data_from, insert_record)
			self.conn.commit()
		
		elif self.exam_code_b is not None:
			insert_record = (
				new_uuid, score, student_id, self.subject_id, 'true', self.exam_code_b, datetime.date.today(),
			)
			insert_data_from = """ INSERT INTO base_score (ID, SCORE, STUDENT_SCORE_ID, SUBJECT_ID, DISPLAY, SCORE_EXAM_CODE_B,
			FINISHED,) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
			
			cur.execute(insert_data_from, insert_record)
			self.conn.commit()
			

# connection = ConnectionToDB(school='Hill@gmail.com')
# print(connection.get_school(), 'get_school')

# conn_get_name = ConnectionToDB()
# print(conn_get_name.get_student(), 'Student')

# conn_upload = ConnectionToDB()


# conn_exam_f = ConnectionToDB(exam_code_f=133441, name_id='555c4dc2-5f8b-48de-9415-503e20791e1b', name='Saron Tamirat Kebede')
# print(conn_exam_f.get_exam_f(score=22), 'get_exam_f')
# print(conn_exam_f.upload_result(score=33, ))
# conn_exam_b = ConnectionToDB(exam_code_b=133442, name_id='555c4dc2-5f8b-48de-9415-503e20791e1b', name='Saron Tamirat Kebede')
# print(conn_exam_b.get_exam_b(score=22), 'get_exam_b')
