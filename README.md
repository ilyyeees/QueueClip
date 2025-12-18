# QueueClip

**Copy Once. Paste Sequentially. Never Alt-Tab Again.**

QueueClip transforms your clipboard into a sequential line-feeder. Copy a block of text containing multiple lines, and paste them one by one automatically.

## Features

- **Batch Processing** - Splits copied blocks by newlines, commas, or custom delimiters
- **Visual Indicator** - Floating window shows next line and remaining count
- **Loop Mode** - Cycle through list repeatedly or stop when empty
- **Global Hotkey** - `F9` to paste and advance (configurable)
- **Cross-Platform** - Works on Windows and Linux

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
## Download

You can download the ready-to-use executable for your system from the [Releases page](https://github.com/ilyyeees/QueueClip/releases).

- **Windows**: Download `QueueClip.exe`
- **Linux**: Download `QueueClip` (Make sure to install dependencies below)

### Linux Dependencies
Even with the standalone executable, you need to install `xdotool` and a clipboard utility (`xclip` or `xsel`) for full functionality:

```bash
sudo apt install xdotool xclip
```

## Running from Source (For Developers)

If you prefer to run the Python code directly:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ilyyeees/QueueClip.git
    cd QueueClip
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or: venv\Scripts\activate  # Windows
    ```

3.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run**:
    ```bash
    python run.py
    ```

## Usage

```bash
python run.py
```

1. Copy multi-line text (e.g., a list of usernames)
2. Press `F9` to paste the first line
3. Press `F9` again for the next line
4. Repeat until queue is empty

## Configuration

Right-click the system tray icon to:
- Toggle **Loop Mode**
- Change **Delimiter** (newline, comma, tab, custom)
- **Clear Queue**
- Access **Settings**

## License

MIT License - Free for personal and commercial use.
