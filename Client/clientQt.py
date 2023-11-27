import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QTextEdit
import client

class ClientApp(QWidget):

    def __init__(self):
        super().__init__()
        self.client = client.Client()
        self.initUI()

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
        self.connectBtn.clicked.connect(self.connect)
        connectHbox.addWidget(self.connectBtn)
        mainBox.addLayout(connectHbox)

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
            self.client.socket()
            self.setText("setting socket")
        except Exception as error:
            print(error)

    def connect(self):
        try:
            ip = self.ip.text()
            port = int(self.port.text())
            self.client.connect(ip, port)
            self.setText("connect complete")
        except Exception as error:
            print(error)

    def send(self):
        self.client.send(self.chatInput.text())
        self.recv()

    def recv(self):
        msg = self.client.recv()
        self.setText(msg)
        self.send()

    def setText(self, newTxt):
        txt = self.log.toPlainText()
        self.log.setText(txt + newTxt +"\n")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClientApp()
    sys.exit(app.exec_())
