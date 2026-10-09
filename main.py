"""
UglyPlayer — точка входа.
"""
import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("UglyPlayer")
    app.setOrganizationName("UglyPlayer")

    # Загрузка шрифтов Inter из assets/fonts/
    from ui.theme import load_fonts
    load_fonts()

    # Шрифт по умолчанию
    f = QFont("Inter")
    if not f.exactMatch():
        f = QFont("Segoe UI")
    f.setPointSize(10)
    app.setFont(f)

    # Главное окно
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()