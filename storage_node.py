import socket
import os


CHUNK_SIZE = 4096


class Server():
	def __init__(self, port, folder):
		self.port = port
		self.folder = folder if folder[-1] == '/' else folder + '/'
	
	def listen(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('0.0.0.0', self.port))
		s.listen(1)
		print('listen')
		while True:
			c, _ = s.accept()
			op = c.recv(2)
			chunk = c.recv(8).decode()
			print(op)
			if op == b'RD':
				if os.path.exists(self.folder + chunk):
					with open(self.folder + chunk, 'rb') as f:
						content = f.read()
					n = str(len(content))
					c.send(n.encode('ascii') + (16 - len(n)) * b' ')
					c.send(content)
				else:
					c.send(b'-1              ')
			elif op == b'WR':
				content = c.recv(CHUNK_SIZE)
				with open(self.folder + chunk, 'wb') as f:
					f.write(content)
			elif op == b'RM':
				try:
					os.remove(self.folder + chunk)
				except:
					pass
			c.close()
			print('done')


def main():
	server = Server(3333, './chunks/')
	server.listen()


if __name__ == '__main__':
	main()
