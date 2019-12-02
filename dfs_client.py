import sys
import argparse
from libclient import Networker

def display_res(networker):
    print(networker.recv_response().decode())


def handle_init(networker, args):
    networker.send_command(args[0])
    display_res(networker)


def handle_file_creation(networker, args):
    if len(args) < 2:
        print('usage: {} <remote_filename>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    display_res(networker)


def handle_file_read(networker, args):
    if len(args) < 3:
        print('usage: {} <remote_filename> <local_filename>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    with open(args[2], 'wb') as f:
        f.write(networker.recv_response())
    print('OK')


def handle_file_write(networker, args):
    if len(args) < 3:
        print('usage: {} <local_filename> <remote_filename>'.format(args[0]))
        return
    with open(args[1], 'rb') as f:
        networker.send_command(args[0], [args[2]], f.read())
    display_res(networker)


def handle_file_info(networker, args):
    if len(args) < 2:
        print('usage: {} <remote_filename>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    display_res(networker)


def handle_file_copy(networker, args):
    if len(args) < 3:
        print('usage: {} <remote_source_filename> <remote_target_filename>'.format(args[0]))
        return
    networker.send_command(args[0], args[1:3])
    display_res(networker)


def handle_file_move(networker, args):
    if len(args) < 3:
        print('usage: {} <remote_source_filename> <remote_target_filename>'.format(args[0]))
        return
    networker.send_command(args[0], args[1:3])
    display_res(networker)


def handle_change_dir(networker, args):
    if len(args) < 2:
        print('usage: {} <remote_dir>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    display_res(networker)


def handle_list_files(networker, args):
    networker.send_command(args[0])
    display_res(networker)


def handle_make_dir(networker, args):
    if len(args) < 2:
        print('usage: {} <remote_dir>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    display_res(networker)


def handle_remove(networker, args):
    if len(args) < 2:
        print('usage: {} <remote_dir>'.format(args[0]))
        return
    networker.send_command(args[0], [args[1]])
    display_res(networker)


# Commands that are sent to server
SERVER_COMMANDS = {
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

# Commands that close connection and terminate program
EXIT_COMMANDS = [
    'Q',
    'QUIT',
    'EXIT',
    'LOGOUT'
]


class CommandProcessor():
    '''
    The class that processes the user input commands
    '''
    def __init__(self, networker):
        self.networker = networker

    def process_command(self, command):
        cmd_tokens = command.split()

        # Make commands register-invariant
        cmd_tokens[0] = cmd_tokens[0].upper()

        # Exit command
        if cmd_tokens[0] in EXIT_COMMANDS:
            self.networker.close_connection()
            print('Finishing execution')
            sys.exit(0)

        # Server commands
        if cmd_tokens[0] in SERVER_COMMANDS:
            handler = SERVER_COMMANDS[cmd_tokens[0]]
            handler(self.networker, cmd_tokens)
        else:
            print('Not a valid command: {}'.format(command))


def client_main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Distributed File System Project (Client)')
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=int, default=2100)
    args = parser.parse_args()

    # Some nice output
    print('Starting the DFS Client')

    # Connect to the DFS Server
    networker = Networker(args.host, args.port)
    networker.connect()
    
    # Create command processor
    command_processor = CommandProcessor(networker)

    # Listen to user commands
    while True:
        command_processor.process_command(input('> ')) # todo show the working directory?


if __name__ == '__main__':
    try:
      client_main()
    except KeyboardInterrupt:
      print('^C')
      print('Finishing execution')
    except ConnectionResetError:
      print('Server forcibly closed connection, shutting down')
