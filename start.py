from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main(object):
    def startLogin(self):
        from login1 import Ui_login1
        self.login1 = QtWidgets.QMainWindow()
        self.ui = Ui_login1()
        self.ui.setupUi(self.login1)
        main.hide()
        self.login1.showMaximized()

    def setupUi(self, main):
        screen = app.primaryScreen()
        size = screen.availableGeometry()
        width = size.width()
        height = size.height()
        print(width, height)
        main.setObjectName("main")
        main.resize(width, height)
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect((width/3), 50, 600, 70))
        font = QtGui.QFont()
        font.setFamily("Broadway")
        font.setPointSize(23)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect((width / 3), 400, 500, 50))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect((width / 3), 500, 600, 50))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 940, 200, 50))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1810, 940, 100, 50))
        self.pushButton_2.setObjectName("pushButton_2")

        #goto next login page
        self.pushButton_2.clicked.connect(self.startLogin)

        self.helpButton = QtWidgets.QPushButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(0, 0, 100, 50))
        self.helpButton.setObjectName("helpButton")
        main.setCentralWidget(self.centralwidget)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "Welkom"))
        self.label.setText(_translate("main", "Welkom bij de Herbank"))
        self.label_2.setText(_translate("main", "Druk op [1] om in te loggen"))
        self.label_3.setText(_translate("main", "Heb je nog geen account bij ons, druk op [2]"))
        self.pushButton.setText(_translate("main", "Aanmelden [2]"))
        self.pushButton_2.setText(_translate("main", "Start [1]"))
        self.helpButton.setText(_translate("main", "Help [3]"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    ui = Ui_main()
    ui.setupUi(main)
    main.showMaximized()
    sys.exit(app.exec_())
