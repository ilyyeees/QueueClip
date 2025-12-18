"""
Queue Manager - Core logic for managing the line queue.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Optional


class QueueManager(QObject):
    """
    Manages a queue of text lines for sequential pasting.
    Emits signals when queue state changes.
    """

    # Signals
    queue_changed = pyqtSignal()      # Emitted when queue content changes
    queue_empty = pyqtSignal()        # Emitted when queue becomes empty
    line_pasted = pyqtSignal(str)     # Emitted when a line is pasted (with the line text)

    # Default delimiters
    DELIMITER_NEWLINE = "\n"
    DELIMITER_COMMA = ","
    DELIMITER_TAB = "\t"
    DELIMITER_SEMICOLON = ";"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue: List[str] = []
        self._original_queue: List[str] = []  # For loop mode
        self._delimiter: str = self.DELIMITER_NEWLINE
        self._loop_mode: bool = False
        self._current_index: int = 0

    @property
    def delimiter(self) -> str:
        """Get current delimiter."""
        return self._delimiter

    @delimiter.setter
    def delimiter(self, value: str):
        """Set delimiter for splitting text."""
        self._delimiter = value if value else self.DELIMITER_NEWLINE

    @property
    def loop_mode(self) -> bool:
        """Get loop mode status."""
        return self._loop_mode

    @loop_mode.setter
    def loop_mode(self, value: bool):
        """Enable or disable loop mode."""
        self._loop_mode = value

    def load_text(self, text: str, delimiter: Optional[str] = None) -> int:
        """
        Load text and split into queue.
        Returns the number of lines loaded.
        """
        if delimiter is not None:
            self._delimiter = delimiter

        # Split by delimiter and filter empty lines
        if self._delimiter == self.DELIMITER_NEWLINE:
            # Handle both \n and \r\n
            lines = text.replace('\r\n', '\n').split('\n')
        else:
            lines = text.split(self._delimiter)

        # Strip whitespace and filter empty lines
        self._queue = [line.strip() for line in lines if line.strip()]
        self._original_queue = self._queue.copy()
        self._current_index = 0

        self.queue_changed.emit()
        return len(self._queue)

    def peek_next(self) -> Optional[str]:
        """
        View the next line without removing it.
        Returns None if queue is empty.
        """
        if self._queue:
            return self._queue[0]
        return None

    def pop_next(self) -> Optional[str]:
        """
        Remove and return the next line from queue.
        In loop mode, cycles back to beginning when empty.
        Returns None if queue is empty (and not looping).
        """
        if not self._queue:
            if self._loop_mode and self._original_queue:
                # Reload from original
                self._queue = self._original_queue.copy()
                self.queue_changed.emit()
            else:
                self.queue_empty.emit()
                return None

        if self._queue:
            line = self._queue.pop(0)
            self.line_pasted.emit(line)
            self.queue_changed.emit()

            # Check if now empty (and not looping)
            if not self._queue and not self._loop_mode:
                self.queue_empty.emit()

            return line

        return None

    def get_count(self) -> int:
        """Return number of remaining lines in queue."""
        return len(self._queue)

    def get_total(self) -> int:
        """Return total number of lines in original load."""
        return len(self._original_queue)

    def get_current_position(self) -> int:
        """Return current position (1-indexed for display)."""
        total = self.get_total()
        remaining = self.get_count()
        return total - remaining + 1 if total > 0 else 0

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def clear(self):
        """Clear the queue."""
        self._queue.clear()
        self._original_queue.clear()
        self._current_index = 0
        self.queue_changed.emit()
        self.queue_empty.emit()

    def get_all_lines(self) -> List[str]:
        """Get all remaining lines (for preview)."""
        return self._queue.copy()
