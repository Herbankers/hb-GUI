from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtCore import *
import functools
import getopt
import sys

from hbp import *
from ui.main import *

#
# TODO
# Client side countdown to automatically end session after hbp.HBP_TIMEOUT seconds
# Keypad control
#

app = None
hbp = None

# although both the server and HBP support PINs of up to 12 numbers, we've decided to hardcode 4 in the client for now
# for convenience sake
PIN_LENGTH = 4

class MainWindow(QtWidgets.QMainWindow):
    CARD_PAGE = 0
    LOGIN_PAGE = 1
    MAIN_PAGE = 2
    WITHDRAW_PAGE = 3
    WITHDRAW_MANUAL_PAGE = 4
    WITHDRAW_BILLS_PAGE = 5
    DONATE_PAGE = 6
    BALANCE_PAGE = 7
    RESULT_PAGE = 8

    MONOSPACE_HTML = '<font face="Fira Mono, DejaVu Sans Mono, Menlo, Consolas, Liberation Mono, Monaco, Lucida Console, monospace">'

    card_id = ''
    iban = ''
    keybuf = []
    keyindex = 0

    translator = QTranslator()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stack.setCurrentIndex(self.CARD_PAGE)

        # Card page
        self.ui.dutch.clicked.connect(self.dutch)
        self.ui.german.clicked.connect(self.german)
        self.ui.english.clicked.connect(self.english)

        # Main page
        self.ui.withdraw.clicked.connect(self.withdrawPage)
        self.ui.donate.clicked.connect(self.donatePage)
        self.ui.balance.clicked.connect(self.balancePage)
        self.ui.quickWithdrawal.clicked.connect(functools.partial(self.withdraw, amount=7000))
        self.ui.logout.clicked.connect(functools.partial(self.showResult, text=self.tr('Nog een fijne dag!')))

        # Withdraw page
        self.ui.withdrawAbort.clicked.connect(self.abort)
        self.ui.withdrawOption0.clicked.connect(functools.partial(self.withdraw, amount=1000))
        self.ui.withdrawOption1.clicked.connect(functools.partial(self.withdraw, amount=2000))
        self.ui.withdrawOption2.clicked.connect(functools.partial(self.withdraw, amount=5000))
        self.ui.withdrawOption3.clicked.connect(functools.partial(self.withdraw, amount=10000))
        self.ui.withdrawManual.clicked.connect(self.withdrawManualPage)

        # Withdraw manual page
        self.ui.withdrawManualAccept.clicked.connect(self.withdrawFromKeybuf)

        # Withdraw bill selection page
        # TODO

        # Donate page
        self.ui.donateAbort.clicked.connect(self.abort)
        self.ui.donateAccept.clicked.connect(self.donate)

        # Balance page
        self.ui.balanceAccept.clicked.connect(self.abort)

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
        if self.ui.stack.currentIndex() == self.CARD_PAGE:
            # TODO build in card reader support and remove this
            self.card_id = 'EBA8001B'
            self.iban = 'NL35HERB2932749274'

            self.ui.pinText.setGraphicsEffect(None)
            self.ui.pinAbort.setGraphicsEffect(None)
            self.ui.stack.setCurrentIndex(self.LOGIN_PAGE)
            self.clearInput()
        elif self.ui.stack.currentIndex() == self.LOGIN_PAGE:
            # store the keyboard key in the keybuffer
            key = self.getKeyFromEvent(event.key())
            if key == None:
                return
            self.keybuf.append(key)

            # change the abort button to a correction button
            try:
                self.ui.pinAbort.clicked.disconnect()
            except TypeError:
                # idk why this happens
                pass
            self.ui.pinAbort.clicked.connect(self.clearInput)
            self.ui.pinAbort.setText(self.tr('﹡    Correctie'))

            # update the pin dots on the display
            if self.keyindex == 0:
                self.ui.pin.setText('•   ')
            elif self.keyindex == 1:
                self.ui.pin.setText('••  ')
            elif self.keyindex == 2:
                self.ui.pin.setText('••• ')
            elif self.keyindex == 3:
                self.ui.pin.setText('••••')

            self.keyindex += 1
            if self.keyindex < PIN_LENGTH:
                return

            # animate the fading of the pinAbort button
            self.pinAbortEff = QtWidgets.QGraphicsOpacityEffect()
            self.pinAbortEff.setOpacity(0.0)
            self.ui.pinAbort.setGraphicsEffect(self.pinAbortEff)

            # animate the fading of the pin entry help text
            self.pinTextEff = QtWidgets.QGraphicsOpacityEffect()
            self.ui.pinText.setGraphicsEffect(self.pinTextEff)
            self.pinTextAnim = QPropertyAnimation(self.pinTextEff, b"opacity")
            self.pinTextAnim.setStartValue(1.0)
            self.pinTextAnim.setEndValue(0.0)
            self.pinTextAnim.setDuration(300)
            self.pinTextAnim.start(self.pinTextAnim.DeletionPolicy.DeleteWhenStopped)

            # animate the translation of the pin dots to the center of the screen
            self.pinAnim = QPropertyAnimation(self.ui.pin, b"pos")
            self.pinAnim.setEndValue(QPoint(self.ui.pin.x(), self.ui.pin.y() - int(self.ui.pinText.height() / 2)))
            self.pinAnim.setDuration(300)
            self.pinAnim.start(self.pinTextAnim.DeletionPolicy.DeleteWhenStopped)

            # short delay here to show that the 4th character has been entered
            self.timer = QTimer()
            self.timer.timeout.connect(self.login)
            self.timer.setSingleShot(True)
            self.timer.start(700)
        elif self.ui.stack.currentIndex() in (self.WITHDRAW_MANUAL_PAGE, self.DONATE_PAGE):
            # store the keyboard key in the keybuffer
            key = self.getKeyFromEvent(event.key())
            if key == None:
                return

            if self.keyindex > 2:
                return
            self.keybuf[self.keyindex] = key
            self.keyindex += 1

            if self.ui.stack.currentIndex() == self.WITHDRAW_MANUAL_PAGE:
                # change the abort button to a correction button
                self.ui.withdrawManualAbort.clicked.disconnect()
                self.ui.withdrawManualAbort.clicked.connect(self.clearInput)
                self.ui.withdrawManualAbort.setText(self.tr('﹡    Correctie'))

                # show the accept button
                self.ui.withdrawManualAccept.show()

                # write the updated amount to the display
                self.ui.withdrawAmount.setText(self.MONOSPACE_HTML + ''.join(self.keybuf).replace(' ', '&nbsp;') + '</font> EUR')
            else:
                # change the abort button to a correction button
                self.ui.donateAbort.clicked.disconnect()
                self.ui.donateAbort.clicked.connect(self.clearInput)
                self.ui.donateAbort.setText(self.tr('﹡    Correctie'))

                # show the accept button
                self.ui.donateAccept.show()

                # write the updated amount to the display
                self.ui.donateAmount.setText(self.MONOSPACE_HTML + ''.join(self.keybuf).replace(' ', '&nbsp;') + '</font> EUR')

    @pyqtSlot()
    def clearInput(self):
        self.keyindex = 0

        if self.ui.stack.currentIndex() == self.LOGIN_PAGE:
            self.keybuf = []

            # change the correction button back to an abort button
            try:
                self.ui.pinAbort.clicked.disconnect()
            except TypeError:
                # idk why this happens
                pass
            self.ui.pinAbort.clicked.connect(self.goHome)
            self.ui.pinAbort.setText(self.tr('﹡    Afbreken'))

            # clear the display
            self.ui.pin.setText('')
        elif self.ui.stack.currentIndex() == self.WITHDRAW_MANUAL_PAGE:
            self.keybuf = [' '] * 3

            # change the correction button back to an abort button
            try:
                self.ui.withdrawManualAbort.clicked.disconnect()
            except TypeError:
                # idk why this happens
                pass
            self.ui.withdrawManualAbort.clicked.connect(self.abort)
            self.ui.withdrawManualAbort.setText(self.tr('﹡    Afbreken'))

            # hide the accept button for now
            self.ui.withdrawManualAccept.hide()

            # clear the display
            self.ui.withdrawAmount.setText(self.MONOSPACE_HTML + '&nbsp;&nbsp;&nbsp;</font> EUR')
        elif self.ui.stack.currentIndex() == self.DONATE_PAGE:
            self.keybuf = [' '] * 3

            # change the correction button back to an abort button
            try:
                self.ui.donateAbort.clicked.disconnect()
            except TypeError:
                # happens only to withdrawManualAbort, but just in case
                pass
            self.ui.donateAbort.clicked.connect(self.abort)
            self.ui.donateAbort.setText(self.tr('﹡    Afbreken'))

            # hide the accept button for now
            self.ui.donateAccept.hide()

            # clear the display
            self.ui.donateAmount.setText(self.MONOSPACE_HTML + '&nbsp;&nbsp;&nbsp;</font> EUR')

    @pyqtSlot()
    def login(self):
        # TODO run on separate thread
        reply = hbp.login(self.card_id, self.iban, ''.join(self.keybuf))

        self.clearInput()

        if reply == hbp.HBP_LOGIN_GRANTED:
            self.ui.stack.setCurrentIndex(self.MAIN_PAGE)

            name = hbp.info()
            if type(name) is list:
                self.ui.name.setText(self.tr('Welkom') + f' {name[0]} {name[1]}!')
            else:
                self.ui.name.setText(self.tr('Welkom!'))
        elif reply == hbp.HBP_LOGIN_DENIED:
            self.showResult(self.tr('Onjuiste PIN'), logout=False)
        elif reply == hbp.HBP_LOGIN_BLOCKED:
            self.showResult(self.tr('Deze kaart is geblokkeerd'), logout=False)
        else:
            self.showResult(self.tr('Een interne fout is opgetreden'), logout=False)
            print(reply)

    # FIXME replace these with lambda or something?
    @pyqtSlot()
    def abort(self):
        self.ui.stack.setCurrentIndex(self.MAIN_PAGE)

    @pyqtSlot()
    def goHome(self):
        self.ui.stack.setCurrentIndex(self.CARD_PAGE)

    @pyqtSlot()
    def showResult(self, text, logout=True):
        self.ui.stack.setCurrentIndex(self.RESULT_PAGE)
        self.ui.resultText.setText(text)

        # automatically logout after 2 seconds
        self.timer = QTimer()
        if logout:
            self.timer.timeout.connect(self.logout)
        else:
            self.timer.timeout.connect(self.goHome)

        self.timer.setSingleShot(True)
        self.timer.start(2000)


    #
    # Card page
    #
    @pyqtSlot()
    def dutch(self):
        app.removeTranslator(self.translator)
        self.ui.retranslateUi(self)

    @pyqtSlot()
    def german(self):
        app.removeTranslator(self.translator)
        self.translator.load("ts/de_DE.qm")
        app.installTranslator(self.translator)
        self.ui.retranslateUi(self)

    @pyqtSlot()
    def english(self):
        app.removeTranslator(self.translator)
        self.translator.load("ts/en_US.qm")
        app.installTranslator(self.translator)
        self.ui.retranslateUi(self)


    #
    # Main page
    #
    @pyqtSlot()
    def withdrawPage(self):
        self.ui.stack.setCurrentIndex(self.WITHDRAW_PAGE)

    @pyqtSlot()
    def donatePage(self):
        self.ui.stack.setCurrentIndex(self.DONATE_PAGE)

        self.clearInput()

    @pyqtSlot()
    def balancePage(self):
        self.ui.balanceAmount.setText(hbp.balance().replace('.', ',') + ' EUR')
        self.ui.stack.setCurrentIndex(self.BALANCE_PAGE)

    @pyqtSlot()
    def logout(self, doServerLogout=True):
        # we can check the reply, but this is really not needed, as it basically always succeeds
        if doServerLogout:
            hbp.logout()

        # we should clear all modified variables and labels here for security
        self.keybuf = []
        self.keyindex = 0
        self.ui.withdrawAmount.setText('')
        self.ui.donateAmount.setText('')
        self.ui.balanceAmount.setText('')

        self.dutch()
        self.ui.stack.setCurrentIndex(self.CARD_PAGE)

    #
    # Withdraw page
    #
    @pyqtSlot()
    def withdraw(self, amount):
        # start processing
        self.ui.stack.setCurrentIndex(self.RESULT_PAGE)
        self.ui.resultText.setText(self.tr('Een moment geduld...'))
        reply = hbp.transfer('', amount);

        if reply in (hbp.HBP_TRANSFER_SUCCESS, hbp.HBP_TRANSFER_PROCESSING):
            # TODO operate money dispenser here (on a separate thread ofc)

            self.timer = QTimer()
            self.timer.timeout.connect(functools.partial(self.showResult, text=self.tr('Nog een fijne dag!')))
            self.timer.setSingleShot(True)
            self.timer.start(3000)
        elif reply == hbp.HBP_TRANSFER_INSUFFICIENT_FUNDS:
            self.ui.resultText.setText(self.tr('Uw saldo is ontoereikend'))

            self.timer = QTimer()
            self.timer.timeout.connect(self.abort)
            self.timer.setSingleShot(True)
            self.timer.start(3000)
        elif reply == hbp.HBP_REP_TERMINATED:
            # server side session has expired
            self.logout(doServerLogout=False)
        else:
            self.showResult(self.tr('Een interne fout is opgetreden'))
            print(reply)

    #
    # Withdraw manual page
    #
    @pyqtSlot()
    def withdrawManualPage(self):
        self.ui.stack.setCurrentIndex(self.WITHDRAW_MANUAL_PAGE)

        self.clearInput()

    @pyqtSlot()
    def withdrawFromKeybuf(self):
        try:
            amount = int(''.join(self.keybuf).replace(' ', '')) * 100
        except ValueError:
            # nothing has been entered yet
            return

        self.withdraw(amount)

    #
    # Withdraw bill selection page
    #
    @pyqtSlot()
    def withdrawBillsPage(self):
        self.ui.stack.setCurrentIndex(self.WITHDRAW_BILLS_PAGE)

        # TODO implement

    #
    # Donate page
    #
    @pyqtSlot()
    def donate(self):
        # TODO implement
        self.ui.stack.setCurrentIndex(self.RESULT_PAGE)
        self.ui.resultText.setText('Nog niet geïmplementeerd')
        self.timer = QTimer()
        self.timer.timeout.connect(self.abort)
        self.timer.setSingleShot(True)
        self.timer.start(2000)

# print usage information
def help():
    print('usage: gui.py [-h] [-s | --serial-port=] [-h | --host=] [-p | --port=]')

def main(argv):
    global app
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
