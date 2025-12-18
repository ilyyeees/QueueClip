"""
QueueClip - Main Application
Entry point and orchestration of all components.
"""

import sys
import signal
import shutil
import os
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QLockFile, QDir

from .queue_manager import QueueManager
from .clipboard_monitor import ClipboardMonitor, set_clipboard, get_clipboard
from .hotkey_handler import HotkeyHandler, get_default_hotkey_text
from .floating_indicator import FloatingIndicator
from .tray_icon import TrayIcon
from .settings import Settings, SettingsDialog


class QueueClipApp:
    """
    Main application class that orchestrates all QueueClip components.
    """

    def __init__(self):
        self.app: Optional[QApplication] = None
        self.settings: Optional[Settings] = None
        self.queue_manager: Optional[QueueManager] = None
        self.clipboard_monitor: Optional[ClipboardMonitor] = None
        self.hotkey_handler: Optional[HotkeyHandler] = None
        self.tray_icon: Optional[TrayIcon] = None
        self.indicator: Optional[FloatingIndicator] = None

    def init(self):
        """Initialize all components."""
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("QueueClip")
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in tray

        # Check for dependencies (Linux)
        if sys.platform == "linux" and not shutil.which("xdotool"):
            QMessageBox.warning(None, "Missing Dependency",
                "QueueClip requires 'xdotool' to simulate pasting in terminals.\n\n"
                "Please run: sudo apt install xdotool")

        # Load settings
        self.settings = Settings()

        # Create queue manager
        self.queue_manager = QueueManager()
        self.queue_manager.loop_mode = self.settings.loop_mode
        self._set_delimiter_from_settings()

        # Create clipboard monitor
        self.clipboard_monitor = ClipboardMonitor(
            min_lines=self.settings.min_lines
        )

        # Create hotkey handler
        self.hotkey_handler = HotkeyHandler()

        # Create UI components
        self.indicator = FloatingIndicator()
        self.indicator.set_position(self.settings.get('indicator_position', 'top-right'))

        self.tray_icon = TrayIcon()
        self.tray_icon.set_loop_mode(self.settings.loop_mode)
        self.tray_icon.set_show_indicator(self.settings.show_indicator)
        self.tray_icon.set_delimiter(self.settings.delimiter)

        # Connect signals
        self._connect_signals()

        # Initial UI state
        if self.settings.show_indicator:
            self.indicator.set_ready()
            self.indicator.show()

        self.tray_icon.show()

    def _set_delimiter_from_settings(self):
        """Set queue manager delimiter from settings."""
        delimiter_map = {
            'newline': QueueManager.DELIMITER_NEWLINE,
            'comma': QueueManager.DELIMITER_COMMA,
            'tab': QueueManager.DELIMITER_TAB,
            'semicolon': QueueManager.DELIMITER_SEMICOLON,
        }
        delimiter = self.settings.delimiter
        self.queue_manager.delimiter = delimiter_map.get(delimiter, QueueManager.DELIMITER_NEWLINE)

    def _connect_signals(self):
        """Connect all component signals."""
        # Clipboard monitor -> Queue loading
        self.clipboard_monitor.content_detected.connect(self._on_clipboard_content)

        # Hotkey -> Paste action
        self.hotkey_handler.paste_triggered.connect(self._on_paste_triggered)

        # Queue manager -> UI updates
        self.queue_manager.queue_changed.connect(self._update_ui)
        self.queue_manager.queue_empty.connect(self._on_queue_empty)

        # Tray icon menu actions
        self.tray_icon.loop_mode_toggled.connect(self._on_loop_mode_toggled)
        self.tray_icon.show_indicator_toggled.connect(self._on_show_indicator_toggled)
        self.tray_icon.delimiter_changed.connect(self._on_delimiter_changed)
        self.tray_icon.clear_queue_requested.connect(self._on_clear_queue)
        self.tray_icon.settings_requested.connect(self._show_settings)
        self.tray_icon.quit_requested.connect(self._quit)

    def _on_clipboard_content(self, content: str):
        """Handle new clipboard content detected."""
        # Load into queue
        count = self.queue_manager.load_text(content)
        # UI updates automatically via queue_changed signal

    def _on_paste_triggered(self):
        """Handle paste hotkey triggered."""
        if self.queue_manager.is_empty():
            return

        # Get the current line from queue
        current_line = self.queue_manager.peek_next()
        if not current_line:
            return

        try:
            # Save original clipboard content
            original_clipboard = get_clipboard()

            # Pause monitor while we manipulate clipboard
            self.clipboard_monitor.pause()

            # Put our queue line in clipboard
            set_clipboard(current_line)

            # Simulate paste (Ctrl+V or Ctrl+Shift+V for terminals)
            self.hotkey_handler.simulate_paste()

            # Pop the current line from queue
            self.queue_manager.pop_next()

            # Restore original clipboard after a short delay
            def restore_clipboard():
                try:
                    # Safety check: only restore if clipboard still has our queue item
                    # This prevents overwriting if user copied something new in the meantime
                    current_clip = get_clipboard()
                    if current_clip == current_line:
                        set_clipboard(original_clipboard)
                        self.clipboard_monitor.update_last_content(original_clipboard)
                    else:
                        print("[Paste] Clipboard changed by user, skipping restore")
                        # Update monitor's last content to what user copied so it doesn't re-trigger
                        self.clipboard_monitor.update_last_content(current_clip)
                finally:
                    # Always resume monitoring
                    self.clipboard_monitor.resume()

            # Configurable delay (default 350ms)
            delay = self.settings.get('paste_delay', 350)
            QTimer.singleShot(delay, restore_clipboard)

        except Exception as e:
            print(f"Paste error: {e}")
            # Ensure we resume if something crashes
            self.clipboard_monitor.resume()

    def _update_ui(self):
        """Update UI to reflect current queue state."""
        next_line = self.queue_manager.peek_next()
        current = self.queue_manager.get_current_position()
        total = self.queue_manager.get_total()

        if next_line:
            self.indicator.update_status(next_line, current, total)
            self.tray_icon.update_status(next_line, current, total)
        else:
            self.indicator.set_empty()
            self.tray_icon.set_empty()

    def _on_queue_empty(self):
        """Handle queue becoming empty."""
        self.indicator.set_empty()
        self.tray_icon.set_empty()

    def _on_loop_mode_toggled(self, enabled: bool):
        """Handle loop mode toggle."""
        self.queue_manager.loop_mode = enabled
        self.settings.loop_mode = enabled

    def _on_show_indicator_toggled(self, visible: bool):
        """Handle indicator visibility toggle."""
        self.settings.show_indicator = visible
        if visible:
            self.indicator.show()
        else:
            self.indicator.hide()

    def _on_delimiter_changed(self, delimiter: str):
        """Handle delimiter change."""
        self.settings.delimiter = delimiter
        self._set_delimiter_from_settings()
        self.tray_icon.set_delimiter(delimiter)

    def _on_clear_queue(self):
        """Handle clear queue request."""
        self.queue_manager.clear()
        self.indicator.set_ready()
        self.tray_icon.set_empty()

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _apply_settings(self):
        """Apply changed settings."""
        self.queue_manager.loop_mode = self.settings.loop_mode
        self._set_delimiter_from_settings()
        self.clipboard_monitor.min_lines = self.settings.min_lines

        # Update indicator visibility
        if self.settings.show_indicator:
            self.indicator.set_position(self.settings.get('indicator_position', 'top-right'))
            self.indicator.show()
        else:
            self.indicator.hide()

        # Update tray icon
        self.tray_icon.set_loop_mode(self.settings.loop_mode)
        self.tray_icon.set_show_indicator(self.settings.show_indicator)
        self.tray_icon.set_delimiter(self.settings.delimiter)

    def _quit(self):
        """Quit the application."""
        # Stop threads
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        if self.hotkey_handler:
            self.hotkey_handler.stop()

        # Quit application
        if self.app:
            self.app.quit()

    def run(self) -> int:
        """Run the application."""
        # Single instance check
        lock_file = QLockFile(QDir.temp().filePath("queueclip.lock"))
        if not lock_file.tryLock(100):
            QMessageBox.critical(None, "QueueClip", "Application is already running!")
            return 1

        # Start background threads
        # self.clipboard_monitor.start()  # Not needed (signal based)
        self.hotkey_handler.start()

        # Run event loop
        return self.app.exec()


def main():
    """Main entry point."""
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create and run application
    app = QueueClipApp()
    app.init()

    sys.exit(app.run())


if __name__ == "__main__":
    main()
