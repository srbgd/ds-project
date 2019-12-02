import socket
import selectors
import argparse
import libserver
import traceback
from threading import Thread
from libstorage import StorageInterface

# Port to listen to (21 as in FTP, zeros for fun)
DEFAULT_PORT = 2100

class Server():
  '''
  Thread to accept new connections
  '''
  def __init__(self, selector, host, port):
    #super().__init__(daemon=True)
    self.host = host
    self.port = port
    self.selector = selector
    self.sock = socket.socket()
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Assign storage nodes
    self.connect_storage()


  def _accept_connection(self, sock):
    # Accept connection
    conn, addr = sock.accept()

    # Make new connection non-blocking
    conn.setblocking(False)

    # Register handler
    message = libserver.Message(self.selector, conn, addr, self.storage)
    self.selector.register(conn, selectors.EVENT_READ, data=message)

    # Output info
    print('[Conductor] Accepted connection from {}'.format(addr))


  def close(self):
    self.selector.close()


  def start(self):
    self.sock.bind((self.host, self.port))
    self.sock.listen()
    self.sock.setblocking(False)
    self.selector.register(self.sock, selectors.EVENT_READ, data=None)
    print('[Conductor] Listening on {}:{}'.format(self.host or '*', self.port))

    while True:
      events = self.selector.select(timeout=None)

      for key, mask in events:
        if key.data is None:
          self._accept_connection(key.fileobj)
        else:
          message = key.data

          try:
            message.process_events(mask)
          except Exception as e:
            print(
              '[Conductor][Error] Exception caught by {}\n{}'.format(message.addr, traceback.format_exc())
            )
            message.close()

  def connect_storage(self):
    self.storage = StorageInterface()


def create_server():
  # Parse arguments
  parser = argparse.ArgumentParser(description='Distributed File System (Project)')
  parser.add_argument('--host', type=str, default='')
  parser.add_argument('--port', type=int, default=DEFAULT_PORT)
  args = parser.parse_args()

  # Create the default selector
  sel = selectors.DefaultSelector()

  # Initialize the server
  server = Server(sel, args.host, args.port)

  # Return the server instance
  return server


if __name__ == '__main__':
  server = create_server()
  server.start()

  # Start the server and watch for KeyboardInterrupts
  # try:
    # server.start()
  # except KeyboardInterrupt:
    # print('Keyboard interrupt, shutting down')
  # finally:
    # server.close()
