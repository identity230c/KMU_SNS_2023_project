from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class ClientWorker(QObject):
    sock_signal = pyqtSignal(bool)

    def __init__(self, clientSock, parent=None):
        super(ClientWorker, self).__init__()
        self.clientSock = clientSock

    def socket(self):
        self.clientSock.socket()
        self.sock_signal.emit(True)

    before_connect_signal = pyqtSignal(str, int)
    after_connect_signal = pyqtSignal(bool)

    @pyqtSlot(str, int)
    def connect(self, ip, port):
        self.clientSock.connect(ip, port)
        self.after_connect_signal.emit(True)
