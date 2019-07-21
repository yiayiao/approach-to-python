import argparse
import socketserver

from core.ftp_handler import FtpHandler


class ArgvHandler(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--host", help="ftp server host address", default='0.0.0.0')
        parser.add_argument("-p", "--port", help="ftp server port", default=9999)
        self.args = parser.parse_args()

    def start(self):
        print('---\033[32;1mStarting FTP server on %s:%s\033[0m----' % (self.args.host, self.args.port))
        server = socketserver.ThreadingTCPServer((self.args.host, self.args.port), FtpHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


