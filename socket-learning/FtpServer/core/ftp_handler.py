import hashlib
import json
import os, subprocess
import re
import socketserver
from bin.ftp_server import BASE_DIR as base_dir

STATUS_CODE = {
    200: "Task finished",
    250: "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251: "Invalid cmd ",
    252: "Invalid auth data",
    253: "Wrong username or password",
    254: "Passed authentication",
    255: "Filename doesn't provided",
    256: "File doesn't exist on server",
    257: "ready to send file",
    258: "md5 verification",
    259: "path doesn't exist on server",
    260: "path changed",
    261: "system error"
}


class FtpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                data = self.request.recv(1024).decode()
                if not data:
                    # print('null data received from client, may be client has closed')
                    break

                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError as e:
                    # print("error message format")
                    self.send_response(250)
                    continue

                if data.get('action') is None:
                    # print("error message format")
                    self.send_response(250)
                elif not hasattr(self, '_%s' % data.get('action')):
                    # print("invalid command")
                    self.send_response(251)
                else:
                    func = getattr(self, '_%s' % data.get('action'))
                    func(data)
        except (BrokenPipeError, ConnectionResetError) as e:
            print('Exception happened, may be some error happened on client')

    def _auth(self, data):
        print('handle command from client "auth"')
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            self.send_response(252)
        elif username != 'mike' or password != 'mike':  # validate username and password
            self.send_response(253)
        else:
            self.user_name = username
            self.home_dir = base_dir + '/data/' + username
            self.current_dir = self.home_dir
            self.send_response(254)

    def _get(self, data):
        filename = data.get('filename')
        if filename is None:
            self.send_response(255)
            return
        file_abs_path = self.current_dir + '/' + filename
        if not os.path.isfile(file_abs_path):  # file does not exist
            self.send_response(256)
            return
        file_obj = open(file_abs_path, 'rb')
        file_size = os.path.getsize(file_abs_path)
        self.send_response(257, data={"file_size": file_size})
        self.request.recv(1)  # receive the response from client

        md5_obj = hashlib.md5()
        for line in file_obj:
            self.request.send(line)
            md5_obj.update(line)
        else:
            file_obj.close()
            md5_value = md5_obj.hexdigest()
            self.send_response(258, {"md5": md5_value})

    def _put(self, data):
        filename = data.get('filename')
        file_size = data.get('file_size')
        file_abs_path = self.current_dir + '/' + filename
        file_obj = open(file_abs_path, 'wb')
        self.request.send(b'0')
        current_size = 0
        md5_obj = hashlib.md5()
        while current_size < file_size:
            if file_size - current_size < 4096:
                data = self.request.recv(file_size - current_size)
            else:
                data = self.request.recv(4096)
            current_size += len(data)
            md5_obj.update(data)
            file_obj.write(data)
        else:
            file_obj.close()
            data_md5_value = md5_obj.hexdigest()
            md5_data = self.request.recv(1024).decode()
            md5_data = json.loads(md5_data)
            md5_value = md5_data.get('md5_value')
            if md5_value == data_md5_value:
                self.send_response(200)
            else:
                self.send_response(258, data='md5 validation failed')

    def _listdir(self, data):
        cmd = "ls -lsh " + self.current_dir
        ret_code, cmd_result = subprocess.getstatusoutput(cmd)
        if ret_code is not 0:
            self.send_response(status_code=261, data=cmd_result)
        else:
            self.send_response(status_code=200, data=cmd_result)

    def _pwd(self, data):
        relative_path = re.sub("^%s" % (base_dir + "/data/" + self.user_name), '', self.current_dir)
        self.send_response(status_code=200, data={"path": relative_path})

    def _mkdir(self, data):
        dirname = data.get('dirname')
        if dirname is None:
            self.send_response(status_code=251)
        cmd = "mkdir " + self.current_dir + '/' + dirname
        ret_code, cmd_result = subprocess.getstatusoutput(cmd)
        if ret_code is not 0:
            self.send_response(status_code=261, data=cmd_result)
        else:
            self.send_response(status_code=200)

    def _cd(self, data):
        dirname = data.get('dirname')
        if dirname is None:
            self.send_response(status_code=251)
        target_dir = self.current_dir + '/' + dirname
        if not os.path.isdir(target_dir):
            self.send_response(status_code=259)
            return
        target_dir = os.path.abspath(target_dir)
        print(target_dir)
        if (self.home_dir not in target_dir) or (target_dir.index(self.home_dir) != 0):
            self.send_response(status_code=259)
            return
        self.current_dir = target_dir
        self.send_response(status_code=260)

    def send_response(self, status_code, data=None):
        response = {'status_code': status_code, 'status_message': STATUS_CODE[status_code]}
        if data is not None:
            response.update({'data': data})
        self.request.send(json.dumps(response).encode())

    def setup(self):
        print("connection setup!")
        print(self.client_address)

    def finish(self):
        print('just finish')
