import sys
from PyQt5.QtCore import QReadWriteLock, QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class DatabaseWithLock:
    def __init__(self, database):
        self.qlock = QReadWriteLock()
        self.database = database

    def getKey(self, key):
        return self.database.getKey(key)

    def setKey(self, key, value):
        self.database.setKey(key,value)

class ReaderThread(QThread):
    afterSignal = pyqtSignal(str, str)
    def __init__(self, db, key, after_read):
        super(ReaderThread, self).__init__()
        self.db = db
        self.key = key
        self.afterSignal.connect(after_read)

    def run(self):
        self.db.qlock.lockForRead()
        getValue = self.db.getKey(self.key)
        self.db.qlock.unlock()
        self.afterSignal.emit(self.key, str(getValue))

class WriterThread(QThread):
    afterSignal = pyqtSignal(str,str)

    def __init__(self, db, key, value,after_write):
        try:
            super(WriterThread, self).__init__()

            self.db = db
            self.key = key
            self.value = value
            self.afterSignal.connect(after_write)
        except Exception as e:
            print("error in WriterThread", e)

    def run(self):
        self.db.qlock.lockForWrite()
        self.db.setKey(self.key, self.value)
        self.db.qlock.unlock()

        self.afterSignal.emit(self.key, self.value)