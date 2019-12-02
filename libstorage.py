from storage import Storage


class StorageInterface():
  def __init__(self):
    self.pwd = '/'
    self.strg = Storage()
    self.strg.add_slave('52.91.167.138')
    self.strg.add_slave('18.208.151.51')
    self.strg.add_slave('54.224.241.232')
    self.absolute_file = lambda name: name if name[0] == '/' else self.pwd + name
    self.absolute_dir = lambda name: self.absolute_file(name if name[-1] == '/' else name + '/')

  def init_storage(self):
    self.strg.wipe()

  def current_directory(self):
    return self.pwd

  def create_directory(self, dirname):
    self.strg.create_dir(self.absolute_dir(dirname))

  def set_directory(self, dirname):
    dirname = self.absolute_dir(dirname)
    if self.strg.dir_exists(dirname):
      self.pwd = dirname
    return self.pwd

  def list_files(self):
    return self.strg.list_files(self.pwd)

  def list_dirs(self):
    return self.strg.list_dirs(self.pwd)

  def create_file(self, filename):
    self.write_file(filename, b'')

  def read_file(self, filename):
    f = self.strg.read_file(self.absolute_file(filename))
    return f

  def write_file(self, filename, file_contents):
    self.strg.write_file(self.absolute_file(filename), file_contents)

  def copy_file(self, source_filename, target_filename):
    self.strg.copy_file(self.absolute_file(source_filename), self.absolute_file(target_filename))

  def move_file(self, source_filename, target_filename):
    self.strg.move_file(self.absolute_file(source_filename), self.absolute_file(target_filename))

  def check_dir_or_file(self, name):
    if self.strg.dir_exists(self.absolute_dir(name)):
      return 'DIR'
    if self.strg.file_exists(self.absolute_file(name)):
      return 'FILE'

  def remove_file(self, filename):
    return self.strg.remove_file(self.absolute_file(filename))

  def remove_dir(self, dirname):
    absolute = self.absolute_dir(dirname)
    return self.strg.remove_dir(absolute) if not self.pwd.startswith(absolute) else False

  def get_info(self, filename):
    return self.strg.get_info(self.absolute_file(filename))
