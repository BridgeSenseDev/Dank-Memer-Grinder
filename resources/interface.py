from PyQt5 import QtCore, QtGui, QtWidgets


def create_font(font_size):
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(font_size)
    font.setBold(True)
    font.setWeight(75)
    return font


class Ui_DankMemerGrinder(object):
    def __init__(self, accounts):
        self.accounts = accounts

    def setupUi(self, DankMemerGrinder):
        DankMemerGrinder.setObjectName("DankMemerGrinder")
        DankMemerGrinder.resize(868, 535)
        self.central_widget = QtWidgets.QWidget(DankMemerGrinder)
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
            "}\n"
            "QCheckBox::indicator:unchecked{\n"
            '    image: url(":/icons/icons/off-button.png");\n'
            '    width: "40px";\n'
            '    height: "40px";\n'
            "}\n"
            "QCheckBox::indicator:checked{\n"
            '    image: url(":/icons/icons/on-button.png");\n'
            '    width: "40px";\n'
            '    height: "40px";\n'
            "}\n"
            "\n"
            "QSpinBox{\n"
            "    background-color: #5c6066;\n"
            "    border-radius: 10px;\n"
            "}\n"
            "QSpinBox::up-button{\n"
            "    width: 20px;\n"
            "}\n"
            "QSpinBox::down-button{\n"
            "    width: 20px;\n"
            "}\n"
            "\n"
            "/* QScrollBar Vertical */\n"
            "QScrollBar:vertical {\n"
            "    width: 14px;\n"
            "    margin: 15px 0 15px 0;\n"
            "    border: 1px transparent #2A2929;\n"
            "    border-radius: 7px;\n"
            "    background: #202225;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:vertical {    \n"
            "    background-color: #5865f2;\n"
            "    min-height: 30px;\n"
            "    border-radius: 7px;\n"
            "}\n"
            "QScrollBar::handle:vertical:hover{    \n"
            "    background-color: #525ee5;\n"
            "}\n"
            "QScrollBar::handle:vertical:pressed {    \n"
            "    background-color: #454fbf;\n"
            "}\n"
            "\n"
            "QScrollBar::sub-line:vertical {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::add-line:vertical {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "/* QScrollBar Horizontal */\n"
            "QScrollBar:horizontal {\n"
            "    height: 14px;\n"
            "    margin: 0 15px 0 15px;\n"
            "    border: 1px transparent #2A2929;\n"
            "    border-radius: 7px;\n"
            "    background: #40444b;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:horizontal {\n"
            "    background-color: #5865f2;\n"
            "    min-width: 30px;\n"
            "    border-radius: 7px;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:horizontal:hover{    \n"
            "    background-color: #525ee5;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:horizontal:pressed {    \n"
            "    background-color: #454fbf;\n"
            "}\n"
            "\n"
            "QScrollBar::sub-line:horizontal {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::add-line:horizontal {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {\n"
            "    background: none;\n"
            "}\n"
            "\n"
            "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
            "    background: none;\n"
            "}"
        )
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.header_frame = QtWidgets.QFrame(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_frame.sizePolicy().hasHeightForWidth())
        self.header_frame.setSizePolicy(sizePolicy)
        self.header_frame.setMinimumSize(QtCore.QSize(850, 65))
        self.header_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.header_frame.setStyleSheet(
            "#header_frame{\n"
            "    background-color: #202225;\n"
            "    border-radius: 20px;\n"
            "}"
        )
        self.header_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.header_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.header_frame.setObjectName("header_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.header_frame)
        self.horizontalLayout_3.setContentsMargins(6, 0, 6, 0)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.header_frame)
        self.scrollArea.setStyleSheet("")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 803, 72))
        self.scrollAreaWidgetContents.setStyleSheet(
            "QPushButton {\npadding: 0 5px 0 5px;\n}"
        )
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.addWidget(self.scrollArea)
        self.add_account_frame = QtWidgets.QFrame(self.header_frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.add_account_frame.sizePolicy().hasHeightForWidth()
        )
        self.add_account_frame.setSizePolicy(sizePolicy)
        self.add_account_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.add_account_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.add_account_frame.setObjectName("add_account_frame")
        self.verticalLayout_85 = QtWidgets.QVBoxLayout(self.add_account_frame)
        self.verticalLayout_85.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_85.setObjectName("verticalLayout_85")
        self.add_account_btn = QtWidgets.QPushButton(self.add_account_frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.add_account_btn.sizePolicy().hasHeightForWidth()
        )
        self.add_account_btn.setSizePolicy(sizePolicy)
        self.add_account_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.add_account_btn.setStyleSheet("background-color : #00FFFFFF;")
        self.add_account_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Active, QtGui.QIcon.On
        )
        self.add_account_btn.setIcon(icon1)
        self.add_account_btn.setIconSize(QtCore.QSize(25, 25))
        self.add_account_btn.setObjectName("add_account_btn")
        self.verticalLayout_85.addWidget(self.add_account_btn)
        self.minus_account_btn = QtWidgets.QPushButton(self.add_account_frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.minus_account_btn.sizePolicy().hasHeightForWidth()
        )
        self.minus_account_btn.setSizePolicy(sizePolicy)
        self.minus_account_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.minus_account_btn.setStyleSheet("background-color : #00FFFFFF;")
        self.minus_account_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus.png"), QtGui.QIcon.Active, QtGui.QIcon.On
        )
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus.svg"),
            QtGui.QIcon.Selected,
            QtGui.QIcon.Off,
        )
        self.minus_account_btn.setIcon(icon2)
        self.minus_account_btn.setIconSize(QtCore.QSize(25, 25))
        self.minus_account_btn.setObjectName("minus_account_btn")
        self.verticalLayout_85.addWidget(self.minus_account_btn)
        self.horizontalLayout_3.addWidget(self.add_account_frame)
        self.verticalLayout.addWidget(self.header_frame, 0, QtCore.Qt.AlignTop)
        self.main_frame = QtWidgets.QFrame(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy)
        self.main_frame.setMinimumSize(QtCore.QSize(850, 0))
        self.main_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.main_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setObjectName("main_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.main_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.side_menu_widget = QtWidgets.QWidget(self.main_frame)
        self.side_menu_widget.setStyleSheet(
            "#side_menu_widget{\n"
            "    background-color: #202225;\n"
            "    border-radius: 20px;\n"
            "}"
        )
        self.side_menu_widget.setObjectName("side_menu_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.side_menu_widget)
        self.verticalLayout_2.setContentsMargins(6, 8, 6, 8)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.buttons = QtWidgets.QFrame(self.side_menu_widget)
        self.buttons.setMinimumSize(QtCore.QSize(150, 0))
        self.buttons.setMaximumSize(QtCore.QSize(150, 16777215))
        self.buttons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttons.setObjectName("buttons")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.buttons)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(8)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        sidebar_buttons = ["home", "settings", "commands", "auto_buy", "auto_use"]
        for button in sidebar_buttons:
            setattr(self, f"{button}_btn", QtWidgets.QPushButton(self.buttons))
            getattr(self, f"{button}_btn").setMinimumSize(QtCore.QSize(0, 45))
            getattr(self, f"{button}_btn").setMaximumSize(QtCore.QSize(16777215, 45))
            getattr(self, f"{button}_btn").setFont(create_font(12))
            getattr(self, f"{button}_btn").setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor)
            )
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(f":/icons/icons/{button}.png"),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off,
            )
            getattr(self, f"{button}_btn").setIcon(icon)
            getattr(self, f"{button}_btn").setIconSize(QtCore.QSize(20, 20))
            getattr(self, f"{button}_btn").setObjectName(f"{button}_btn")
            self.verticalLayout_3.addWidget(getattr(self, f"{button}_btn"))
        self.verticalLayout_2.addWidget(self.buttons, 0, QtCore.Qt.AlignTop)
        self.toggle = QtWidgets.QPushButton(self.side_menu_widget)
        self.toggle.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggle.sizePolicy().hasHeightForWidth())
        self.toggle.setSizePolicy(sizePolicy)
        self.toggle.setMinimumSize(QtCore.QSize(0, 45))
        self.toggle.setMaximumSize(QtCore.QSize(16777215, 45))
        self.toggle.setFont(create_font(12))
        self.toggle.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggle.setStyleSheet("background-color : #d83c3e")
        self.toggle.setObjectName("toggle")
        self.verticalLayout_2.addWidget(self.toggle)
        self.horizontalLayout.addWidget(self.side_menu_widget)
        self.main_menu_widget = QtWidgets.QStackedWidget(self.main_frame)
        self.main_menu_widget.setObjectName("main_menu_widget")
        self.horizontalLayout.addWidget(self.main_menu_widget)
        self.verticalLayout.addWidget(self.main_frame)
        DankMemerGrinder.setCentralWidget(self.central_widget)
        self.main_menu_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DankMemerGrinder)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    DankMemerGrinder = QtWidgets.QMainWindow()
    ui = Ui_DankMemerGrinder()
    ui.setupUi(DankMemerGrinder)
    DankMemerGrinder.show()
    sys.exit(app.exec_())
