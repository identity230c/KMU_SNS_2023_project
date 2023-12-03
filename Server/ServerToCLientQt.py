import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QTextEdit, QDialog, QLabel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from QWorkers.ClientWorker import ClientWorker
from QWorkers.ReadWriteThread import ReaderThread, WriterThread
from QWorkers.RecvSendWorker import RecvWorker, SendWorker
from Server import server
from Server.server import RecvSendSocket
from socket import *
from DnsInfo import gethostbyaddr, gethostbyname
from Byteorder import convert_to_bytes

class ServerToClient(QWidget):
    def __init__(self, socket, db):
        super().__init__()
        self.initUI()
        self.setSocket(socket)
        self.sleep = 0
        self.db = db

    def initUI(self):
        # title and size
        self.setWindowTitle('FromServerToClient')
        self.setGeometry(300, 300, 600, 400)

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
        self.chatInput = QLineEdit(self)
        self.chatInput.returnPressed.connect(self.on_enter_pressed)
        sendHBox.addWidget(self.chatInput)
        self.sendBtn = QPushButton('send', self)
        sendHBox.addWidget(self.sendBtn)
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
            self.setText(f"{self.serverTitle} {data}")

    @pyqtSlot(str)
    def recv(self, data):
        try:
            ret = ""
            if len(data.split(" ")) >= 2:
                if len(data.split(" ")) == 2:
                    [method, attr] = data.split(" ")
                    if method == "gethostbyname":
                        ret += gethostbyname(attr)
                    if method == "gethostbyaddr":
                        ret += gethostbyaddr(attr)
                    if method == "big":
                        ret += " ".join(convert_to_bytes(attr, "big"))
                    if method == "little":
                        ret += " ".join(convert_to_bytes(attr, "little"))
                    if method == "get":
                        print("getValue")
                        readThread = ReaderThread(self.db, attr, self.recvGet, self.sleep)
                        readThread.run()
                    if method == "setsleep":
                        try:
                            self.sleep = int(attr)
                            ret += f"sleep in set to {attr}"
                        except:
                            self.setText("Please enter an integer as a parameter.")
                elif len(data.split(" ")) == 3:
                    [method, key, value] = data.split(" ")
                    if method == "set":
                        writeThread = WriterThread(self.db,key,value, self.recvSet, self.sleep)
                        writeThread.run()


            self.setText(f"{self.clientTitle} {data}")
            if ret:
                self.chatInput.setText(ret)
                self.beforeSend()
            self.chatInput.setText("")
        except Exception as e:
            print("error in serverToClient, recv",e)

    @pyqtSlot(str, str)
    def recvGet(self, getKey, getValue):
        self.chatInput.setText(f"GET - {getKey} : {getValue}")
        self.beforeSend()

    @pyqtSlot(str, str)
    def recvSet(self, setKey, setValue):
        self.chatInput.setText(f"SET - {setKey} : {setValue}")
        self.beforeSend()


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

        self.serverTitle = f"[Server-{sIp}:{sPort}]"
        self.clientTitle = f"[Client-{cIp}:{cPort}]"

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

    def on_enter_pressed(self):
        text = self.chatInput.text()
        if text:
            self.beforeSend()
            self.chatInput.setText("")