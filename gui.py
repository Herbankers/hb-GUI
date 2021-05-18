from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtCore import *
import getopt
import sys

from hbp import *

hbp = None

# although both the server and HBP support PINs of up to 12 numbers, we've decided to hardcode 4 in the client for now
# for convenience sake
PIN_LENGTH = 4

class MainWindow(QtWidgets.QMainWindow):
    CARD_PAGE = 0
    LOGIN_PAGE = 1
    MAIN_PAGE = 2
    WITHDRAW_PAGE = 3
    DONATE_PAGE = 4
    BALANCE_PAGE = 5
    RESULT_PAGE = 6

    card_id = ''
    iban = ''
    keybuf = []
    keyindex = 0

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)
        self.stack.setCurrentIndex(self.CARD_PAGE)

        # Main page
        self.withdraw.clicked.connect(self.doWithdrawPage)
        self.donate.clicked.connect(self.doDonatePage)
        self.balance.clicked.connect(self.doBalancePage)
        self.quickWithdrawal.clicked.connect(self.doQuickWithdrawal)
        self.logout.clicked.connect(self.doLogout)

        # Withdraw page
        self.withdrawAbort.clicked.connect(self.doAbort)
        self.withdrawManual.clicked.connect(self.doWithdrawManualPage)
        self.withdrawAccept.clicked.connect(self.doWithdrawal)

        # Donate page
        self.donateAbort.clicked.connect(self.doAbort)
        self.donateAccept.clicked.connect(self.doDonation)

        # Balance page
        self.balanceAccept.clicked.connect(self.doAbort)

    # resolve the key event code to a character (only numbers are accepted)
    def getKeyFromEvent(self, key):
        if key == Qt.Key.Key_0:
            return '0'
        elif key == Qt.Key.Key_1:
            return '1'
        elif key == Qt.Key.Key_2:
            return '2'
        elif key == Qt.Key.Key_3:
            return '3'
        elif key == Qt.Key.Key_4:
            return '4'
        elif key == Qt.Key.Key_5:
            return '5'
        elif key == Qt.Key.Key_6:
            return '6'
        elif key == Qt.Key.Key_7:
            return '7'
        elif key == Qt.Key.Key_8:
            return '8'
        elif key == Qt.Key.Key_9:
            return '9'
        else:
            return None

    # keyboard input handling (not keypad!)
    def keyPressEvent(self, event):
        if self.stack.currentIndex() == self.CARD_PAGE:
            # TODO build in card reader support and remove this
            self.card_id = 'EBA8001B'
            self.iban = 'NL35HERB2932749274'

            self.stack.setCurrentIndex(self.LOGIN_PAGE)
        elif self.stack.currentIndex() == self.LOGIN_PAGE:
            # store the keyboard key in the keybuffer
            key = self.getKeyFromEvent(event.key())
            if key == None:
                return
            self.keybuf.append(key)

            # update the pin dots on the display
            if self.keyindex == 0:
                self.pin.setText('•   ')
            elif self.keyindex == 1:
                self.pin.setText('••  ')
            elif self.keyindex == 2:
                self.pin.setText('••• ')
            elif self.keyindex == 3:
                self.pin.setText('••••')

            self.keyindex += 1
            if self.keyindex < PIN_LENGTH:
                return

            # short delay here to show that the 4th character has been entered
            self.timer = QTimer()
            self.timer.timeout.connect(self.doLogin)
            self.timer.setSingleShot(True)
            self.timer.start(500)
        elif self.stack.currentIndex() in (self.WITHDRAW_PAGE, self.DONATE_PAGE):
            # store the keyboard key in the keybuffer
            key = self.getKeyFromEvent(event.key())
            if key == None:
                return

            if self.keyindex > 2:
                return
            self.keybuf[self.keyindex] = key
            self.keyindex += 1

            # write the updated amount to the display
            self.withdrawAmount.setText(''.join(self.keybuf) + ' EUR')
            self.donateAmount.setText(''.join(self.keybuf) + ' EUR')

    @QtCore.pyqtSlot()
    def doLogin(self):
        # TODO run on separate thread
        reply = hbp.login(self.card_id, self.iban, ''.join(self.keybuf))

        self.pin.setText('')
        self.keybuf = []
        self.keyindex = 0

        if reply == hbp.HBP_LOGIN_GRANTED:
            self.stack.setCurrentIndex(self.MAIN_PAGE)

            name = hbp.info()
            if type(name) is list:
                self.name.setText(self.tr('Welkom') + f' {name[0]} {name[1]}!')
            else:
                self.name.setText(self.tr('Welkom!'))
        elif reply == hbp.HBP_LOGIN_DENIED:
            # TODO show user
            pass
        elif reply == hbp.HBP_LOGIN_BLOCKED:
            # TODO show user
            self.stack.setCurrentIndex(self.CARD_PAGE)
        else:
            print(reply)

    @QtCore.pyqtSlot()
    def doAbort(self):
        self.stack.setCurrentIndex(self.MAIN_PAGE)

    @QtCore.pyqtSlot()
    def onFinish(self):
        self.resultText.setText(self.tr('Nog een fijne dag!'))

        # automatically logout after 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.doLogout)
        self.timer.setSingleShot(True)
        self.timer.start(2000)

    #
    # Main page
    #
    @QtCore.pyqtSlot()
    def doWithdrawPage(self):
        self.stack.setCurrentIndex(self.WITHDRAW_PAGE)

        self.keybuf = ['_'] * 3
        self.keyindex = 0
        self.withdrawAmount.setText(''.join(self.keybuf) + ' EUR')

    @QtCore.pyqtSlot()
    def doDonatePage(self):
        self.stack.setCurrentIndex(self.DONATE_PAGE)

        self.keybuf = ['_'] * 3
        self.keyindex = 0
        self.donateAmount.setText(''.join(self.keybuf) + ' EUR')

    @QtCore.pyqtSlot()
    def doBalancePage(self):
        self.balanceAmount.setText(hbp.balance().replace('.', ',') + ' EUR')
        self.stack.setCurrentIndex(self.BALANCE_PAGE)

    @QtCore.pyqtSlot()
    def doQuickWithdrawal(self):
        self.keybuf = '70'
        self.doWithdrawal()

    @QtCore.pyqtSlot()
    def doLogout(self):
        # we can check the reply, but this is really not needed, as it basically always succeeds
        hbp.logout()

        # we should clear all modified variables and labels here for security
        self.keybuf = []
        self.keyindex = 0
        self.withdrawAmount.setText('')
        self.donateAmount.setText('')
        self.balanceAmount.setText('')

        self.stack.setCurrentIndex(self.CARD_PAGE)

    #
    # Withdraw page
    #
    @QtCore.pyqtSlot()
    def doWithdrawal(self):
        try:
            amount = int(''.join(self.keybuf).replace('_', '')) * 100
        except ValueError:
            # nothing has been entered yet
            return

        # start processing
        self.stack.setCurrentIndex(self.RESULT_PAGE)
        self.resultText.setText(self.tr('Een moment geduld...'))
        reply = hbp.transfer('', amount);

        if reply in (hbp.HBP_TRANSFER_SUCCESS, hbp.HBP_TRANSFER_PROCESSING):
            # TODO operate money dispenser here (on a separate thread ofc) instead of this delay
            self.timer = QTimer()
            self.timer.timeout.connect(self.onFinish)
            self.timer.setSingleShot(True)
            self.timer.start(3000)
        elif reply == hbp.HBP_TRANSFER_INSUFFICIENT_FUNDS:
            self.resultText.setText(self.tr('Uw saldo is ontoereikend'))

            self.timer = QTimer()
            self.timer.timeout.connect(self.doAbort)
            self.timer.setSingleShot(True)
            self.timer.start(3000)
        else:
            print(reply)

            # TODO handle session timeout
            self.resultText.setText(self.tr('Een interne fout is opgetreden'))

            self.timer = QTimer()
            self.timer.timeout.connect(self.doAbort)
            self.timer.setSingleShot(True)
            self.timer.start(3000)

    @QtCore.pyqtSlot()
    def doWithdrawManualPage(self):
        # TODO implement
        self.stack.setCurrentIndex(self.RESULT_PAGE)
        self.resultText.setText('Nog niet geïmplementeerd')
        self.timer = QTimer()
        self.timer.timeout.connect(self.doAbort)
        self.timer.setSingleShot(True)
        self.timer.start(2000)

    #
    # Donate page
    #
    @QtCore.pyqtSlot()
    def doDonation(self):
        # TODO implement
        self.stack.setCurrentIndex(self.RESULT_PAGE)
        self.resultText.setText('Nog niet geïmplementeerd')
        self.timer = QTimer()
        self.timer.timeout.connect(self.doAbort)
        self.timer.setSingleShot(True)
        self.timer.start(2000)

# print usage information
def help():
    print('usage: gui.py [-h] [-s | --serial-port=] [-h | --host=] [-p | --port=]')

def main(argv):
    global hbp
    #  global arduino

    # parse command line options
    try:
        opts, args = getopt.getopt(argv, '?s:h:p:', [ 'serial-port=', 'host=', 'port=' ])
    except getopt.GetoptError:
        help()
        sys.exit(1)

    # empty input_souce means that we'll use the keyboard as input
    #  serial_port = ''

    host = '145.24.222.242'
    port = 8420

    for opt, arg in opts:
        if opt == '-?':
            help()
            sys.exit(0)
        elif opt in ('-s', '--serial-port'):
            serial_port = arg
        elif opt in ('-h', '--host'):
            host = arg
        elif opt in ('-p', '--port'):
            port = arg

    print('Copyright (C) 2021 INGrid GUI v1.0')
    try:
        hbp = HBP(host, port)
    except ConnectionRefusedError:
        print(f'Failed to connect to {host}:{port}')
        exit(1)
    print(f'Connected to Herbank Server @ {host}:{port}')

    #  if serial_port != '':
        #  arduino = serial.Serial(serial_port, 9600, timeout=.1)

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main(sys.argv[1:])
