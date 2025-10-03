#!/usr/bin/env python3
"""
Main entry point for Tkinter AI GUI.
"""
import os
import sys
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkai.ui.main_window import TkAIMainWindow
from tkai.services.logger_service import LoggerService
from tkai.state import AppState
from tkai.config import DEFAULTS


def main():
    # Ensure directories exist
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    logger = LoggerService(log_file="logs/app.log")
    state = AppState()
    logger.info("Starting Tkinter AI GUI")

    try:
        root = tk.Tk()
        root.title("Tkinter AI GUI")
        # Set a minimum size for Windows small screens
        root.minsize(1000, 700)

        app = TkAIMainWindow(root, state, logger)
        app.pack(fill="both", expand=True)

        root.mainloop()
    except Exception as e:
        logger.exception("Fatal error during app launch")
        traceback.print_exc()
        messagebox.showerror("Fatal Error", f"{e}")

if __name__ == "__main__":
    main()
