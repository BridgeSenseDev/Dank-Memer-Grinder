import json
import math

from PyQt5 import QtCore, QtGui, QtWidgets


def create_font(font_size):
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(font_size)
    font.setBold(True)
    font.setWeight(75)
    return font


def load_account(self, account_id, config_example):
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
    commands = list(config_example["commands"].keys())

    # Account btn
    setattr(
        self.ui,
        f"account_btn_{account_id}",
        QtWidgets.QPushButton(self.ui.scrollAreaWidgetContents),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"account_btn_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"account_btn_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"account_btn_{account_id}").setMinimumSize(QtCore.QSize(0, 45))
    getattr(self.ui, f"account_btn_{account_id}").setMaximumSize(QtCore.QSize(150, 45))
    getattr(self.ui, f"account_btn_{account_id}").setFont(create_font(12))
    getattr(self.ui, f"account_btn_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    icon = QtGui.QIcon()
    icon.addPixmap(
        QtGui.QPixmap(":/icons/icons/user.png"),
        QtGui.QIcon.Normal,
        QtGui.QIcon.Off,
    )
    getattr(self.ui, f"account_btn_{account_id}").setIcon(icon)
    getattr(self.ui, f"account_btn_{account_id}").setIconSize(QtCore.QSize(22, 22))
    getattr(self.ui, f"account_btn_{account_id}").setObjectName(
        f"account_btn_{account_id}"
    )
    self.ui.horizontalLayout_5.addWidget(getattr(self.ui, f"account_btn_{account_id}"))

    # Account settings
    setattr(self.ui, f"account_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"account_widget_{account_id}").setObjectName(
        f"account_widget_{account_id}"
    )
    self.ui.horizontalLayout_29 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"account_widget_{account_id}")
    )
    self.ui.horizontalLayout_29.setObjectName("horizontalLayout_29")
    setattr(
        self.ui,
        f"main_menu_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"account_widget_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"main_menu_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"main_menu_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"main_menu_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"main_menu_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"main_menu_frame_{account_id}").setObjectName(
        f"main_menu_frame_{account_id}"
    )
    self.ui.verticalLayout_4 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"main_menu_frame_{account_id}")
    )
    self.ui.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
    self.ui.verticalLayout_4.setSpacing(0)
    self.ui.verticalLayout_4.setObjectName("verticalLayout_4")
    setattr(
        self.ui,
        f"main_menu_widget_{account_id}",
        QtWidgets.QStackedWidget(getattr(self.ui, f"main_menu_frame_{account_id}")),
    )
    getattr(self.ui, f"main_menu_widget_{account_id}").setObjectName(
        f"main_menu_widget_{account_id}"
    )

    # Home widget
    setattr(self.ui, f"home_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"home_widget_{account_id}").setObjectName(
        f"home_widget_{account_id}"
    )
    self.ui.verticalLayout_6 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"home_widget_{account_id}")
    )
    self.ui.verticalLayout_6.setObjectName("verticalLayout_6")
    setattr(
        self.ui,
        f"home_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"home_widget_{account_id}")),
    )
    getattr(self.ui, f"home_label_{account_id}").setMinimumSize(QtCore.QSize(0, 50))
    getattr(self.ui, f"home_label_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"home_label_{account_id}").setFont(create_font(25))
    getattr(self.ui, f"home_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"home_label_{account_id}").setObjectName(
        f"home_label_{account_id}"
    )
    self.ui.verticalLayout_6.addWidget(
        getattr(self.ui, f"home_label_{account_id}"), 0, QtCore.Qt.AlignTop
    )
    setattr(
        self.ui,
        f"home_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"home_widget_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"home_frame_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"home_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"home_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"home_frame_{account_id}").setFrameShadow(QtWidgets.QFrame.Raised)
    getattr(self.ui, f"home_frame_{account_id}").setObjectName(
        f"home_frame_{account_id}"
    )
    self.ui.horizontalLayout_2 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"home_frame_{account_id}")
    )
    self.ui.horizontalLayout_2.setObjectName("horizontalLayout_2")
    setattr(
        self.ui,
        f"output_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"home_frame_{account_id}")),
    )
    getattr(self.ui, f"output_frame_{account_id}").setStyleSheet(
        "background-color: #40444b; border-radius: 20px;"
    )
    getattr(self.ui, f"output_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"output_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"output_frame_{account_id}").setObjectName(
        f"output_frame_{account_id}"
    )
    self.ui.verticalLayout_11 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"output_frame_{account_id}")
    )
    self.ui.verticalLayout_11.setObjectName("verticalLayout_11")
    setattr(
        self.ui,
        f"output_text_{account_id}",
        QtWidgets.QTextEdit(getattr(self.ui, f"output_frame_{account_id}")),
    )
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(12)
    getattr(self.ui, f"output_text_{account_id}").setFont(font)
    getattr(self.ui, f"output_text_{account_id}").setReadOnly(True)
    getattr(self.ui, f"output_text_{account_id}").setObjectName(
        f"output_text_{account_id}"
    )
    self.ui.verticalLayout_11.addWidget(getattr(self.ui, f"output_text_{account_id}"))
    self.ui.horizontalLayout_2.addWidget(getattr(self.ui, f"output_frame_{account_id}"))
    setattr(
        self.ui,
        f"output_scrollbar_{account_id}",
        QtWidgets.QScrollBar(getattr(self.ui, f"home_frame_{account_id}")),
    )
    getattr(self.ui, f"output_scrollbar_{account_id}").setOrientation(
        QtCore.Qt.Vertical
    )
    getattr(self.ui, f"output_scrollbar_{account_id}").setObjectName(
        f"output_scrollbar_{account_id}"
    )
    self.ui.horizontalLayout_2.addWidget(
        getattr(self.ui, f"output_scrollbar_{account_id}")
    )
    self.ui.verticalLayout_6.addWidget(getattr(self.ui, f"home_frame_{account_id}"))
    getattr(self.ui, f"main_menu_widget_{account_id}").addWidget(
        getattr(self.ui, f"home_widget_{account_id}")
    )

    # Settings widget
    setattr(self.ui, f"settings_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"settings_widget_{account_id}").setObjectName(
        f"settings_widget_{account_id}"
    )
    self.ui.verticalLayout_7 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"settings_widget_{account_id}")
    )
    self.ui.verticalLayout_7.setObjectName("verticalLayout_7")
    setattr(
        self.ui,
        f"settings_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"settings_widget_{account_id}")),
    )
    getattr(self.ui, f"settings_label_{account_id}").setMinimumSize(QtCore.QSize(0, 50))
    getattr(self.ui, f"settings_label_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"settings_label_{account_id}").setFont(create_font(25))
    getattr(self.ui, f"settings_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"settings_label_{account_id}").setObjectName(
        f"settings_label_{account_id}"
    )
    self.ui.verticalLayout_7.addWidget(
        getattr(self.ui, f"settings_label_{account_id}"), 0, QtCore.Qt.AlignTop
    )
    setattr(
        self.ui,
        f"settings_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"settings_widget_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"settings_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"settings_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"settings_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"settings_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"settings_frame_{account_id}").setObjectName(
        f"settings_frame_{account_id}"
    )
    self.ui.verticalLayout_19 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"settings_frame_{account_id}")
    )
    self.ui.verticalLayout_19.setObjectName("verticalLayout_19")
    setattr(
        self.ui,
        f"token_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"settings_frame_{account_id}")),
    )
    getattr(self.ui, f"token_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"token_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"token_frame_{account_id}").setObjectName(
        f"token_frame_{account_id}"
    )
    self.ui.horizontalLayout_17 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"token_frame_{account_id}")
    )
    self.ui.horizontalLayout_17.setObjectName("horizontalLayout_17")
    setattr(
        self.ui,
        f"token_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"token_frame_{account_id}")),
    )
    getattr(self.ui, f"token_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"token_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"token_frame_2_{account_id}").setObjectName(
        f"token_frame_2_{account_id}"
    )
    self.ui.horizontalLayout_19 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"token_frame_2_{account_id}")
    )
    self.ui.horizontalLayout_19.setObjectName("horizontalLayout_19")
    setattr(
        self.ui,
        f"token_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"token_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"token_label_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"token_label_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"token_label_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"token_label_{account_id}").setObjectName(
        f"token_label_{account_id}"
    )
    self.ui.horizontalLayout_19.addWidget(getattr(self.ui, f"token_label_{account_id}"))
    setattr(
        self.ui,
        f"token_input_{account_id}",
        QtWidgets.QLineEdit(getattr(self.ui, f"token_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"token_input_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"token_input_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"token_input_{account_id}").setMinimumSize(QtCore.QSize(440, 0))
    getattr(self.ui, f"token_input_{account_id}").setMaximumSize(
        QtCore.QSize(440, 16777215)
    )
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(12)
    getattr(self.ui, f"token_input_{account_id}").setFont(font)
    getattr(self.ui, f"token_input_{account_id}").setStyleSheet(
        "background-color: #5c6066; border-radius: 10px;"
    )
    getattr(self.ui, f"token_input_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"token_input_{account_id}").setObjectName(
        f"token_input_{account_id}"
    )
    self.ui.horizontalLayout_19.addWidget(getattr(self.ui, f"token_input_{account_id}"))
    self.ui.horizontalLayout_17.addWidget(
        getattr(self.ui, f"token_frame_2_{account_id}")
    )
    self.ui.verticalLayout_19.addWidget(
        getattr(self.ui, f"token_frame_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
    )
    setattr(
        self.ui,
        f"channel_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"settings_frame_{account_id}")),
    )
    getattr(self.ui, f"channel_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"channel_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"channel_frame_{account_id}").setObjectName(
        f"channel_frame_{account_id}"
    )
    self.ui.horizontalLayout_22 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"channel_frame_{account_id}")
    )
    self.ui.horizontalLayout_22.setObjectName("horizontalLayout_22")
    setattr(
        self.ui,
        f"channel_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"channel_frame_{account_id}")),
    )
    getattr(self.ui, f"channel_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"channel_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"channel_frame_2_{account_id}").setObjectName(
        f"channel_frame_2_{account_id}"
    )
    self.ui.horizontalLayout_21 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"channel_frame_2_{account_id}")
    )
    self.ui.horizontalLayout_21.setObjectName("horizontalLayout_21")
    setattr(
        self.ui,
        f"channel_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"channel_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"channel_label_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"channel_label_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"channel_label_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"channel_label_{account_id}").setObjectName(
        f"channel_label_{account_id}"
    )
    self.ui.horizontalLayout_21.addWidget(
        getattr(self.ui, f"channel_label_{account_id}")
    )
    setattr(
        self.ui,
        f"channel_input_{account_id}",
        QtWidgets.QLineEdit(getattr(self.ui, f"channel_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"channel_input_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"channel_input_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"channel_input_{account_id}").setMinimumSize(QtCore.QSize(200, 0))
    getattr(self.ui, f"channel_input_{account_id}").setMaximumSize(
        QtCore.QSize(500, 200)
    )
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(12)
    getattr(self.ui, f"channel_input_{account_id}").setFont(font)
    getattr(self.ui, f"channel_input_{account_id}").setStyleSheet(
        "background-color: #5c6066; border-radius: 10px;"
    )
    getattr(self.ui, f"channel_input_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"channel_input_{account_id}").setObjectName(
        f"channel_input_{account_id}"
    )
    self.ui.horizontalLayout_21.addWidget(
        getattr(self.ui, f"channel_input_{account_id}")
    )
    self.ui.horizontalLayout_22.addWidget(
        getattr(self.ui, f"channel_frame_2_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
    )
    self.ui.verticalLayout_19.addWidget(getattr(self.ui, f"channel_frame_{account_id}"))
    setattr(
        self.ui,
        f"trivia_correct_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"settings_frame_{account_id}")),
    )
    getattr(self.ui, f"trivia_correct_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"trivia_correct_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"trivia_correct_frame_{account_id}").setObjectName(
        f"trivia_correct_frame_{account_id}"
    )
    self.ui.horizontalLayout_25 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"trivia_correct_frame_{account_id}")
    )
    self.ui.horizontalLayout_25.setObjectName("horizontalLayout_25")
    setattr(
        self.ui,
        f"trivia_correct_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"trivia_correct_frame_{account_id}")),
    )
    getattr(self.ui, f"trivia_correct_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"trivia_correct_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"trivia_correct_frame_2_{account_id}").setObjectName(
        f"trivia_correct_frame_2_{account_id}"
    )
    self.ui.horizontalLayout_24 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"trivia_correct_frame_2_{account_id}")
    )
    self.ui.horizontalLayout_24.setObjectName("horizontalLayout_24")
    setattr(
        self.ui,
        f"trivia_correct_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"trivia_correct_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"trivia_correct_label_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"trivia_correct_label_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"trivia_correct_label_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"trivia_correct_label_{account_id}").setObjectName(
        f"trivia_correct_label_{account_id}"
    )
    self.ui.horizontalLayout_24.addWidget(
        getattr(self.ui, f"trivia_correct_label_{account_id}")
    )
    setattr(
        self.ui,
        f"trivia_correct_chance_{account_id}",
        QtWidgets.QSpinBox(getattr(self.ui, f"trivia_correct_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"trivia_correct_chance_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setMinimumSize(
        QtCore.QSize(50, 30)
    )
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setMaximumSize(
        QtCore.QSize(50, 30)
    )
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(12)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setFont(font)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setAutoFillBackground(False)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setStyleSheet("")
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setWrapping(False)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setFrame(True)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setAlignment(
        QtCore.Qt.AlignCenter
    )
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setMinimum(25)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setMaximum(100)
    getattr(self.ui, f"trivia_correct_chance_{account_id}").setObjectName(
        f"trivia_correct_chance_{account_id}"
    )
    self.ui.horizontalLayout_24.addWidget(
        getattr(self.ui, f"trivia_correct_chance_{account_id}")
    )
    self.ui.horizontalLayout_25.addWidget(
        getattr(self.ui, f"trivia_correct_frame_2_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter,
    )
    self.ui.verticalLayout_19.addWidget(
        getattr(self.ui, f"trivia_correct_frame_{account_id}"),
        0,
        QtCore.Qt.AlignVCenter,
    )
    setattr(
        self.ui,
        f"toggles_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"settings_frame_{account_id}")),
    )
    getattr(self.ui, f"toggles_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"toggles_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"toggles_frame_{account_id}").setObjectName(
        f"toggles_frame_{account_id}"
    )
    self.horizontalLayout_6 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"toggles_frame_{account_id}")
    )
    self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
    self.horizontalLayout_6.setSpacing(0)
    self.horizontalLayout_6.setObjectName("horizontalLayout_6")
    setattr(
        self.ui,
        f"toggles_left_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"toggles_frame_{account_id}")),
    )
    getattr(self.ui, f"toggles_left_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"toggles_left_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"toggles_left_frame_{account_id}").setObjectName(
        f"toggles_left_frame_{account_id}"
    )
    self.verticalLayout_10 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"toggles_left_frame_{account_id}")
    )
    self.verticalLayout_10.setObjectName("verticalLayout_10")
    setattr(
        self.ui,
        f"toggles_left_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"toggles_left_frame_{account_id}")),
    )
    getattr(self.ui, f"toggles_left_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"toggles_left_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"toggles_left_frame_2_{account_id}").setObjectName(
        f"toggles_left_frame_2_{account_id}"
    )
    self.verticalLayout_15 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"toggles_left_frame_2_{account_id}")
    )
    self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout_15.setSpacing(0)
    self.verticalLayout_15.setObjectName("verticalLayout_15")
    setattr(
        self.ui,
        f"offline_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"toggles_left_frame_2_{account_id}")),
    )
    getattr(self.ui, f"offline_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"offline_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"offline_checkbox_{account_id}").setObjectName(
        f"offline_checkbox_{account_id}"
    )
    self.verticalLayout_15.addWidget(
        getattr(self.ui, f"offline_checkbox_{account_id}"), 0, QtCore.Qt.AlignHCenter
    )
    self.verticalLayout_10.addWidget(
        getattr(self.ui, f"toggles_left_frame_2_{account_id}")
    )
    self.horizontalLayout_6.addWidget(
        getattr(self.ui, f"toggles_left_frame_{account_id}")
    )
    setattr(
        self.ui,
        f"toggles_right_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"toggles_frame_{account_id}")),
    )
    getattr(self.ui, f"toggles_right_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"toggles_right_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"toggles_right_frame_{account_id}").setObjectName(
        f"toggles_right_frame_{account_id}"
    )
    self.verticalLayout_16 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"toggles_right_frame_{account_id}")
    )
    self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout_16.setSpacing(0)
    self.verticalLayout_16.setObjectName("verticalLayout_16")
    setattr(
        self.ui,
        f"toggles_right_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"toggles_right_frame_{account_id}")),
    )
    getattr(self.ui, f"toggles_right_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"toggles_right_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"toggles_right_frame_2_{account_id}").setObjectName(
        f"toggles_right_frame_2_{account_id}"
    )
    self.verticalLayout_17 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"toggles_right_frame_2_{account_id}")
    )
    self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout_17.setSpacing(0)
    self.verticalLayout_17.setObjectName("verticalLayout_17")
    setattr(
        self.ui,
        f"alerts_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"toggles_right_frame_2_{account_id}")),
    )
    getattr(self.ui, f"alerts_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"alerts_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"alerts_checkbox_{account_id}").setObjectName(
        f"alerts_checkbox_{account_id}"
    )
    self.verticalLayout_17.addWidget(
        getattr(self.ui, f"alerts_checkbox_{account_id}"), 0, QtCore.Qt.AlignHCenter
    )
    self.verticalLayout_16.addWidget(
        getattr(self.ui, f"toggles_right_frame_2_{account_id}")
    )
    self.horizontalLayout_6.addWidget(
        getattr(self.ui, f"toggles_right_frame_{account_id}")
    )
    self.ui.verticalLayout_19.addWidget(getattr(self.ui, f"toggles_frame_{account_id}"))
    self.ui.verticalLayout_7.addWidget(getattr(self.ui, f"settings_frame_{account_id}"))
    getattr(self.ui, f"main_menu_widget_{account_id}").addWidget(
        getattr(self.ui, f"settings_widget_{account_id}")
    )

    # Commands widget
    setattr(self.ui, f"commands_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"commands_widget_{account_id}").setObjectName(
        f"commands_widget_{account_id}"
    )
    self.ui.verticalLayout_8 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"commands_widget_{account_id}")
    )
    self.ui.verticalLayout_8.setObjectName("verticalLayout_8")
    setattr(
        self.ui,
        f"commands_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"commands_widget_{account_id}")),
    )
    getattr(self.ui, f"commands_label_{account_id}").setMinimumSize(QtCore.QSize(0, 50))
    getattr(self.ui, f"commands_label_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"commands_label_{account_id}").setFont(create_font(25))
    getattr(self.ui, f"commands_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"commands_label_{account_id}").setObjectName(
        f"commands_label_{account_id}"
    )
    self.ui.verticalLayout_8.addWidget(getattr(self.ui, f"commands_label_{account_id}"))
    setattr(
        self.ui,
        f"commands_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"commands_widget_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"commands_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"commands_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"commands_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"commands_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"commands_frame_{account_id}").setObjectName(
        f"commands_frame_{account_id}"
    )
    self.ui.verticalLayout_12 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"commands_frame_{account_id}")
    )
    self.ui.verticalLayout_12.setObjectName("verticalLayout_12")
    setattr(
        self.ui,
        f"commands_settings_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"commands_frame_{account_id}")),
    )
    getattr(self.ui, f"commands_settings_frame_{account_id}").setStyleSheet(
        "QSpinBox {"
        "    font-size: 14px;"
        "    font-weight: bold;"
        "}"
        "QSpinBox::up-button{"
        "    width: 0px;"
        "}"
        "QSpinBox::down-button{"
        "    width: 0px;"
        "}"
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"commands_settings_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"commands_settings_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"commands_settings_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"commands_settings_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"commands_settings_frame_{account_id}").setObjectName(
        f"commands_settings_frame_{account_id}"
    )
    self.ui.horizontalLayout_4 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"commands_settings_frame_{account_id}")
    )
    self.ui.horizontalLayout_4.setSpacing(50)
    self.ui.horizontalLayout_4.setObjectName("horizontalLayout_4")
    for i in ["left", "right"]:
        setattr(
            self.ui,
            f"commands_settings_{i}_frame_{account_id}",
            QtWidgets.QFrame(getattr(self.ui, f"commands_settings_frame_{account_id}")),
        )
        getattr(self.ui, f"commands_settings_{i}_frame_{account_id}").setFrameShape(
            QtWidgets.QFrame.StyledPanel
        )
        getattr(self.ui, f"commands_settings_{i}_frame_{account_id}").setFrameShadow(
            QtWidgets.QFrame.Raised
        )
        getattr(self.ui, f"commands_settings_{i}_frame_{account_id}").setObjectName(
            f"commands_settings_{i}_frame_{account_id}"
        )
        self.ui.verticalLayout_20 = QtWidgets.QVBoxLayout(
            getattr(self.ui, f"commands_settings_{i}_frame_{account_id}")
        )
        self.ui.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.ui.verticalLayout_20.setSpacing(0)
        self.ui.verticalLayout_20.setObjectName("verticalLayout_20")
        setattr(
            self.ui,
            f"commands_settings_{i}_frame_2_{account_id}",
            QtWidgets.QFrame(
                getattr(self.ui, f"commands_settings_{i}_frame_{account_id}")
            ),
        )
        getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}").setFrameShape(
            QtWidgets.QFrame.StyledPanel
        )
        getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}").setFrameShadow(
            QtWidgets.QFrame.Raised
        )
        getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}").setObjectName(
            f"commands_settings_{i}_frame_2_{account_id}"
        )
        self.ui.verticalLayout_13 = QtWidgets.QVBoxLayout(
            getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
        )
        self.ui.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.ui.verticalLayout_13.setSpacing(0)
        self.ui.verticalLayout_13.setObjectName("verticalLayout_13")
        if i == "left":
            commands_list = commands[: math.floor(len(commands) / 2)]
        elif i == "right":
            commands_list = commands[math.floor(len(commands) / 2) :]
        for command in commands_list:
            setattr(
                self.ui,
                f"{command}_frame_{account_id}",
                QtWidgets.QFrame(
                    getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
                ),
            )
            getattr(self.ui, f"{command}_frame_{account_id}").setFrameShape(
                QtWidgets.QFrame.StyledPanel
            )
            getattr(self.ui, f"{command}_frame_{account_id}").setFrameShadow(
                QtWidgets.QFrame.Raised
            )
            getattr(self.ui, f"{command}_frame_{account_id}").setObjectName(
                f"{command}_frame_{account_id}"
            )
            setattr(
                self.ui,
                f"horizontalLayout_{int(account_id) + 30}",
                QtWidgets.QHBoxLayout(
                    getattr(self.ui, f"{command}_frame_{account_id}")
                ),
            )
            getattr(
                self.ui, f"horizontalLayout_{int(account_id) + 30}"
            ).setContentsMargins(0, 0, 0, 0)
            getattr(self.ui, f"horizontalLayout_{int(account_id) + 30}").setObjectName(
                f"horizontalLayout_{int(account_id) + 30}"
            )
            setattr(
                self.ui,
                f"{command}_spinbox_{account_id}",
                QtWidgets.QSpinBox(getattr(self.ui, f"{command}_frame_{account_id}")),
            )
            getattr(self.ui, f"{command}_spinbox_{account_id}").setMinimumSize(
                QtCore.QSize(45, 25)
            )
            getattr(self.ui, f"{command}_spinbox_{account_id}").setMaximumSize(
                QtCore.QSize(45, 25)
            )
            font = QtGui.QFont()
            font.setFamily("Segoe UI")
            font.setBold(True)
            font.setWeight(75)
            getattr(self.ui, f"{command}_spinbox_{account_id}").setFont(font)
            getattr(self.ui, f"{command}_spinbox_{account_id}").setStyleSheet("")
            getattr(self.ui, f"{command}_spinbox_{account_id}").setAlignment(
                QtCore.Qt.AlignCenter
            )
            getattr(self.ui, f"{command}_spinbox_{account_id}").setButtonSymbols(
                QtWidgets.QAbstractSpinBox.NoButtons
            )
            getattr(self.ui, f"{command}_spinbox_{account_id}").setMaximum(100000)
            getattr(self.ui, f"{command}_spinbox_{account_id}").setProperty("value", 0)
            getattr(self.ui, f"{command}_spinbox_{account_id}").setObjectName(
                f"{command}_spinbox_{account_id}"
            )
            getattr(self.ui, f"horizontalLayout_{int(account_id) + 30}").addWidget(
                getattr(self.ui, f"{command}_spinbox_{account_id}")
            )
            setattr(
                self.ui,
                f"{command}_checkbox_{account_id}",
                QtWidgets.QCheckBox(
                    getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
                ),
            )
            getattr(self.ui, f"{command}_checkbox_{account_id}").setFont(
                create_font(15)
            )
            getattr(self.ui, f"{command}_checkbox_{account_id}").setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor)
            )
            getattr(self.ui, f"{command}_checkbox_{account_id}").setObjectName(
                f"{command}_checkbox_{account_id}"
            )
            getattr(self.ui, f"horizontalLayout_{int(account_id) + 30}").addWidget(
                getattr(self.ui, f"{command}_checkbox_{account_id}")
            )
            self.ui.verticalLayout_13.addWidget(
                getattr(self.ui, f"{command}_frame_{account_id}")
            )
        self.ui.verticalLayout_20.addWidget(
            getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
        )
        self.ui.horizontalLayout_4.addWidget(
            getattr(self.ui, f"commands_settings_{i}_frame_{account_id}"),
            0,
            QtCore.Qt.AlignRight,
        )

    self.ui.verticalLayout_12.addWidget(
        getattr(self.ui, f"commands_settings_frame_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter,
    )
    setattr(
        self.ui,
        f"commands_toggle_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"commands_frame_{account_id}")),
    )
    getattr(self.ui, f"commands_toggle_frame_{account_id}").setMinimumSize(
        QtCore.QSize(0, 50)
    )
    getattr(self.ui, f"commands_toggle_frame_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"commands_toggle_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"commands_toggle_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"commands_toggle_frame_{account_id}").setObjectName(
        f"commands_toggle_frame_{account_id}"
    )
    self.ui.horizontalLayout_26 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"commands_toggle_frame_{account_id}")
    )
    self.ui.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
    self.ui.horizontalLayout_26.setSpacing(0)
    self.ui.horizontalLayout_26.setObjectName("horizontalLayout_26")
    setattr(
        self.ui,
        f"commands_toggle_btn_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"commands_toggle_frame_{account_id}")),
    )
    getattr(self.ui, f"commands_toggle_btn_{account_id}").setLayoutDirection(
        QtCore.Qt.LeftToRight
    )
    getattr(self.ui, f"commands_toggle_btn_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"commands_toggle_btn_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"commands_toggle_btn_{account_id}").setObjectName(
        f"commands_toggle_btn_{account_id}"
    )
    self.ui.horizontalLayout_27 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"commands_toggle_btn_{account_id}")
    )
    self.ui.horizontalLayout_27.setContentsMargins(0, 0, 0, 0)
    self.ui.horizontalLayout_27.setSpacing(10)
    self.ui.horizontalLayout_27.setObjectName("horizontalLayout_27")
    setattr(
        self.ui,
        f"start_btn_{account_id}",
        QtWidgets.QPushButton(getattr(self.ui, f"commands_toggle_btn_{account_id}")),
    )
    getattr(self.ui, f"start_btn_{account_id}").setEnabled(True)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"start_btn_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"start_btn_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"start_btn_{account_id}").setMinimumSize(QtCore.QSize(140, 45))
    getattr(self.ui, f"start_btn_{account_id}").setMaximumSize(QtCore.QSize(50, 45))
    getattr(self.ui, f"start_btn_{account_id}").setFont(create_font(12))
    getattr(self.ui, f"start_btn_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"start_btn_{account_id}").setStyleSheet(
        "background-color : #2d7d46"
    )
    getattr(self.ui, f"start_btn_{account_id}").setObjectName(f"start_btn_{account_id}")
    self.ui.horizontalLayout_27.addWidget(getattr(self.ui, f"start_btn_{account_id}"))
    setattr(
        self.ui,
        f"stop_btn_{account_id}",
        QtWidgets.QPushButton(getattr(self.ui, f"commands_toggle_btn_{account_id}")),
    )
    getattr(self.ui, f"stop_btn_{account_id}").setEnabled(True)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"stop_btn_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"stop_btn_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"stop_btn_{account_id}").setMinimumSize(QtCore.QSize(140, 45))
    getattr(self.ui, f"stop_btn_{account_id}").setMaximumSize(QtCore.QSize(50, 45))
    getattr(self.ui, f"stop_btn_{account_id}").setFont(create_font(12))
    getattr(self.ui, f"stop_btn_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"stop_btn_{account_id}").setStyleSheet(
        "background-color : #d83c3e"
    )
    getattr(self.ui, f"stop_btn_{account_id}").setObjectName(f"stop_btn_{account_id}")
    self.ui.horizontalLayout_27.addWidget(getattr(self.ui, f"stop_btn_{account_id}"))
    self.ui.horizontalLayout_26.addWidget(
        getattr(self.ui, f"commands_toggle_btn_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
    )
    self.ui.verticalLayout_12.addWidget(
        getattr(self.ui, f"commands_toggle_frame_{account_id}"),
        0,
        QtCore.Qt.AlignBottom,
    )
    self.ui.verticalLayout_8.addWidget(getattr(self.ui, f"commands_frame_{account_id}"))
    getattr(self.ui, f"main_menu_widget_{account_id}").addWidget(
        getattr(self.ui, f"commands_widget_{account_id}")
    )

    # Autobuy Widget
    setattr(self.ui, f"auto_buy_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"auto_buy_widget_{account_id}").setObjectName(
        f"auto_buy_widget_{account_id}"
    )
    self.ui.verticalLayout_9 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"auto_buy_widget_{account_id}")
    )
    self.ui.verticalLayout_9.setObjectName("verticalLayout_9")
    setattr(
        self.ui,
        f"auto_buy_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"auto_buy_widget_{account_id}")),
    )
    getattr(self.ui, f"auto_buy_label_{account_id}").setMinimumSize(QtCore.QSize(0, 50))
    getattr(self.ui, f"auto_buy_label_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"auto_buy_label_{account_id}").setFont(create_font(25))
    getattr(self.ui, f"auto_buy_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"auto_buy_label_{account_id}").setObjectName(
        f"auto_buy_label_{account_id}"
    )
    self.ui.verticalLayout_9.addWidget(getattr(self.ui, f"auto_buy_label_{account_id}"))
    setattr(
        self.ui,
        f"auto_buy_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_buy_widget_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"auto_buy_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"auto_buy_frame_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"auto_buy_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_buy_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_buy_frame_{account_id}").setObjectName(
        f"auto_buy_frame_{account_id}"
    )
    self.ui.verticalLayout_18 = QtWidgets.QVBoxLayout(
        getattr(self.ui, f"auto_buy_frame_{account_id}")
    )
    self.ui.verticalLayout_18.setObjectName("verticalLayout_18")
    setattr(
        self.ui,
        f"lifesavers_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_buy_frame_{account_id}")),
    )
    getattr(self.ui, f"lifesavers_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"lifesavers_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"lifesavers_frame_{account_id}").setObjectName(
        f"lifesavers_frame_{account_id}"
    )
    self.ui.horizontalLayout_16 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"lifesavers_frame_{account_id}")
    )
    self.ui.horizontalLayout_16.setObjectName("horizontalLayout_16")
    setattr(
        self.ui,
        f"lifesavers_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"lifesavers_frame_{account_id}")),
    )
    getattr(self.ui, f"lifesavers_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"lifesavers_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"lifesavers_frame_2_{account_id}").setObjectName(
        f"lifesavers_frame_2_{account_id}"
    )
    self.ui.horizontalLayout_15 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"lifesavers_frame_2_{account_id}")
    )
    self.ui.horizontalLayout_15.setObjectName("horizontalLayout_15")
    setattr(
        self.ui,
        f"lifesavers_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"lifesavers_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"lifesavers_checkbox_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setStyleSheet("")
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setObjectName(
        f"lifesavers_checkbox_{account_id}"
    )
    self.ui.horizontalLayout_15.addWidget(
        getattr(self.ui, f"lifesavers_checkbox_{account_id}")
    )
    setattr(
        self.ui,
        f"lifesavers_amount_{account_id}",
        QtWidgets.QSpinBox(getattr(self.ui, f"lifesavers_frame_2_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"lifesavers_amount_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"lifesavers_amount_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setMinimumSize(
        QtCore.QSize(50, 30)
    )
    getattr(self.ui, f"lifesavers_amount_{account_id}").setMaximumSize(
        QtCore.QSize(50, 30)
    )
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(12)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setFont(font)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setAutoFillBackground(False)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setStyleSheet("")
    getattr(self.ui, f"lifesavers_amount_{account_id}").setWrapping(False)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setFrame(True)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setAlignment(
        QtCore.Qt.AlignCenter
    )
    getattr(self.ui, f"lifesavers_amount_{account_id}").setMaximum(100)
    getattr(self.ui, f"lifesavers_amount_{account_id}").setObjectName(
        f"lifesavers_amount_{account_id}"
    )
    self.ui.horizontalLayout_15.addWidget(
        getattr(self.ui, f"lifesavers_amount_{account_id}")
    )
    self.ui.horizontalLayout_16.addWidget(
        getattr(self.ui, f"lifesavers_frame_2_{account_id}")
    )
    self.ui.verticalLayout_18.addWidget(
        getattr(self.ui, f"lifesavers_frame_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
    )
    setattr(
        self.ui,
        f"fishing_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_buy_frame_{account_id}")),
    )
    getattr(self.ui, f"fishing_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"fishing_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"fishing_frame_{account_id}").setObjectName(
        f"fishing_frame_{account_id}"
    )
    self.ui.horizontalLayout_12 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"fishing_frame_{account_id}")
    )
    self.ui.horizontalLayout_12.setObjectName("horizontalLayout_12")
    setattr(
        self.ui,
        f"fishing_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"fishing_frame_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"fishing_checkbox_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"fishing_checkbox_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"fishing_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"fishing_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"fishing_checkbox_{account_id}").setStyleSheet("")
    getattr(self.ui, f"fishing_checkbox_{account_id}").setObjectName(
        f"fishing_checkbox_{account_id}"
    )
    self.ui.horizontalLayout_12.addWidget(
        getattr(self.ui, f"fishing_checkbox_{account_id}")
    )
    self.ui.verticalLayout_18.addWidget(getattr(self.ui, f"fishing_frame_{account_id}"))
    setattr(
        self.ui,
        f"shovel_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_buy_frame_{account_id}")),
    )
    getattr(self.ui, f"shovel_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"shovel_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"shovel_frame_{account_id}").setObjectName("shovel_frame")
    self.ui.horizontalLayout_9 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"shovel_frame_{account_id}")
    )
    self.ui.horizontalLayout_9.setObjectName("horizontalLayout_9")
    setattr(
        self.ui,
        f"shovel_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"shovel_frame_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"shovel_checkbox_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"shovel_checkbox_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"shovel_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"shovel_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"shovel_checkbox_{account_id}").setStyleSheet("")
    getattr(self.ui, f"shovel_checkbox_{account_id}").setObjectName(
        f"shovel_checkbox_{account_id}"
    )
    self.ui.horizontalLayout_9.addWidget(
        getattr(self.ui, f"shovel_checkbox_{account_id}")
    )
    self.ui.verticalLayout_18.addWidget(getattr(self.ui, f"shovel_frame_{account_id}"))
    setattr(
        self.ui,
        f"rifle_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_buy_frame_{account_id}")),
    )
    getattr(self.ui, f"rifle_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"rifle_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"rifle_frame_{account_id}").setObjectName(
        f"rifle_frame_{account_id}"
    )
    self.ui.horizontalLayout_14 = QtWidgets.QHBoxLayout(
        getattr(self.ui, f"rifle_frame_{account_id}")
    )
    self.ui.horizontalLayout_14.setObjectName("horizontalLayout_14")
    setattr(
        self.ui,
        f"rifle_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"rifle_frame_{account_id}")),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        getattr(self.ui, f"rifle_checkbox_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"rifle_checkbox_{account_id}").setSizePolicy(size_policy)
    getattr(self.ui, f"rifle_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"rifle_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"rifle_checkbox_{account_id}").setStyleSheet("")
    getattr(self.ui, f"rifle_checkbox_{account_id}").setObjectName(
        f"rifle_checkbox_{account_id}"
    )
    self.ui.horizontalLayout_14.addWidget(
        getattr(self.ui, f"rifle_checkbox_{account_id}")
    )
    self.ui.verticalLayout_18.addWidget(getattr(self.ui, f"rifle_frame_{account_id}"))
    self.ui.verticalLayout_9.addWidget(getattr(self.ui, f"auto_buy_frame_{account_id}"))
    getattr(self.ui, f"main_menu_widget_{account_id}").addWidget(
        getattr(self.ui, f"auto_buy_widget_{account_id}")
    )

    # Autouse widget
    setattr(self.ui, f"auto_use_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"auto_use_widget_{account_id}").setObjectName(
        f"auto_use_widget_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 100}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"auto_use_widget_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 100}").setObjectName(
        f"verticallayout_{int(account_id) + 100}"
    )
    setattr(
        self.ui,
        f"auto_use_label_{account_id}",
        QtWidgets.QLabel(
            getattr(self.ui, f"auto_use_widget_{account_id}"),
        ),
    )
    getattr(self.ui, f"auto_use_label_{account_id}").setMinimumSize(QtCore.QSize(0, 50))
    getattr(self.ui, f"auto_use_label_{account_id}").setMaximumSize(
        QtCore.QSize(16777215, 50)
    )
    getattr(self.ui, f"auto_use_label_{account_id}").setFont(create_font(25))
    getattr(self.ui, f"auto_use_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"auto_use_label_{account_id}").setObjectName(
        f"auto_use_label_{account_id}"
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 100}").addWidget(
        getattr(self.ui, f"auto_use_label_{account_id}")
    )
    setattr(
        self.ui,
        f"auto_use_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_widget_{account_id}")),
    )
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        getattr(self.ui, f"auto_use_frame_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"auto_use_frame_{account_id}").setSizePolicy(sizePolicy)
    getattr(self.ui, f"auto_use_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_use_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_use_frame_{account_id}").setObjectName(
        f"auto_use_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"horizontallayout_{int(account_id) + 102}",
        QtWidgets.QHBoxLayout(getattr(self.ui, f"auto_use_frame_{account_id}")),
    )
    getattr(self.ui, f"horizontallayout_{int(account_id) + 102}").setObjectName(
        f"horizontallayout_{int(account_id) + 102}"
    )
    setattr(
        self.ui,
        f"auto_use_left_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_frame_{account_id}")),
    )
    getattr(self.ui, f"auto_use_left_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_use_left_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_use_left_frame_{account_id}").setObjectName(
        f"auto_use_left_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 101}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"auto_use_left_frame_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 101}").setObjectName(
        f"verticallayout_{int(account_id) + 101}"
    )
    setattr(
        self.ui,
        f"auto_use_left_frame_2_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_left_frame_{account_id}")),
    )
    getattr(self.ui, f"auto_use_left_frame_2_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_use_left_frame_2_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_use_left_frame_2_{account_id}").setObjectName(
        f"auto_use_left_frame_2_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 102}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"auto_use_left_frame_2_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 102}").setObjectName(
        f"verticallayout_{int(account_id) + 102}"
    )
    setattr(
        self.ui,
        f"auto_use_btn_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_left_frame_2_{account_id}")),
    )
    getattr(self.ui, f"auto_use_btn_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_use_btn_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_use_btn_frame_{account_id}").setObjectName(
        f"auto_use_btn_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 103}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"auto_use_btn_frame_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 103}").setObjectName(
        f"verticallayout_{int(account_id) + 103}"
    )
    setattr(
        self.ui,
        f"auto_use_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"auto_use_btn_frame_{account_id}")),
    )
    getattr(self.ui, f"auto_use_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"auto_use_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"auto_use_checkbox_{account_id}").setObjectName(
        f"auto_use_checkbox_{account_id}"
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 103}").addWidget(
        getattr(self.ui, f"auto_use_checkbox_{account_id}")
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"auto_use_btn_frame_{account_id}")
    )
    setattr(
        self.ui,
        f"search_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_left_frame_2_{account_id}")),
    )
    getattr(self.ui, f"search_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"search_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"search_frame_{account_id}").setObjectName(
        f"search_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 106}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"search_frame_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 106}").setObjectName(
        f"verticallayout_{int(account_id) + 106}"
    )
    setattr(
        self.ui,
        f"search_label_{account_id}",
        QtWidgets.QLabel(getattr(self.ui, f"search_frame_{account_id}")),
    )
    getattr(self.ui, f"search_label_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"search_label_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"search_label_{account_id}").setObjectName(
        f"search_label_{account_id}"
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 106}").addWidget(
        getattr(self.ui, f"search_label_{account_id}")
    )
    setattr(
        self.ui,
        f"search_input_{account_id}",
        QtWidgets.QLineEdit(getattr(self.ui, f"search_frame_{account_id}")),
    )
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        getattr(self.ui, f"search_input_{account_id}").sizePolicy().hasHeightForWidth()
    )
    getattr(self.ui, f"search_input_{account_id}").setSizePolicy(sizePolicy)
    getattr(self.ui, f"search_input_{account_id}").setMinimumSize(QtCore.QSize(200, 0))
    getattr(self.ui, f"search_input_{account_id}").setMaximumSize(QtCore.QSize(500, 30))
    getattr(self.ui, f"search_input_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"search_input_{account_id}").setStyleSheet(
        "background-color: #5c6066; border-radius: 10px;"
    )
    getattr(self.ui, f"search_input_{account_id}").setAlignment(QtCore.Qt.AlignCenter)
    getattr(self.ui, f"search_input_{account_id}").setObjectName(
        f"search_input_{account_id}"
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 106}").addWidget(
        getattr(self.ui, f"search_input_{account_id}")
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"search_frame_{account_id}")
    )
    setattr(
        self.ui,
        f"hide_disabled_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_left_frame_2_{account_id}")),
    )
    getattr(self.ui, f"hide_disabled_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"hide_disabled_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"hide_disabled_frame_{account_id}").setObjectName(
        f"hide_disabled_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 105}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"hide_disabled_frame_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 105}").setObjectName(
        f"verticallayout_{int(account_id) + 105}"
    )
    setattr(
        self.ui,
        f"hide_disabled_checkbox_{account_id}",
        QtWidgets.QCheckBox(getattr(self.ui, f"hide_disabled_frame_{account_id}")),
    )
    getattr(self.ui, f"hide_disabled_checkbox_{account_id}").setFont(create_font(15))
    getattr(self.ui, f"hide_disabled_checkbox_{account_id}").setCursor(
        QtGui.QCursor(QtCore.Qt.PointingHandCursor)
    )
    getattr(self.ui, f"hide_disabled_checkbox_{account_id}").setObjectName(
        f"hide_disabled_checkbox_{account_id}"
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 105}").addWidget(
        getattr(self.ui, f"hide_disabled_checkbox_{account_id}")
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"hide_disabled_frame_{account_id}")
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 101}").addWidget(
        getattr(self.ui, f"auto_use_left_frame_2_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter,
    )
    getattr(self.ui, f"horizontallayout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"auto_use_left_frame_{account_id}")
    )
    setattr(
        self.ui,
        f"auto_use_right_frame_{account_id}",
        QtWidgets.QFrame(getattr(self.ui, f"auto_use_frame_{account_id}")),
    )
    getattr(self.ui, f"auto_use_right_frame_{account_id}").setFrameShape(
        QtWidgets.QFrame.StyledPanel
    )
    getattr(self.ui, f"auto_use_right_frame_{account_id}").setFrameShadow(
        QtWidgets.QFrame.Raised
    )
    getattr(self.ui, f"auto_use_right_frame_{account_id}").setObjectName(
        f"auto_use_right_frame_{account_id}"
    )
    setattr(
        self.ui,
        f"horizontalLayout_{int(account_id) + 101}",
        QtWidgets.QHBoxLayout(getattr(self.ui, f"auto_use_right_frame_{account_id}")),
    )
    getattr(self.ui, f"horizontalLayout_{int(account_id) + 101}").setContentsMargins(
        0, 0, 0, 0
    )
    getattr(self.ui, f"horizontalLayout_{int(account_id) + 101}").setSpacing(0)
    getattr(self.ui, f"horizontalLayout_{int(account_id) + 101}").setObjectName(
        f"horizontalLayout_{int(account_id) + 101}"
    )
    setattr(
        self.ui,
        f"auto_use_right_frame_2_{account_id}",
        QtWidgets.QScrollArea(getattr(self.ui, f"auto_use_right_frame_{account_id}")),
    )
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        getattr(self.ui, f"auto_use_right_frame_2_{account_id}")
        .sizePolicy()
        .hasHeightForWidth()
    )
    getattr(self.ui, f"auto_use_right_frame_2_{account_id}").setSizePolicy(sizePolicy)
    getattr(self.ui, f"auto_use_right_frame_2_{account_id}").setWidgetResizable(True)
    getattr(self.ui, f"auto_use_right_frame_2_{account_id}").setObjectName(
        f"auto_use_right_frame_2_{account_id}"
    )
    setattr(self.ui, f"auto_use_right_widget_{account_id}", QtWidgets.QWidget())
    getattr(self.ui, f"auto_use_right_widget_{account_id}").setGeometry(
        QtCore.QRect(0, 0, 232, 329)
    )
    getattr(self.ui, f"auto_use_right_widget_{account_id}").setObjectName(
        f"auto_use_right_widget_{account_id}"
    )
    setattr(
        self.ui,
        f"verticallayout_{int(account_id) + 104}",
        QtWidgets.QVBoxLayout(getattr(self.ui, f"auto_use_right_widget_{account_id}")),
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 104}").setObjectName(
        f"verticallayout_{int(account_id) + 104}"
    )
    if "autouse" not in list(config_dict[account_id]):
        config_dict[account_id]["autouse"] = config_example["autouse"]
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
    for autouse in list(config_example["autouse"]):
        if autouse not in config_dict[account_id]["autouse"]:
            config_dict[account_id]["autouse"].update(
                {autouse: config_example["autouse"][autouse]}
            )
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        if autouse in ["state", "hide_disabled"]:
            continue
        setattr(
            self.ui,
            f"{autouse}_frame_{account_id}",
            QtWidgets.QFrame(getattr(self.ui, f"auto_use_right_widget_{account_id}")),
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            getattr(self.ui, f"{autouse}_frame_{account_id}")
            .sizePolicy()
            .hasHeightForWidth()
        )
        getattr(self.ui, f"{autouse}_frame_{account_id}").setSizePolicy(sizePolicy)
        getattr(self.ui, f"{autouse}_frame_{account_id}").setMinimumSize(
            QtCore.QSize(0, 50)
        )
        getattr(self.ui, f"{autouse}_frame_{account_id}").setMaximumSize(
            QtCore.QSize(16777215, 50)
        )
        getattr(self.ui, f"{autouse}_frame_{account_id}").setFrameShape(
            QtWidgets.QFrame.StyledPanel
        )
        getattr(self.ui, f"{autouse}_frame_{account_id}").setFrameShadow(
            QtWidgets.QFrame.Raised
        )
        getattr(self.ui, f"{autouse}_frame_{account_id}").setObjectName(
            f"{autouse}_frame_{account_id}"
        )
        setattr(
            self.ui,
            f"horizontalLayout_{int(account_id) + 100}",
            QtWidgets.QHBoxLayout(getattr(self.ui, f"{autouse}_frame_{account_id}")),
        )
        getattr(self.ui, f"horizontalLayout_{int(account_id) + 100}").setObjectName(
            f"horizontalLayout_{int(account_id) + 100}"
        )
        setattr(
            self.ui,
            f"{autouse}_checkbox_{account_id}",
            QtWidgets.QCheckBox(getattr(self.ui, f"{autouse}_frame_{account_id}")),
        )
        getattr(self.ui, f"{autouse}_checkbox_{account_id}").setFont(create_font(15))
        getattr(self.ui, f"{autouse}_checkbox_{account_id}").setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )
        getattr(self.ui, f"{autouse}_checkbox_{account_id}").setText(
            autouse.replace("_", " ").title()
        )
        getattr(self.ui, f"{autouse}_checkbox_{account_id}").setObjectName(
            f"{autouse}_checkbox_{account_id}"
        )
        getattr(self.ui, f"horizontalLayout_{int(account_id) + 100}").addWidget(
            getattr(self.ui, f"{autouse}_checkbox_{account_id}")
        )
        getattr(self.ui, f"verticallayout_{int(account_id) + 104}").addWidget(
            getattr(self.ui, f"{autouse}_frame_{account_id}")
        )
    getattr(self.ui, f"auto_use_right_frame_2_{account_id}").setWidget(
        getattr(self.ui, f"auto_use_right_widget_{account_id}")
    )
    getattr(self.ui, f"horizontalLayout_{int(account_id) + 101}").addWidget(
        getattr(self.ui, f"auto_use_right_frame_2_{account_id}"),
        0,
        QtCore.Qt.AlignHCenter,
    )
    getattr(self.ui, f"horizontallayout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"auto_use_right_frame_{account_id}")
    )
    getattr(self.ui, f"verticallayout_{int(account_id) + 100}").addWidget(
        getattr(self.ui, f"auto_use_frame_{account_id}")
    )
    getattr(self.ui, f"main_menu_widget_{account_id}").addWidget(
        getattr(self.ui, f"auto_use_widget_{account_id}")
    )
    self.ui.verticalLayout_4.addWidget(
        getattr(self.ui, f"main_menu_widget_{account_id}")
    )
    self.ui.horizontalLayout_29.addWidget(
        getattr(self.ui, f"main_menu_frame_{account_id}")
    )
    self.ui.main_menu_widget.addWidget(getattr(self.ui, f"account_widget_{account_id}"))

    # Labels
    getattr(self.ui, f"account_btn_{account_id}").setText(f"Account {account_id}")
    self.ui.home_btn.setText("Home")
    self.ui.settings_btn.setText("Settings")
    self.ui.commands_btn.setText("Commands")
    self.ui.auto_buy_btn.setText("Auto Buy")
    self.ui.auto_use_btn.setText("Auto Use")
    self.ui.home_btn.setStyleSheet("background-color: #5865f2;")
    getattr(self.ui, f"home_label_{account_id}").setText("Home")
    getattr(self.ui, f"output_text_{account_id}").setHtml(
        (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"'
            ' "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta'
            ' name="qrichtext" content="1" /><style type="text/css">\np, li {'
            ' white-space: pre-wrap; }\n</style></head><body style="'
            " font-family:'Segoe UI'; font-size:12pt; font-weight:400;"
            ' font-style:normal;">\n<p style="-qt-paragraph-type:empty;'
            " margin-top:0px; margin-bottom:0px; margin-left:0px;"
            ' margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br'
            " /></p></body></html>"
        ),
    )
    getattr(self.ui, f"settings_label_{account_id}").setText("Settings")
    getattr(self.ui, f"token_label_{account_id}").setText("Discord Token")
    getattr(self.ui, f"channel_label_{account_id}").setText("Channel ID")
    getattr(self.ui, f"trivia_correct_label_{account_id}").setText(
        "Correct Trivia Chance"
    )
    getattr(self.ui, f"offline_checkbox_{account_id}").setText("Appear Offline")
    getattr(self.ui, f"alerts_checkbox_{account_id}").setText("Read Alerts")
    getattr(self.ui, f"commands_label_{account_id}").setText("Commands")

    # Command labels
    for command in commands:
        if command in ["pm", "hl", "dep_all"]:
            continue
        getattr(self.ui, f"{command}_checkbox_{account_id}").setText(
            command.capitalize()
        )
    getattr(self.ui, f"pm_checkbox_{account_id}").setText("Post Memes")
    getattr(self.ui, f"hl_checkbox_{account_id}").setText("High Low")
    getattr(self.ui, f"dep_all_checkbox_{account_id}").setText("Deposit All")
    getattr(self.ui, f"start_btn_{account_id}").setText("Start All")
    getattr(self.ui, f"stop_btn_{account_id}").setText("Stop All")
    getattr(self.ui, f"auto_buy_label_{account_id}").setText("Auto Buy")
    getattr(self.ui, f"lifesavers_checkbox_{account_id}").setText("Life Savers")
    getattr(self.ui, f"fishing_checkbox_{account_id}").setText("Fishing Pole")
    getattr(self.ui, f"shovel_checkbox_{account_id}").setText("Shovel")
    getattr(self.ui, f"rifle_checkbox_{account_id}").setText("Hunting Rifle")
    getattr(self.ui, f"auto_use_label_{account_id}").setText("Auto Use")
    getattr(self.ui, f"auto_use_checkbox_{account_id}").setText("Auto Use")
    getattr(self.ui, f"search_label_{account_id}").setText("Search")
    getattr(self.ui, f"hide_disabled_checkbox_{account_id}").setText("Hide Disabled")
    getattr(self.ui, f"home_label_{account_id}").setText("Home")
    getattr(self.ui, f"output_text_{account_id}").setHtml(
        (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"'
            ' "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta'
            ' name="qrichtext" content="1" /><style type="text/css">\np, li {'
            ' white-space: pre-wrap; }\n</style></head><body style="'
            " font-family:'Segoe UI'; font-size:12pt; font-weight:400;"
            ' font-style:normal;">\n<p style="-qt-paragraph-type:empty;'
            " margin-top:0px; margin-bottom:0px; margin-left:0px;"
            ' margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br'
            " /></p></body></html>"
        ),
    )
    getattr(self.ui, f"main_menu_widget_{account_id}").setCurrentIndex(0)
    getattr(self.ui, f"output_text_{account_id}").setVerticalScrollBar(
        getattr(self.ui, f"output_scrollbar_{account_id}")
    )

    # Initialize settings
    while True:
        try:
            getattr(self.ui, f"lifesavers_checkbox_{account_id}").setChecked(
                config_dict[account_id]["autobuy"]["lifesavers"]["state"]
            )
            getattr(self.ui, f"lifesavers_amount_{account_id}").setValue(
                config_dict[account_id]["autobuy"]["lifesavers"]["amount"]
            )
            getattr(self.ui, f"token_input_{account_id}").setText(
                config_dict[account_id]["discord_token"]
            )
            getattr(self.ui, f"channel_input_{account_id}").setText(
                config_dict[account_id]["channel_id"]
            )
            getattr(self.ui, f"trivia_correct_chance_{account_id}").setValue(
                int(config_dict[account_id]["trivia_correct_chance"] * 100)
            )
            getattr(self.ui, f"offline_checkbox_{account_id}").setChecked(
                config_dict[account_id]["offline"]
            )
            getattr(self.ui, f"alerts_checkbox_{account_id}").setChecked(
                config_dict[account_id]["alerts"]
            )

            for command in commands:
                try:
                    getattr(self.ui, f"{command}_checkbox_{account_id}").setChecked(
                        config_dict[account_id]["commands"][command]["state"]
                    )
                    getattr(self.ui, f"{command}_spinbox_{account_id}").setProperty(
                        "value", config_dict[account_id]["commands"][command]["delay"]
                    )
                except KeyError as e:
                    config_dict[account_id]["commands"][str(e).split("'")[1]] = {
                        "state": False,
                        "delay": config_example["commands"][command]["delay"],
                    }
                    with open("config.json", "w") as file:
                        json.dump(config_dict, file, ensure_ascii=False, indent=4)
                    getattr(self.ui, f"{command}_spinbox_{account_id}").setProperty(
                        "value", config_dict[account_id]["commands"][command]["delay"]
                    )
                except TypeError as e:
                    config_dict[account_id]["commands"][command] = {
                        "state": config_dict[account_id]["commands"][command],
                        "delay": config_example["commands"][command]["delay"],
                    }
                    with open("config.json", "w") as file:
                        json.dump(config_dict, file, ensure_ascii=False, indent=4)
                    getattr(self.ui, f"{command}_spinbox_{account_id}").setProperty(
                        "value", config_dict[account_id]["commands"][command]["delay"]
                    )

            for autobuy in config_dict[account_id]["autobuy"]:
                try:
                    getattr(self.ui, f"{autobuy}_checkbox_{account_id}").setChecked(
                        config_dict[account_id]["autobuy"][autobuy]
                    )
                except (TypeError, AttributeError):
                    pass

            getattr(self.ui, f"auto_use_checkbox_{account_id}").setChecked(
                config_dict[account_id]["autouse"]["state"]
            )
            getattr(self.ui, f"hide_disabled_checkbox_{account_id}").setChecked(
                config_dict[account_id]["autouse"]["hide_disabled"]
            )
            for autouse in config_dict[account_id]["autouse"]:
                try:
                    getattr(self.ui, f"{autouse}_checkbox_{account_id}").setChecked(
                        config_dict[account_id]["autouse"][autouse]["state"]
                    )
                except (TypeError, AttributeError):
                    pass
            break
        except KeyError as e:
            if e not in config_dict[account_id]:
                value = config_example[str(e).split("'")[1]]
                config_dict[account_id].update({str(e).split("'")[1]: value})
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)

    # Commands
    for button in commands:
        getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
            lambda checked, account_id=account_id, button=button: self.commands(
                button,
                {
                    "state": getattr(
                        self.ui, f"{button}_checkbox_{account_id}"
                    ).isChecked()
                },
            )
        )
        getattr(self.ui, f"{button}_spinbox_{account_id}").valueChanged.connect(
            lambda checked, account_id=account_id, button=button: self.commands(
                button,
                {"delay": getattr(self.ui, f"{button}_spinbox_{account_id}").value()},
            )
        )
    getattr(self.ui, f"start_btn_{account_id}").clicked.connect(
        lambda: self.toggle_all(True)
    )
    getattr(self.ui, f"stop_btn_{account_id}").clicked.connect(
        lambda: self.toggle_all(False)
    )

    # Autobuy
    autobuy_buttons = ["lifesavers", "fishing", "shovel", "rifle"]
    for button in autobuy_buttons:
        getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
            lambda checked, account_id=account_id, button=button: self.autobuy(
                button,
                getattr(self.ui, f"{button}_checkbox_{account_id}").isChecked(),
                "state",
            )
        )
    getattr(self.ui, f"lifesavers_amount_{account_id}").valueChanged.connect(
        lambda checked, account_id=account_id: self.autobuy(
            "lifesavers",
            getattr(self.ui, f"lifesavers_amount_{account_id}").value(),
            "amount",
        )
    )

    # Autouse
    getattr(self.ui, f"auto_use_checkbox_{account_id}").clicked.connect(
        lambda: self.autouse(
            "state",
            getattr(self.ui, f"auto_use_checkbox_{account_id}").isChecked(),
        )
    )
    getattr(self.ui, f"search_input_{account_id}").textChanged.connect(
        lambda: self.autouse(
            "search",
            getattr(self.ui, f"search_input_{account_id}").text(),
        )
    )
    for button in config_dict[account_id]["autouse"]:
        if button == "state":
            continue
        getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
            lambda checked, account_id=account_id, button=button: self.autouse(
                button,
                getattr(self.ui, f"{button}_checkbox_{account_id}").isChecked(),
                "state",
            )
        )

    # Settings buttons
    getattr(self.ui, f"token_input_{account_id}").textChanged.connect(
        lambda checked, account_id=account_id: self.settings(
            "token", getattr(self.ui, f"token_input_{account_id}").text()
        )
    )
    getattr(self.ui, f"channel_input_{account_id}").textChanged.connect(
        lambda checked, account_id=account_id: self.settings(
            "channel", getattr(self.ui, f"channel_input_{account_id}").text()
        )
    )
    getattr(self.ui, f"trivia_correct_chance_{account_id}").valueChanged.connect(
        lambda checked, account_id=account_id: self.settings(
            "trivia_correct_chance",
            getattr(self.ui, f"trivia_correct_chance_{account_id}").value(),
        )
    )
    getattr(self.ui, f"offline_checkbox_{account_id}").clicked.connect(
        lambda checked, account_id=account_id: self.settings(
            "offline",
            getattr(self.ui, f"offline_checkbox_{account_id}").isChecked(),
        )
    )
    getattr(self.ui, f"alerts_checkbox_{account_id}").clicked.connect(
        lambda checked, account_id=account_id: self.settings(
            "alerts",
            getattr(self.ui, f"alerts_checkbox_{account_id}").isChecked(),
        )
    )

    # Account buttons
    getattr(self.ui, f"account_btn_{account_id}").clicked.connect(
        lambda checked, account_id=account_id: self.accounts(account_id),
    )
