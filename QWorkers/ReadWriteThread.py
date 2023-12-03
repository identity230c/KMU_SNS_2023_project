import sys
from PyQt5.QtCore import QReadWriteLock, QThread, Qt, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import datetime
import time

class DatabaseWithLock:
    def __init__(self, database, log):
        self.qlock = QReadWriteLock()
        self.database = database
        self.log = log

    def getKey(self, key):
        return self.database.getKey(key)

    def setKey(self, key, value):
        self.database.setKey(key,value)

    def writeLockLog(self, log):
        txt = self.log.toPlainText()
        current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.log.setText(txt + f"[{current_time}]{log}\n")

    def lockForRead(self):
        self.qlock.lockForRead()

    def lockForWrite(self):
        self.qlock.lockForWrite()

    def unlock(self):
        self.qlock.unlock()

class ReadWorker(QObject):
    before_read_signal = pyqtSignal(str)
    after_read_signal = pyqtSignal(str, str)
    log_signal = pyqtSignal(str)

    def __init__(self, db, client):
        super(ReadWorker, self).__init__()
        self.db = db
        self.before_read_signal.connect(self.read)
        self.clientTitle = client

    @pyqtSlot(str)
    def read(self, key):
        self.log_signal.emit(f"{self.clientTitle} : Read-Wait")
        self.db.lockForRead()
        self.log_signal.emit(f"{self.clientTitle} : Read-Lock")
        time.sleep(1.5)
        value = self.db.getKey(key)
        self.log_signal.emit(f"{self.clientTitle} : Read-Work")
        time.sleep(1.5)
        self.log_signal.emit(f"{self.clientTitle} : Read-UnLock")
        self.db.unlock()
        self.after_read_signal.emit(key, value)

class WriteWorker(QObject):
    before_write_signal = pyqtSignal(str, str)
    after_write_signal = pyqtSignal(str, str)
    log_signal = pyqtSignal(str)

    def __init__(self, db, client):
        super(WriteWorker, self).__init__()
        self.db = db
        self.before_write_signal.connect(self.write)
        self.clientTitle = client

    @pyqtSlot(str, str)
    def write(self, key, value):
        self.log_signal.emit(f"{self.clientTitle} : Write-Wait")
        self.db.lockForWrite()
        self.log_signal.emit(f"{self.clientTitle} : Write-Lock")
        time.sleep(1.5)
        self.db.setKey(key,value)
        self.log_signal.emit(f"{self.clientTitle} : Write-Work")
        time.sleep(1.5)
        self.log_signal.emit(f"{self.clientTitle} : Write-UnLock")
        self.db.unlock()
        self.after_write_signal.emit(key, value)
