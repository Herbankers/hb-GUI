from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_login1(object):
    def gotoLogin2(self):
        from login2 import Ui_login2
        self.login2 = QtWidgets.QMainWindow()
        self.ui = Ui_login2()
        self.ui.setupUi(self.login2)
        main.hide()
        self.login2.showMaximized()

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
        self.label.setGeometry(QtCore.QRect((width/3), 20, 500, 60))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(23)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect((width/3),(height/3), 250, 25))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(1800, 940, 100, 50))
        self.startButton.setObjectName("startButton")

        self.startButton.clicked.connect(self.gotoLogin2)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect((width/3)+150, (height/3), 140, 30))
        self.lineEdit.setObjectName("lineEdit")
        self.helpButton = QtWidgets.QPushButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(0, 0, 100, 50))
        self.helpButton.setObjectName("helpButton")
        main.setCentralWidget(self.centralwidget)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "Login"))
        self.label.setText(_translate("main", "Scan uw kaart bij de lezer"))
        self.label_2.setText(_translate("main", "Kaart ID:"))
        self.startButton.setText(_translate("main", "Verder [1]"))
        self.helpButton.setText(_translate("main", "Help [2]"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    ui = Ui_login1()
    ui.setupUi(main)
    main.showMaximized()
    sys.exit(app.exec_())
