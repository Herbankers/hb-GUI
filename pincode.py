from PyQt5 import *
from welkom import *

class Ui_pincode(object):
    def openNext(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_welkom()
        self.ui.setupUi(self.window)
        self.window.showMaximized()
        main.hide()

    def setupUi(self, main):
        width = 1920
        height = 1034
        main.setObjectName("main")
        main.resize(width, height)
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect((width / 3), 50, 600, 70))
        font = QtGui.QFont()
        font.setFamily("Calibri")
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
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1810, 875, 100, 50))
        self.pushButton_2.setObjectName("pushButton_2")

        #self.pushButton_2.clicked.connect(self.openNext)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(230, 170, 113, 20))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.setObjectName("lineEdit")
        main.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 620, 22))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        main.setMenuBar(self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "Welkom"))
        self.label.setText(_translate("main", "Voer uw 4-cijferige pincode in"))
        self.label_2.setText(_translate("main", "PIN:"))
        self.pushButton_2.setText(_translate("main", "Verder [1]"))
        self.menuHelp.setTitle(_translate("main", " Help [2]"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    ui = Ui_main()
    ui.setupUi(main)
    main.show()
    sys.exit(app.exec_())
