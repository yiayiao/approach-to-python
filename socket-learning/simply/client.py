import socket

client = socket.socket(family=socket.AF_INET)
client.connect(('localhost', 6971))

while True:
    data = input("please input >>")
    if len(data) == 0:
        continue
    client.send(data.encode('utf-8'))
    data = client.recv(1024)
    print(data.decode('utf-8'))

client.close()