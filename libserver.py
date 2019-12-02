import selectors
import struct
import traceback

class Message():
  def __init__(self, selector, sock, addr, storage):
    self.selector = selector
    self.sock = sock
    self.addr = addr
    self.storage = storage
    self.command = None
    self.args = None
    self.content = None
    self._recv_buffer = b''
    self._send_buffer = b''
    self._command_len = None
    self._args_len = None
    self._content_len = None
    self.response_created = False

  def process_events(self, mask):
    if mask & selectors.EVENT_READ:
      self.read()
    if mask & selectors.EVENT_WRITE:
      self.write()

  def read(self):
    self._read()

    # State machine
    if self._command_len is None:
      self.process_command_len()

    if self._command_len is not None and self.command is None:
      #print(1)
      self.process_command()

    if self.command is not None and self._args_len is None:
      #print(2)
      self.process_args_len()

    if self._args_len is not None:
      #print(3)
      self.process_args()

    if self._content_len is None:
      #print(4)
      self.process_content_len()

    if self._content_len is not None:
      #print(5)
      self.process_content()

    #print('Parsing done')
    #print(self._recv_buffer)
    #print(self._command_len, self.command, self._args_len, self.args, self._content_len, self.content)

    if self.command is not None:
      self.process_request()

  def write(self):
    if self.command:
      if not self.response_created:
        self.create_response()

    self._write()

  def close(self):
    print('[Handler] Closing connection to {}'.format(self.addr))

    try:
      self.selector.unregister(self.sock)
    except Exception as e:
      print(
        'Error: selector.unregister() for {}: {}'.format(self.addr, repr(e))
      )

    try:
      self.sock.close()
    except OSError as e:
      print(
        'Error: socket.close() for {}: {}'.format(self.addr, repr(e))
      )
    finally:
      self.sock = None

  def process_command_len(self):
    cmdlen = 2
    if len(self._recv_buffer) >= cmdlen:
      self._command_len = struct.unpack(
        '!H', self._recv_buffer[:cmdlen]
      )[0]
      self._recv_buffer = self._recv_buffer[cmdlen:]

  def process_command(self):
    cmdlen = self._command_len
    if len(self._recv_buffer) >= cmdlen:
      self.command = self._recv_buffer[:cmdlen]
      self._recv_buffer = self._recv_buffer[cmdlen:]

  def process_args_len(self):
    argslen = 2
    if len(self._recv_buffer) >= argslen:
      self._args_len = struct.unpack(
        '!H', self._recv_buffer[:argslen]
      )[0]
      self._recv_buffer = self._recv_buffer[argslen:]

  def process_args(self):
    argslen = self._args_len
    if argslen > 0 and len(self._recv_buffer) >= argslen:
      self.args = self._recv_buffer[:argslen]
      self._recv_buffer = self._recv_buffer[argslen:]

  def process_content_len(self):
    contlen = 2
    if len(self._recv_buffer) >= contlen:
      self._content_len = struct.unpack(
        '!H', self._recv_buffer[:contlen]
      )[0]
      self._recv_buffer = self._recv_buffer[contlen:]

  def process_content(self):
    contlen = self._content_len
    if contlen > 0 and len(self._recv_buffer) >= contlen:
      self.content = self._recv_buffer[:contlen]
      self._recv_buffer = self._recv_buffer[contlen:]

  def process_request(self):
    '''
    The request processor
    '''
    
    # Transform the command
    if self.command is not None:
        self.command = self.command.decode()

    # Transform args to be an array
    if self.args is not None:
        self.args = self.args.decode()
        self.args = self.args.split('\r\n')

    # Toggle writing
    self._set_selector_events_mask('w')

  def create_response(self):
    '''
    The Response creator
    '''
    res = b'OK'

    try:
      res = StorageHandler.handle_command(self.storage, self.command, self.args, self.content)
    except:
      print('[Handler][Error] Exception caught by {}\n{}'.format(self.addr, traceback.format_exc()))
      res = b'Error'

    self._send_buffer += res
    self.response_created = True

  def _clear_request(self):
    '''
    Cleans up everything after client's been served
    '''
    self.command = self._command_len = self.args = self._args_len = self.content = self._content_len = None

  def _read(self):
    try:
      data = self.sock.recv(4096)
    except BlockingIOError:
      pass
    else:
      if data:
        self._recv_buffer += data
        print('Received {} from {}'.format(repr(data), self.addr))
      else:
        raise RuntimeError('Peer closed')

  def _write(self):
    if self._send_buffer:
      try:
        sent = self.sock.send(self._send_buffer)
        print('Sent {} bytes to {}'.format(sent, self.addr))
      except BlockingIOError:
        pass
      else:
        self._send_buffer = self._send_buffer[sent:]
    else:
      print('Clearing things')
      self.response_created = False
      self._clear_request()
      self._set_selector_events_mask('r')

  def _set_selector_events_mask(self, mode):
    if mode == 'r':
      events = selectors.EVENT_READ
    elif mode == 'w':
      events = selectors.EVENT_WRITE
    elif mode == 'rw':
      events = selectors.EVENT_READ | selectors.EVENT_WRITE
    else:
      raise ValueError('Invalid mask mode: {}'.format(mode))

    self.selector.modify(self.sock, events, data=self)


CODE_OK = b'OK'
CODE_FILE_NOT_FOUND = b'Error: resource not found'
CODE_ACCESS_DENIED = b'Error: access denied'

class StorageHandler():
  def handle_init(storage, *_):
    storage.init_storage()
    return CODE_OK

  def handle_file_creation(storage, args, *_):
    storage.create_file(args[0])
    return CODE_OK

  def handle_file_read(storage, args, *_):
    r = storage.read_file(args[0])
    if r is None:
      return CODE_FILE_NOT_FOUND

    return r

  def handle_file_write(storage, args, content):
    storage.write_file(args[0], content)
    return CODE_OK

  def handle_file_info(storage, args, *_):
    return str(storage.get_info(args[0])).encode()

  def handle_file_copy(storage, args, *_):
    storage.copy_file(args[0], args[1])
    return CODE_OK

  def handle_file_move(storage, args, *_):
    storage.move_file(args[0], args[1])
    return CODE_OK

  def handle_change_dir(storage, args, *_):
    return storage.set_directory(args[0]).encode()

  def handle_list_files(storage, *_):
    files = storage.list_files()
    dirs = storage.list_dirs()
    return ' '.join(dirs + files).encode() if len(dirs + files) else b' '

  def handle_make_dir(storage, args, *_):
    storage.create_directory(args[0])
    return CODE_OK

  def handle_remove(storage, args, *_):
    type = storage.check_dir_or_file(args[0])
    if type is None:
      return CODE_FILE_NOT_FOUND

    if type == 'DIR':
      r = storage.remove_dir(args[0])
    elif type == 'FILE':
      r = storage.remove_file(args[0])

    if r is None:
      return CODE_FILE_NOT_FOUND
    elif r is False:
      return CODE_ACCESS_DENIED

    return CODE_OK

  COMMANDS = {
    'INIT': handle_init,
    'TOUCH': handle_file_creation,
    'FREAD': handle_file_read,
    'FWRITE': handle_file_write,
    'FINFO': handle_file_info,
    'FCP': handle_file_copy,
    'FMV': handle_file_move,
    'CD': handle_change_dir,
    'LS': handle_list_files,
    'MKDIR': handle_make_dir,
    'RM': handle_remove
  }

  def handle_command(storage, command, args = None, content = None):
    cmd = command.upper()

    if cmd in StorageHandler.COMMANDS:
      r = StorageHandler.COMMANDS[cmd](storage, args, content)
      return struct.pack('!H', len(r)) + r
    else:
      return 'Command not found: {}'.format(command).encode()