import sys
from socket import *
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import client
from QWorkers.ClientWorker import ClientWorker
from QWorkers.RecvSendWorker import RecvWorker, SendWorker
from utils.ipconifg import executeIpConfig

class ClientApp(QWidget):

    def __init__(self):
        super().__init__()
        self.client = client.Client()
        self.serverTitle = "Server"
        self.clientTitle = "Client"
        self.initUI()
        self.initThread()

    def initUI(self):
        # title and size
        self.setWindowTitle('Client')
        self.setGeometry(600, 300, 600, 400)

        mainBox = QVBoxLayout()

        # sock
        sockHbox = QHBoxLayout()
        #sockHbox.addStretch(3)
        sockHbox.addStretch(1)
        sockHbox.addWidget(QLabel("물리적 주소 : "))
        sockHbox.addWidget(QLabel(executeIpConfig()))
        sockHbox.addStretch(1)
        self.sockBtn = QPushButton('socket()', self)
        self.sockBtn.clicked.connect(self.socket)
        sockHbox.addWidget(self.sockBtn)
        mainBox.addLayout(sockHbox)

        connectHbox = QHBoxLayout()
        # ip input
        connectHbox.addWidget(QLabel("IP:"))
        self.ip = QLineEdit(self)
        connectHbox.addWidget(self.ip)
        # port input
        connectHbox.addWidget(QLabel("port:"))
        self.port = QLineEdit(self)
        connectHbox.addWidget(self.port)

        # connect
        self.connectBtn = QPushButton('connect()', self)
        connectHbox.addWidget(self.connectBtn)
        mainBox.addLayout(connectHbox)

        # send message
        sendHBox = QHBoxLayout()
        self.chatInput = QLineEdit(self)
        self.chatInput.returnPressed.connect(self.on_enter_pressed)
        sendHBox.addWidget(self.chatInput)
        self.sendBtn = QPushButton('send', self)
        sendHBox.addWidget(self.sendBtn)
        mainBox.addLayout(sendHBox)

        # connectInfo
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

        # log text
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        mainBox.addWidget(self.log)

        self.setLayout(mainBox)

        # default value
        self.ip.setText("127.0.0.1")
        self.port.setText("8080")

        # show
        self.show()

    def initThread(self):
        self.worker = ClientWorker(self.client)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.workerThread.start()

        # 각 버튼과 연결
        # socket()
        self.sockBtn.clicked.connect(self.worker.socket)
        self.worker.sock_signal.connect(self.socket)

        # connect()
        self.connectBtn.clicked.connect(self.beforeConnect)
        self.worker.before_connect_signal.connect(self.worker.connect)
        self.worker.after_connect_signal.connect(self.afterConnect)

    @pyqtSlot(bool)
    def socket(self, isSuccess):
        try:
            if isSuccess:
                self.setText("[SystemInfo] setting socket")
        except Exception as error:
            print(error)

    def beforeConnect(self):
        try:
            ip = self.ip.text()
            port = int(self.port.text())
            self.worker.before_connect_signal.emit(ip, port)

            ipv4_binary_address = inet_pton(AF_INET, ip)
            self.setText(f"[SystemInfo] pton({ip}) = {hex(int.from_bytes(ipv4_binary_address, sys.byteorder))}")
        except Exception as error:
            print(error)

    @pyqtSlot(bool)
    def afterConnect(self, isSuccess):
        try:
            if isSuccess:
                self.setText("[SystemInfo] connect suceess")

                self.workerThread.quit()
                # recv 연결하기
                self.recv_worker = RecvWorker(self.client)
                self.recvThread = QThread()
                self.recv_worker.moveToThread(self.recvThread)
                self.recvThread.start()

                self.recv_worker.after_recv_signal.connect(self.recv)
                self.recv_worker.before_recv_signal.emit()

                # send 연결하기
                self.send_worker = SendWorker(self.client)
                self.sendThread = QThread()
                self.send_worker.moveToThread(self.sendThread)
                self.sendThread.start()
                self.send_worker.after_send_signal.connect(self.afterSend)
                self.sendBtn.clicked.connect(self.beforeSend)

                self.recv_worker.disconnect_signal.connect(self.disconnectSocket)

                ip,port = self.client.socket.getpeername()
                self.serverTitle = f"[Server-{ip}:{port}] "
                self.serverIpLabel.setText(ip)
                self.serverPortLabel.setText(str(port))
                ip,port = self.client.socket.getsockname()
                self.clientTitle = f"[Client-{ip}:{port}] "
                self.clientIpLabel.setText(ip)
                self.clientPortLabel.setText(str(port))



        except Exception as error:
            print(error)

    def beforeSend(self):
        self.send_worker.before_send_signal.emit(self.chatInput.text())

    @pyqtSlot(bool, str)
    def afterSend(self,isSuccess, data):
        if isSuccess:
            self.setText(self.clientTitle+data)

    @pyqtSlot(str)
    def recv(self, data):
        self.setText(self.serverTitle+data)

    def setText(self, newTxt):
        try:
            txt = self.log.toPlainText()
            self.log.setText(txt + newTxt +"\n")
        except Exception as e:
            print("에러발생", e)

    @pyqtSlot()
    def disconnectSocket(self):
        self.recvThread.quit()
        self.sendThread.quit()
        self.setText("서버와의 연결이 끊어졌습니다")

    def on_enter_pressed(self):
        text = self.chatInput.text()
        if text:
            self.beforeSend()
            self.chatInput.setText("")
        


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = ClientApp()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
