import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QTextEdit, QDialog
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from QWorkers.ClientWorker import ClientWorker
from QWorkers.RecvSendWorker import RecvWorker, SendWorker

class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # title and size
        self.setWindowTitle('sub')
        self.setGeometry(300, 300, 300, 200)

        mainBox = QVBoxLayout()

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
        print("why?")
        self.show()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # title and size
        self.setWindowTitle('main')
        self.setGeometry(300, 300, 300, 200)

        mainBox = QVBoxLayout()

        # sock
        sockHbox = QHBoxLayout()
        sockHbox.addStretch(3)
        self.sockBtn = QPushButton('socket()', self)
        self.sockBtn.clicked.connect(self.open)
        sockHbox.addWidget(self.sockBtn)
        mainBox.addLayout(sockHbox)


        self.setLayout(mainBox)
        # show
        self.show()

    def open(self):
        self.newWindow = SubWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_dialog = MainWindow()
    app.exec_()

