from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ui.theme import Colors, Sizes, font
from ui import icons


class SectionHeader(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(font(11, "bold"))
        self.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px; padding: 12px 0 8px;")


class SettingRow(QFrame):
    def __init__(self, label, widget, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 6, 0, 6)
        h.setSpacing(16)
        lbl = QLabel(label)
        lbl.setFont(font(13))
        lbl.setStyleSheet(f"color: {Colors.TEXT};")
        h.addWidget(lbl, 1)
        h.addWidget(widget, 0)


class MenuItem(QPushButton):
    def __init__(self, icon_name, text, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(36)
        self.setIcon(icons.svg_icon(icon_name, Colors.TEXT_SECONDARY, 16))
        self.setIconSize(QSize(16, 16))
        self.setText(f"  {text}")
        self.setFont(font(13))
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {Colors.TEXT_SECONDARY};
                text-align: left; padding: 0 12px; border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GLASS_HOVER}; color: {Colors.TEXT};
            }}
            QPushButton:checked {{
                background-color: {Colors.GLASS_ACTIVE}; color: {Colors.TEXT};
            }}
        """)


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 16)
        v.setSpacing(16)

        title = QLabel("4. SETTINGS")
        title.setFont(font(11, "bold"))
        title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px;")
        v.addWidget(title)

        h = QHBoxLayout()
        h.setSpacing(24)

        menu = QWidget()
        menu.setFixedWidth(180)
        menu.setStyleSheet("background: transparent;")
        mv = QVBoxLayout(menu)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(4)

        self.menu_items = {}
        for key, icon_name, text in [
            ("general", icons.ICON_SETTINGS, "General"),
            ("audio", icons.ICON_HEADPHONES, "Audio"),
            ("appearance", icons.ICON_SLIDERS, "Appearance"),
            ("shortcuts", icons.ICON_KEYBOARD, "Shortcuts"),
            ("about", icons.ICON_INFO, "About"),
        ]:
            btn = MenuItem(icon_name, text)
            btn.clicked.connect(lambda _, k=key: self._switch(k))
            mv.addWidget(btn)
            self.menu_items[key] = btn
        mv.addStretch()
        h.addWidget(menu)

        self.content = QScrollArea()
        self.content.setWidgetResizable(True)
        self.content.setFrameShape(QFrame.Shape.NoFrame)
        self.content.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.1); border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_v = QVBoxLayout(self.content_widget)
        self.content_v.setContentsMargins(0, 0, 0, 0)
        self.content_v.setSpacing(4)

        self.content.setWidget(self.content_widget)
        h.addWidget(self.content, 1)

        v.addLayout(h, 1)
        self._switch("general")

    def _switch(self, key):
        for k, btn in self.menu_items.items():
            btn.setChecked(k == key)

        while self.content_v.count():
            item = self.content_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if key == "general":
            self._build_general()
        elif key == "audio":
            self._build_audio()
        elif key == "appearance":
            self._build_appearance()
        elif key == "shortcuts":
            self._build_shortcuts()
        elif key == "about":
            self._build_about()

        self.content_v.addStretch()

    def _build_general(self):
        self.content_v.addWidget(SectionHeader("GENERAL"))

        device = QComboBox()
        device.addItems(["Default Device (Speakers)"])
        device.setFixedHeight(34)
        self.content_v.addWidget(SettingRow("Output device", device))

        quality = QComboBox()
        quality.addItems(["High (320 kbps)", "Standard (192 kbps)", "Low (128 kbps)"])
        quality.setFixedHeight(34)
        self.content_v.addWidget(SettingRow("Audio quality", quality))

        norm = QCheckBox()
        norm.setChecked(True)
        self.content_v.addWidget(SettingRow("Volume normalization", norm))

        cross = QCheckBox()
        self.content_v.addWidget(SettingRow("Crossfade", cross))

        dur = QSlider(Qt.Orientation.Horizontal)
        dur.setRange(0, 12)
        dur.setValue(5)
        dur.setFixedWidth(200)
        self.content_v.addWidget(SettingRow("Crossfade duration", dur))

    def _build_audio(self):
        self.content_v.addWidget(SectionHeader("AUDIO"))
        device = QComboBox()
        device.addItems(["Default Device (Speakers)", "Headphones", "Speakers"])
        device.setFixedHeight(34)
        self.content_v.addWidget(SettingRow("Playback device", device))

        quality = QComboBox()
        quality.addItems(["High (320 kbps)", "Standard (192 kbps)"])
        quality.setFixedHeight(34)
        self.content_v.addWidget(SettingRow("Quality", quality))

    def _build_appearance(self):
        self.content_v.addWidget(SectionHeader("APPEARANCE"))

        theme = QComboBox()
        theme.addItems(["Dark", "Light", "System"])
        theme.setFixedHeight(34)
        self.content_v.addWidget(SettingRow("Theme", theme))

        accent_row = QWidget()
        accent_row.setStyleSheet("background: transparent;")
        ah = QHBoxLayout(accent_row)
        ah.setContentsMargins(0, 0, 0, 0)
        ah.setSpacing(8)

        for color in ["#F04444", "#A855F7", "#06B6D4", "#22C55E", "#F59E0B"]:
            dot = QPushButton()
            dot.setFixedSize(20, 20)
            dot.setCursor(Qt.CursorShape.PointingHandCursor)
            dot.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid transparent; border-radius: 10px;
                }}
                QPushButton:hover {{ border-color: rgba(255,255,255,0.4); }}
            """)
            ah.addWidget(dot)

        self.content_v.addWidget(SettingRow("Accent color", accent_row))

        blur = QSlider(Qt.Orientation.Horizontal)
        blur.setRange(0, 30); blur.setValue(20); blur.setFixedWidth(200)
        self.content_v.addWidget(SettingRow("Glass blur", blur))

        scale = QSlider(Qt.Orientation.Horizontal)
        scale.setRange(50, 150); scale.setValue(100); scale.setFixedWidth(200)
        self.content_v.addWidget(SettingRow("Interface scale", scale))

    def _build_shortcuts(self):
        self.content_v.addWidget(SectionHeader("SHORTCUTS"))
        for label, key in [
            ("Play / Pause", "Space"),
            ("Next track", "Ctrl + →"),
            ("Previous track", "Ctrl + ←"),
            ("Open lyrics", "Ctrl + L"),
        ]:
            kl = QLabel(key)
            kl.setFont(font(12))
            kl.setStyleSheet(f"""
                color: {Colors.TEXT};
                background-color: {Colors.GLASS_BG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: 6px; padding: 4px 12px;
            """)
            self.content_v.addWidget(SettingRow(label, kl))

    def _build_about(self):
        self.content_v.addWidget(SectionHeader("ABOUT"))
        t = QLabel("UglyPlayer")
        t.setFont(font(20, "bold"))
        t.setStyleSheet(f"color: {Colors.TEXT};")
        self.content_v.addWidget(t)
        v = QLabel("Version 1.0.0")
        v.setFont(font(12))
        v.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.content_v.addWidget(v)