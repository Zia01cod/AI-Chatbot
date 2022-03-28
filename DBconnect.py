import sqlite3

class DBconnect:
	def __init__(self):
		self.conn = None
		self.fname = None
		self.cursor = None

	def getConnection(self,fname):
		try:
			self.conn = sqlite3.connect(fname)
			self.fname = fname
			print(sqlite3.version)

		except sqlite3.Error as err:
			print(err)


	def putQuery(self,query):
		try:
			self.cursor = self.conn.cursor()
			self.cursor.execute(query)

		except sqlite3.Error as err:
			print(err)

	def getQuery(self,query):
		try:
			self.cursor = self.conn.cursor()
			self.cursor.execute(query)

			rows = self.cursor.fetchall()
			return rows

		except sqlite3.Error as err:
			print(err)
			return None

	def closeConnection(self):
		self.conn.commit()
		self.conn.close()
