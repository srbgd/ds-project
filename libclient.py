import socket
import struct

BUFFER_SIZE = 1024

class Networker():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket()

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            print('Connected to {}:{}'.format(self.host, self.port))
        except:
            print('Failed to connect to {}:{}'.format(self.host, self.port))
            exit(-1)

    def close_connection(self):
        self.sock.close()

    def __del__(self):
        self.close_connection()

    def send_command(self, command, command_args = None, content = None):
        command_len = struct.pack('!H', len(command))
        req = command_len + command.encode()

        if command_args is not None:
            args = '\r\n'.join(command_args)
            args_len = struct.pack('!H', len(args))
            req += args_len + args.encode()
        else:
            req += struct.pack('!H', 0)

        if content is not None:
            content_len = struct.pack('!H', len(content))
            req += content_len + content
        else:
            req += struct.pack('!H', 0)

        self.sock.send(req)

    def recv_response(self):
        response_len = self.sock.recv(2)
        response_len = struct.unpack('!H', response_len)[0]
        buf = self.sock.recv(response_len)

        return buf
