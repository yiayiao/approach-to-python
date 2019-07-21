# import socket
#
# server = socket.socket()
# server.bind(('localhost', 6971))
# server.listen(0)
#
# while True:
#     conn, addr = server.accept()
#     print(conn, addr)
#
#     while True:
#         data = conn.recv(1)
#         if len(data) == 0: #在Windows平台上，客户端断连会抛出异常
#             print('client is closed')
#             break
#         print('received data', data.decode('utf-8'))
#         conn.send(data.decode('utf-8').upper().encode('utf-8'))
#
#     conn.close()
# server.close()

import socketserver

class SimpleHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024)
            if len(data) == 0:
                print('client is closed')
                break
            print('received data', data.decode())
            self.request.send(data.decode().upper().encode())

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('localhost', 6971), SimpleHandler)
    server.serve_forever()
