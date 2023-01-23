import psycopg2

conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='243313')

cur = conn.cursor()

def retrieve_data(data):
	cur.execute(f'SELECT * FROM base_{data}')
	conn.commit()

	result = cur.fetchall()
	cur.close()
	conn.close()

	return result

for rd in retrieve_data('user'):
	print(rd)