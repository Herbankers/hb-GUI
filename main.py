import sys
import serial, time
import serial.tools.list_ports
from  PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi

name="Eigenaar"

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

arduino = serial.Serial(p[0],9600,timeout=.1)
print("connected to: " + arduino.portstr)

class Start(QMainWindow):
    def __init__(self):
        super(Start,self).__init__()
        loadUi("start.ui",self)
        while(True):
            if(arduino.in_waiting > 0):
                # #[:-2] removes last 2 characters which in this case will be the newline
                data = arduino.readline()[:-2]
                #decode the data
                decoded_data = str(data,'utf-8')
                if(decoded_data[0:1] == '1'):
                    self.gotoLogin1
        #self.pushButton_2.clicked.connect(self.gotoLogin1)

    def gotoLogin1(self):
        login1= Login1()
        widget.addWidget(login1)
        widget.setCurrentIndex(widget.currentIndex()+1)

class Login1(QMainWindow):
    def __init__(self):
        super(Login1,self).__init__()
        loadUi("login1.ui",self)
        self.startButton.clicked.connect(self.gotoLogin2)

    def gotoLogin2(self):
        cardID = self.cardUID.text()
        if(len(cardID) == 5):
            login2= Login2(cardID)
            widget.addWidget(login2)
            widget.setCurrentIndex(widget.currentIndex()+1)
        else:
            self.label_3.setText("Error: pas incorrect")
            self.cardUID.setText("")
            
class Login2(QMainWindow):
    def __init__(self,cardID):
        super(Login2,self).__init__()
        self.cardID = cardID
        loadUi("login2.ui",self)
        self.loginButton.clicked.connect(self.login)

    def login(self):
        pincode = self.pin.text()
        if(len(pincode) == 4):
            menu = Menu()
            widget.addWidget(menu)
            widget.setCurrentIndex(widget.currentIndex()+1)
            print(self.cardID)
            print(pincode)
        else:
            if(len(pincode) < 4):
                self.label_3.setText("Error: pincode moet 4 cijfers zijn")
                self.pin.setText("")
            elif(len(pincode) > 4):
                self.label_3.setText("Error: pin is maximaal 4 cijfers")
                self.pin.setText("")

class Menu(QMainWindow):
    def __init__(self):
        super(Menu,self).__init__()
        loadUi("menu.ui",self)
        self.label.setText("Welkom "+ name)
        self.pushButton.clicked.connect(self.logout)

    def logout(self):
        startWindow = Start()
        widget.addWidget(startWindow)
        widget.setCurrentIndex(0)

app = QApplication(sys.argv)
startWindow=Start()
widget = QtWidgets.QStackedWidget()
widget.addWidget(startWindow)
widget.showMaximized()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")