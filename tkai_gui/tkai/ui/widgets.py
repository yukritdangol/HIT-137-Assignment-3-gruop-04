import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class StatusBar(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar(value="Ready.")
        self.label = ttk.Label(self, textvariable=self.var, anchor="w")
        self.label.pack(fill="x")
    def set(self, text: str):
        self.var.set(text)
        self.update_idletasks()

class Console(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, height=8, wrap="word")
        self.text.pack(fill="both", expand=True)
    def log(self, msg: str):
        self.text.insert("end", msg + "\n")
        self.text.see("end")

class ImageViewer(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, width=320, height=240, bg="#f0f0f0")
        self.canvas.pack(fill="both", expand=True)
        self._imgtk = None
    def show_pil_image(self, img):
        # Fit into canvas while keeping aspect ratio
        cw = self.canvas.winfo_width() or 320
        ch = self.canvas.winfo_height() or 240
        iw, ih = img.size
        scale = min(cw/iw, ch/ih)
        nw, nh = max(1, int(iw*scale)), max(1, int(ih*scale))
        resized = img.resize((nw, nh))
        self._imgtk = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(cw//2, ch//2, image=self._imgtk, anchor="center")
        self.canvas.update()
