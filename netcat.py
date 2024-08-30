import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable()

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    try:
        logging.debug(f"Executing command: {cmd}")
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command execution failed: {e}")
        return str(e)

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.debug(f"Initialized NetCat with target: {self.args.target}, port: {self.args.port}")

    def run(self):
        if self.args.listen:
            logging.info("Listening mode enabled.")
            self.listen()
        else:
            logging.info("Sending mode enabled.")
            self.send()

    def send(self):
        try:
            self.socket.connect((self.args.target, self.args.port))
            logging.info(f"Connected to {self.args.target}:{self.args.port}")
            if self.buffer:
                self.socket.send(self.buffer)
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    logging.debug(f"Received response: {response}")
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            logging.warning("User terminated the connection.")
            self.socket.close()
            sys.exit()
        except Exception as e:
            logging.error(f"Error during send: {e}")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        logging.info(f"Listening on {self.args.target}:{self.args.port}")
        while True:
            client_socket, address = self.socket.accept()
            logging.info(f"Accepted connection from {address}")
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        logging.debug("Handling client socket.")
        try:
            if self.args.execute:
                logging.info(f"Executing command: {self.args.execute}")
                output = execute(self.args.execute)
                client_socket.send(output.encode())
            elif self.args.upload:
                logging.info(f"Receiving file to save as: {self.args.upload}")
                file_buffer = b''
                while True:
                    data = client_socket.recv(4096)
                    if data:
                        file_buffer += data
                    else:
                        break
                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())
                logging.info(f"File saved: {self.args.upload}")
            elif self.args.command:
                logging.info("Command shell enabled.")
                cmd_buffer = b''
                while True:
                    try:
                        client_socket.send(b'BHP: #> ')
                        while '\n' not in cmd_buffer.decode():
                            cmd_buffer += client_socket.recv(64)
                        response = execute(cmd_buffer.decode())
                        if response:
                            client_socket.send(response.encode())
                        logging.debug(f"Command executed: {cmd_buffer.decode().strip()}")
                        cmd_buffer = b''
                    except Exception as e:
                        logging.error(f"Server error: {e}")
                        self.socket.close()
                        sys.exit()
        finally:
            client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    logging.info("NetCat initialized.")
    nc.run()
