"""
Settings - Configuration management and settings dialog.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QSpinBox, QPushButton,
    QGroupBox, QFormLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal


def get_config_dir() -> Path:
    """Get the configuration directory path (cross-platform)."""
    system = platform.system()

    if system == 'Windows':
        base = Path(os.environ.get('APPDATA', Path.home()))
    elif system == 'Darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:  # Linux
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))

    config_dir = base / 'QueueClip'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / 'settings.json'


# Default settings
DEFAULT_SETTINGS: Dict[str, Any] = {
    'delimiter': 'newline',
    'loop_mode': False,
    'show_indicator': True,
    'min_lines': 2,
    'indicator_opacity': 0.9,
    'indicator_position': 'top-right',
    'hotkey': 'F9',
    'paste_delay': 350,
}


class Settings:
    """
    Manages application settings with persistence.
    """

    def __init__(self):
        self._settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Load settings from file."""
        config_file = get_config_file()

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    self._settings = {**DEFAULT_SETTINGS, **loaded}
            except Exception as e:
                print(f"Error loading settings: {e}")
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self._settings = DEFAULT_SETTINGS.copy()

    def save(self):
        """Save settings to file."""
        config_file = get_config_file()

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and save."""
        self._settings[key] = value
        self.save()

    def reset(self):
        """Reset all settings to defaults."""
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

    @property
    def delimiter(self) -> str:
        """Get the delimiter setting."""
        return self._settings.get('delimiter', 'newline')

    @delimiter.setter
    def delimiter(self, value: str):
        self.set('delimiter', value)

    @property
    def loop_mode(self) -> bool:
        """Get loop mode setting."""
        return self._settings.get('loop_mode', False)

    @loop_mode.setter
    def loop_mode(self, value: bool):
        self.set('loop_mode', value)

    @property
    def show_indicator(self) -> bool:
        """Get show indicator setting."""
        return self._settings.get('show_indicator', True)

    @show_indicator.setter
    def show_indicator(self, value: bool):
        self.set('show_indicator', value)

    @property
    def min_lines(self) -> int:
        """Get minimum lines threshold."""
        return self._settings.get('min_lines', 2)

    @min_lines.setter
    def min_lines(self, value: int):
        self.set('min_lines', value)


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring QueueClip.
    """

    settings_changed = pyqtSignal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("QueueClip Settings")
        self.setMinimumWidth(350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Queue Settings Group
        queue_group = QGroupBox("Queue Settings")
        queue_layout = QFormLayout()

        # Delimiter
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(['Newline', 'Comma', 'Tab', 'Semicolon', 'Custom'])
        queue_layout.addRow("Default Delimiter:", self.delimiter_combo)

        # Custom delimiter input
        self.custom_delimiter = QLineEdit()
        self.custom_delimiter.setPlaceholderText("Enter custom delimiter")
        self.custom_delimiter.setMaxLength(10)
        self.custom_delimiter.setVisible(False)
        queue_layout.addRow("", self.custom_delimiter)

        # Connect delimiter change
        self.delimiter_combo.currentTextChanged.connect(self._on_delimiter_changed)

        # Loop mode
        self.loop_mode_check = QCheckBox("Loop Mode (cycle through list)")
        queue_layout.addRow("", self.loop_mode_check)

        # Minimum lines
        self.min_lines_spin = QSpinBox()
        self.min_lines_spin.setRange(1, 100)
        self.min_lines_spin.setValue(2)
        queue_layout.addRow("Min lines to activate:", self.min_lines_spin)

        # Paste Delay
        self.paste_delay_spin = QSpinBox()
        self.paste_delay_spin.setRange(50, 2000)
        self.paste_delay_spin.setSingleStep(50)
        self.paste_delay_spin.setSuffix(" ms")
        self.paste_delay_spin.setValue(350)
        queue_layout.addRow("Paste Delay:", self.paste_delay_spin)

        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        # Indicator Settings Group
        indicator_group = QGroupBox("Indicator Settings")
        indicator_layout = QFormLayout()

        # Show indicator
        self.show_indicator_check = QCheckBox("Show floating indicator")
        indicator_layout.addRow("", self.show_indicator_check)

        # Position
        self.position_combo = QComboBox()
        self.position_combo.addItems(['Top Right', 'Top Left', 'Bottom Right', 'Bottom Left'])
        indicator_layout.addRow("Position:", self.position_combo)

        indicator_group.setLayout(indicator_layout)
        layout.addWidget(indicator_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _on_delimiter_changed(self, text: str):
        """Show/hide custom delimiter input."""
        self.custom_delimiter.setVisible(text == 'Custom')

    def _load_values(self):
        """Load current settings into UI."""
        # Delimiter
        delimiter = self._settings.delimiter
        delimiter_map = {
            'newline': 0, 'comma': 1, 'tab': 2, 'semicolon': 3
        }
        self.delimiter_combo.setCurrentIndex(delimiter_map.get(delimiter, 0))

        # Loop mode
        self.loop_mode_check.setChecked(self._settings.loop_mode)

        # Min lines
        self.min_lines_spin.setValue(self._settings.min_lines)

        # Paste delay
        self.paste_delay_spin.setValue(self._settings.get('paste_delay', 350))

        # Show indicator
        self.show_indicator_check.setChecked(self._settings.show_indicator)

        # Position
        position = self._settings.get('indicator_position', 'top-right')
        position_map = {
            'top-right': 0, 'top-left': 1, 'bottom-right': 2, 'bottom-left': 3
        }
        self.position_combo.setCurrentIndex(position_map.get(position, 0))

    def _save_settings(self):
        """Save settings and close dialog."""
        # Delimiter
        delimiter_map = ['newline', 'comma', 'tab', 'semicolon', 'custom']
        self._settings.delimiter = delimiter_map[self.delimiter_combo.currentIndex()]

        if self._settings.delimiter == 'custom':
            self._settings.set('custom_delimiter', self.custom_delimiter.text())

        # Loop mode
        self._settings.loop_mode = self.loop_mode_check.isChecked()

        # Min lines
        self._settings.min_lines = self.min_lines_spin.value()

        # Paste delay
        self._settings.set('paste_delay', self.paste_delay_spin.value())

        # Show indicator
        self._settings.show_indicator = self.show_indicator_check.isChecked()

        # Position
        position_map = ['top-right', 'top-left', 'bottom-right', 'bottom-left']
        self._settings.set('indicator_position', position_map[self.position_combo.currentIndex()])

        self.settings_changed.emit()
        self.accept()

    def _reset_defaults(self):
        """Reset to default values."""
        self._settings.reset()
        self._load_values()
