import tkinter as tk
from tkinter import ttk

def apply_styles(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TButton", padding=6)
    style.configure("TLabel", anchor="w")
    style.configure("TFrame", padding=6)
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
