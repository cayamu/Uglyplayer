"""
MP4-фон через QGraphicsVideoItem.
Работает как обычный виджет — не перекрывает другие.
"""
import os
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import Qt, QUrl, QRectF


class VideoBackground(QGraphicsView):
    """Видео-фон: НЕ перекрывает виджеты Qt."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: black; border: none;")
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Сцена
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Видео-итем
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        # Плеер
        self.media = QMediaPlayer()
        self.audio = QAudioOutput()
        self.audio.setVolume(0.0)   # ЗВУК ВЫКЛЮЧЕН
        self.media.setAudioOutput(self.audio)
        self.media.setVideoOutput(self.video_item)

        # Loop
        self.media.mediaStatusChanged.connect(self._on_status)

        self._current_path = None

    def _on_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media.setPosition(0)
            self.media.play()

    def resizeEvent(self, event):
        """Видео растягивается под размер view."""
        super().resizeEvent(event)
        r = QRectF(0, 0, self.width(), self.height())
        self.scene.setSceneRect(r)
        self.video_item.setSize(r.size())

    def play_video(self, path: str):
        if not path or not os.path.exists(path):
            return False
        self._current_path = path
        self.media.setSource(QUrl.fromLocalFile(path))
        self.media.play()
        print(f"[VideoBackground] Запущено: {os.path.basename(path)}")
        return True

    def stop(self):
        self.media.stop()
        self._current_path = None

    def pause(self):
        self.media.pause()

    def resume(self):
        if self._current_path:
            self.media.play()

    def is_video_active(self) -> bool:
        return self.media.playbackState() == QMediaPlayer.PlaybackState.PlayingState