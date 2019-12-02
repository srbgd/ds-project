from slave import Slave
import random


EXTRA_NODES_COUNT = 2
CHUNK_SIZE = 4096


class Storage():
	def __init__(self):
		self.slaves = []
		self.files = dict()
		self.sizes = dict()
		self.dirs = ['/']
		self.rr = -1
	
	def write_file(self, path, file_content):
		self.remove_file(path)
		self.sizes[path] = len(file_content)
		if file_content == b'':
			chunks = [(''.join(random.choices('0123456789ABCDEF', k=8)), b'')]
		else:
			chunks = [(''.join(random.choices('0123456789ABCDEF', k=8)), file_content[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]) for i in range((len(file_content) + CHUNK_SIZE - 1) // CHUNK_SIZE)]
		f = []
		for chunk in chunks:
			f.append((chunk[0], []))
			for _ in range(EXTRA_NODES_COUNT):
				slave = self.get_slave()
				attempts_count = 0
				while slave in f[-1][1] and attempts_count <= len(self.slaves):
					slave = self.get_slave()
					attempts_count += 1
				if not slave in f[-1][1]:
					slave.write(chunk)
					f[-1][1].append(slave)
		self.files[path] = f
	
	def read_file(self, path):
		if not path in self.files:
			return None
		chunks = []
		for chunk in self.files[path]:
			for slave in chunk[1]:
				content = slave.read(chunk[0])
				if content != None:
					break
			if content == None:
				return None
			chunks.append(content)
		return b''.join(chunks)
	
	def remove_file(self, path):
		if path in self.files:
			for chunk in self.files[path]:
				for slave in chunk[1]:
					slave.remove(chunk[0])
			del self.files[path]
			del self.sizes[path]
			return True
		else:
			return None
	
	def get_slave(self):
		if self.slaves == []:
			return None
		else:
			self.rr += 1
			return self.slaves[self.rr % len(self.slaves)]
	
	def add_slave(self, name):
		self.slaves.append(Slave(name))
	
	def wipe(self):
		names = list(self.files.keys())
		for path in names:
			self.remove_file(path)
		self.dirs = ['/']
	
	def dir_exists(self, name):
		return name in self.dirs
	
	def file_exists(self, name):
		return name in self.files.keys()
	
	def create_dir(self, name):
		if not self.dir_exists(name):
			self.dirs.append(name)
	
	def list_files(self, name):
		result = []
		for f in self.files.keys():
			if f.startswith(name) and f.count('/') == name.count('/'):
				result.append(f)
		return result
	
	def list_dirs(self, name):
		result = []
		for d in self.dirs:
			if d.startswith(name) and d.count('/') == name.count('/') + 1:
				result.append(d)
		return result
	
	def copy_file(self, src, dst):
		if self.file_exists(src):
			content = self.read_file(src)
			self.write_file(dst, content)
	
	def move_file(self, src, dst):
		self.copy_file(src, dst)
		self.remove_file(src)
	
	def remove_dir(self, name):
		if self.dir_exists(name):
			if self.list_files(name) == [] and self.list_dirs(name) == []:
				self.dirs.remove(name)
				return True
			else:
				return False
		else:
			return None
	
	def get_info(self, filename):
		if self.file_exists(filename):
			return self.sizes[filename]
