#!/usr/bin/env python3
"""
QueueClip - Clipboard Queue Application
Run this script to start the application.
"""

import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from queueclip.main import main

if __name__ == "__main__":
    main()
