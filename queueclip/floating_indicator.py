"""
Floating Indicator - Visual display of queue status.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QScreen


class FloatingIndicator(QWidget):
    """
    A small floating window that displays the current queue status.
    Shows the next line to be pasted and the remaining count.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._drag_position = QPoint()
        self._setup_ui()
        self._position_window()

    def _setup_ui(self):
        """Set up the indicator UI."""
        # Window flags: frameless, always on top, tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint |  # Better behavior on Linux
            Qt.WindowType.WindowDoesNotAcceptFocus
        )

        # Make window translucent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container widget with background
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: #1e1e1e;
                border-radius: 6px;
                border: 1px solid #333333;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 8, 10, 8)
        container_layout.setSpacing(2)

        # Header row with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # App name label
        self.title_label = QLabel("QueueClip")
        self.title_label.setStyleSheet("""
            color: #888888;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Count label
        self.count_label = QLabel("0/0")
        self.count_label.setStyleSheet("""
            color: #555555;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 10px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.count_label)

        container_layout.addLayout(header_layout)

        # Next line preview
        self.preview_label = QLabel("Ready")
        self.preview_label.setStyleSheet("""
            color: #e0e0e0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            padding: 4px 0px;
        """)
        self.preview_label.setWordWrap(False)
        container_layout.addWidget(self.preview_label)

        # Hint label
        self.hint_label = QLabel("F9 to paste")
        self.hint_label.setStyleSheet("""
            color: #444444;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 9px;
        """)
        container_layout.addWidget(self.hint_label)

        main_layout.addWidget(self.container)

        # Set FIXED width so it doesn't grow
        self.setFixedWidth(240)

    def _position_window(self, position: str = 'top-right'):
        """Position the window on screen."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()

            # Calculate position
            margin = 20
            self.adjustSize()

            if position == 'top-right':
                x = geometry.right() - self.width() - margin
                y = geometry.top() + margin
            elif position == 'top-left':
                x = geometry.left() + margin
                y = geometry.top() + margin
            elif position == 'bottom-right':
                x = geometry.right() - self.width() - margin
                y = geometry.bottom() - self.height() - margin
            elif position == 'bottom-left':
                x = geometry.left() + margin
                y = geometry.bottom() - self.height() - margin
            else:
                x = geometry.right() - self.width() - margin
                y = geometry.top() + margin

            self.move(x, y)

    def set_position(self, position: str):
        """Set window position."""
        self._position_window(position)

    def update_status(self, next_line: str, current: int, total: int):
        """
        Update the indicator display.

        Args:
            next_line: The next line to be pasted
            current: Current position (1-indexed)
            total: Total number of lines
        """
        # Truncate long lines (shorter to fit fixed width)
        max_chars = 30
        display_line = next_line.strip()
        if len(display_line) > max_chars:
            display_line = display_line[:max_chars-3] + "..."

        self.preview_label.setText(display_line)
        self.count_label.setText(f"{current}/{total}")
        self.hint_label.setText("F9 to paste")

        # Show the indicator
        if not self.isVisible():
            self.show()

    def set_empty(self):
        """Set indicator to empty/ready state."""
        self.preview_label.setText("Queue empty")
        self.count_label.setText("0/0")
        self.hint_label.setText("Copy multi-line text to start")

    def set_ready(self):
        """Set indicator to ready state."""
        self.preview_label.setText("Ready")
        self.count_label.setText("0/0")
        self.hint_label.setText("Copy multi-line text to start")

    # --- Drag support ---

    def mousePressEvent(self, event):
        """Start dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle dragging."""
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Stop dragging."""
        self._dragging = False
        event.accept()
