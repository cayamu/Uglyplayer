from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ui.theme import Colors, Sizes
from ui import icons


class SidebarButton(QPushButton):
    def __init__(self, icon_name, tooltip, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 12px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {Colors.GLASS_HOVER}; }}
            QPushButton:checked {{ background-color: {Colors.GLASS_ACTIVE}; }}
            QPushButton:focus {{ border: none; outline: none; }}
        """)
        self.toggled.connect(self._update_icon)
        self._update_icon()

    def _update_icon(self):
        color = Colors.ACCENT if self.isChecked() else Colors.TEXT_SECONDARY
        self.setIcon(icons.svg_icon(self.icon_name, color, 22))
        self.setIconSize(QSize(22, 22))


class Sidebar(QFrame):
    nav_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(Sizes.SIDEBAR_W)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GLASS_BG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.RADIUS}px;
            }}
        """)
        self.buttons = {}
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 16, 12, 16)
        v.setSpacing(10)

        for icon_name, tip, key in [
            (icons.ICON_HOME, "Главная", "home"),
            (icons.ICON_SEARCH, "Поиск", "search"),
            (icons.ICON_LIBRARY, "Библиотека", "library"),
        ]:
            btn = SidebarButton(icon_name, tip)
            btn.clicked.connect(lambda _, k=key: self._on_click(k))
            v.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
            self.buttons[key] = btn

        v.addStretch()

        st = SidebarButton(icons.ICON_SETTINGS, "Настройки")
        st.clicked.connect(lambda: self._on_click("settings"))
        v.addWidget(st, 0, Qt.AlignmentFlag.AlignHCenter)
        self.buttons["settings"] = st
        self.buttons["home"].setChecked(True)

    def _on_click(self, key):
        for k, btn in self.buttons.items():
            btn.setChecked(k == key)
        self.nav_clicked.emit(key)