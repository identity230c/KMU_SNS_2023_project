from socket import * 

class Client:
  def socket(self):
    # Client-socket
    self.socket = socket(AF_INET, SOCK_STREAM)
  
  def connect(self, ip, port):
    # Client-connect
    self.socket.connect((ip, port))
    
  def send(self, msg):
    # Client-Send
    code = msg.encode('utf-8')
    self.socket.send(code)
    
  def recv(self):
    # Client-Recv 
    code = self.socket.recv(65536) # MaxLength
    msg = code.decode('utf-8')
    return msg
  
if __name__ == "__main__":
  server = Client()
  server.socket()
  server.connect("127.0.0.1", 8080)
  while(True):
    server.send(input())
    print(server.recv())
    