import socket

PORT = 3333

class Slave():
	def __init__(self, name):
		self.name = name
	
	def read(self, chunk):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.name, PORT))
			s.send(b'RD' + chunk.encode('ascii'))
			size = int(s.recv(16).decode().strip())
			if size == -1:
				return None
			chunk = s.recv(size)
			s.close()
			return chunk
		except Exception as e:
			print(e)
			return None
	
	def write(self, chunk):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.name, PORT))
			s.send(b'WR' + chunk[0].encode('ascii'))
			s.send(chunk[1])
			s.close()
		except:
			return None
	
	def remove(self, chunk):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.name, PORT))
			s.send(b'RM' + chunk.encode('ascii'))
			s.close()
		except:
			return None


