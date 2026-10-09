"""
Плеер с автопереключением треков.
"""
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, pyqtSignal, QObject


class Player(QObject):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    track_ended = pyqtSignal()          # НОВОЕ: трек закончился

    def __init__(self):
        super().__init__()
        self.media = QMediaPlayer()
        self.audio = QAudioOutput()
        self.audio.setVolume(0.8)
        self.media.setAudioOutput(self.audio)

        self.media.positionChanged.connect(self.position_changed.emit)
        self.media.durationChanged.connect(self.duration_changed.emit)
        self.media.playbackStateChanged.connect(self._on_state)
        self.media.errorOccurred.connect(self._on_error)
        self.media.mediaStatusChanged.connect(self._on_status)  # НОВОЕ

    def _on_state(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.state_changed.emit("playing")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.state_changed.emit("paused")
        else:
            self.state_changed.emit("stopped")

    def _on_error(self, error, error_string):
        if error_string:
            print(f"[Player] error: {error_string}")
            self.error_occurred.emit(error_string)

    def _on_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("[Player] Трек закончился")
            self.track_ended.emit()

    def play_file(self, path: str):
        self.media.setSource(QUrl.fromLocalFile(path))
        self.media.play()

    def play_url(self, url: str):
        self.media.setSource(QUrl(url))
        self.media.play()

    def toggle_pause(self):
        if self.media.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media.pause()
        else:
            self.media.play()

    def stop(self):
        self.media.stop()

    def seek(self, ms: int):
        self.media.setPosition(ms)

    def set_volume(self, v: float):
        self.audio.setVolume(float(v))

    def is_playing(self) -> bool:
        return self.media.playbackState() == QMediaPlayer.PlaybackState.PlayingState