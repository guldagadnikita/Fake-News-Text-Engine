"""
================================================================================
Package: gui
================================================================================
Concept Demonstrated: Python Packages
Contains the Tkinter desktop application interface.
================================================================================
"""

# Import from the root-level tkinter_app.py
import sys
import os
_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_dir not in sys.path:
    sys.path.insert(0, _project_dir)

from tkinter_app import FakeNewsApp

__all__ = ["FakeNewsApp"]
