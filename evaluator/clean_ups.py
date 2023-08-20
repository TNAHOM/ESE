num_str = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F':5, 'G':6, 'H':7, 'I':8, 'J':9}
num_str_tf = {'T': 0, 'F': 1}

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
			if x == z:
				answer_list.append(y)
	return answer_list

def to_list(variable):
	x = variable.replace(',', '').replace("'", '').replace(' ', '').replace('[', '').replace(']', '')
	return x

def to_list_tf(variable):
	x = variable.replace(',', '').replace("'", '').replace('[', '').replace(']', '')
	return x

def to_list_fill(variable):
	x = variable.replace('[', '').replace(']', '').replace(' ', '')
	return x

def multi_ans_func(variable):
	variable = to_list_fill(variable)
	sign = []
	qoute = []
	comma = []
	ans_cleaned = []
	
	for y in range(len(variable)):
		if variable[y]=="'":
			# print(y, x[y])
			sign.append(y)
			qoute.append(y)
		if variable[y]==',':
			# print(y, x[y])
			sign.append(y)
			comma.append(y)
	
	for ind in range(len(sign)):
		try:
			find_hypen = variable.find(',', qoute[ind], qoute[ind + 1])
			multi_ans = variable[qoute[ind]:qoute[ind + 1] + 1]
			if find_hypen!=-1 and int(qoute[ind] + 2)!=int(qoute[ind + 1]):
				# Clean up for split
				multi_ans = multi_ans[1:-1].split(',')
				ans_cleaned.append(multi_ans)
			elif any(c.isalpha() for c in multi_ans[1:-1].split(',')):
				ans_cleaned.extend(multi_ans[1:-1].split(','))
		
		except IndexError as IE:
			pass
	
	return ans_cleaned
