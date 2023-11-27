from socket import *

class Server:
  
  def socket(self):
    # Server-socket
    self.listenSock = socket(AF_INET, SOCK_STREAM)
    
  def bind(self, ip, port):
    # Server-bind
    self.listenSock.bind((ip,port))

  def listen(self):
    # Server-listen
    self.listenSock.listen(1)
    
  def accept(self):
    # client sock and addr
    self.clientSock, self.addr = self.listenSock.accept()
    return self.addr
  
  def send(self, msg):
    # Server-Send
    code = msg.encode('utf-8')
    self.clientSock.send(code)
    
  def recv(self):
    # Server-Recv 
    code = self.clientSock.recv(65536) # MaxLength
    msg = code.decode('utf-8')
    return msg
    
if __name__ == "__main__":
  server = Server()
  server.socket()
  server.bind("127.0.0.1", 8080)
  server.listen()
  server.accept()
  print("연결완료", server.addr)
  while(True):
    print(server.recv())
    server.send(input())