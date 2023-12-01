from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class RecvWorker(QObject):
    before_recv_signal = pyqtSignal()
    after_recv_signal = pyqtSignal(str)
    disconnect_signal = pyqtSignal()

    def __init__(self, socket):
        super(RecvWorker, self).__init__()
        self.socket = socket
        self.before_recv_signal.connect(self.recv)

    @pyqtSlot()
    def recv(self):
        while True:
            try:
                data = self.socket.recv()
                self.after_recv_signal.emit(data)
            except Exception as e:
                print("에러발생", e)
                self.disconnect_signal.emit()
                break


class SendWorker(QObject):
    before_send_signal = pyqtSignal(str)
    after_send_signal = pyqtSignal(bool, str)

    def __init__(self, socket):
        super(SendWorker, self).__init__()
        self.socket = socket
        self.before_send_signal.connect(self.send)

    @pyqtSlot(str)
    def send(self, data):
        self.socket.send(data)
        self.after_send_signal.emit(True, data)
