from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


def fade_in(widget: QWidget, duration: int = 300, delay: int = 0):
    """Плавное появление виджета (opacity 0 -> 1)."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    if delay > 0:
        anim.setStartValue(0.0)
        # Запуск с задержкой через QTimer
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(delay, anim.start)
    else:
        anim.start()
    
    # Чтобы анимация не удалилась сборщиком мусора
    widget._fade_anim = anim
    return anim


def slide_in(widget: QWidget, duration: int = 250, offset: int = 20):
    """Плавное появление с небольшим сдвигом."""
    from PyQt6.QtCore import QPropertyAnimation, QPoint
    original_pos = widget.pos()
    
    widget.move(original_pos.x(), original_pos.y() + offset)
    
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(widget.pos())
    anim.setEndValue(original_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    
    widget._slide_anim = anim
    return anim


def pulse(widget: QWidget, duration: int = 1000):
    """Пульсация (для индикатора «играет»)."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.3)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    anim.setLoopCount(-1)  # бесконечно
    anim.start()
    
    widget._pulse_anim = anim
    return anim