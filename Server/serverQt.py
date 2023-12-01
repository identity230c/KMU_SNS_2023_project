import sys
from socket import * 

from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit,QLabel
import server
from QWorkers.RecvSendWorker import RecvWorker, SendWorker
from QWorkers.ServerWorker import ServerWorker
from Server.ServerToCLientQt import ServerToClient
from ServerNetstat import executeNetstat

class ServerApp(QWidget):

    def __init__(self):
        super().__init__()
        self.s2cList = []
        self.server = server.Server()
        self.initUI()
        self.initThread()

    def initUI(self):
        # title and size
        self.setWindowTitle('Server')
        self.setGeometry(900, 300, 600, 400)

        mainBox = QVBoxLayout()

        # sock
        sockHbox = QHBoxLayout()
        sockHbox.addStretch(3)
        self.sockBtn = QPushButton('socket()', self)
        sockHbox.addWidget(self.sockBtn)
        mainBox.addLayout(sockHbox)

        bindHbox = QHBoxLayout()
        # ip input
        self.ip = QLineEdit(self)
        bindHbox.addWidget(self.ip)
        # port input
        self.port = QLineEdit(self)
        bindHbox.addWidget(self.port)

        # bind
        self.bindBtn = QPushButton('bind()', self)
        bindHbox.addWidget(self.bindBtn)
        mainBox.addLayout(bindHbox)

        listenAccessHBox = QHBoxLayout()
        # listen message
        self.listenBtn = QPushButton('listen() and accept()', self)
        listenAccessHBox.addWidget(self.listenBtn)
        # access message
        self.netstatBtn = QPushButton('netStat()', self)
        self.netstatBtn.clicked.connect(self.viewNetStat)
        listenAccessHBox.addWidget(self.netstatBtn)
        mainBox.addLayout(listenAccessHBox)

        logNetStatBox = QHBoxLayout()

        netStatBox = QVBoxLayout()
        netStatTitle= QLabel("NetStatInfo")
        self.netStatText = QTextEdit()
        self.netStatText.setReadOnly(True)
        netStatBox.addWidget(netStatTitle)
        netStatBox.addWidget(self.netStatText)

        # log text
        logBox = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        logBox.addWidget(QLabel("Log"))
        logBox.addWidget(self.log)

        logNetStatBox.addLayout(netStatBox)
        logNetStatBox.addLayout(logBox)
        mainBox.addLayout(logNetStatBox)
        self.setLayout(mainBox)
        # show
        self.show()

    def viewNetStat(self):
        try:
            ret = executeNetstat(int(self.port.text()))
            self.netStatText.setText(ret)
        except Exception as e:
            print("view netstat에서 에러발생", e)

    def initThread(self):
        self.listenWorker = ServerWorker(self.server)
        self.listenThread = QThread()
        self.listenWorker.moveToThread(self.listenThread)
        self.listenThread.start()

        # 각 버튼과 연결
        # socket()
        self.sockBtn.clicked.connect(self.listenWorker.socket)
        self.listenWorker.sock_signal.connect(self.socket)

        # bind()
        self.bindBtn.clicked.connect(self.bind)

        # listen
        self.listenBtn.clicked.connect(self.listenWorker.listen)
        self.listenWorker.listen_signal.connect(self.afterListen)

        self.netstatBtn.clicked.connect(self.listenWorker.accept)
        self.listenWorker.accept_signal.connect(self.accept)

    def socket(self):
        try:
            self.setText("[SystemInfo]setting socket")
        except Exception as error:
            print(error)

    def bind(self):
        try:
            ip = self.ip.text()
            port = int(self.port.text())
            # bind는 멀티 쓰레드로 가면 프로그램이 꺼진다 -> 왜?
            self.server.bind(ip,port)
            # self.listenWorker.before_bind_signal.emit(ip, port)
            self.setText("[SystemInfo]bind")

            ipv4_binary_address = inet_pton(AF_INET, ip)
            self.setText(f"IPv4 Address: {int.from_bytes(ipv4_binary_address, sys.byteorder)} {ipv4_binary_address}")
        except Exception as error:
            print(error)

    @pyqtSlot(bool)
    def afterListen(self, isSuccess):
        if isSuccess:
            self.setText("[SystemInfo]open listening port and execute accpet()")
            self.viewNetStat()
        else:
            self.setText("[SystemInfo]Listen fail")

    @pyqtSlot(tuple)
    def accept(self, addr):
        self.setText(f"[SystemInfo] client:{addr} access")

        # set send-recv worker
        try:
            self.s2cList.append(ServerToClient(self.server.clientSock))
            self.viewNetStat()
        except Exception as e:
            print(e)

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerApp()
    sys.exit(app.exec_())
