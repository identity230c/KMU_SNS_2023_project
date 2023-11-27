import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit
import server

class ServerApp(QWidget):

    def __init__(self):
        super().__init__()
        self.server = server.Server()
        self.initUI()

    def initUI(self):
        # title and size
        self.setWindowTitle('Server')
        self.setGeometry(300, 300, 300, 200)

        mainBox = QVBoxLayout()

        # sock
        sockHbox = QHBoxLayout()
        sockHbox.addStretch(3)
        self.sockBtn = QPushButton('socket()', self)
        self.sockBtn.clicked.connect(self.socket)
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
        self.bindBtn.clicked.connect(self.bind)
        bindHbox.addWidget(self.bindBtn)
        mainBox.addLayout(bindHbox)

        listenAccessHBox = QHBoxLayout()
        # listen message
        self.listenBtn = QPushButton('listen', self)
        self.listenBtn.clicked.connect(self.listen)
        listenAccessHBox.addWidget(self.listenBtn)
        # access message
        self.accessBtn = QPushButton('access', self)
        self.accessBtn.clicked.connect(self.access)
        listenAccessHBox.addWidget(self.accessBtn)
        mainBox.addLayout(listenAccessHBox)


        sendHBox = QHBoxLayout()
        # send message
        self.sendBtn = QPushButton('send', self)
        self.sendBtn.clicked.connect(self.send)
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

    def socket(self):
        try:
            self.server.socket()
            self.setText("setting socket")
        except Exception as error:
            print(error)

    def bind(self):
        try:
            ip = self.ip.text()
            port = int(self.port.text())
            self.server.bind(ip, port)
            self.setText("bind complete")
        except Exception as error:
            print(error)

    def listen(self):
        try:
            self.server.listen()
            self.setText("listening now")
            self.access()
        except Exception as e:
            print(e)

    def access(self):
        addr = self.server.accept()
        self.setText(f"client:{addr} access")
        self.recv()

    def send(self):
        self.server.send(self.chatInput.text())
        self.recv()

    def recv(self):
        msg = self.server.recv()
        self.setText(msg)
        self.send()

    def setText(self, newTxt):
        txt = self.log.toPlainText()
        self.log.setText(txt + newTxt +"\n")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerApp()
    sys.exit(app.exec_())
