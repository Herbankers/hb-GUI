import sys, time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from hbp import *

# create hbp instance to communicate with the server
host = '145.24.222.242'
port = 8420
hbp = HBP(host,port)
print(f'Connected to Herbank Server @ {host}:{port}')


class Start(QMainWindow):
    def __init__(self):
        super(Start, self).__init__()
        loadUi("start.ui", self)
        self.startButton.clicked.connect(self.checkCard)

    def checkCard(self):
        # TODO check serial input for card
        card = 'EBA8001B'
        print("Card detected")
        startWindow.destroy()
        login = Login(card)
        stack.addWidget(login)
        stack.setCurrentIndex(stack.currentIndex() + 1)
        #     else:
        #         self.label_3.setText("Kan de kaart niet lezen, probeer opnieuw")
        # else:
        #     self.label_3.setText("Kaart is geblokeerd, neem contact op met ons\n \ttel: 911")

class Login(QMainWindow):
    def __init__(self, card_id):
        super(Login, self).__init__()
        self.cardID = card_id
        loadUi("login.ui", self)
        self.pin.setText("")
        self.loginButton.clicked.connect(self.login)

    def login(self):
        pincode = self.pin.text()
        iban = 'NL35HERB2932749274'
        if len(pincode) == 4:
            reply = hbp.login(self.cardID,iban,pincode)
            if reply == hbp.HBP_LOGIN_GRANTED:
                print("Logging in...")
                menu = Menu()
                stack.addWidget(menu)
                stack.setCurrentIndex(stack.currentIndex() + 1)
            elif reply == hbp.HBP_LOGIN_DENIED:
                self.pin.setText("")
                self.label_3.setText("Pincode incorrect, nog x pogingen over")
            elif reply == hbp.HBP_LOGIN_BLOCKED:
                self.pin.setText("")
                self.label_3.setText("3 foutieve pogingen\n kaart geblokeerd")
            else:
                print(reply)
                time.sleep(2)
        elif len(pincode) == 0:
            self.label_3.setText("Error: voer een geldige pincode in, nog x pogingen over")
            self.pin.setText("")
        else:
            if len(pincode) < 4:
                self.label_3.setText("Error: pincode moet 4 cijfers zijn, nog x pogingen over")
                self.pin.setText("")
            elif len(pincode) > 4:
                self.label_3.setText("Error: pin is maximaal 4 cijfers, nog x pogingen over")
                self.pin.setText("")




class Menu(QMainWindow):
    def __init__(self):
        super(Menu, self).__init__()
        loadUi("menu.ui", self)
        name = hbp.info()
        if type(name) is list:
            self.label.setText(f"Welkom bij INGrid {name[0]} {name[1]}")
        else:
        # name is not received for some strange reason
            self.label.setText("Welkom bij INGrid ")
        
        self.pushButton.clicked.connect(self.logout)
        self.balance.clicked.connect(self.showBalance)
        self.quickWithdraw.clicked.connect(self.withdraw70)
        self.customWithdraw.clicked.connect(self.withdraw)
        self.donate.clicked.connect(self.gotoDonate)

    def logout(self):
        logout = Logout()
        stack.addWidget(logout)
        stack.setCurrentWidget(logout)

    def showBalance(self):
        showBalance = balance()
        stack.addWidget(showBalance)
        stack.setCurrentWidget(showBalance)

    def withdraw70(self):
        print("withdraw 70 quick...")
        amount = 70
        reply = hbp.transfer('',amount*100)

        if reply == hbp.HBP_TRANSFER_SUCCESS:
            self.successLabel.setText("Succesvol €70 opgenomen, neem uw geld uit")
        elif reply == hbp.HBP_TRANSFER_PROCESSING:
            self.successLabel.setText("Nog bezig..., neem uw geld uit")
            time.sleep(3)
        elif reply == hbp.HBP_TRANSFER_INSUFFICIENT_FUNDS:
            self.errorLable.setText("Uw saldo is te laag om €70 op te nemen")
        else:
            print(reply)

    def withdraw(self):
        print("goto withdraw")

    def gotoDonate(self):
        donate = donations()
        stack.addWidget(donate)
        stack.setCurrentIndex(stack.currentIndex() + 1)

class balance(QMainWindow):
    def __init__(self):
        super(balance, self).__init__()
        loadUi("balance.ui", self)
        self.label.setText("Uw saldo bedraagd €"+hbp.balance())
        self.backButton.clicked.connect(self.back)

    def back(self):
        stack.setCurrentIndex(stack.currentIndex() -1)

class donations(QMainWindow):
    def __init__(self):
        super(donations, self).__init__()
        loadUi("donate.ui", self)
        self.pushButton.clicked.connect(self.back)

    def back(self):
        stack.setCurrentIndex(stack.currentIndex() -1)

class withdraw1(QMainWindow):
    def __init__(self):
        super(withdraw1, self).__init__()
        loadUi("balance.ui", self)
        self.loginButton.clicked.connect(self.login)

class withdraw2(QMainWindow):
    def __init__(self):
        super(withdraw2, self).__init__()
        loadUi("balance.ui", self)
        self.loginButton.clicked.connect(self.login)

class Logout(QMainWindow):
    def __init__(self):
        super(Logout, self).__init__()
        loadUi("logout.ui", self)
        self.backButton.clicked.connect(self.back)
        self.logoutButton.clicked.connect(self.logout)

    def back(self):
        stack.setCurrentIndex(stack.currentIndex() -1)

    def logout(self):
        print("Logging out...")
        hbp.logout()
        stack.setCurrentWidget(startWindow)



app = QApplication(sys.argv)
startWindow = Start()
stack = QtWidgets.QStackedWidget()
stack.addWidget(startWindow)
stack.showMaximized()
sys.exit(app.exec_())

