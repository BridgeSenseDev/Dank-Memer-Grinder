import json
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


def set_and_get_attr(obj, name, value):
    setattr(obj, name, value)
    return getattr(obj, name)


def create_font(font_size, bold=False):
    font = QtGui.QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(font_size)
    if bold:
        font.setBold(True)
    return font


# noinspection PyUnresolvedReferences
def load_account(self, account_id, config_example):
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
    commands = list(config_example["commands"].keys())

    # Account btn
    account_btn = set_and_get_attr(
        self.ui,
        f"account_btn_{account_id}",
        QtWidgets.QPushButton(self.ui.scrollAreaWidgetContents),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(account_btn.sizePolicy().hasHeightForWidth())
    account_btn.setSizePolicy(size_policy)
    account_btn.setMinimumSize(QtCore.QSize(0, 45))
    account_btn.setMaximumSize(QtCore.QSize(150, 45))
    account_btn.setFont(create_font(12, True))
    account_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    icon = QtGui.QIcon()
    icon.addPixmap(
        QtGui.QPixmap(":/icons/icons/user.png"),
        QIcon.Normal,
        QIcon.Off,
    )
    account_btn.setIcon(icon)
    account_btn.setIconSize(QtCore.QSize(22, 22))
    account_btn.setObjectName(f"account_btn_{account_id}")
    self.ui.horizontal_layout_5.addWidget(account_btn)

    # Account settings
    account_widget = set_and_get_attr(
        self.ui, f"account_widget_{account_id}", QtWidgets.QWidget()
    )
    account_widget.setObjectName(f"account_widget_{account_id}")
    self.ui.horizontal_layout_29 = QtWidgets.QHBoxLayout(account_widget)
    self.ui.horizontal_layout_29.setObjectName("horizontal_layout_29")
    main_menu_frame = set_and_get_attr(
        self.ui,
        f"main_menu_frame_{account_id}",
        QtWidgets.QFrame(account_widget),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(main_menu_frame.sizePolicy().hasHeightForWidth())
    main_menu_frame.setSizePolicy(size_policy)
    main_menu_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    main_menu_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    main_menu_frame.setObjectName(f"main_menu_frame_{account_id}")
    self.ui.vertical_layout_4 = QtWidgets.QVBoxLayout(main_menu_frame)
    self.ui.vertical_layout_4.setContentsMargins(0, 0, 0, 0)
    self.ui.vertical_layout_4.setSpacing(0)
    self.ui.vertical_layout_4.setObjectName("vertical_layout_4")
    main_menu_widget = set_and_get_attr(
        self.ui,
        f"main_menu_widget_{account_id}",
        QtWidgets.QStackedWidget(main_menu_frame),
    )
    main_menu_widget.setObjectName(f"main_menu_widget_{account_id}")

    # Home widget
    home_widget = set_and_get_attr(
        self.ui, f"home_widget_{account_id}", QtWidgets.QWidget()
    )
    home_widget.setObjectName(f"home_widget_{account_id}")

    self.ui.vertical_layout_6 = QtWidgets.QVBoxLayout(home_widget)
    self.ui.vertical_layout_6.setObjectName("vertical_layout_6")

    home_label = set_and_get_attr(
        self.ui, f"home_label_{account_id}", QtWidgets.QLabel(home_widget)
    )
    home_label.setMinimumSize(QtCore.QSize(0, 50))
    home_label.setMaximumSize(QtCore.QSize(16777215, 50))
    home_label.setFont(create_font(25, True))
    home_label.setAlignment(Qt.AlignCenter)
    home_label.setObjectName(f"home_label_{account_id}")

    self.ui.vertical_layout_6.addWidget(home_label, 0, Qt.AlignTop)

    home_frame = set_and_get_attr(
        self.ui, f"home_frame_{account_id}", QtWidgets.QFrame(home_widget)
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(home_frame.sizePolicy().hasHeightForWidth())
    home_frame.setSizePolicy(size_policy)
    home_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    home_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    home_frame.setObjectName(f"home_frame_{account_id}")

    self.ui.horizontal_layout_2 = QtWidgets.QHBoxLayout(home_frame)
    self.ui.horizontal_layout_2.setObjectName("horizontal_layout_2")

    output_frame = set_and_get_attr(
        self.ui, f"output_frame_{account_id}", QtWidgets.QFrame(home_frame)
    )
    output_frame.setStyleSheet("background-color: #40444b; border-radius: 20px;")
    output_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    output_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    output_frame.setObjectName(f"output_frame_{account_id}")

    self.ui.vertical_layout_11 = QtWidgets.QVBoxLayout(output_frame)
    self.ui.vertical_layout_11.setObjectName("vertical_layout_11")

    output_text = set_and_get_attr(
        self.ui, f"output_text_{account_id}", QtWidgets.QTextEdit(output_frame)
    )
    output_text.setFont(create_font(12))
    output_text.setReadOnly(True)
    output_text.setObjectName(f"output_text_{account_id}")

    self.ui.vertical_layout_11.addWidget(output_text)
    self.ui.horizontal_layout_2.addWidget(output_frame)

    output_scrollbar = set_and_get_attr(
        self.ui, f"output_scrollbar_{account_id}", QtWidgets.QScrollBar(home_frame)
    )
    output_scrollbar.setOrientation(Qt.Vertical)
    output_scrollbar.setObjectName(f"output_scrollbar_{account_id}")

    self.ui.horizontal_layout_2.addWidget(output_scrollbar)
    self.ui.vertical_layout_6.addWidget(home_frame)
    main_menu_widget.addWidget(home_widget)

    # Settings widget
    settings_widget = set_and_get_attr(
        self.ui,
        f"settings_widget_{account_id}",
        QtWidgets.QWidget(),
    )
    settings_widget.setObjectName(f"settings_widget_{account_id}")

    self.ui.vertical_layout_7 = QtWidgets.QVBoxLayout(settings_widget)
    self.ui.vertical_layout_7.setObjectName("vertical_layout_7")

    settings_label = set_and_get_attr(
        self.ui,
        f"settings_label_{account_id}",
        QtWidgets.QLabel(settings_widget),
    )
    settings_label.setMinimumSize(QtCore.QSize(0, 50))
    settings_label.setMaximumSize(QtCore.QSize(16777215, 50))
    settings_label.setFont(create_font(25, True))
    settings_label.setAlignment(Qt.AlignCenter)
    settings_label.setObjectName(f"settings_label_{account_id}")

    self.ui.vertical_layout_7.addWidget(settings_label, 0, Qt.AlignTop)

    settings_frame = QtWidgets.QFrame(settings_widget)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(settings_frame.sizePolicy().hasHeightForWidth())
    settings_frame.setSizePolicy(size_policy)
    settings_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    settings_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    settings_frame.setObjectName(f"settings_frame_{account_id}")
    setattr(self.ui, f"settings_frame_{account_id}", settings_frame)

    self.ui.vertical_layout_19 = QtWidgets.QVBoxLayout(settings_frame)
    self.ui.vertical_layout_19.setObjectName("vertical_layout_19")

    # Token
    token_frame = QtWidgets.QFrame(settings_frame)
    setattr(self.ui, f"token_frame_{account_id}", token_frame)
    token_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    token_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    token_frame.setObjectName(f"token_frame_{account_id}")

    horizontal_layout_17 = QtWidgets.QHBoxLayout(token_frame)
    horizontal_layout_17.setObjectName("horizontal_layout_17")

    token_frame_2 = QtWidgets.QFrame(token_frame)
    setattr(self.ui, f"token_frame_2_{account_id}", token_frame_2)
    token_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    token_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    token_frame_2.setObjectName(f"token_frame_2_{account_id}")

    horizontal_layout_19 = QtWidgets.QHBoxLayout(token_frame_2)
    horizontal_layout_19.setObjectName("horizontal_layout_19")

    token_label = QtWidgets.QLabel(token_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(token_label.sizePolicy().hasHeightForWidth())
    token_label.setSizePolicy(size_policy)
    token_label.setFont(create_font(15, True))
    token_label.setObjectName(f"token_label_{account_id}")

    setattr(self.ui, f"token_label_{account_id}", token_label)
    horizontal_layout_19.addWidget(token_label)

    token_input = QtWidgets.QLineEdit(token_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(token_input.sizePolicy().hasHeightForWidth())
    token_input.setSizePolicy(size_policy)
    token_input.setMinimumSize(QtCore.QSize(440, 0))
    token_input.setMaximumSize(QtCore.QSize(440, 16777215))
    token_input.setFont(create_font(12))
    token_input.setStyleSheet("background-color: #5c6066; border-radius: 10px;")
    token_input.setAlignment(Qt.AlignCenter)
    token_input.setObjectName(f"token_input_{account_id}")

    setattr(self.ui, f"token_input_{account_id}", token_input)
    horizontal_layout_19.addWidget(token_input)

    horizontal_layout_17.addWidget(token_frame_2)
    self.ui.vertical_layout_19.addWidget(token_frame, 0, Qt.AlignHCenter | Qt.AlignTop)

    # Channel ID
    channel_frame = QtWidgets.QFrame(settings_frame)
    setattr(self.ui, f"channel_frame_{account_id}", channel_frame)
    channel_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    channel_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    channel_frame.setObjectName(f"channel_frame_{account_id}")

    horizontal_layout_22 = QtWidgets.QHBoxLayout(channel_frame)
    horizontal_layout_22.setObjectName("horizontal_layout_22")

    channel_frame_2 = QtWidgets.QFrame(channel_frame)
    setattr(self.ui, f"channel_frame_2_{account_id}", channel_frame_2)
    channel_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    channel_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    channel_frame_2.setObjectName(f"channel_frame_2_{account_id}")

    horizontal_layout_21 = QtWidgets.QHBoxLayout(channel_frame_2)
    horizontal_layout_21.setObjectName("horizontal_layout_21")

    channel_label = QtWidgets.QLabel(channel_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(channel_label.sizePolicy().hasHeightForWidth())
    channel_label.setSizePolicy(size_policy)
    channel_label.setFont(create_font(15, True))
    channel_label.setObjectName(f"channel_label_{account_id}")

    setattr(self.ui, f"channel_label_{account_id}", channel_label)
    horizontal_layout_21.addWidget(channel_label)

    channel_input = QtWidgets.QLineEdit(channel_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(channel_input.sizePolicy().hasHeightForWidth())
    channel_input.setSizePolicy(size_policy)
    channel_input.setMinimumSize(QtCore.QSize(200, 0))
    channel_input.setMaximumSize(QtCore.QSize(500, 200))
    channel_input.setFont(create_font(12))
    channel_input.setStyleSheet("background-color: #5c6066; border-radius: 10px;")
    channel_input.setAlignment(Qt.AlignCenter)
    channel_input.setObjectName(f"channel_input_{account_id}")

    setattr(self.ui, f"channel_input_{account_id}", channel_input)
    horizontal_layout_21.addWidget(channel_input)

    horizontal_layout_22.addWidget(
        channel_frame_2, 0, Qt.AlignHCenter | Qt.AlignVCenter
    )
    self.ui.vertical_layout_19.addWidget(channel_frame)

    # Trivia correct chance
    trivia_correct_frame = QtWidgets.QFrame(settings_frame)
    setattr(self.ui, f"trivia_correct_frame_{account_id}", trivia_correct_frame)
    trivia_correct_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    trivia_correct_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    trivia_correct_frame.setObjectName(f"trivia_correct_frame_{account_id}")

    horizontal_layout_25 = QtWidgets.QHBoxLayout(trivia_correct_frame)
    horizontal_layout_25.setObjectName("horizontal_layout_25")

    trivia_correct_frame_2 = QtWidgets.QFrame(trivia_correct_frame)
    trivia_correct_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    trivia_correct_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    trivia_correct_frame_2.setObjectName(f"trivia_correct_frame_2_{account_id}")
    setattr(self.ui, f"trivia_correct_frame_2_{account_id}", trivia_correct_frame_2)

    horizontal_layout_24 = QtWidgets.QHBoxLayout(trivia_correct_frame_2)
    horizontal_layout_24.setObjectName("horizontal_layout_24")

    trivia_correct_label = QtWidgets.QLabel(trivia_correct_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(trivia_correct_label.sizePolicy().hasHeightForWidth())
    trivia_correct_label.setSizePolicy(size_policy)
    trivia_correct_label.setFont(create_font(15, True))
    trivia_correct_label.setObjectName(f"trivia_correct_label_{account_id}")
    setattr(self.ui, f"trivia_correct_label_{account_id}", trivia_correct_label)
    horizontal_layout_24.addWidget(trivia_correct_label)

    trivia_correct_chance = QtWidgets.QSpinBox(trivia_correct_frame_2)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        trivia_correct_chance.sizePolicy().hasHeightForWidth()
    )
    trivia_correct_chance.setSizePolicy(size_policy)
    trivia_correct_chance.setMinimumSize(QtCore.QSize(50, 30))
    trivia_correct_chance.setMaximumSize(QtCore.QSize(50, 30))
    trivia_correct_chance.setFont(create_font(12))
    trivia_correct_chance.setAutoFillBackground(False)
    trivia_correct_chance.setStyleSheet("")
    trivia_correct_chance.setWrapping(False)
    trivia_correct_chance.setFrame(True)
    trivia_correct_chance.setAlignment(Qt.AlignCenter)
    trivia_correct_chance.setMinimum(25)
    trivia_correct_chance.setMaximum(100)
    trivia_correct_chance.setObjectName(f"trivia_correct_chance_{account_id}")
    setattr(self.ui, f"trivia_correct_chance_{account_id}", trivia_correct_chance)
    horizontal_layout_24.addWidget(trivia_correct_chance)

    horizontal_layout_25.addWidget(trivia_correct_frame_2, 0, Qt.AlignHCenter)
    self.ui.vertical_layout_19.addWidget(trivia_correct_frame, 0, Qt.AlignVCenter)

    # Adventure
    adventure_frame = QtWidgets.QFrame(settings_frame)
    setattr(self.ui, f"adventure_frame_{account_id}", adventure_frame)

    adventure_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    adventure_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    adventure_frame.setObjectName(f"adventure_frame_{account_id}")

    horizontal_layout_85 = QtWidgets.QHBoxLayout(adventure_frame)
    horizontal_layout_85.setObjectName(f"horizontal_layout_85_{account_id}")

    adventure_frame_2_1 = QtWidgets.QFrame(adventure_frame)
    adventure_frame_2_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
    adventure_frame_2_1.setFrameShadow(QtWidgets.QFrame.Raised)
    adventure_frame_2_1.setObjectName(f"adventure_frame_2_{account_id}")

    horizontal_layout_84 = QtWidgets.QHBoxLayout(adventure_frame_2_1)
    horizontal_layout_84.setObjectName(f"horizontal_layout_84_{account_id}")

    adventure_label = QtWidgets.QLabel(adventure_frame_2_1)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(adventure_label.sizePolicy().hasHeightForWidth())
    adventure_label.setSizePolicy(size_policy)
    adventure_label.setFont(create_font(15, True))
    adventure_label.setObjectName(f"adventure_label_{account_id}")
    horizontal_layout_84.addWidget(adventure_label)

    adventure_box = QtWidgets.QComboBox(adventure_frame_2_1)
    adventure_box.setMinimumSize(QtCore.QSize(80, 30))
    adventure_box.setMaximumSize(QtCore.QSize(100, 100))
    adventure_box.setFont(create_font(12))
    adventure_box.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    adventure_box.setStyleSheet("")
    adventure_box.setFrame(True)
    adventure_box.setObjectName(f"adventure_box_{account_id}")
    setattr(self.ui, f"adventure_box_{account_id}", adventure_box)

    horizontal_layout_84.addWidget(adventure_box)
    horizontal_layout_85.addWidget(adventure_frame_2_1, 0, Qt.AlignHCenter)
    self.ui.vertical_layout_19.addWidget(adventure_frame)

    # Toggles right
    toggles_frame = QtWidgets.QFrame(settings_frame)
    toggles_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    toggles_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    toggles_frame.setObjectName(f"toggles_frame_{account_id}")
    setattr(self.ui, f"toggles_frame_{account_id}", toggles_frame)

    self.horizontal_layout_6 = QtWidgets.QHBoxLayout(toggles_frame)
    self.horizontal_layout_6.setContentsMargins(0, 0, 0, 0)
    self.horizontal_layout_6.setSpacing(0)
    self.horizontal_layout_6.setObjectName("horizontal_layout_6")

    toggles_left_frame = QtWidgets.QFrame(toggles_frame)
    toggles_left_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    toggles_left_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    toggles_left_frame.setObjectName(f"toggles_left_frame_{account_id}")
    setattr(self.ui, f"toggles_left_frame_{account_id}", toggles_left_frame)

    self.vertical_layout_10 = QtWidgets.QVBoxLayout(toggles_left_frame)
    self.vertical_layout_10.setContentsMargins(0, 0, 0, 0)
    self.vertical_layout_10.setObjectName("vertical_layout_10")

    toggles_left_frame_2 = QtWidgets.QFrame(toggles_left_frame)
    toggles_left_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    toggles_left_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    toggles_left_frame_2.setObjectName(f"toggles_left_frame_2_{account_id}")
    setattr(self.ui, f"toggles_left_frame_2_{account_id}", toggles_left_frame_2)

    self.vertical_layout_15 = QtWidgets.QVBoxLayout(toggles_left_frame_2)
    self.vertical_layout_15.setContentsMargins(0, 0, 0, 0)
    self.vertical_layout_15.setSpacing(0)
    self.vertical_layout_15.setObjectName("vertical_layout_15")

    offline_checkbox = QtWidgets.QCheckBox(toggles_left_frame_2)
    offline_checkbox.setFont(create_font(15, True))
    offline_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    offline_checkbox.setObjectName(f"offline_checkbox_{account_id}")
    setattr(self.ui, f"offline_checkbox_{account_id}", offline_checkbox)

    self.vertical_layout_15.addWidget(offline_checkbox)

    auto_vote_checkbox = QtWidgets.QCheckBox(toggles_left_frame_2)
    auto_vote_checkbox.setFont(create_font(15, True))
    auto_vote_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    auto_vote_checkbox.setObjectName(f"auto_vote_checkbox_{account_id}")
    setattr(self.ui, f"auto_vote_checkbox_{account_id}", auto_vote_checkbox)

    self.vertical_layout_15.addWidget(auto_vote_checkbox)
    self.vertical_layout_10.addWidget(toggles_left_frame_2, 0, Qt.AlignHCenter)
    self.horizontal_layout_6.addWidget(toggles_left_frame)

    # Toggles left
    toggles_right_frame_name = f"toggles_right_frame_{account_id}"
    toggles_frame_name = f"toggles_frame_{account_id}"
    toggles_right_frame_2_name = f"toggles_right_frame_2_{account_id}"
    alerts_checkbox_name = f"alerts_checkbox_{account_id}"

    toggles_right_frame = QtWidgets.QFrame(getattr(self.ui, toggles_frame_name))
    toggles_right_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    toggles_right_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    toggles_right_frame.setObjectName(toggles_right_frame_name)
    setattr(self.ui, toggles_right_frame_name, toggles_right_frame)

    self.vertical_layout_16 = QtWidgets.QVBoxLayout(toggles_right_frame)
    self.vertical_layout_16.setContentsMargins(0, 0, 0, 0)
    self.vertical_layout_16.setSpacing(0)
    self.vertical_layout_16.setObjectName("vertical_layout_16")

    toggles_right_frame_2 = QtWidgets.QFrame(toggles_right_frame)
    toggles_right_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    toggles_right_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    toggles_right_frame_2.setObjectName(toggles_right_frame_2_name)
    setattr(self.ui, toggles_right_frame_2_name, toggles_right_frame_2)

    self.vertical_layout_17 = QtWidgets.QVBoxLayout(toggles_right_frame_2)
    self.vertical_layout_17.setContentsMargins(0, 0, 0, 0)
    self.vertical_layout_17.setSpacing(0)
    self.vertical_layout_17.setObjectName("vertical_layout_17")

    alerts_checkbox = QtWidgets.QCheckBox(toggles_right_frame_2)
    alerts_checkbox.setFont(create_font(15, True))
    alerts_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    alerts_checkbox.setObjectName(alerts_checkbox_name)
    setattr(self.ui, alerts_checkbox_name, alerts_checkbox)

    self.vertical_layout_17.addWidget(alerts_checkbox, 0, Qt.AlignHCenter)
    self.vertical_layout_16.addWidget(toggles_right_frame_2)
    self.horizontal_layout_6.addWidget(toggles_right_frame)
    self.ui.vertical_layout_19.addWidget(getattr(self.ui, toggles_frame_name))

    self.ui.vertical_layout_7.addWidget(settings_frame)
    main_menu_widget.addWidget(settings_widget)

    # Commands widget
    commands_widget = set_and_get_attr(
        self.ui, f"commands_widget_{account_id}", QtWidgets.QWidget()
    )
    commands_widget.setObjectName(f"commands_widget_{account_id}")

    self.ui.vertical_layout_8 = QtWidgets.QVBoxLayout(commands_widget)
    self.ui.vertical_layout_8.setObjectName("vertical_layout_8")

    commands_label = set_and_get_attr(
        self.ui, f"commands_label_{account_id}", QtWidgets.QLabel(commands_widget)
    )
    commands_label.setMinimumSize(QtCore.QSize(0, 50))
    commands_label.setMaximumSize(QtCore.QSize(16777215, 50))
    commands_label.setFont(create_font(25, True))
    commands_label.setAlignment(Qt.AlignCenter)
    commands_label.setObjectName(f"commands_label_{account_id}")

    self.ui.vertical_layout_8.addWidget(commands_label, 0, Qt.AlignTop)

    commands_frame = set_and_get_attr(
        self.ui, f"commands_frame_{account_id}", QtWidgets.QFrame(commands_widget)
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(commands_frame.sizePolicy().hasHeightForWidth())
    commands_frame.setSizePolicy(size_policy)
    commands_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    commands_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    commands_frame.setObjectName(f"commands_frame_{account_id}")

    vertical_layout_12 = QtWidgets.QVBoxLayout(commands_frame)
    vertical_layout_12.setObjectName("vertical_layout_12")

    commands_settings_frame = set_and_get_attr(
        self.ui,
        f"commands_settings_frame_{account_id}",
        QtWidgets.QFrame(commands_frame),
    )
    commands_settings_frame.setStyleSheet(
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
        commands_settings_frame.sizePolicy().hasHeightForWidth()
    )
    commands_settings_frame.setSizePolicy(size_policy)
    commands_settings_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    commands_settings_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    commands_settings_frame.setObjectName(f"commands_settings_frame_{account_id}")

    horizontal_layout_4 = QtWidgets.QHBoxLayout(commands_settings_frame)
    horizontal_layout_4.setSpacing(50)
    horizontal_layout_4.setObjectName("horizontal_layout_4")

    for i in ["left", "right"]:
        commands_settings_frame_i = set_and_get_attr(
            self.ui,
            f"commands_settings_{i}_frame_{account_id}",
            QtWidgets.QFrame(commands_settings_frame),
        )
        commands_settings_frame_i.setFrameShape(QtWidgets.QFrame.StyledPanel)
        commands_settings_frame_i.setFrameShadow(QtWidgets.QFrame.Raised)
        commands_settings_frame_i.setObjectName(
            f"commands_settings_{i}_frame_{account_id}"
        )

        vertical_layout_20 = QtWidgets.QVBoxLayout(commands_settings_frame_i)
        vertical_layout_20.setContentsMargins(0, 0, 0, 0)
        vertical_layout_20.setSpacing(0)
        vertical_layout_20.setObjectName("vertical_layout_20")

        commands_settings_frame_2_i = set_and_get_attr(
            self.ui,
            f"commands_settings_{i}_frame_2_{account_id}",
            QtWidgets.QFrame(commands_settings_frame_i),
        )
        commands_settings_frame_2_i.setFrameShape(QtWidgets.QFrame.StyledPanel)
        commands_settings_frame_2_i.setFrameShadow(QtWidgets.QFrame.Raised)
        commands_settings_frame_2_i.setObjectName(
            f"commands_settings_{i}_frame_2_{account_id}"
        )

        vertical_layout_13 = QtWidgets.QVBoxLayout(commands_settings_frame_2_i)
        vertical_layout_13.setContentsMargins(0, 0, 0, 0)
        vertical_layout_13.setSpacing(0)
        vertical_layout_13.setObjectName("vertical_layout_13")

        if i == "left":
            commands_list = commands[: math.floor(len(commands) / 2)]
        else:
            commands_list = commands[math.floor(len(commands) / 2) :]

        for command in commands_list:
            frame = set_and_get_attr(
                self.ui,
                f"{command}_frame_{account_id}",
                QtWidgets.QFrame(
                    getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
                ),
            )
            frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frame.setFrameShadow(QtWidgets.QFrame.Raised)
            frame.setObjectName(f"{command}_frame_{account_id}")

            horizontal_layout = QtWidgets.QHBoxLayout(frame)
            horizontal_layout.setContentsMargins(0, 0, 0, 0)
            horizontal_layout.setObjectName(f"horizontal_layout_{int(account_id) + 30}")

            spinbox = set_and_get_attr(
                self.ui, f"{command}_spinbox_{account_id}", QtWidgets.QSpinBox(frame)
            )
            spinbox.setMinimumSize(QtCore.QSize(45, 25))
            spinbox.setMaximumSize(QtCore.QSize(45, 25))
            spinbox.setFont(create_font(12))
            spinbox.setStyleSheet("")
            spinbox.setAlignment(Qt.AlignCenter)
            spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            spinbox.setMaximum(100000)
            spinbox.setProperty("value", 0)
            spinbox.setObjectName(f"{command}_spinbox_{account_id}")
            horizontal_layout.addWidget(spinbox)

            checkbox = set_and_get_attr(
                self.ui,
                f"{command}_checkbox_{account_id}",
                QtWidgets.QCheckBox(
                    getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
                ),
            )
            checkbox.setFont(create_font(15, True))
            checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            checkbox.setObjectName(f"{command}_checkbox_{account_id}")
            horizontal_layout.addWidget(checkbox)

            vertical_layout_13.addWidget(frame)
        vertical_layout_20.addWidget(
            getattr(self.ui, f"commands_settings_{i}_frame_2_{account_id}")
        )
        horizontal_layout_4.addWidget(
            getattr(self.ui, f"commands_settings_{i}_frame_{account_id}"),
            0,
            Qt.AlignRight,
        )

    vertical_layout_12.addWidget(commands_settings_frame, 0, Qt.AlignHCenter)

    commands_toggle_frame = set_and_get_attr(
        self.ui,
        f"commands_toggle_frame_{account_id}",
        QtWidgets.QFrame(commands_settings_frame),
    )
    commands_toggle_frame.setMinimumSize(QtCore.QSize(0, 50))
    commands_toggle_frame.setMaximumSize(QtCore.QSize(16777215, 50))
    commands_toggle_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    commands_toggle_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    commands_toggle_frame.setObjectName(f"commands_toggle_frame_{account_id}")

    horizontal_layout_26 = QtWidgets.QHBoxLayout(commands_toggle_frame)
    horizontal_layout_26.setContentsMargins(0, 0, 0, 0)
    horizontal_layout_26.setSpacing(0)
    horizontal_layout_26.setObjectName("horizontal_layout_26")

    commands_toggle_btn = set_and_get_attr(
        self.ui,
        f"commands_toggle_btn_{account_id}",
        QtWidgets.QFrame(commands_toggle_frame),
    )
    commands_toggle_btn.setFrameShape(QtWidgets.QFrame.StyledPanel)
    commands_toggle_btn.setFrameShadow(QtWidgets.QFrame.Raised)
    commands_toggle_btn.setObjectName(f"commands_toggle_btn_{account_id}")

    horizontal_layout_27 = QtWidgets.QHBoxLayout(commands_toggle_btn)
    horizontal_layout_27.setContentsMargins(0, 0, 0, 0)
    horizontal_layout_27.setSpacing(10)
    horizontal_layout_27.setObjectName("horizontal_layout_27")

    start_btn = set_and_get_attr(
        self.ui, f"start_btn_{account_id}", QtWidgets.QPushButton(commands_toggle_btn)
    )
    start_btn.setEnabled(True)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(start_btn.sizePolicy().hasHeightForWidth())
    start_btn.setSizePolicy(size_policy)
    start_btn.setMinimumSize(QtCore.QSize(140, 45))
    start_btn.setMaximumSize(QtCore.QSize(50, 45))
    start_btn.setFont(create_font(12, True))
    start_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    start_btn.setStyleSheet("background-color : #2d7d46")
    start_btn.setObjectName(f"start_btn_{account_id}")

    horizontal_layout_27.addWidget(start_btn)

    stop_btn = set_and_get_attr(
        self.ui, f"stop_btn_{account_id}", QtWidgets.QPushButton(commands_toggle_btn)
    )
    stop_btn.setEnabled(True)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(stop_btn.sizePolicy().hasHeightForWidth())
    stop_btn.setSizePolicy(size_policy)
    stop_btn.setMinimumSize(QtCore.QSize(140, 45))
    stop_btn.setMaximumSize(QtCore.QSize(50, 45))
    stop_btn.setFont(create_font(12, True))
    stop_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    stop_btn.setStyleSheet("background-color : #d83c3e")
    stop_btn.setObjectName(f"stop_btn_{account_id}")

    horizontal_layout_27.addWidget(stop_btn)
    horizontal_layout_26.addWidget(
        commands_toggle_btn, 0, Qt.AlignHCenter | Qt.AlignVCenter
    )

    vertical_layout_12.addWidget(commands_toggle_frame, 0, Qt.AlignBottom)

    self.ui.vertical_layout_8.addWidget(commands_frame)
    main_menu_widget.addWidget(commands_widget)

    # Autobuy Widget
    auto_buy_widget = set_and_get_attr(
        self.ui, f"auto_buy_widget_{account_id}", QtWidgets.QWidget()
    )
    auto_buy_widget.setObjectName(f"auto_buy_widget_{account_id}")

    vertical_layout_9 = QtWidgets.QVBoxLayout(auto_buy_widget)
    vertical_layout_9.setObjectName("vertical_layout_9")

    auto_buy_label = set_and_get_attr(
        self.ui, f"auto_buy_label_{account_id}", QtWidgets.QLabel(auto_buy_widget)
    )
    auto_buy_label.setMinimumSize(QtCore.QSize(0, 50))
    auto_buy_label.setMaximumSize(QtCore.QSize(16777215, 50))
    auto_buy_label.setFont(create_font(25, True))
    auto_buy_label.setAlignment(Qt.AlignCenter)
    auto_buy_label.setObjectName(f"auto_buy_label_{account_id}")

    vertical_layout_9.addWidget(auto_buy_label)

    auto_buy_frame = set_and_get_attr(
        self.ui, f"auto_buy_frame_{account_id}", QtWidgets.QFrame(auto_buy_widget)
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(auto_buy_frame.sizePolicy().hasHeightForWidth())
    auto_buy_frame.setSizePolicy(size_policy)
    auto_buy_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_buy_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_buy_frame.setObjectName(f"auto_buy_frame_{account_id}")

    vertical_layout_18 = QtWidgets.QVBoxLayout(auto_buy_frame)
    vertical_layout_18.setObjectName("vertical_layout_18")

    # Lifesaver autobuy
    lifesavers_frame = set_and_get_attr(
        self.ui, f"lifesavers_frame_{account_id}", QtWidgets.QFrame(auto_buy_frame)
    )
    lifesavers_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    lifesavers_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    lifesavers_frame.setObjectName(f"lifesavers_frame_{account_id}")

    horizontal_layout_16 = QtWidgets.QHBoxLayout(lifesavers_frame)
    horizontal_layout_16.setObjectName("horizontal_layout_16")

    lifesavers_frame_2 = set_and_get_attr(
        self.ui, f"lifesavers_frame_2_{account_id}", QtWidgets.QFrame(lifesavers_frame)
    )
    lifesavers_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    lifesavers_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    lifesavers_frame_2.setObjectName(f"lifesavers_frame_2_{account_id}")

    horizontal_layout_15 = QtWidgets.QHBoxLayout(lifesavers_frame_2)
    horizontal_layout_15.setObjectName("horizontal_layout_15")

    lifesavers_checkbox = set_and_get_attr(
        self.ui,
        f"lifesavers_checkbox_{account_id}",
        QtWidgets.QCheckBox(lifesavers_frame_2),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(lifesavers_checkbox.sizePolicy().hasHeightForWidth())
    lifesavers_checkbox.setSizePolicy(size_policy)
    lifesavers_checkbox.setFont(create_font(15, True))
    lifesavers_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    lifesavers_checkbox.setStyleSheet("")
    lifesavers_checkbox.setObjectName(f"lifesavers_checkbox_{account_id}")

    horizontal_layout_15.addWidget(lifesavers_checkbox)

    lifesavers_amount = set_and_get_attr(
        self.ui,
        f"lifesavers_amount_{account_id}",
        QtWidgets.QSpinBox(lifesavers_frame_2),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(lifesavers_amount.sizePolicy().hasHeightForWidth())
    lifesavers_amount.setSizePolicy(size_policy)
    lifesavers_amount.setMinimumSize(QtCore.QSize(50, 30))
    lifesavers_amount.setMaximumSize(QtCore.QSize(50, 30))
    lifesavers_amount.setFont(create_font(12))
    lifesavers_amount.setAutoFillBackground(False)
    lifesavers_amount.setStyleSheet("")
    lifesavers_amount.setWrapping(False)
    lifesavers_amount.setFrame(True)
    lifesavers_amount.setAlignment(Qt.AlignCenter)
    lifesavers_amount.setMaximum(100)
    lifesavers_amount.setObjectName(f"lifesavers_amount_{account_id}")

    horizontal_layout_15.addWidget(lifesavers_amount)
    horizontal_layout_16.addWidget(lifesavers_frame_2)
    vertical_layout_18.addWidget(lifesavers_frame, 0, Qt.AlignHCenter | Qt.AlignVCenter)

    for autobuy in ["fishing", "shovel", "rifle"]:
        item_frame = set_and_get_attr(
            self.ui, f"{autobuy}_frame_{account_id}", QtWidgets.QFrame(auto_buy_frame)
        )
        item_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        item_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        item_frame.setObjectName(f"{autobuy}_frame_{account_id}")

        horizontal_layout = QtWidgets.QHBoxLayout(item_frame)
        horizontal_layout.setObjectName(f"horizontal_layout_{autobuy}")

        item_checkbox = set_and_get_attr(
            self.ui, f"{autobuy}_checkbox_{account_id}", QtWidgets.QCheckBox(item_frame)
        )
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(item_checkbox.sizePolicy().hasHeightForWidth())
        item_checkbox.setSizePolicy(size_policy)
        item_checkbox.setFont(create_font(15, True))
        item_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        item_checkbox.setStyleSheet("")
        item_checkbox.setObjectName(f"{autobuy}_checkbox_{account_id}")

        horizontal_layout.addWidget(item_checkbox)
        vertical_layout_18.addWidget(item_frame)

    vertical_layout_9.addWidget(auto_buy_frame)
    main_menu_widget.addWidget(auto_buy_widget)

    # Autobuy widget
    auto_use_widget = set_and_get_attr(
        self.ui, f"auto_use_widget_{account_id}", QtWidgets.QWidget()
    )
    auto_use_widget.setObjectName(f"auto_use_widget_{account_id}")

    vertical_layout = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 100}",
        QtWidgets.QVBoxLayout(auto_use_widget),
    )
    vertical_layout.setObjectName(f"vertical_layout_{int(account_id) + 100}")

    auto_use_label = set_and_get_attr(
        self.ui, f"auto_use_label_{account_id}", QtWidgets.QLabel(auto_use_widget)
    )
    auto_use_label.setMinimumSize(QtCore.QSize(0, 50))
    auto_use_label.setMaximumSize(QtCore.QSize(16777215, 50))
    auto_use_label.setFont(create_font(25, True))
    auto_use_label.setAlignment(Qt.AlignCenter)
    auto_use_label.setObjectName(f"auto_use_label_{account_id}")

    vertical_layout.addWidget(auto_use_label)

    auto_use_frame = set_and_get_attr(
        self.ui, f"auto_use_frame_{account_id}", QtWidgets.QFrame(auto_use_widget)
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(auto_use_frame.sizePolicy().hasHeightForWidth())
    auto_use_frame.setSizePolicy(size_policy)
    auto_use_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_use_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_use_frame.setObjectName(f"auto_use_frame_{account_id}")

    horizontal_layout = set_and_get_attr(
        self.ui,
        f"horizontal_layout_{int(account_id) + 102}",
        QtWidgets.QHBoxLayout(auto_use_frame),
    )
    horizontal_layout.setObjectName(f"horizontal_layout_{int(account_id) + 102}")

    auto_use_left_frame = set_and_get_attr(
        self.ui, f"auto_use_left_frame_{account_id}", QtWidgets.QFrame(auto_use_frame)
    )
    auto_use_left_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_use_left_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_use_left_frame.setObjectName(f"auto_use_left_frame_{account_id}")

    vertical_layout_left = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 101}",
        QtWidgets.QVBoxLayout(auto_use_left_frame),
    )
    vertical_layout_left.setObjectName(f"vertical_layout_{int(account_id) + 101}")

    auto_use_left_frame_2 = set_and_get_attr(
        self.ui,
        f"auto_use_left_frame_2_{account_id}",
        QtWidgets.QFrame(auto_use_left_frame),
    )
    auto_use_left_frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_use_left_frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_use_left_frame_2.setObjectName(f"auto_use_left_frame_2_{account_id}")

    vertical_layout_left_2 = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 102}",
        QtWidgets.QVBoxLayout(auto_use_left_frame_2),
    )
    vertical_layout_left_2.setObjectName(f"vertical_layout_{int(account_id) + 102}")

    auto_use_btn_frame = set_and_get_attr(
        self.ui,
        f"auto_use_btn_frame_{account_id}",
        QtWidgets.QFrame(auto_use_left_frame_2),
    )
    auto_use_btn_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_use_btn_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_use_btn_frame.setObjectName(f"auto_use_btn_frame_{account_id}")

    vertical_layout_btn = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 103}",
        QtWidgets.QVBoxLayout(auto_use_btn_frame),
    )
    vertical_layout_btn.setObjectName(f"vertical_layout_{int(account_id) + 103}")

    auto_use_checkbox = set_and_get_attr(
        self.ui,
        f"auto_use_checkbox_{account_id}",
        QtWidgets.QCheckBox(auto_use_btn_frame),
    )
    auto_use_checkbox.setFont(create_font(15, True))
    auto_use_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    auto_use_checkbox.setObjectName(f"auto_use_checkbox_{account_id}")

    vertical_layout_btn.addWidget(auto_use_checkbox)

    getattr(self.ui, f"vertical_layout_{int(account_id) + 102}").addWidget(
        auto_use_btn_frame
    )

    search_frame = set_and_get_attr(
        self.ui,
        f"search_frame_{account_id}",
        QtWidgets.QFrame(auto_use_left_frame_2),
    )
    search_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    search_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    search_frame.setObjectName(f"search_frame_{account_id}")

    vertical_layout = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 106}",
        QtWidgets.QVBoxLayout(search_frame),
    )
    vertical_layout.setObjectName(f"vertical_layout_{int(account_id) + 106}")

    search_label = set_and_get_attr(
        self.ui, f"search_label_{account_id}", QtWidgets.QLabel(search_frame)
    )
    search_label.setFont(create_font(15, True))
    search_label.setAlignment(Qt.AlignCenter)
    search_label.setObjectName(f"search_label_{account_id}")

    vertical_layout.addWidget(search_label)

    search_input = set_and_get_attr(
        self.ui, f"search_input_{account_id}", QtWidgets.QLineEdit(search_frame)
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(search_input.sizePolicy().hasHeightForWidth())
    search_input.setSizePolicy(size_policy)
    search_input.setMinimumSize(QtCore.QSize(200, 0))
    search_input.setMaximumSize(QtCore.QSize(500, 30))
    search_input.setFont(create_font(15, True))
    search_input.setStyleSheet("background-color: #5c6066; border-radius: 10px;")
    search_input.setAlignment(Qt.AlignCenter)
    search_input.setObjectName(f"search_input_{account_id}")

    vertical_layout.addWidget(search_input)

    getattr(self.ui, f"vertical_layout_{int(account_id) + 102}").addWidget(search_frame)

    hide_disabled_frame = set_and_get_attr(
        self.ui,
        f"hide_disabled_frame_{account_id}",
        QtWidgets.QFrame(auto_use_left_frame_2),
    )
    hide_disabled_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    hide_disabled_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    hide_disabled_frame.setObjectName(f"hide_disabled_frame_{account_id}")

    vertical_layout_hide_disabled = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 105}",
        QtWidgets.QVBoxLayout(hide_disabled_frame),
    )
    vertical_layout_hide_disabled.setObjectName(
        f"vertical_layout_{int(account_id) + 105}"
    )

    hide_disabled_checkbox = set_and_get_attr(
        self.ui,
        f"hide_disabled_checkbox_{account_id}",
        QtWidgets.QCheckBox(hide_disabled_frame),
    )
    hide_disabled_checkbox.setFont(create_font(15, True))
    hide_disabled_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
    hide_disabled_checkbox.setObjectName(f"hide_disabled_checkbox_{account_id}")

    vertical_layout_hide_disabled.addWidget(hide_disabled_checkbox)

    getattr(self.ui, f"vertical_layout_{int(account_id) + 102}").addWidget(
        hide_disabled_frame
    )

    getattr(self.ui, f"vertical_layout_{int(account_id) + 101}").addWidget(
        auto_use_left_frame_2, 0, Qt.AlignHCenter
    )
    getattr(self.ui, f"horizontal_layout_{int(account_id) + 102}").addWidget(
        getattr(self.ui, f"auto_use_left_frame_{account_id}")
    )

    auto_use_right_frame = set_and_get_attr(
        self.ui, f"auto_use_right_frame_{account_id}", QtWidgets.QFrame(auto_use_frame)
    )
    auto_use_right_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    auto_use_right_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    auto_use_right_frame.setObjectName(f"auto_use_right_frame_{account_id}")

    horizontal_layout = set_and_get_attr(
        self.ui,
        f"horizontal_layout_{int(account_id) + 101}",
        QtWidgets.QHBoxLayout(auto_use_right_frame),
    )
    horizontal_layout.setContentsMargins(0, 0, 0, 0)
    horizontal_layout.setSpacing(0)
    horizontal_layout.setObjectName(f"horizontal_layout_{int(account_id) + 101}")

    auto_use_right_frame_2 = set_and_get_attr(
        self.ui,
        f"auto_use_right_frame_2_{account_id}",
        QtWidgets.QScrollArea(auto_use_right_frame),
    )
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
    )
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(
        auto_use_right_frame_2.sizePolicy().hasHeightForWidth()
    )
    auto_use_right_frame_2.setSizePolicy(size_policy)
    auto_use_right_frame_2.setWidgetResizable(True)
    auto_use_right_frame_2.setHorizontalScrollBarPolicy(
        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    auto_use_right_frame_2.setObjectName(f"auto_use_right_frame_2_{account_id}")

    auto_use_right_widget = set_and_get_attr(
        self.ui, f"auto_use_right_widget_{account_id}", QtWidgets.QWidget()
    )
    auto_use_right_widget.setGeometry(QtCore.QRect(0, 0, 232, 329))
    auto_use_right_widget.setObjectName(f"auto_use_right_widget_{account_id}")

    vertical_layout = set_and_get_attr(
        self.ui,
        f"vertical_layout_{int(account_id) + 104}",
        QtWidgets.QVBoxLayout(auto_use_right_widget),
    )
    vertical_layout.setObjectName(f"vertical_layout_{int(account_id) + 104}")

    if "autouse" not in list(config_dict[account_id]):
        config_dict[account_id]["autouse"] = config_example["autouse"]
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    for autouse in sorted(list(config_example["autouse"])):
        if autouse not in config_dict[account_id]["autouse"]:
            config_dict[account_id]["autouse"].update(
                {autouse: config_example["autouse"][autouse]}
            )
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        if autouse in ["state", "hide_disabled"]:
            continue

        autouse_frame = set_and_get_attr(
            self.ui,
            f"{autouse}_frame_{account_id}",
            QtWidgets.QFrame(auto_use_right_widget),
        )
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(autouse_frame.sizePolicy().hasHeightForWidth())
        autouse_frame.setSizePolicy(size_policy)
        autouse_frame.setMinimumSize(QtCore.QSize(0, 50))
        autouse_frame.setMaximumSize(QtCore.QSize(16777215, 50))
        autouse_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        autouse_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        autouse_frame.setObjectName(f"{autouse}_frame_{account_id}")

        horizontal_layout_autouse = set_and_get_attr(
            self.ui,
            f"horizontal_layout_{int(account_id) + 100}",
            QtWidgets.QHBoxLayout(autouse_frame),
        )
        horizontal_layout_autouse.setObjectName(
            f"horizontal_layout_{int(account_id) + 100}"
        )

        autouse_checkbox = set_and_get_attr(
            self.ui,
            f"{autouse}_checkbox_{account_id}",
            QtWidgets.QCheckBox(autouse_frame),
        )
        autouse_checkbox.setFont(create_font(15, True))
        autouse_checkbox.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        autouse_checkbox.setText(autouse.replace("_", " ").title())
        autouse_checkbox.setObjectName(f"{autouse}_checkbox_{account_id}")

        horizontal_layout_autouse.addWidget(autouse_checkbox)
        vertical_layout.addWidget(autouse_frame)

    auto_use_right_frame_2.setWidget(auto_use_right_widget)
    horizontal_layout.addWidget(auto_use_right_frame_2, 0, Qt.AlignHCenter)
    getattr(self.ui, f"horizontal_layout_{int(account_id) + 102}").addWidget(
        auto_use_right_frame
    )
    getattr(self.ui, f"vertical_layout_{int(account_id) + 100}").addWidget(
        auto_use_frame
    )
    main_menu_widget.addWidget(auto_use_widget)

    self.ui.vertical_layout_4.addWidget(main_menu_widget)
    self.ui.horizontal_layout_29.addWidget(main_menu_frame)
    self.ui.main_menu_widget.addWidget(account_widget)

    # Labels
    account_btn.setText(f"Account {account_id}")
    self.ui.home_btn.setText("Home")
    self.ui.settings_btn.setText("Settings")
    self.ui.commands_btn.setText("Commands")
    self.ui.auto_buy_btn.setText("Auto Buy")
    self.ui.auto_use_btn.setText("Auto Use")
    self.ui.home_btn.setStyleSheet("background-color: #5865f2;")
    home_label.setText("Home")
    output_text.setHtml(
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

    settings_label.setText("Settings")
    token_label.setText("Discord Token")
    channel_label.setText("Channel ID")
    trivia_correct_label.setText("Correct Trivia Chance")
    adventure_label.setText("Adventure")
    for i in ["space", "west", "brazil", "vacation"]:
        adventure_box.addItem(i)
    offline_checkbox.setText("Appear Offline")
    auto_vote_checkbox.setText("Auto Vote")
    alerts_checkbox.setText("Read Alerts")
    commands_label.setText("Commands")

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

    main_menu_widget.setCurrentIndex(0)
    output_text.setVerticalScrollBar(output_scrollbar)

    # Initialize settings
    while True:
        try:
            lifesavers_checkbox.setChecked(
                config_dict[account_id]["autobuy"]["lifesavers"]["state"]
            )
            lifesavers_amount.setValue(
                config_dict[account_id]["autobuy"]["lifesavers"]["amount"]
            )
            token_input.setText(config_dict[account_id]["discord_token"])
            channel_input.setText(config_dict[account_id]["channel_id"])
            try:
                trivia_correct_chance.setValue(
                    int(
                        config_dict[account_id]["commands"]["trivia"][
                            "trivia_correct_chance"
                        ]
                        * 100
                    )
                )
            except KeyError:
                trivia_correct_chance.setValue(75)
                config_dict[account_id]["commands"]["trivia"][
                    "trivia_correct_chance"
                ] = 0.75
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)
            offline_checkbox.setChecked(config_dict[account_id]["offline"])
            auto_vote_checkbox.setChecked(config_dict[account_id]["auto_vote"])
            alerts_checkbox.setChecked(config_dict[account_id]["alerts"])

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
                except TypeError:
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

            auto_use_checkbox.setChecked(config_dict[account_id]["autouse"]["state"])
            hide_disabled_checkbox.setChecked(
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
            lambda checked, clicked_account_id=account_id, clicked_button=button: self.commands(
                clicked_button,
                {
                    "state": getattr(
                        self.ui, f"{clicked_button}_checkbox_{clicked_account_id}"
                    ).isChecked()
                },
            )
        )
        getattr(self.ui, f"{button}_spinbox_{account_id}").valueChanged.connect(
            lambda checked, clicked_account_id=account_id, clicked_button=button: self.commands(
                button,
                {
                    "delay": getattr(
                        self.ui, f"{clicked_button}_spinbox_{clicked_account_id}"
                    ).value()
                },
            )
        )
    start_btn.clicked.connect(lambda: self.toggle_all(True))
    stop_btn.clicked.connect(lambda: self.toggle_all(False))

    # Autobuy
    autobuy_buttons = ["lifesavers", "fishing", "shovel", "rifle"]
    for button in autobuy_buttons:
        getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
            lambda checked, clicked_account_id=account_id, clicked_button=button: self.autobuy(
                button,
                getattr(
                    self.ui, f"{clicked_button}_checkbox_{clicked_account_id}"
                ).isChecked(),
                "state",
            )
        )
    lifesavers_amount.valueChanged.connect(
        lambda checked: self.autobuy(
            "lifesavers",
            lifesavers_amount.value(),
            "amount",
        )
    )

    # Autouse
    auto_use_checkbox.clicked.connect(
        lambda: self.autouse(
            "state",
            autouse_checkbox.isChecked(),
        )
    )
    search_input.textChanged.connect(
        lambda: self.autouse(
            "search",
            search_input.text(),
        )
    )
    for button in config_dict[account_id]["autouse"]:
        if button == "state":
            continue
        getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
            lambda checked, clicked_account_id=account_id, clicked_button=button: self.autouse(
                clicked_button,
                getattr(self.ui, f"{button}_checkbox_{clicked_account_id}").isChecked(),
                "state",
            )
        )

    # Settings buttons
    token_input.textChanged.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "token", getattr(self.ui, f"token_input_{clicked_account_id}").text()
        )
    )
    channel_input.textChanged.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "channel", getattr(self.ui, f"channel_input_{clicked_account_id}").text()
        )
    )
    trivia_correct_chance.valueChanged.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "trivia_correct_chance",
            getattr(self.ui, f"trivia_correct_chance_{clicked_account_id}").value(),
        )
    )
    offline_checkbox.clicked.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "offline",
            getattr(self.ui, f"offline_checkbox_{clicked_account_id}").isChecked(),
        )
    )
    auto_vote_checkbox.clicked.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "auto_vote",
            getattr(self.ui, f"auto_vote_checkbox_{clicked_account_id}").isChecked(),
        )
    )
    alerts_checkbox.clicked.connect(
        lambda checked, clicked_account_id=account_id: self.settings(
            "alerts",
            getattr(self.ui, f"alerts_checkbox_{clicked_account_id}").isChecked(),
        )
    )

    # Account buttons
    account_btn.clicked.connect(
        lambda checked, clicked_account_id=account_id: self.accounts(
            clicked_account_id
        ),
    )
