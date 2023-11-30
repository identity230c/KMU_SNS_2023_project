import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QTextEdit, QDialog, QLabel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from QWorkers.ClientWorker import ClientWorker
from QWorkers.RecvSendWorker import RecvWorker, SendWorker
from Server import server
from Server.server import RecvSendSocket


class ServerToClient(QWidget):
    def __init__(self, socket):
        super().__init__()
        self.initUI()
        self.setSocket(socket)

    def initUI(self):
        # title and size
        self.setWindowTitle('FromServerToClient')
        self.setGeometry(300, 300, 300, 200)

        mainBox = QVBoxLayout()

        headBox = QVBoxLayout()
        headheadBox = QHBoxLayout()
        headheadBox.addWidget(QLabel("socket"))
        headheadBox.addWidget(QLabel("ip"))
        headheadBox.addWidget(QLabel("port"))

        serverInfoBox = QHBoxLayout()
        clientInfoBox = QHBoxLayout()

        self.serverIpLabel = QLabel()
        self.serverPortLabel = QLabel()
        serverInfoBox.addWidget(QLabel("Server : "))
        serverInfoBox.addWidget(self.serverIpLabel)
        serverInfoBox.addWidget(self.serverPortLabel)

        self.clientIpLabel = QLabel()
        self.clientPortLabel = QLabel()
        clientInfoBox.addWidget(QLabel("Client : "))
        clientInfoBox.addWidget(self.clientIpLabel)
        clientInfoBox.addWidget(self.clientPortLabel)

        headBox.addLayout(headheadBox)
        headBox.addLayout(serverInfoBox)
        headBox.addLayout(clientInfoBox)
        mainBox.addLayout(headBox)

        sendHBox = QHBoxLayout()
        # send message
        self.sendBtn = QPushButton('send', self)
        sendHBox.addWidget(self.sendBtn)

        # text input
        self.chatInput = QLineEdit(self)
        sendHBox.addWidget(self.chatInput)
        mainBox.addLayout(sendHBox)

        # log text
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        mainBox.addWidget(self.log)

        self.setLayout(mainBox)
        # show
        self.show()

    def beforeSend(self):
        self.send_worker.before_send_signal.emit(self.chatInput.text())

    @pyqtSlot(bool, str)
    def afterSend(self,isSuccess, data):
        if isSuccess:
            self.setText("[Server]"+data)

    @pyqtSlot(str)
    def recv(self, data):
        self.setText("[Client]"+data)

    def setText(self, newTxt):
        txt = self.log.toPlainText()
        self.log.setText(txt + newTxt +"\n")

    def setSocket(self, socket):
        # recv 연결하기
        self.recvSendSocket = RecvSendSocket(socket)
        self.recv_worker = RecvWorker(self.recvSendSocket)
        self.recvThread = QThread()
        self.recv_worker.moveToThread(self.recvThread)
        self.recvThread.start()

        self.recv_worker.after_recv_signal.connect(self.recv)
        self.recv_worker.before_recv_signal.emit()

        # send 연결하기
        self.send_worker = SendWorker(self.recvSendSocket)
        self.sendThread = QThread()
        self.send_worker.moveToThread(self.sendThread)
        self.sendThread.start()
        self.send_worker.after_send_signal.connect(self.afterSend)
        self.sendBtn.clicked.connect(self.beforeSend)

        cIp, cPort = socket.getpeername()
        sIp, sPort = socket.getsockname()
        self.clientIpLabel.setText(cIp)
        self.clientPortLabel.setText(str(cPort))
        self.serverIpLabel.setText(sIp)
        self.serverPortLabel.setText(str(sPort))

        self.recv_worker.disconnect_signal.connect(self.disconnectSocket)

    @pyqtSlot()
    def disconnectSocket(self):
        self.recvThread.quit()
        self.sendThread.quit()
        self.close()

    def closeEvent(self, QCloseEvent):
        self.recvSendSocket.socket.close()
        self.recvThread.quit()
        self.sendThread.quit()

        self.close()
