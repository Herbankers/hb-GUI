from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import *
from datetime import datetime
import functools
import getopt
import math
import sys

from hbp import *
from ui.main import *

import time
import adafruit_thermal_printer
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.67)

#
# On PC keyboards,
#   '-' can be used instead of '*'
#  and
#   '=' can be used instead of '#'
#


#
# TODO
# Client side countdown to automatically end session after hbp.HBP_TIMEOUT seconds
#

app = None      # QApplication
hbp = None      # hbp object
arduino = None  # serial object
printer = None  # printer object

# although both the server and HBP support PINs of up to 12 numbers, we've decided to hardcode 4 in the client for now
# for convenience sake
PIN_LENGTH = 4

# TODO stop this thread properly on exit, we should handle exiting properly in the first place, which is not done right
# now at alllll
mutex = QMutex()
class Arduino(QObject):
    keyPress = pyqtSignal(str)
    cardUID = pyqtSignal(str)
    cardIBAN = pyqtSignal(str)
    finishDispense = pyqtSignal()
    listening = True

    def run(self):
        self.listening = True

        while self.listening:
            mutex.lock()

            if arduino.in_waiting == 0:
                time.sleep(0.1)
                mutex.unlock()
                continue

            data = arduino.readline()[:-2]
            mutex.unlock()

            try:
                decoded_data = str(data, 'utf-8')
            except UnicodeDecodeError:
                continue

            # key pressed
            if decoded_data[0:1] == 'K':
                self.keyPress.emit(decoded_data[1:])
            # card scanned: UID
            if decoded_data[0:1] == 'U':
                self.cardUID.emit(decoded_data[1:])
            # card scanned: IBAN
            if decoded_data[0:1] == 'I':
                iban = decoded_data[1:]

                # check IBAN country code for validity
                if iban[0:2].isalpha() == False:
                    continue

                # check 'check digits' for validitiy
                if iban[2:4].isdecimal() == False:
                    continue

                # check bank name for validitiy
                if iban[4:8].isalpha() == False:
                    continue

                # check account number for validitiy
                # only check the first 16 numbers bcs everyone else is too lazy to write 2 additional bytes to their
                # RFID cards bcs it's not by default in the example that literally EVERYONE has copied, lazy fuckers
                if iban[8:16].isdecimal() == False:
                    continue

                self.cardIBAN.emit(iban)
            # finished dispensing bills
            if decoded_data[0:1] == 'D':
                self.finishDispense.emit()

    def stop(self):
        self.listening = False

class MainWindow(QtWidgets.QMainWindow):
    # Page index numbers
    CARD_PAGE                     = 0
    LOGIN_PAGE                    = 1
    MAIN_PAGE                     = 2
    WITHDRAW_PAGE                 = 3
    WITHDRAW_MANUAL_PAGE          = 4
    WITHDRAW_BILL_SELECTION_PAGE  = 5
    DONATE_PAGE                   = 6
    BALANCE_PAGE                  = 7
    CONFIRM_PAGE                  = 8
    RESULT_PAGE                   = 9

    MONOSPACE_HTML = '<font face="Fira Mono, DejaVu Sans Mono, Menlo, Consolas, Liberation Mono, Monaco, Lucida Console, monospace">'

    translator = QTranslator()

    card_id     = ''
    iban        = ''
    keybuf      = []
    keyindex    = 0

    # Confirm page modes
    confirmMode = -1

    CONFIRM_AMOUNT  = 0
    CONFIRM_RECEIPT = 1

    billOption0 = None
    billOption1 = None
    billOption2 = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stack.setCurrentIndex(self.CARD_PAGE)

        # create a thread for serial connections if an arduino is connected
        if arduino != None:
            self.thread = QThread()
            self.worker = Arduino()
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.keyPress.connect(self.keypadPress)
            self.worker.cardUID.connect(self.cardUID)
            self.worker.cardIBAN.connect(self.cardIBAN)

            self.thread.start()

        self.fullScrSc = QtGui.QShortcut(QtGui.QKeySequence.StandardKey.FullScreen, self)
        self.fullScrSc.activated.connect(lambda: self.showNormal() if self.isFullScreen() else self.showFullScreen())

        # Card page
        self.card_menu = {
            '1': self.dutch, '2': self.german, '3': self.english
        }
        self.ui.dutch.clicked.connect(self.card_menu['1'])
        self.ui.german.clicked.connect(self.card_menu['2'])
        self.ui.english.clicked.connect(self.card_menu['3'])

        self.login_menu = {
            '*': self.clearInput
        }
        self.ui.loginAbort.clicked.connect(self.login_menu['*'])

        # Main page
        self.main_menu = {
            '1': self.withdrawPage,
            '4': self.donatePage,   '6': functools.partial(self.withdraw, amount=7000),
            '7': self.balancePage,
                                    '#': functools.partial(self.showResult, text=self.tr('Nog een fijne dag!'))
        }
        self.ui.withdraw.clicked.connect(self.main_menu['1'])
        self.ui.donate.clicked.connect(self.main_menu['4'])
        self.ui.balance.clicked.connect(self.main_menu['7'])
        self.ui.quickWithdrawal.clicked.connect(self.main_menu['6'])
        self.ui.logout.clicked.connect(self.main_menu['#'])

        # Withdraw page
        self.withdraw_menu = {
            '1': functools.partial(self.withdraw, amount=1000), '3': functools.partial(self.withdraw, amount=5000),
            '4': functools.partial(self.withdraw, amount=2000), '6': functools.partial(self.withdraw, amount=10000),
            '*': self.abort,                                    '#': self.withdrawManualPage
        }
        self.ui.withdrawOption0.clicked.connect(self.withdraw_menu['1'])
        self.ui.withdrawOption1.clicked.connect(self.withdraw_menu['4'])
        self.ui.withdrawOption2.clicked.connect(self.withdraw_menu['3'])
        self.ui.withdrawOption3.clicked.connect(self.withdraw_menu['6'])
        self.ui.withdrawAbort.clicked.connect(self.withdraw_menu['*'])
        self.ui.withdrawManual.clicked.connect(self.withdraw_menu['#'])

        # Withdraw manual page
        self.withdrawManual_menu = {
            '*': self.clearInput, '#': self.withdrawFromKeybuf
        }
        self.ui.withdrawManualAbort.clicked.connect(self.withdrawManual_menu['*'])
        self.ui.withdrawManualAccept.clicked.connect(self.withdrawManual_menu['#'])

        # Withdraw bill selection page
        self.withdrawBillSelection_menu = {
                            '3': functools.partial(self.withdrawBillSelection, option=0),
                            '6': functools.partial(self.withdrawBillSelection, option=1),
                            '9': functools.partial(self.withdrawBillSelection, option=2),
            '*': self.abort
        }
        self.ui.withdrawBillSelectOption0.clicked.connect(self.withdrawBillSelection_menu['3'])
        self.ui.withdrawBillSelectOption1.clicked.connect(self.withdrawBillSelection_menu['6'])
        self.ui.withdrawBillSelectOption2.clicked.connect(self.withdrawBillSelection_menu['9'])
        self.ui.withdrawBillSelectAbort.clicked.connect(self.withdrawBillSelection_menu['*'])

        # Donate page
        self.donate_menu = {
            '*': self.clearInput, '#': self.donate
        }
        self.ui.donateAbort.clicked.connect(self.donate_menu['*'])
        self.ui.donateAccept.clicked.connect(self.donate_menu['#'])

        # Balance page
        self.balance_menu = {
            '#': self.abort
        }
        self.ui.balanceAccept.clicked.connect(self.balance_menu['#'])

        # Confirm page
        self.confirm_menu = {
            '*': self.confirmNegative, '#': self.confirmPositive
        }
        self.ui.confirmNegative.clicked.connect(self.confirm_menu['*'])
        self.ui.confirmPositive.clicked.connect(self.confirm_menu['#'])

        # list of menus for keyboard handler
        self.menus = {
            self.CARD_PAGE: self.card_menu,
            self.LOGIN_PAGE: self.login_menu,
            self.MAIN_PAGE: self.main_menu,
            self.WITHDRAW_PAGE: self.withdraw_menu,
            self.WITHDRAW_MANUAL_PAGE: self.withdrawManual_menu,
            self.WITHDRAW_BILL_SELECTION_PAGE: self.withdrawBillSelection_menu,
            self.DONATE_PAGE: self.donate_menu,
            self.BALANCE_PAGE: self.balance_menu,
            self.CONFIRM_PAGE: self.confirm_menu
        }

    # card UID scan handler
    @pyqtSlot(str)
    def cardUID(self, data):
        if self.ui.stack.currentIndex() == self.CARD_PAGE:
            self.card_id = data

    # card IBAN scan handler
    @pyqtSlot(str)
    def cardIBAN(self, data):
        if self.ui.stack.currentIndex() == self.CARD_PAGE:
            self.iban = data

            self.ui.pinText.setGraphicsEffect(None)
            self.ui.loginAbort.setGraphicsEffect(None)
            self.ui.stack.setCurrentIndex(self.LOGIN_PAGE)
            self.clearInput(abort=False)

    # dispense the specified amount of bills
    def dispenseBills(self, amount, billmix):
        mutex.lock()

        # send the dispense command
        arduino.write(f'{billmix}'.encode())

        # ask the customer to print a receipt after the dispensing has finished
        self.worker.finishDispense.connect(functools.partial(self.confirmReceipt, amount=amount, billmix=billmix))

        mutex.unlock()

    # print a receipt
    def printReceipt(self):
        mutex.lock()
        arduino.write('['.encode())

        # print the logo
        printer.size = adafruit_thermal_printer.SIZE_LARGE
        printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
        printer.print('INGrid')
        printer.size = adafruit_thermal_printer.SIZE_SMALL
        printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
        printer.feed(1)

        # TODO include the billmix on the receipt
        # TODO non-hardcoded location?

        now = QDateTime.currentDateTime()

        # compose and print the receipt
        receiptText =         'IBAN     '  + f'**************{self.iban[-4:]}\n' + \
                      self.tr('Bedrag   ') + f'EUR {self.receiptAmount}\n' + \
                      self.tr('Datum    ') + f'{QLocale().toString(now, "d MMMM yyyy")}\n' + \
                      self.tr('Tijd     ') + f'{QLocale().toString(now, "HH:mm:ss")}\n' + \
                      self.tr('Locatie  ') +  'INGB Rotterdam\n\n'
        if self.receiptBillmix[0] > 0:
            receiptText +=    'EUR  5   '  + f'{self.receiptBillmix[0]}x\n'
        if self.receiptBillmix[1] > 0:
            receiptText +=    'EUR 10   '  + f'{self.receiptBillmix[1]}x\n'
        if self.receiptBillmix[2] > 0:
            receiptText +=    'EUR 20   '  + f'{self.receiptBillmix[2]}x\n'

        printer.print(receiptText)
        printer.feed(3)

        # start listening for keys and RFID tags again
        arduino.write(']'.encode())
        mutex.unlock()

    # generic (for both keypad and keyboard) input handler
    # mouse clicks are handled using Qt's signals and slots
    def keyHandler(self, key):
        page = self.ui.stack.currentIndex()

        try:
            self.menus[page][key]()
            return
        except KeyError:
            pass

        # XXX Temporary XXX
        if page == self.CARD_PAGE:
            if key == '*':
                self.card_id = 'EBA8001B'
                self.iban = 'NL35HERB2932749274'

                self.ui.pinText.setGraphicsEffect(None)
                self.ui.loginAbort.setGraphicsEffect(None)
                self.ui.stack.setCurrentIndex(self.LOGIN_PAGE)
                self.clearInput(abort=False)
                return
        elif page == self.LOGIN_PAGE:
            # store the key in the keybuffer
            self.keybuf.append(key)

            # change the abort button to a correction button
            self.ui.loginAbort.setText(self.tr('﹡    Correctie'))

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
            if self.keyindex < PIN_LENGTH or self.keyindex > PIN_LENGTH:
                return

            # animate the fading of the loginAbort button
            self.loginAbortEff = QtWidgets.QGraphicsOpacityEffect()
            self.loginAbortEff.setOpacity(0.0)
            self.ui.loginAbort.setGraphicsEffect(self.loginAbortEff)

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
        elif page in (self.WITHDRAW_MANUAL_PAGE, self.DONATE_PAGE):
            # limit the user's input to 100 EUR and divisible by 5
            if self.ui.stack.currentIndex() == self.WITHDRAW_MANUAL_PAGE:
                if self.keyindex == 0 and key == '0':
                    return
                elif self.keyindex == 1 and key not in ('0', '5'):
                    return
                elif self.keyindex == 2 and (self.keybuf[0] != '1' or self.keybuf[1] != '0' or key != '0'):
                    return

            # store the keyboard key in the keybuffer
            if self.keyindex > 2:
                return
            self.keybuf[self.keyindex] = key
            self.keyindex += 1


            if self.ui.stack.currentIndex() == self.WITHDRAW_MANUAL_PAGE:
                # change the abort button to a correction button
                self.ui.withdrawManualAbort.setText(self.tr('﹡    Correctie'))

                # show the accept button
                self.ui.withdrawManualAccept.show()

                # write the updated amount to the display
                self.ui.withdrawAmount.setText(self.MONOSPACE_HTML + ''.join(self.keybuf).replace(' ', '&nbsp;') + '</font> EUR')
            else:
                # change the abort button to a correction button
                self.ui.donateAbort.setText(self.tr('﹡    Correctie'))

                # show the accept button
                self.ui.donateAccept.show()

                # write the updated amount to the display
                self.ui.donateAmount.setText(self.MONOSPACE_HTML + ''.join(self.keybuf).replace(' ', '&nbsp;') + '</font> EUR')

    # keypad input handler
    @pyqtSlot(str)
    def keypadPress(self, data):
        self.keyHandler(data)

    # resolve the keyboard key event code to a character (only numbers are accepted)
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
        elif key == Qt.Key.Key_Minus:
            return '*'
        elif key == Qt.Key.Key_Equal:
            return '#'
        else:
            return None

    # keyboard input handler
    def keyPressEvent(self, event):
        key = self.getKeyFromEvent(event.key())
        if key == None:
            return

        self.keyHandler(key)

    # either clear input from the key buffer or abort if the buffer is empty
    @pyqtSlot()
    def clearInput(self, abort=True):
        if self.ui.stack.currentIndex() == self.LOGIN_PAGE:
            if not abort or self.keyindex > 0:
                self.keybuf = []

                # change the correction button back to an abort button
                self.ui.loginAbort.setText(self.tr('﹡    Afbreken'))

                # clear the display
                self.ui.pin.setText('')
            else:
                self.goHome()
        elif self.ui.stack.currentIndex() == self.WITHDRAW_MANUAL_PAGE:
            if not abort or self.keyindex > 0:
                self.keybuf = [' '] * 3

                # change the correction button back to an abort button
                self.ui.withdrawManualAbort.setText(self.tr('﹡    Afbreken'))

                # hide the accept button for now
                self.ui.withdrawManualAccept.hide()

                # clear the display
                self.ui.withdrawAmount.setText(self.MONOSPACE_HTML + '&nbsp;&nbsp;&nbsp;</font> EUR')
            else:
                self.abort()
        elif self.ui.stack.currentIndex() == self.DONATE_PAGE:
            if not abort or self.keyindex > 0:
                self.keybuf = [' '] * 3

                # change the correction button back to an abort button
                self.ui.donateAbort.setText(self.tr('﹡    Afbreken'))

                # hide the accept button for now
                self.ui.donateAccept.hide()

                # clear the display
                self.ui.donateAmount.setText(self.MONOSPACE_HTML + '&nbsp;&nbsp;&nbsp;</font> EUR')
            else:
                self.abort()

        self.keyindex = 0

    @pyqtSlot()
    def login(self):
        # TODO run on separate thread
        reply = hbp.login(self.card_id, self.iban, ''.join(self.keybuf))

        self.clearInput(abort=False)

        if reply == hbp.HBP_LOGIN_GRANTED:
            name = hbp.info()
            if type(name) is list:
                self.ui.name.setText(self.tr('Welkom') + f' {name[0]} {name[1]}!')
            else:
                self.ui.name.setText(self.tr('Welkom!'))

            self.ui.stack.setCurrentIndex(self.MAIN_PAGE)

            # enable all functionality
            self.remote = False

            self.ui.donate.setVisible(True)
        elif reply == hbp.HBP_LOGIN_GRANTED_REMOTE:
            self.ui.name.setText(self.tr('Welkom!'))
            self.ui.stack.setCurrentIndex(self.MAIN_PAGE)

            # disable functionality that is not available over remote connections (i.e. via NOOB)
            self.remote = True

            sp = self.ui.donate.sizePolicy()
            sp.setRetainSizeWhenHidden(True)
            self.ui.donate.setSizePolicy(sp)
            self.ui.donate.setVisible(False)
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


    #
    # Card page
    #
    @pyqtSlot()
    def dutch(self):
        app.removeTranslator(self.translator)
        self.ui.retranslateUi(self)

        QLocale.setDefault(QLocale('nl_NL'))

    @pyqtSlot()
    def german(self):
        app.removeTranslator(self.translator)
        self.translator.load('ts/de_DE.qm')
        app.installTranslator(self.translator)
        self.ui.retranslateUi(self)

        QLocale.setDefault(QLocale('de_DE'))

    @pyqtSlot()
    def english(self):
        app.removeTranslator(self.translator)
        self.translator.load('ts/en_US.qm')
        app.installTranslator(self.translator)
        self.ui.retranslateUi(self)

        QLocale.setDefault(QLocale('en_US'))


    #
    # Main page
    #
    @pyqtSlot()
    def withdrawPage(self):
        self.ui.stack.setCurrentIndex(self.WITHDRAW_PAGE)

    @pyqtSlot()
    def donatePage(self):
        # donating is not supported on remote logins
        if self.remote:
            return

        self.ui.stack.setCurrentIndex(self.DONATE_PAGE)

        self.clearInput(abort=False)

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
        self.billOption0 = None
        self.billOption1 = None
        self.billOption2 = None
        self.receiptAmount = '0'
        self.receiptBillmix = None

        self.dutch()
        self.ui.stack.setCurrentIndex(self.CARD_PAGE)


    #
    # Withdraw page
    #
    @pyqtSlot()
    def withdraw(self, amount, billmix=None):
        # start processing
        self.ui.stack.setCurrentIndex(self.RESULT_PAGE)
        self.ui.resultText.setText(self.tr('Een moment geduld...'))
        reply = hbp.transfer('', amount);

        if reply in (hbp.HBP_TRANSFER_SUCCESS, hbp.HBP_TRANSFER_PROCESSING):
            # generate a billmix here if one wasn't provided already
            if billmix == None:
                remainder = amount / 100

                twenties = math.floor(remainder / 20)
                remainder -= twenties * 20

                tens = math.floor(remainder / 10)
                remainder -= tens * 10

                fives = math.floor(remainder / 5)

                billmix = (fives, tens, twenties)

            # start the money dispensing process
            if arduino == None:
                self.showResult(self.tr('Geld uitgave niet beschikbaar, wel afgeschreven 😈'))
            else:
                self.dispenseBills(amount, billmix)
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

        self.clearInput(abort=False)

    @pyqtSlot()
    def withdrawFromKeybuf(self):
        try:
            amount = int(''.join(self.keybuf).replace(' ', '')) * 100
        except ValueError:
            # nothing has been entered yet
            return

        self.withdrawBillSelectionPage(amount)


    #
    # Withdraw bill selection page
    #
    def withdrawBillSelectionPage(self, amount):
        # smallest bills
        if amount >= 1000 and amount <= 5000:
            fives = math.floor(amount / 500)

            self.billOption0 = (amount, (fives, 0, 0))
            self.ui.withdrawBillSelectOption0.setText(f'{fives}x€5    3')
            self.ui.withdrawBillSelectOption0.setVisible(True)
        else:
            self.ui.withdrawBillSelectOption0.setVisible(False)

        # standard billmix (largest)
        remainder = amount / 100
        billsStr = ''

        twenties = math.floor(remainder / 20)
        remainder -= twenties * 20
        if twenties > 0:
            billsStr += f'{twenties}x€20 '

        tens = math.floor(remainder / 10)
        remainder -= tens * 10
        if tens > 0:
            billsStr += f'{tens}x€10 '

        fives = math.floor(remainder / 5)
        if fives > 0:
            billsStr += f'{fives}x€5 '

        self.billOption1 = (amount, (fives, tens, twenties))
        self.ui.withdrawBillSelectOption1.setText(f'{billsStr}   6')

        # use mostly 10 EUR bills
        if amount >= 2000:
            remainder = amount / 100
            billsStr = ''

            tens = math.floor(remainder / 10)
            remainder -= tens * 10
            if tens > 0:
                billsStr += f'{tens}x€10 '

            fives = math.floor(remainder / 5)
            remainder -= fives * 5
            if fives > 0:
                billsStr += f'{fives}x€5 '

            self.billOption2 = (amount, (fives, tens, twenties))
            self.ui.withdrawBillSelectOption2.setText(f'{billsStr}   9')
            self.ui.withdrawBillSelectOption2.setVisible(True)
        else:
            self.ui.withdrawBillSelectOption2.setVisible(False)

        self.ui.stack.setCurrentIndex(self.WITHDRAW_BILL_SELECTION_PAGE)

    def withdrawBillSelection(self, option):
        if option == 0 and self.billOption0 != None:
            self.withdraw(*self.billOption0)
        elif option == 1 and self.billOption1 != None:
            self.withdraw(*self.billOption1)
        elif option == 2 and self.billOption2 != None:
            self.withdraw(*self.billOption2)


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


    #
    # Confirm page
    #
    @pyqtSlot()
    def confirmReceipt(self, amount, billmix):
        self.worker.finishDispense.disconnect()

        # check if the printer has paper
        hasPaper = False
        if printer != None:
            mutex.lock()
            arduino.write('['.encode())
            printer.feed(1)

            # for some reason printer.has_paper() craps out, so we use this
            printer.send_command("\x1Bv\x00")
            hasPaper = not int.from_bytes(printer._uart.read(1), byteorder=sys.byteorder) & 0b000100

            arduino.write(']'.encode())
            mutex.unlock()

        # show a message to show the printer is not available
        if printer == None or not hasPaper:
            self.ui.resultText.setText(self.tr('Een bon is helaas niet beschikbaar'))
            self.timer = QTimer()
            self.timer.timeout.connect(functools.partial(self.showResult, text=self.tr('Nog een fijne dag!')))
            self.timer.setSingleShot(True)
            self.timer.start(2000)
            return

        # ask if the customer wants a receipt
        self.confirmMode = self.CONFIRM_RECEIPT
        self.receiptAmount = str(round(amount / 100))
        self.receiptBillmix = billmix

        self.ui.confirmText.setText(self.tr('Wilt u een bon?'))
        self.ui.confirmNegative.setText(self.tr('﹡    Nee'))
        self.ui.confirmPositive.setText(self.tr('Ja    #'))

        # TODO save amount and billmix to memory

        self.ui.stack.setCurrentIndex(self.CONFIRM_PAGE)

    @pyqtSlot()
    def confirmNegative(self):
        if self.confirmMode == self.CONFIRM_RECEIPT:
            self.showResult(self.tr('Nog een fijne dag!'))

    @pyqtSlot()
    def confirmPositive(self):
        if self.confirmMode == self.CONFIRM_RECEIPT:
            self.printReceipt()

            self.showResult(self.tr('Nog een fijne dag!'))


    #
    # Result page
    #
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

# print usage information
def help():
    print('usage: gui.py [-?] [-s | --serial-port=] [-h | --host=] [-p | --port=]')

def main(argv):
    global app
    global hbp
    global arduino
    global printer

    # parse command line options
    try:
        opts, args = getopt.getopt(argv, '?s:h:p:', [ 'serial-port=', 'host=', 'port=' ])
    except getopt.GetoptError:
        help()
        sys.exit(1)

    # empty input_souce means that we'll use only the keyboard and mouse as input
    serial_port = ''

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

    if serial_port != '':
        arduino = serial.Serial(serial_port, 9600, timeout=.1)
        printer = ThermalPrinter(arduino)

    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main(sys.argv[1:])
