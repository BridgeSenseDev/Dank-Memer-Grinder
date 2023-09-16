from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


def create_font(font_size):
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(font_size)
    font.setBold(True)
    font.setWeight(75)
    return font


class UiUpdater(object):
    def __init__(self):
        self.vertical_layout = None
        self.vertical_layout_2 = None
        self.vertical_layout_3 = None

        self.horizontal_layout = None
        self.horizontal_layout_2 = None
        self.horizontal_layout_3 = None

        self.central_widget = None
        self.main_frame = None
        self.header_frame = None
        self.side_menu_widget = None

        self.label = None
        self.label_2 = None
        self.changelog_label = None

        self.buttons_frame = None
        self.update_btn = None
        self.skip_btn = None

        self.changelog_frame = None

    def setup_ui(self, updater_ui):
        updater_ui.setObjectName("Updater")
        updater_ui.resize(467, 307)
        self.central_widget = QtWidgets.QWidget(updater_ui)
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
        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setObjectName("vertical_layout")
        self.header_frame = QtWidgets.QFrame(self.central_widget)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.header_frame.sizePolicy().hasHeightForWidth()
        )
        self.header_frame.setSizePolicy(size_policy)
        self.header_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.header_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.header_frame.setObjectName("header_frame")
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.header_frame)
        self.horizontal_layout.setObjectName("horizontal_layout")
        self.label = QtWidgets.QLabel(self.header_frame)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(size_policy)
        self.label.setFont(create_font(25))
        self.label.setStyleSheet(
            "#side_menu_widget{\n"
            "    background-color: #202225;\n"
            "    border-radius: 20px;\n"
            "}"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.horizontal_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.header_frame)
        self.main_frame = QtWidgets.QFrame(self.central_widget)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(size_policy)
        self.main_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.main_frame.setObjectName("main_frame")
        self.horizontal_layout_2 = QtWidgets.QHBoxLayout(self.main_frame)
        self.horizontal_layout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_2.setSpacing(0)
        self.horizontal_layout_2.setObjectName("horizontal_layout_2")
        self.side_menu_widget = QtWidgets.QWidget(self.main_frame)
        self.side_menu_widget.setMinimumSize(QtCore.QSize(120, 0))
        self.side_menu_widget.setMaximumSize(QtCore.QSize(120, 16777215))
        self.side_menu_widget.setStyleSheet(
            "background-color: #202225; border-radius: 20px;"
        )
        self.side_menu_widget.setObjectName("side_menu_widget")
        self.vertical_layout_2 = QtWidgets.QVBoxLayout(self.side_menu_widget)
        self.vertical_layout_2.setObjectName("vertical_layout_2")
        self.label_2 = QtWidgets.QLabel(self.side_menu_widget)
        self.label_2.setMinimumSize(QtCore.QSize(100, 100))
        self.label_2.setMaximumSize(QtCore.QSize(100, 100))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/icons/icon.ico"))
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.vertical_layout_2.addWidget(self.label_2)
        self.buttons_frame = QtWidgets.QFrame(self.side_menu_widget)
        self.buttons_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.buttons_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.buttons_frame.setObjectName("buttons_frame")
        self.vertical_layout_3 = QtWidgets.QVBoxLayout(self.buttons_frame)
        self.vertical_layout_3.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout_3.setObjectName("vertical_layout_3")
        self.update_btn = QtWidgets.QPushButton(self.buttons_frame)
        self.update_btn.setEnabled(True)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.update_btn.sizePolicy().hasHeightForWidth())
        self.update_btn.setSizePolicy(size_policy)
        self.update_btn.setMinimumSize(QtCore.QSize(100, 45))
        self.update_btn.setMaximumSize(QtCore.QSize(100, 45))
        self.update_btn.setFont(create_font(12))
        self.update_btn.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_btn.setStyleSheet("background-color : #2d7d46")
        self.update_btn.setObjectName("update_btn")
        self.vertical_layout_3.addWidget(self.update_btn)
        self.skip_btn = QtWidgets.QPushButton(self.buttons_frame)
        self.skip_btn.setEnabled(True)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.skip_btn.sizePolicy().hasHeightForWidth())
        self.skip_btn.setSizePolicy(size_policy)
        self.skip_btn.setMinimumSize(QtCore.QSize(100, 45))
        self.skip_btn.setMaximumSize(QtCore.QSize(100, 45))
        self.skip_btn.setFont(create_font(12))
        self.skip_btn.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.skip_btn.setStyleSheet("background-color : #d83c3e")
        self.skip_btn.setObjectName("skip_btn")
        self.vertical_layout_3.addWidget(self.skip_btn)
        self.vertical_layout_2.addWidget(
            self.buttons_frame, 0, Qt.AlignmentFlag.AlignBottom
        )
        self.horizontal_layout_2.addWidget(self.side_menu_widget)
        self.changelog_frame = QtWidgets.QFrame(self.main_frame)
        self.changelog_frame.setStyleSheet("")
        self.changelog_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.changelog_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.changelog_frame.setObjectName("changelog_frame")
        self.horizontal_layout_3 = QtWidgets.QHBoxLayout(self.changelog_frame)
        self.horizontal_layout_3.setObjectName("horizontal_layout_3")
        self.changelog_label = QtWidgets.QLabel(self.changelog_frame)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.changelog_label.setFont(font)
        self.changelog_label.setText("")
        self.changelog_label.setAlignment(
            Qt.AlignLeading | Qt.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.changelog_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse
            | Qt.TextSelectableByKeyboard
            | Qt.TextSelectableByMouse
        )
        self.changelog_label.setObjectName("changelog_label")
        self.horizontal_layout_3.addWidget(self.changelog_label)
        self.horizontal_layout_2.addWidget(self.changelog_frame)
        self.vertical_layout.addWidget(self.main_frame)
        updater_ui.setCentralWidget(self.central_widget)

        QtCore.QMetaObject.connectSlotsByName(updater_ui)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Updater = QtWidgets.QMainWindow()
    ui = UiUpdater()
    ui.setup_ui(Updater)
    Updater.show()
    sys.exit(app.exec_())
