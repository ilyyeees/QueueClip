# QueueClip

**Copy Once. Paste Sequentially. Never Alt-Tab Again.**

QueueClip transforms your clipboard into a sequential line-feeder. Copy a block of text containing multiple lines, and paste them one by one automatically.

## Features

- 🔄 **Batch Processing** - Splits copied blocks by newlines, commas, or custom delimiters
- 👁️ **Visual Indicator** - Floating window shows next line and remaining count
- 🔁 **Loop Mode** - Cycle through list repeatedly or stop when empty
- ⌨️ **Global Hotkey** - `Super+V` to paste and advance (configurable)
- 🖥️ **Cross-Platform** - Works on Windows and Linux

## Requirements

- Python 3.6+
- PyQt6
- pynput
- pyperclip

### Linux Dependencies
On Linux, you need to install `xdotool` and a clipboard utility (`xclip` or `xsel`) for full functionality:

```bash
sudo apt install xdotool xclip
```

## Installation

```bash
# Clone or download, then:
cd QueueClip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

**Linux only:** Install xclip for clipboard support:
```bash
sudo apt install xclip  # Debian/Ubuntu
sudo pacman -S xclip    # Arch
```

## Usage

```bash
python run.py
```

1. Copy multi-line text (e.g., a list of usernames)
2. Press `Super+V` to paste the first line
3. Press `Super+V` again for the next line
4. Repeat until queue is empty

## Configuration

Right-click the system tray icon to:
- Toggle **Loop Mode**
- Change **Delimiter** (newline, comma, tab, custom)
- **Clear Queue**
- Access **Settings**

## License

MIT License - Free for personal and commercial use.
