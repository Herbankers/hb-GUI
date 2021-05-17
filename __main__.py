from PyQt6 import QtCore, QtWidgets, uic
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)

        # main page
        self.withdraw.clicked.connect(self.doWithdrawPage)
        self.donate.clicked.connect(self.doDonatePage)
        self.balance.clicked.connect(self.doBalancePage)
        self.quickWithdrawal.clicked.connect(self.doQuickWithdrawal)
        self.logout.clicked.connect(self.doLogout)

        # withdraw page
        self.withdrawAbort.clicked.connect(self.doAbort)
        self.withdrawAccept.clicked.connect(self.doWithdrawal)

        # donate page
        self.donateAbort.clicked.connect(self.doAbort)
        self.donateAccept.clicked.connect(self.doDonation)

        # balance page
        self.balanceAccept.clicked.connect(self.doAbort)

    @QtCore.pyqtSlot()
    def doWithdrawPage(self):
        self.stack.setCurrentIndex(3)

    @QtCore.pyqtSlot()
    def doDonatePage(self):
        self.stack.setCurrentIndex(4)

    @QtCore.pyqtSlot()
    def doBalancePage(self):
        self.stack.setCurrentIndex(5)
        pass

    @QtCore.pyqtSlot()
    def doQuickWithdrawal(self):
        # TODO
        pass

    @QtCore.pyqtSlot()
    def doLogout(self):
        # TODO perform logout

        self.stack.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def doAbort(self):
        self.stack.setCurrentIndex(2)

    @QtCore.pyqtSlot()
    def doWithdrawal(self):
        # TODO
        pass

    @QtCore.pyqtSlot()
    def doDonation(self):
        # TODO
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
