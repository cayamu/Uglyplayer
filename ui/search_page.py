from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ui.theme import Colors, Sizes, font
from ui import icons
from ui.track_row import TrackRow


class SearchPage(QWidget):
    search_requested = pyqtSignal(str)
    track_clicked = pyqtSignal(dict)
    like_clicked = pyqtSignal(dict)
    download_clicked = pyqtSignal(dict)

    TABS = ["All", "Tracks", "Albums", "Artists", "Playlists"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.current_tab = "All"
        self._tracks = []

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 16)
        v.setSpacing(14)

        title = QLabel("2. SEARCH")
        title.setFont(font(11, "bold"))
        title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px;")
        v.addWidget(title)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search tracks, artists, albums...")
        self.search.setFixedHeight(Sizes.SEARCH_H)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.GLASS_BG_STRONG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.SEARCH_H // 2}px;
                padding: 0 16px 0 44px;
                color: {Colors.TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {Colors.ACCENT}; }}
        """)
        self.search.returnPressed.connect(self._on_search)
        self.search.textChanged.connect(self._on_text_changed)
        v.addWidget(self.search)

        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(8)
        self.tab_buttons = {}
        for tab_name in self.TABS:
            btn = QPushButton(tab_name)
            btn.setFont(font(12, "semibold"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, t=tab_name: self._on_tab(t))
            tabs_row.addWidget(btn)
            self.tab_buttons[tab_name] = btn
        tabs_row.addStretch()
        v.addLayout(tabs_row)
        self._update_tabs()

        # Popular
        self.popular_widget = QWidget()
        self.popular_widget.setStyleSheet("background: transparent;")
        pv = QVBoxLayout(self.popular_widget)
        pv.setContentsMargins(0, 8, 0, 0)
        pv.setSpacing(8)

        pt = QLabel("Popular searches")
        pt.setFont(font(14, "bold"))
        pt.setStyleSheet(f"color: {Colors.TEXT};")
        pv.addWidget(pt)

        for q in ["Lil Peep", "Phonk", "Tired", "CUPSIZE", "Баста"]:
            b = QPushButton(f"   {q}")
            b.setFont(font(12))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setIcon(icons.svg_icon(icons.ICON_SEARCH, Colors.TEXT_SECONDARY, 14))
            b.setIconSize(QSize(14, 14))
            b.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {Colors.TEXT_SECONDARY};
                    text-align: left; padding: 8px 4px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    color: {Colors.TEXT};
                    background-color: {Colors.GLASS_HOVER};
                }}
            """)
            b.clicked.connect(lambda _, text=q: self._fill_and_search(text))
            pv.addWidget(b)
        pv.addStretch()
        v.addWidget(self.popular_widget, 1)

        # Results
        self.results_widget = QWidget()
        self.results_widget.setStyleSheet("background: transparent;")
        self.results_widget.setVisible(False)
        rv = QVBoxLayout(self.results_widget)
        rv.setContentsMargins(0, 8, 0, 0)
        rv.setSpacing(4)

        self.results_label = QLabel("Tracks")
        self.results_label.setFont(font(14, "bold"))
        self.results_label.setStyleSheet(f"color: {Colors.TEXT};")
        rv.addWidget(self.results_label)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.results_scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.1); border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.results_list = QWidget()
        self.results_list.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_list)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(2)
        self.results_layout.addStretch()

        self.results_scroll.setWidget(self.results_list)
        rv.addWidget(self.results_scroll, 1)
        v.addWidget(self.results_widget, 1)

    def _on_search(self):
        q = self.search.text().strip()
        if q:
            self.search_requested.emit(q)

    def _on_text_changed(self, text):
        if not text.strip():
            self.popular_widget.setVisible(True)
            self.results_widget.setVisible(False)

    def _fill_and_search(self, text):
        self.search.setText(text)
        self.search_requested.emit(text)

    def _on_tab(self, tab):
        self.current_tab = tab
        self._update_tabs()

    def _update_tabs(self):
        for name, btn in self.tab_buttons.items():
            if name == self.current_tab:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.GLASS_ACTIVE};
                        border: 1px solid {Colors.GLASS_BORDER};
                        color: {Colors.TEXT};
                        padding: 6px 14px; border-radius: 16px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: 1px solid transparent;
                        color: {Colors.TEXT_SECONDARY};
                        padding: 6px 14px; border-radius: 16px;
                    }}
                    QPushButton:hover {{
                        color: {Colors.TEXT};
                        background-color: {Colors.GLASS_BG};
                    }}
                """)

    def show_results(self, tracks, query=""):
        self._tracks = tracks
        self.popular_widget.setVisible(False)
        self.results_widget.setVisible(True)
        self.results_label.setText(f"Top results for '{query}'" if query else "Tracks")

        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tracks:
            e = QLabel(f"Nothing found for '{query}'")
            e.setFont(font(13))
            e.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 40px;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.insertWidget(0, e)
            return

        for i, track in enumerate(tracks):
            row = TrackRow(track, index=i)
            row.clicked.connect(self.track_clicked.emit)
            row.play_clicked.connect(self.track_clicked.emit)
            row.like_clicked.connect(self.like_clicked.emit)
            row.download_clicked.connect(self.download_clicked.emit)
            self.results_layout.insertWidget(self.results_layout.count() - 1, row)