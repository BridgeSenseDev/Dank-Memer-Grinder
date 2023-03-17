from PyQt5 import QtCore, QtGui, QtWidgets


def create_font(font_size):
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(font_size)
    font.setBold(True)
    font.setWeight(75)
    return font


class Ui_Updater(object):
    def setupUi(self, Updater):
        Updater.setObjectName("Updater")
        Updater.resize(467, 307)
        self.central_widget = QtWidgets.QWidget(Updater)
        self.central_widget.setStyleSheet(
            "*{\n"
            "    border: none;\n"
            "    background-color: transparent;\n"
            "    color: #e8e6e3;\n"
            "}\n"
            "#central_widget{\n"
            "    background-color: #36393f;\n"
            "}\n"
            "QPushButton{\n"
            "    background-color: #42464d;;\n"
            "    border-radius: 15px;\n"
            "}\n"
            "#main_frame{\n"
            "    background-color: #2f3136;\n"
            "    border-radius: 20px;\n"
            "}"
        )
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.header_frame = QtWidgets.QFrame(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_frame.sizePolicy().hasHeightForWidth())
        self.header_frame.setSizePolicy(sizePolicy)
        self.header_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.header_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.header_frame.setObjectName("header_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.header_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.header_frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFont(create_font(25))
        self.label.setStyleSheet(
            "#side_menu_widget{\n"
            "    background-color: #202225;\n"
            "    border-radius: 20px;\n"
            "}"
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.header_frame)
        self.main_frame = QtWidgets.QFrame(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy)
        self.main_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setObjectName("main_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.main_frame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.side_menu_widget = QtWidgets.QWidget(self.main_frame)
        self.side_menu_widget.setMinimumSize(QtCore.QSize(120, 0))
        self.side_menu_widget.setMaximumSize(QtCore.QSize(120, 16777215))
        self.side_menu_widget.setStyleSheet(
            "background-color: #202225; border-radius: 20px;"
        )
        self.side_menu_widget.setObjectName("side_menu_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.side_menu_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.side_menu_widget)
        self.label_2.setMinimumSize(QtCore.QSize(100, 100))
        self.label_2.setMaximumSize(QtCore.QSize(100, 100))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/icons/icon.ico"))
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.buttons_frame = QtWidgets.QFrame(self.side_menu_widget)
        self.buttons_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttons_frame.setObjectName("buttons_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.buttons_frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.update_btn = QtWidgets.QPushButton(self.buttons_frame)
        self.update_btn.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_btn.sizePolicy().hasHeightForWidth())
        self.update_btn.setSizePolicy(sizePolicy)
        self.update_btn.setMinimumSize(QtCore.QSize(100, 45))
        self.update_btn.setMaximumSize(QtCore.QSize(100, 45))
        self.update_btn.setFont(create_font(12))
        self.update_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.update_btn.setStyleSheet("background-color : #2d7d46")
        self.update_btn.setObjectName("update_btn")
        self.verticalLayout_3.addWidget(self.update_btn)
        self.skip_btn = QtWidgets.QPushButton(self.buttons_frame)
        self.skip_btn.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skip_btn.sizePolicy().hasHeightForWidth())
        self.skip_btn.setSizePolicy(sizePolicy)
        self.skip_btn.setMinimumSize(QtCore.QSize(100, 45))
        self.skip_btn.setMaximumSize(QtCore.QSize(100, 45))
        self.skip_btn.setFont(create_font(12))
        self.skip_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.skip_btn.setStyleSheet("background-color : #d83c3e")
        self.skip_btn.setObjectName("skip_btn")
        self.verticalLayout_3.addWidget(self.skip_btn)
        self.verticalLayout_2.addWidget(self.buttons_frame, 0, QtCore.Qt.AlignBottom)
        self.horizontalLayout_2.addWidget(self.side_menu_widget)
        self.changelog_frame = QtWidgets.QFrame(self.main_frame)
        self.changelog_frame.setStyleSheet("")
        self.changelog_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.changelog_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.changelog_frame.setObjectName("changelog_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.changelog_frame)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.changelog_label = QtWidgets.QLabel(self.changelog_frame)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.changelog_label.setFont(font)
        self.changelog_label.setText("")
        self.changelog_label.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.changelog_label.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse
            | QtCore.Qt.TextSelectableByKeyboard
            | QtCore.Qt.TextSelectableByMouse
        )
        self.changelog_label.setObjectName("changelog_label")
        self.horizontalLayout_3.addWidget(self.changelog_label)
        self.horizontalLayout_2.addWidget(self.changelog_frame)
        self.verticalLayout.addWidget(self.main_frame)
        Updater.setCentralWidget(self.central_widget)

        self.retranslateUi(Updater)
        QtCore.QMetaObject.connectSlotsByName(Updater)

    def retranslateUi(self, Updater):
        _translate = QtCore.QCoreApplication.translate
        Updater.setWindowTitle(_translate("Updater", "Updater"))
        self.label.setText(_translate("Updater", "Update Available"))
        self.update_btn.setText(_translate("Updater", "Update"))
        self.skip_btn.setText(_translate("Updater", "Skip"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Updater = QtWidgets.QMainWindow()
    ui = Ui_Updater()
    ui.setupUi(Updater)
    Updater.show()
    sys.exit(app.exec_())
