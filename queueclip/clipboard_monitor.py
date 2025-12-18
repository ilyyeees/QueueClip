"""
Clipboard Monitor - Watches for clipboard changes.
Cross-platform support for Windows and Linux.
"""

import time
import pyperclip
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


class ClipboardMonitor(QObject):
    """
    Monitors the system clipboard for changes using Qt signals.
    Efficient event-driven architecture (0% CPU idle).
    """

    # Signal emitted when new multi-line content is detected
    content_detected = pyqtSignal(str)

    def __init__(self, min_lines: int = 2, parent=None):
        super().__init__(parent)
        self._min_lines = min_lines
        self._paused = False
        self._last_content = ""

        # Access system clipboard via Qt
        self.clipboard = QApplication.clipboard()

        # Connect to signal
        self.clipboard.dataChanged.connect(self._on_data_changed)

    @property
    def min_lines(self) -> int:
        """Minimum number of lines to trigger queue mode."""
        return self._min_lines

    @min_lines.setter
    def min_lines(self, value: int):
        """Set minimum lines threshold."""
        self._min_lines = max(1, value)

    def pause(self):
        """Pause monitoring temporarily."""
        if not self._paused:
            print("[Monitor] Paused")
            self._paused = True
            # Disconnect signal to stop receiving events
            try:
                self.clipboard.dataChanged.disconnect(self._on_data_changed)
            except Exception:
                pass

    def resume(self):
        """Resume monitoring."""
        if self._paused:
            print("[Monitor] Resumed")
            self._paused = False
            # Reconnect signal
            try:
                self.clipboard.dataChanged.connect(self._on_data_changed)
            except Exception:
                pass

    def _on_data_changed(self):
        """Handle clipboard data changed signal."""
        if self._paused:
            return

        try:
            # Get text from clipboard
            # mode=QClipboard.Mode.Clipboard is default
            text = self.clipboard.text()

            if not text:
                return

            # Avoid processing same content twice (though signal usually dedupes)
            if text == self._last_content:
                return

            self._last_content = text

            # Count lines
            # Optimization: count newlines directly
            line_count = text.count('\n') + 1

            print(f"[Monitor] Changed! {len(text)} chars, {line_count} lines")

            if line_count >= self._min_lines:
                print(f"[Monitor] EMITTING!")
                self.content_detected.emit(text)

        except Exception as e:
            print(f"[Monitor] Error: {e}")

    def stop(self):
        """Stop monitoring (cleanup)."""
        try:
            self.clipboard.dataChanged.disconnect(self._on_data_changed)
        except Exception:
            pass

    def update_last_content(self, content: str):
        """Update tracked content (call when we modify clipboard ourselves)."""
        self._last_content = content


def set_clipboard(text: str) -> bool:
    """
    Set clipboard content. Cross-platform.
    Returns True on success.
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Clipboard write error: {e}")
        return False


def get_clipboard() -> str:
    """
    Get clipboard content. Cross-platform.
    Returns empty string on failure.
    """
    try:
        return pyperclip.paste() or ""
    except Exception:
        return ""
