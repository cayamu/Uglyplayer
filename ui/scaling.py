"""
Централизованное масштабирование интерфейса под любой экран.
Учитывает DPI монитора + размер экрана + масштаб Windows.
"""
from PyQt6.QtGui import QGuiApplication, QFont
from PyQt6.QtWidgets import QApplication


class Scale:
    """Единая точка для всех размеров."""

    def __init__(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            # Fallback
            self.dpi = 96.0
            self.screen_w = 1920
            self.screen_h = 1080
        else:
            self.dpi = screen.logicalDotsPerInch()
            geo = screen.availableGeometry()
            self.screen_w = geo.width()
            self.screen_h = geo.height()

        # DPI-коэффициент (норма 96)
        self.dpi_scale = self.dpi / 96.0

        # Размер экрана относительно 1920×1080
        self.size_scale = min(self.screen_w / 1920.0, self.screen_h / 1080.0)

        # Итоговый масштаб: среднее между DPI и размером
        raw = (self.dpi_scale + self.size_scale) / 2.0

        # Ограничиваем: не меньше 0.7, не больше 2.5
        self.scale = max(0.7, min(2.5, raw))

        print(f"[Scale] DPI={self.dpi}, экран={self.screen_w}×{self.screen_h}, "
              f"масштаб={self.scale:.2f}")

    # -------- ГЛАВНЫЕ МЕТОДЫ --------
    def px(self, value: int) -> int:
        """Пиксели с учётом масштаба."""
        return max(1, int(value * self.scale))

    def pt(self, value: int) -> int:
        """Размер шрифта."""
        return max(8, int(value * self.scale))

    def font(self, base_size: int = 14, bold: bool = False,
             family: str = "Segoe UI") -> QFont:
        """Готовый QFont с правильным размером."""
        f = QFont(family)
        f.setPointSize(self.pt(base_size))
        if bold:
            f.setBold(True)
        return f


# -------- ГЛОБАЛЬНЫЙ ДОСТУП --------
SCALE: Scale | None = None


def init_scale() -> Scale:
    """Вызывается один раз в main.py после создания QApplication."""
    global SCALE
    SCALE = Scale()
    return SCALE


def px(v: int) -> int:
    """Сокращение для размеров в пикселях."""
    return SCALE.px(v) if SCALE else v


def pt(v: int) -> int:
    """Сокращение для размеров шрифта."""
    return SCALE.pt(v) if SCALE else v


def font(base: int = 14, bold: bool = False) -> QFont:
    """Сокращение для шрифта."""
    if SCALE:
        return SCALE.font(base, bold)
    f = QFont("Segoe UI")
    f.setPointSize(base)
    if bold:
        f.setBold(True)
    return f