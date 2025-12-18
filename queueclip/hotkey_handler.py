"""
Hotkey Handler - Global keyboard shortcuts.
Cross-platform support for Windows and Linux.
"""

import time
import platform
import subprocess
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, Controller
from PyQt6.QtCore import QThread, pyqtSignal


def get_active_window_class() -> str:
    """Get the window class of the currently focused window (Linux only)."""
    try:
        # Use xdotool to get active window name
        result = subprocess.run(
            ['xdotool', 'getactivewindow', 'getwindowname'],
            capture_output=True, text=True, timeout=1
        )
        window_name = result.stdout.strip().lower()

        # Use xprop to get WM_CLASS (more reliable)
        try:
            window_id = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()

            result2 = subprocess.run(
                ['xprop', '-id', window_id, 'WM_CLASS'],
                capture_output=True, text=True, timeout=1
            )
            window_class = result2.stdout.strip().lower()
        except Exception:
            window_class = ""

        return f"{window_class} {window_name}"
    except Exception:
        return ""


def is_terminal_window() -> bool:
    """Check if the active window is a terminal."""
    window_info = get_active_window_class()
    terminal_indicators = [
        'terminal', 'konsole', 'gnome-terminal', 'xterm', 'kitty',
        'alacritty', 'terminator', 'x-terminator', 'tilix', 'urxvt',
        'st', 'foot', 'wezterm', 'hyper', 'iterm', 'term', 'rxvt',
        'sakura', 'guake', 'tilda', 'yakuake', 'terminology'
    ]
    return any(term in window_info for term in terminal_indicators)


class HotkeyHandler(QThread):
    """
    Handles global hotkey detection and paste simulation.
    Runs in a separate thread.
    """

    # Signal emitted when the paste hotkey is triggered
    paste_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._listener: Optional[keyboard.Listener] = None
        self._controller = Controller()
        self._enabled = True

        # Default hotkey: F9 - simple, rarely used function key
        self._hotkey_combination = {keyboard.Key.f9}
        self._current_keys = set()

        # Platform detection
        self._is_windows = platform.system() == 'Windows'
        self._is_linux = platform.system() == 'Linux'

    @property
    def enabled(self) -> bool:
        """Check if hotkey handling is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable hotkey handling."""
        self._enabled = value

    def set_hotkey(self, keys: set):
        """
        Set the hotkey combination.
        Example: {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.KeyCode.from_char('v')}
        """
        self._hotkey_combination = keys

    def _on_press(self, key):
        """Handle key press events."""
        if not self._enabled:
            return

        # Normalize key representation
        try:
            self._current_keys.add(key)
        except Exception:
            pass

        # Check if our hotkey combination is pressed
        if self._check_hotkey():
            # Emit signal (will be handled in main thread)
            self.paste_triggered.emit()
            # Clear keys to prevent repeat triggering
            self._current_keys.clear()

    def _on_release(self, key):
        """Handle key release events."""
        try:
            self._current_keys.discard(key)
        except Exception:
            pass

    def _check_hotkey(self) -> bool:
        """Check if current keys match the hotkey combination."""
        # We need all hotkey keys to be pressed
        for hk in self._hotkey_combination:
            matched = False
            for ck in self._current_keys:
                # Compare keys - handle both Key enums and KeyCodes
                if self._keys_match(hk, ck):
                    matched = True
                    break
            if not matched:
                return False
        return True

    def _keys_match(self, key1, key2) -> bool:
        """Check if two key representations match."""
        # Direct equality
        if key1 == key2:
            return True

        # Handle Key.cmd matching Key.cmd_l or Key.cmd_r
        if hasattr(key1, 'name') and hasattr(key2, 'name'):
            name1 = key1.name if hasattr(key1, 'name') else str(key1)
            name2 = key2.name if hasattr(key2, 'name') else str(key2)

            # Match cmd with cmd_l/cmd_r (Super key on Linux)
            if 'cmd' in name1 and 'cmd' in name2:
                return True
            if 'ctrl' in name1 and 'ctrl' in name2:
                return True
            if 'alt' in name1 and 'alt' in name2:
                return True
            if 'shift' in name1 and 'shift' in name2:
                return True

        # Handle KeyCode comparison for regular characters
        try:
            if hasattr(key1, 'char') and hasattr(key2, 'char'):
                if key1.char and key2.char:
                    return key1.char.lower() == key2.char.lower()
        except Exception:
            pass

        return False

    def simulate_paste(self):
        """
        Simulate paste. Uses xdotool for terminals (Linux) and pynput for others.
        """
        try:
            # Small delay to ensure hotkey is fully released
            time.sleep(0.05)

            # Check if we're in a terminal (Linux)
            if self._is_linux and is_terminal_window():
                # Terminal: use xdotool directly for reliability
                try:
                    subprocess.run(
                        ['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+v'],
                        check=False, timeout=1
                    )
                except Exception as e:
                    print(f"xdotool paste error: {e}")
                    # Fallback to pynput if xdotool fails
                    with self._controller.pressed(Key.ctrl):
                        with self._controller.pressed(Key.shift):
                            self._controller.tap('v')
            else:
                # Regular app: use Ctrl+V
                with self._controller.pressed(Key.ctrl):
                    self._controller.tap('v')

            # Small delay after paste
            time.sleep(0.05)

        except Exception as e:
            print(f"Paste simulation error: {e}")

    def type_text(self, text: str):
        """
        Type out text directly using keyboard simulation.
        This doesn't touch the clipboard at all.
        """
        try:
            # Small delay before typing
            time.sleep(0.05)

            if self._is_linux and is_terminal_window():
                 # Use xdotool type for terminals as it handles special chars better
                try:
                    subprocess.run(
                        ['xdotool', 'type', '--clearmodifiers', '--delay', '10', text],
                        check=False, timeout=2
                    )
                    return
                except Exception:
                    pass

            # Type the text directly (fallback)
            self._controller.type(text)

            # Small delay after typing
            time.sleep(0.02)

        except Exception as e:
            print(f"Type text error: {e}")

    def run(self):
        """Start the hotkey listener."""
        self._running = True

        # Create and start the listener
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

        # Keep thread alive while running
        while self._running:
            time.sleep(0.1)

        # Clean up
        if self._listener:
            self._listener.stop()

    def stop(self):
        """Stop the hotkey listener."""
        self._running = False
        if self._listener:
            self._listener.stop()
        self.wait()


def get_default_hotkey_text() -> str:
    """Get human-readable text for the default hotkey."""
    return "F9"
