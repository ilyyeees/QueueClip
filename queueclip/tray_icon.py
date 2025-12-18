"""
System Tray Icon - Tray icon with context menu.
"""

import platform
from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QApplication, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import pyqtSignal, QSize


def create_default_icon() -> QIcon:
    """Create a simple default icon (clipboard with lines)."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw clipboard background
    painter.setBrush(QColor(70, 130, 180))  # Steel blue
    painter.setPen(QColor(50, 100, 150))
    painter.drawRoundedRect(8, 4, 48, 56, 6, 6)

    # Draw clipboard clip
    painter.setBrush(QColor(100, 160, 210))
    painter.drawRoundedRect(20, 0, 24, 12, 3, 3)

    # Draw lines (representing text)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawLine(16, 22, 48, 22)
    painter.drawLine(16, 32, 44, 32)
    painter.drawLine(16, 42, 48, 42)
    painter.drawLine(16, 52, 36, 52)

    painter.end()

    return QIcon(pixmap)


def create_icon_with_count(count: int) -> QIcon:
    """Create icon with count badge."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw clipboard background
    painter.setBrush(QColor(70, 130, 180))
    painter.setPen(QColor(50, 100, 150))
    painter.drawRoundedRect(4, 4, 44, 52, 6, 6)

    # Draw clipboard clip
    painter.setBrush(QColor(100, 160, 210))
    painter.drawRoundedRect(14, 0, 20, 10, 3, 3)

    # Draw lines
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawLine(12, 20, 40, 20)
    painter.drawLine(12, 28, 36, 28)
    painter.drawLine(12, 36, 40, 36)

    # Draw count badge
    if count > 0:
        badge_color = QColor(255, 100, 100) if count <= 3 else QColor(100, 200, 100)
        painter.setBrush(badge_color)
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(40, 36, 22, 22)

        # Draw count text
        font = QFont()
        font.setBold(True)
        font.setPixelSize(14)
        painter.setFont(font)
        painter.drawText(40, 36, 22, 22, 0x84, str(min(count, 99)))  # AlignCenter = 0x84

    painter.end()

    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    """
    System tray icon with context menu for QueueClip.
    """

    # Signals
    show_indicator_toggled = pyqtSignal(bool)
    loop_mode_toggled = pyqtSignal(bool)
    delimiter_changed = pyqtSignal(str)
    clear_queue_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setIcon(create_default_icon())
        self.setToolTip("QueueClip - Ready")

        self._setup_menu()

        # Connect activation
        self.activated.connect(self._on_activated)

    def _setup_menu(self):
        """Set up the context menu."""
        menu = QMenu()

        # Status display (not clickable)
        self.status_action = QAction("Queue: Empty", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)

        # Next line preview
        self.preview_action = QAction("Next: (none)", menu)
        self.preview_action.setEnabled(False)
        menu.addAction(self.preview_action)

        menu.addSeparator()

        # Loop mode toggle
        self.loop_action = QAction("Loop Mode", menu)
        self.loop_action.setCheckable(True)
        self.loop_action.triggered.connect(lambda checked: self.loop_mode_toggled.emit(checked))
        menu.addAction(self.loop_action)

        # Show indicator toggle
        self.indicator_action = QAction("Show Indicator", menu)
        self.indicator_action.setCheckable(True)
        self.indicator_action.setChecked(True)
        self.indicator_action.triggered.connect(lambda checked: self.show_indicator_toggled.emit(checked))
        menu.addAction(self.indicator_action)

        menu.addSeparator()

        # Delimiter submenu
        delimiter_menu = QMenu("Delimiter", menu)

        self.delimiter_group = []
        delimiters = [
            ("Newline (↵)", "newline"),
            ("Comma (,)", "comma"),
            ("Tab (⇥)", "tab"),
            ("Semicolon (;)", "semicolon"),
        ]

        for label, value in delimiters:
            action = QAction(label, delimiter_menu)
            action.setCheckable(True)
            action.setChecked(value == "newline")
            action.triggered.connect(lambda checked, v=value: self._on_delimiter_selected(v))
            delimiter_menu.addAction(action)
            self.delimiter_group.append((action, value))

        menu.addMenu(delimiter_menu)

        menu.addSeparator()

        # Clear queue
        clear_action = QAction("Clear Queue", menu)
        clear_action.triggered.connect(self.clear_queue_requested.emit)
        menu.addAction(clear_action)

        # Settings
        settings_action = QAction("Settings...", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Quit
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Could show settings or indicator
            self.settings_requested.emit()

    def _on_delimiter_selected(self, delimiter: str):
        """Handle delimiter selection."""
        # Update checkmarks
        for action, value in self.delimiter_group:
            action.setChecked(value == delimiter)

        self.delimiter_changed.emit(delimiter)

    def set_delimiter(self, delimiter: str):
        """Set the current delimiter (update menu checkmarks)."""
        for action, value in self.delimiter_group:
            action.setChecked(value == delimiter)

    def set_loop_mode(self, enabled: bool):
        """Set loop mode state."""
        self.loop_action.setChecked(enabled)

    def set_show_indicator(self, visible: bool):
        """Set indicator visibility state."""
        self.indicator_action.setChecked(visible)

    def update_status(self, next_line: str, current: int, total: int):
        """Update the tray icon status."""
        if total > 0:
            self.status_action.setText(f"Queue: {total - current + 1} remaining")

            # Truncate preview
            preview = next_line[:30] + "..." if len(next_line) > 30 else next_line
            self.preview_action.setText(f"Next: {preview}")

            self.setToolTip(f"QueueClip - {current}/{total}: {preview}")
            self.setIcon(create_icon_with_count(total - current + 1))
        else:
            self.status_action.setText("Queue: Empty")
            self.preview_action.setText("Next: (none)")
            self.setToolTip("QueueClip - Ready")
            self.setIcon(create_default_icon())

    def set_empty(self):
        """Set to empty state."""
        self.update_status("", 0, 0)

    def show_message(self, title: str, message: str, icon=None):
        """Show a tray notification."""
        if icon is None:
            icon = QSystemTrayIcon.MessageIcon.Information
        self.showMessage(title, message, icon, 2000)
