"""
================================================================================
Project: Fake News & Text Processing Engine
File: main.py
================================================================================
Entry point for the Tkinter desktop application.
Run with: python main.py

Alternatively run directly:  python tkinter_app.py
================================================================================
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Ensure the project directory is on sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from tkinter_app import FakeNewsApp


def main():
    """Launches the Fake News & Text Processing Engine desktop application."""
    try:
        app = FakeNewsApp()
        app.mainloop()
    except Exception as e:
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror(
            "Fatal Application Error",
            f"An unexpected error occurred while launching the application:\n\n{str(e)}"
        )
        root_err.destroy()


if __name__ == "__main__":
    main()
