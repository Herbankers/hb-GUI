from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_login2(object):
    def clear(self,main):#function to clear the password field
        self.lineEdit.setText("")
    
    def setupUi(self, main):
        # screen = app.primaryScreen()
        # size = screen.availableGeometry()
        width = 1920 #size.width()
        height = 1034 #size.height()
        main.setObjectName("main")
        main.resize(width, height)
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect((width/3), 20, 600, 60))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(23)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect((width/3)+20, 400, 90, 25))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.loginButton = QtWidgets.QPushButton(self.centralwidget)
        self.loginButton.setGeometry(QtCore.QRect(1810, 940, 100, 50))
        self.loginButton.setObjectName("loginButton")
        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setGeometry(QtCore.QRect((width/3)+240, 400, 100, 30))
        self.clearButton.setObjectName("clearButton")
        # clear the password
        self.clearButton.clicked.connect(self.clear)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect((width/3)+100, 400, 115, 30))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.setObjectName("lineEdit")
        self.helpButton = QtWidgets.QPushButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(0, 0, 100, 50))
        self.helpButton.setObjectName("helpButton")
        main.setCentralWidget(self.centralwidget)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "Welkom"))
        self.label.setText(_translate("main", "Voer uw 4-cijferige pincode in"))
        self.label_2.setText(_translate("main", "PIN:"))
        self.loginButton.setText(_translate("main", "Login [1]"))
        self.helpButton.setText(_translate("main", "Help [2]"))
        self.clearButton.setText(_translate("main", "wissen [3]"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    ui = Ui_login2()
    ui.setupUi(main)
    main.showMaximized()
    sys.exit(app.exec_())
