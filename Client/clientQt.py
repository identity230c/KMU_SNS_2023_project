import sys
from socket import *
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import client
from QWorkers.ClientWorker import ClientWorker
from QWorkers.RecvSendWorker import RecvWorker, SendWorker


class ClientApp(QWidget):

    def __init__(self):
        super().__init__()
        self.client = client.Client()
        self.initUI()
        self.initThread()

    def initUI(self):
        # title and size
        self.setWindowTitle('Client')
        self.setGeometry(300, 300, 300, 200)

        mainBox = QVBoxLayout()

        # sock
        sockHbox = QHBoxLayout()
        sockHbox.addStretch(3)
        self.sockBtn = QPushButton('socket()', self)
        self.sockBtn.clicked.connect(self.socket)
        sockHbox.addWidget(self.sockBtn)
        mainBox.addLayout(sockHbox)

        connectHbox = QHBoxLayout()
        # ip input
        self.ip = QLineEdit(self)
        connectHbox.addWidget(self.ip)
        # port input
        self.port = QLineEdit(self)
        connectHbox.addWidget(self.port)

        # connect
        self.connectBtn = QPushButton('connect()', self)
        connectHbox.addWidget(self.connectBtn)
        mainBox.addLayout(connectHbox)

        sendHBox = QHBoxLayout()
        # send message
        self.sendBtn = QPushButton('send', self)
        sendHBox.addWidget(self.sendBtn)

        # text input
        self.chatInput = QLineEdit(self)
        sendHBox.addWidget(self.chatInput)

        dnsHBox = QHBoxLayout()
        # gethostbyname
        self.gethostbynameBtn = QPushButton('gethostbyname', self)
        dnsHBox.addWidget(self.gethostbynameBtn)

        # getnamebyhost
        self.getnamebyhostBtn = QPushButton('getnamebyhost', self)
        dnsHBox.addWidget(self.getnamebyhostBtn)

        mainBox.addLayout(sendHBox)
        mainBox.addLayout(dnsHBox)


        # log text
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        mainBox.addWidget(self.log)

        self.setLayout(mainBox)
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

        self.gethostbynameBtn.clicked.connect(self.gethostbyname)
        self.getnamebyhostBtn.clicked.connect(self.getnamebyhost)

    @pyqtSlot(bool)
    def socket(self, isSuccess):
        try:
            if isSuccess:
                self.setText("[SystemInfo]setting socket")
        except Exception as error:
            print(error)

    def beforeConnect(self):
        try:
            ip = self.ip.text()
            port = int(self.port.text())
            self.worker.before_connect_signal.emit(ip, port)

            ipv4_binary_address = inet_pton(AF_INET, ip)
            self.setText(f"pton({ip}) = {hex(int.from_bytes(ipv4_binary_address, sys.byteorder))}")
        except Exception as error:
            print(error)

    @pyqtSlot(bool)
    def afterConnect(self, isSuccess):
        try:
            if isSuccess:
                self.setText("[SystemInfo]connect suceess")

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

        except Exception as error:
            print(error)

    def beforeSend(self):
        self.send_worker.before_send_signal.emit(self.chatInput.text())

    @pyqtSlot(bool, str)
    def afterSend(self,isSuccess, data):
        if isSuccess:
            self.setText("[Client]"+data)

    @pyqtSlot(str)
    def recv(self, data):
        self.setText("[Server]"+data)

    @pyqtSlot(bool)
    def getnamebyhost(self):
        ip_address = self.chatInput.text()
        try:
            host_name, _ = getnameinfo((ip_address, 0), NI_NAMEREQD)
            self.setText(f"The host name for IP address {ip_address} is: {host_name}")
        except error as e:
            self.setText(f"Unable to get host name for {ip_address}. Error: {e}")

    @pyqtSlot(bool)
    def gethostbyname(self):
        domain = self.chatInput.text()
        try:
            ip_address = gethostbyname(domain)
            self.setText(f"The IP address of {domain} is: {ip_address}")
        except error as e:
            self.setText(f"Unable to get IP address for {domain}. Error: {e}")

    def setText(self, newTxt):
        try:
            txt = self.log.toPlainText()
            self.log.setText(txt + newTxt +"\n")
        except Exception as e:
            print("에러발생", e)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = ClientApp()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
