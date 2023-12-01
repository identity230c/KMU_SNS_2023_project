from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from socket import *

class ServerWorker(QObject):
    sock_signal = pyqtSignal(bool)

    def __init__(self, serverSock, parent=None):
        super(ServerWorker, self).__init__()
        self.serverSock = serverSock
        self.before_bind_signal.connect(self.bind)

    def socket(self):
        self.serverSock.socket()
        self.sock_signal.emit(True)

    before_bind_signal = pyqtSignal(str, int)
    after_bind_signal = pyqtSignal(bool)

    @pyqtSlot(str, int)
    def bind(self, ip, port):
        self.serverSock.bind(ip, port)
        self.after_bind_signal.emit(True)

    listen_signal = pyqtSignal(bool)
    def listen(self):
        try:
            self.serverSock.listen()
            self.listen_signal.emit(True)
            self.accept()
        except Exception as e:
            self.listen_signal.emit(False)
            print(e)

    accept_signal = pyqtSignal(tuple)

    def accept(self):
        try:
            while True:
                addr = self.serverSock.accept()
                print(addr)
                self.accept_signal.emit(addr)
        except Exception as e:
            print(e)
