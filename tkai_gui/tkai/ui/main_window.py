from __future__ import annotations
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional

from PIL import Image

from tkai.ui.styles import apply_styles
from tkai.ui.widgets import StatusBar, Console, ImageViewer
from tkai.state import AppState
from tkai.services.logger_service import LoggerService
from tkai.models.t2i_controller import TextToImageController
from tkai.models.clf_controller import ImageClassifierController
from tkai.config import DEFAULTS

OOP_EXPLANATION = """
• Multiple Inheritance: Controllers use mixins (TextIOMixin, ImageIOMixin) + BaseModelController.
• Encapsulation: Protected attrs (_model, _name, _category, _loaded) hide internal state.
• Polymorphism: Same method names (load_model, run, summarize_info) on different controllers.
• Method Overriding: Each controller implements its own load_model() and run().
• Multiple Decorators: @measure_time, @catch_exceptions, @require_loaded stacked on methods.
"""

class TkAIMainWindow(ttk.Frame):
    def __init__(self, master, state: AppState, logger: LoggerService, **kwargs):
        super().__init__(master, **kwargs)
        self.master: tk.Tk = master
        self.state = state
        self.logger = logger

        apply_styles(self.master)

        # Controllers
        self.t2i = TextToImageController(logger=self.logger)
        self.clf = ImageClassifierController(logger=self.logger)

        self._build_ui()
        self._bind_events()

    # ---------- UI ----------
    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Task:", style="Header.TLabel").pack(side="left", padx=(0,6))
        self.task_var = tk.StringVar(value=self.state.selected_task)
        ttk.Combobox(top, textvariable=self.task_var, state="readonly",
                     values=["Text-to-Image", "Image Classification"], width=24).pack(side="left")
        self.btn_load = ttk.Button(top, text="Load Model", command=self.on_load_model)
        self.btn_load.pack(side="left", padx=8)

        # Input section
        input_frame = ttk.LabelFrame(self, text="User Input")
        input_frame.pack(fill="x", pady=6)

        self.input_mode = tk.StringVar(value="Text")  # Text | Image
        ttk.Radiobutton(input_frame, text="Text", variable=self.input_mode, value="Text").pack(side="left")
        ttk.Radiobutton(input_frame, text="Image", variable=self.input_mode, value="Image").pack(side="left", padx=(8,0))

        self.txt_prompt = tk.Text(input_frame, height=4, width=60)
        self.txt_prompt.insert("end", "a cozy reading nook with a warm lamp, watercolor style")
        self.txt_prompt.pack(fill="x", padx=6, pady=6)

        self.txt_negative = tk.Entry(input_frame)
        self.txt_negative.insert(0, self.state.last_negative_prompt)
        ttk.Label(input_frame, text="Negative prompt:").pack(anchor="w", padx=6)
        self.txt_negative.pack(fill="x", padx=6, pady=(0,6))

        browse_row = ttk.Frame(input_frame)
        browse_row.pack(fill="x")
        self.entry_image = ttk.Entry(browse_row)
        self.entry_image.pack(side="left", fill="x", expand=True, padx=6, pady=4)
        ttk.Button(browse_row, text="Browse...", command=self.on_browse).pack(side="left", padx=6)

        btns = ttk.Frame(input_frame)
        btns.pack(fill="x", pady=(4,2))
        self.btn_run1 = ttk.Button(btns, text="Run Model 1")
        self.btn_run2 = ttk.Button(btns, text="Run Model 2")
        self.btn_clear = ttk.Button(btns, text="Clear")
        self.btn_run1.pack(side="left")
        self.btn_run2.pack(side="left", padx=6)
        self.btn_clear.pack(side="left")

        # Output + info
        out = ttk.Frame(self)
        out.pack(fill="both", expand=True)

        left = ttk.LabelFrame(out, text="Model Output")
        left.pack(side="left", fill="both", expand=True, padx=(0,6))

        self.viewer = ImageViewer(left)
        self.viewer.pack(fill="both", expand=True, padx=6, pady=6)

        self.txt_output = tk.Text(left, height=10, wrap="word")
        self.txt_output.pack(fill="x", padx=6, pady=(0,6))

        right = ttk.Frame(out)
        right.pack(side="left", fill="both", expand=False)

        info = ttk.LabelFrame(right, text="Model Info")
        info.pack(fill="x", padx=6, pady=(0,6))
        self.txt_info = tk.Text(info, height=8, wrap="word")
        self.txt_info.pack(fill="both", expand=True, padx=6, pady=6)

        oop = ttk.LabelFrame(right, text="OOP Concepts Explanation")
        oop.pack(fill="both", expand=True, padx=6, pady=(0,6))
        self.txt_oop = tk.Text(oop, height=14, wrap="word")
        self.txt_oop.pack(fill="both", expand=True, padx=6, pady=6)
        self.txt_oop.insert("end", OOP_EXPLANATION.strip())

        notes = ttk.LabelFrame(self, text="Notes")
        notes.pack(fill="x", pady=(6,0))
        self.txt_notes = tk.Text(notes, height=4)
        self.txt_notes.pack(fill="x", padx=6, pady=6)

        # Console + status
        self.console = Console(self)
        self.console.pack(fill="x", pady=(6,0))
        self.status = StatusBar(self)
        self.status.pack(fill="x")

        self._set_running(False)

    def _bind_events(self):
        self.btn_run1.configure(command=lambda: self._run_clicked(which=1))
        self.btn_run2.configure(command=lambda: self._run_clicked(which=2))
        self.btn_clear.configure(command=self._clear)
        # Update info pane on task change
        def on_task_change(*_):
            self.state.selected_task = self.task_var.get()
            self._refresh_model_info()
        self.task_var.trace_add("write", on_task_change)

    # ---------- Handlers ----------
    def on_browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.entry_image.delete(0, "end")
            self.entry_image.insert(0, path)
            self.state.last_image_path = path
            self.console.log(f"Selected image: {path}")

    def on_load_model(self):
        task = self.task_var.get()
        self._set_running(True)
        self.status.set(f"Loading {task} model...")

        def worker():
            try:
                if task == "Text-to-Image":
                    res = self.t2i.load_model()
                else:
                    res = self.clf.load_model()
            finally:
                self.master.after(0, lambda: self._after_load(task, res))

        threading.Thread(target=worker, daemon=True).start()

    def _after_load(self, task, res):
        self._set_running(False)
        if res and res.get("ok"):
            self.state.model_loaded[task] = True
            self.console.log(f"{task} loaded: {res}")
            self.status.set(f"{task} model loaded.")
            self._refresh_model_info()
        else:
            err = res.get("error") if res else "Unknown error"
            messagebox.showerror("Load Failed", err)
            self.console.log(f"Load error: {err}")
            self.status.set("Load failed.")

    def _run_clicked(self, which: int):
        # which 1 = T2I, which 2 = CLF by default; but allow polymorphic behavior based on selected task & mode
        mode = self.input_mode.get()
        task = self.task_var.get()
        self._set_running(True)
        self.status.set("Running...")

        def worker():
            try:
                if which == 1:
                    # Prefer text-to-image unless user chose classifier explicitly with image input
                    if task == "Text-to-Image" or mode == "Text":
                        prompt = self.txt_prompt.get("1.0", "end").strip()
                        negative = self.txt_negative.get().strip()
                        res = self.t2i.run(prompt=prompt, negative_prompt=negative,
                                           width=DEFAULTS["image_size"][0], height=DEFAULTS["image_size"][1],
                                           steps=DEFAULTS["t2i_steps"], guidance=DEFAULTS["t2i_guidance"])
                    else:
                        img_path = self.entry_image.get().strip() or (self.state.last_output_path or "")
                        res = self.clf.run(image_path=img_path, top_k=DEFAULTS["clf_topk"])
                else:
                    # which == 2
                    if task == "Image Classification" or mode == "Image":
                        img_path = self.entry_image.get().strip() or (self.state.last_output_path or "")
                        res = self.clf.run(image_path=img_path, top_k=DEFAULTS["clf_topk"])
                    else:
                        prompt = self.txt_prompt.get("1.0", "end").strip()
                        negative = self.txt_negative.get().strip()
                        res = self.t2i.run(prompt=prompt, negative_prompt=negative,
                                           width=DEFAULTS["image_size"][0], height=DEFAULTS["image_size"][1],
                                           steps=DEFAULTS["t2i_steps"], guidance=DEFAULTS["t2i_guidance"])
            finally:
                self.master.after(0, lambda: self._after_run(res))

        threading.Thread(target=worker, daemon=True).start()

    def _after_run(self, res):
        self._set_running(False)
        if res and res.get("ok"):
            self.console.log(f"Run ok: {res}")
            self.status.set("Done.")
            self._render_result(res)
        else:
            err = res.get("error") if res else "Unknown error"
            messagebox.showerror("Run Failed", err)
            self.console.log(f"Run error: {err}")
            self.status.set("Failed.")

    def _render_result(self, res: dict):
        task = res.get("task")
        if task == "text-to-image":
            path = res.get("image_path")
            if path:
                try:
                    img = Image.open(path).convert("RGB")
                    self.viewer.show_pil_image(img)
                    self.state.last_output_path = path
                    self.txt_output.delete("1.0", "end")
                    self.txt_output.insert("end", f"Saved image to: {path}\nJSON: {res.get('json_path','')}")
                except Exception as e:
                    self.console.log(f"Preview error: {e}")
        elif task == "image-classification":
            preds = res.get("predictions", [])
            self.txt_output.delete("1.0", "end")
            for p in preds:
                self.txt_output.insert("end", f"{p['label']}: {p['score']:.4f}\n")
            # Try thumbnail if we have an image path
            ipath = res.get("image_path")
            if ipath:
                try:
                    img = Image.open(ipath).convert("RGB")
                    self.viewer.show_pil_image(img)
                except Exception as e:
                    self.console.log(f"Preview error: {e}")

    def _refresh_model_info(self):
        task = self.task_var.get()
        info = self.t2i.summarize_info() if task == "Text-to-Image" else self.clf.summarize_info()
        self.txt_info.delete("1.0", "end")
        for k, v in info.items():
            self.txt_info.insert("end", f"{k}: {v}\n")

    def _clear(self):
        self.txt_output.delete("1.0", "end")
        self.viewer.canvas.delete("all")
        self.status.set("Cleared.")

    def _set_running(self, is_running: bool):
        state = "disabled" if is_running else "normal"
        for w in [self.btn_load, self.btn_run1, self.btn_run2, self.btn_clear,
                  self.txt_prompt, self.txt_negative, self.entry_image]:
            try:
                w.configure(state=state)
            except Exception:
                pass
        if is_running:
            self.status.set("Working... Please wait.")
        else:
            self.status.set("Ready.")
