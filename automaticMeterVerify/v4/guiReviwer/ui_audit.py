# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'water_meter r2.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QMenuBar, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.text_0 = QLabel(self.centralwidget)
        self.text_0.setObjectName(u"text_0")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.text_0.sizePolicy().hasHeightForWidth())
        self.text_0.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.text_0, 0, 0, 1, 1)

        self.text_1 = QLabel(self.centralwidget)
        self.text_1.setObjectName(u"text_1")
        sizePolicy1.setHeightForWidth(self.text_1.sizePolicy().hasHeightForWidth())
        self.text_1.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.text_1, 0, 1, 1, 1)

        self.img_0 = QLabel(self.centralwidget)
        self.img_0.setObjectName(u"img_0")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.img_0.sizePolicy().hasHeightForWidth())
        self.img_0.setSizePolicy(sizePolicy2)
        self.img_0.setMinimumSize(QSize(50, 50))
        self.img_0.setScaledContents(True)

        self.gridLayout.addWidget(self.img_0, 1, 0, 1, 1)

        self.img_1 = QLabel(self.centralwidget)
        self.img_1.setObjectName(u"img_1")
        sizePolicy2.setHeightForWidth(self.img_1.sizePolicy().hasHeightForWidth())
        self.img_1.setSizePolicy(sizePolicy2)
        self.img_1.setMinimumSize(QSize(50, 50))
        self.img_1.setScaledContents(True)

        self.gridLayout.addWidget(self.img_1, 1, 1, 1, 1)

        self.text_2 = QLabel(self.centralwidget)
        self.text_2.setObjectName(u"text_2")
        sizePolicy1.setHeightForWidth(self.text_2.sizePolicy().hasHeightForWidth())
        self.text_2.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.text_2, 2, 0, 1, 1)

        self.text_3 = QLabel(self.centralwidget)
        self.text_3.setObjectName(u"text_3")
        sizePolicy1.setHeightForWidth(self.text_3.sizePolicy().hasHeightForWidth())
        self.text_3.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.text_3, 2, 1, 1, 1)

        self.img_2 = QLabel(self.centralwidget)
        self.img_2.setObjectName(u"img_2")
        sizePolicy2.setHeightForWidth(self.img_2.sizePolicy().hasHeightForWidth())
        self.img_2.setSizePolicy(sizePolicy2)
        self.img_2.setMinimumSize(QSize(50, 50))
        self.img_2.setScaledContents(True)

        self.gridLayout.addWidget(self.img_2, 3, 0, 1, 1)

        self.img_3 = QLabel(self.centralwidget)
        self.img_3.setObjectName(u"img_3")
        sizePolicy2.setHeightForWidth(self.img_3.sizePolicy().hasHeightForWidth())
        self.img_3.setSizePolicy(sizePolicy2)
        self.img_3.setMinimumSize(QSize(50, 50))
        self.img_3.setScaledContents(True)

        self.gridLayout.addWidget(self.img_3, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.progress = QLabel(self.centralwidget)
        self.progress.setObjectName(u"progress")
        sizePolicy.setHeightForWidth(self.progress.sizePolicy().hasHeightForWidth())
        self.progress.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.progress)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1920, 18))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.text_0.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.text_1.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.img_0.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.img_1.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.text_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.text_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.img_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.img_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.progress.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

