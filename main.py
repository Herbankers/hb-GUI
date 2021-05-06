import sys, time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi

class Start(QMainWindow):
    def __init__(self):
        super(Start, self).__init__()
        loadUi("start.ui", self)
        self.startButton.clicked.connect(self.checkCard)

    def checkCard(self):
        c= "test"
        login = Login(c)
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class Login(QMainWindow):
    def __init__(self, cardID):
        super(Login, self).__init__()
        self.cardID = cardID
        loadUi("login.ui", self)
        self.pin.setText("")
        self.loginButton.clicked.connect(self.login)

    def login(self):
        pincode = self.pin.text()
        print("login for pair: card: "+ self.cardID+"& pin: "+pincode)
        if len(pincode) == 4:
            menu = Menu()
            widget.addWidget(menu)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        elif len(pincode) == 0:
            self.label_3.setText("Error: voer een geldige pincode in")
            self.pin.setText("")
        else:
            if len(pincode) < 4:
                self.label_3.setText("Error: pincode moet 4 cijfers zijn")
                self.pin.setText("")
            elif len(pincode) > 4:
                self.label_3.setText("Error: pin is maximaal 4 cijfers")
                self.pin.setText("")


class Menu(QMainWindow):
    def __init__(self):
        super(Menu, self).__init__()
        loadUi("menu.ui", self)
        self.label.setText("Welkom bij INGrid ")
        self.pushButton.clicked.connect(self.logout)

    def logout(self):
        startWindow = Start()
        widget.addWidget(startWindow)
        widget.setCurrentIndex(0)


app = QApplication(sys.argv)
startWindow = Start()
widget = QtWidgets.QStackedWidget()
widget.addWidget(startWindow)
widget.showMaximized()
sys.exit(app.exec_())
