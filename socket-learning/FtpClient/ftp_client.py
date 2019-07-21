import argparse
import hashlib
import json
import os
import socket

STATUS_CODE = {
    250: "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251: "Invalid cmd ",
    252: "Invalid auth data",
    253: "Wrong username or password",
    254: "Passed authentication",
}


class FtpClient(object):
    def __init__(self):
        self.sock = socket.socket()
        self.connected = False
        parser = argparse.ArgumentParser(description="Ftp Client Write by Python")
        parser.add_argument("-s", "--server", help="ftp server address", required=True)
        parser.add_argument("-P", "--port", type=int, help="ftp server port", required=True)
        parser.add_argument("-u", "--username", help="username", required=True)
        parser.add_argument("-p", "--password", help="password", required=True)
        self.args = parser.parse_args()
        self.make_connection()

    def make_connection(self):
        try:
            self.sock.connect((self.args.server, self.args.port))
            self.connected = True
        except ConnectionRefusedError as e:
            print("connection refused, please check the server address and port")
            self.connected = False

    def get_response(self):
        data = self.sock.recv(1024)
        if len(data) == 0:
            print('received null data')
            return None
        try:
            data = data.decode()
            data = json.loads(data)
        except json.decoder.JSONDecodeError as e:
            print('error format of response message')
            data = {'status_code': 250, 'status_message': 'error format of response data : %s' % data}
        return data

    def authenticate(self):
        data = {"action": "auth", "username": self.args.username, "password": self.args.password}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        if response is None:
            print("authenticate failed, ftp server returned Null Data")
            return False
        elif response.get('status_code') == 254:
            self.user = self.args.username
            return True
        else:
            print("authenticate failed, error message :\n\t%s" % response.get('status_message'))
            return False

    @staticmethod
    def show_progress(total_size):
        received_size = 0
        current_percent = 0
        while received_size < total_size:
            if int((received_size / total_size) * 100) > current_percent:
                print("#", end="", flush=True)
                current_percent = int((received_size / total_size) * 100)
            new_size = yield
            received_size += new_size

    def interactive(self):
        if not self.connected:
            print("not connected")
            return
        if not self.authenticate():
            print("authenticate failed")
            return
        self.terminal_hint = "[%s]$:" % self.user
        exit_interactive = False
        while not exit_interactive:
            choice = input(self.terminal_hint).strip()
            if len(choice) == 0:
                continue
            cmd_list = choice.split(' ')
            if cmd_list[0] == 'quit' or cmd_list[0] == 'exit':
                print('Good Bye')
                exit_interactive = True
                continue
            if hasattr(self, '_%s' % cmd_list[0]):
                func = getattr(self, '_%s' % cmd_list[0])
                func(cmd_list[1:])
            else:
                print('invalid command, type help to check the help message')

    def _get(self, data):
        if len(data) != 1:
            print('should one filename followed')
            return
        data_header = {
            "action": "get",
            "filename": data[0]
        }
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()
        if response is None or response.get('status_code') is None:
            print("error message received")
            return
        elif response.get('status_code') != 257:
            print("error status_code received, error_message: %s" % response.get('status_message'))
            return

        file_size = response.get('data').get('file_size')
        if file_size is None or type(file_size) is not int:
            print('file_size is required and should be a int value')
            return
        self.sock.send(b'0')  # ready to received file

        file_name = data[0]
        file_obj = open(file_name, 'wb')
        md5_obj = hashlib.md5()
        progress = self.show_progress(total_size=file_size)
        next(progress)
        received_size = 0
        while received_size < file_size:
            if file_size - received_size < 4096:
                data = self.sock.recv(file_size - received_size)
            else:
                data = self.sock.recv(4096)
            received_size += len(data)
            try:
                progress.send(len(data))
            except StopIteration:
                print('\ndata received completely: 100%')
            file_obj.write(data)
            md5_obj.update(data)
        else:
            file_obj.close()
            current_md5 = md5_obj.hexdigest()
            response = self.get_response()
            received_md5 = response.get('data').get('md5')
            if current_md5 == received_md5:
                print('validate file hash value success')
            else:
                print('validate file hash value failed')

    def _put(self, data):
        if len(data) != 1:
            print("cmd should be one dirname followed")
            return
        filename = data[0]
        if not os.path.isfile(filename):
            print("local file does not exist")
            return
        file_size = os.path.getsize(filename)
        self.sock.send(json.dumps({"action": "put", "filename": filename, "file_size": file_size}).encode())
        self.sock.recv(1)
        md5_obj = hashlib.md5()
        sent_size = 0
        file_obj = open(filename, 'rb')
        progress = self.show_progress(total_size=file_size)
        next(progress)
        for line in file_obj:
            self.sock.send(line)
            sent_size += len(line)
            try:
                progress.send(len(line))
            except StopIteration:
                print('\ndata send completely: 100%')
            md5_obj.update(line)
        else:
            file_obj.close()
            md5_value = md5_obj.hexdigest()
            self.sock.send(json.dumps({"md5_value": md5_value}).encode())

        response = self.get_response()
        if response is None or response.get('status_code') != 200:
            print("some error happened, status_message: %s, detail_message: %s"
                  % (response.get('status_message'), response.get('data')))
        else:
            print("put file successfully")

    def _ls(self, data):
        action = {"action": "listdir"}
        self.sock.send(json.dumps(action).encode())
        response = self.get_response()
        if response is None or response.get('status_code') != 200:
            print("some error happened, status_message: %s, detail_message: %s"
                  % (response.get('status_message'), response.get('data')))
        else:
            data = response.get('data')
            if data is None:
                print("some error happened, empty data received")
            else:
                print(data)

    def _mkdir(self, data):
        if len(data) != 1:
            print("cmd should be one dirname followed")
            return
        action = {"action": "mkdir", "dirname": data[0]}
        self.sock.send(json.dumps(action).encode())
        response = self.get_response()
        if response is None or response.get('status_code') != 200:
            print("some error happened, status_message: %s, detail_message: %s"
                  % (response.get('status_message'), response.get('data')))
        else:
            print("command execute successfully")

    def _cd(self, data):
        if len(data) != 1:
            print("cmd should be one dirname followed")
            return
        action = {"action": "cd", "dirname": data[0]}
        self.sock.send(json.dumps(action).encode())
        response = self.get_response()
        if response is None:
            print("some error happened, status_message: %s" % response.get('status_message'))
        elif response.get('status_code') != 260:
            print(response.get('status_message'))
        else:
            relative_path = self._pwd()
            if relative_path is None:
                print("get current path failed")
                return
            elif relative_path == '' or relative_path == '/':
                self.terminal_hint = "[%s]$:" % self.user
            else:
                self.terminal_hint = "[%s]:%s$" % (self.user, relative_path)

    def _pwd(self, data=None):
        action = {"action": "pwd"}
        self.sock.send(json.dumps(action).encode())
        response = self.get_response()
        if response is None or response.get('status_code') != 200:
            print("some error happened, status_message: %s, detail_message: %s"
                  % (response.get('status_message'), response.get('data')))
            return None
        data = response.get('data')
        if data is None or data.get('path') is None:
            print('None data received')
            return None
        path = data.get('path')
        if len(path) == 0:
            print('/')
        else:
            print(path)
        return path

    def _help(self, data):
        supported_action = """
        get filename    #get file from FTP server
        put filename    #upload file to FTP server
        mkdir dirname   #make dir on FTP server
        ls              #list files in current dir on FTP server
        pwd             #check current path on server
        cd path         #change directory , same usage as linux cd command
        """
        print(supported_action)


if __name__ == '__main__':
    ftp_client = FtpClient()
    ftp_client.interactive()
