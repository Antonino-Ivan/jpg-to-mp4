import os
import threading
from datetime import datetime

import customtkinter as ctk
from PIL import Image as PILImage

from converter import convert_images_to_video, find_images


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ConverterApp(ctk.CTk):
    WIDTH = 820
    HEIGHT = 760

    def __init__(self):
        super().__init__()
        self.title("JPG to MP4 Converter")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(720, 680)
        self.resizable(True, True)

        self.input_dir = os.path.abspath("immagini")
        self.output_file = os.path.abspath("output.mp4")
        self._running = False

        self._build_ui()

    def _section_title(self, parent, icon, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            frame,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(side="left")
        return frame

    def _build_ui(self):

        self._build_top_banner()

        scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        card_pad = 20

        self._build_input_card(scroll, card_pad)
        self._build_preview_card(scroll, card_pad)
        self._build_settings_card(scroll, card_pad)
        self._build_progress_card(scroll, card_pad)
        self._build_log_card(scroll, card_pad)
        self._build_footer(scroll, card_pad)

    def _card(self, parent, pad):
        frame = ctk.CTkFrame(
            parent,
            corner_radius=14,
            border_width=0,
        )
        frame.pack(fill="x", padx=pad, pady=(0, 14))
        frame.grid_columnconfigure(0, weight=1)
        return frame

    def _build_top_banner(self):
        banner = ctk.CTkFrame(self, corner_radius=0, height=100, fg_color=("#e8f0fe", "#1a2332"))
        banner.pack(fill="x")
        banner.pack_propagate(False)

        accent = ctk.CTkFrame(banner, corner_radius=0, height=3, fg_color="#3b82f6")
        accent.pack(fill="x", side="bottom")

        inner = ctk.CTkFrame(banner, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=28, pady=14)

        ctk.CTkLabel(
            inner,
            text="🎬  JPG to MP4 Converter",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text="Convert your JPG / JPEG images into an MP4 video",
            font=ctk.CTkFont(size=13),
            text_color=("gray", "#8899aa"),
        ).pack(anchor="w")

    def _build_input_card(self, parent, pad):
        card = self._card(parent, pad)
        self._section_title(card, "📁", "Image Folder")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        row.grid_columnconfigure(0, weight=1)

        self._entry_input = ctk.CTkEntry(
            row,
            placeholder_text="Path to the folder containing images…",
            border_width=1,
            corner_radius=8,
        )
        self._entry_input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._entry_input.insert(0, self.input_dir)
        self._entry_input.bind("<KeyRelease>", self._on_input_changed)

        ctk.CTkButton(
            row,
            text="✏️  Browse",
            width=110,
            corner_radius=8,
            fg_color=("#dbeafe", "#1e3a5f"),
            text_color=("#1e40af", "#93c5fd"),
            hover_color=("#bfdbfe", "#2a4f7f"),
            command=self._browse_input,
        ).grid(row=0, column=1, sticky="e")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", pady=(6, 0))

        self._status_dot = ctk.CTkLabel(info, text="●", font=ctk.CTkFont(size=10), text_color=("#6b7280", "#6b7280"))
        self._status_dot.pack(side="left", padx=(0, 4))

        self._lbl_count = ctk.CTkLabel(info, text="No folder selected", font=ctk.CTkFont(size=12))
        self._lbl_count.pack(side="left")

        self._lbl_size = ctk.CTkLabel(info, text="", font=ctk.CTkFont(size=12), text_color=("gray", "#667788"))
        self._lbl_size.pack(side="left", padx=(10, 0))

    def _build_preview_card(self, parent, pad):
        card = self._card(parent, pad)

        self._section_title(card, "🖼️", "Image Preview")

        self._preview_container = ctk.CTkFrame(card, fg_color="transparent")
        self._preview_container.pack(fill="x")
        self._preview_cells = []

    def _refresh_preview(self, images):
        for w in self._preview_cells:
            w.destroy()
        self._preview_cells.clear()

        max_shown = min(len(images), 30)
        cols = min(6, max_shown)
        cols = max(cols, 1)

        flow = ctk.CTkFrame(self._preview_container, fg_color="transparent")
        flow.pack(fill="x")
        flow.grid_columnconfigure(tuple(range(cols)), weight=1, uniform="thumb")

        for idx, img_path in enumerate(images[:max_shown]):
            r, c = divmod(idx, cols)
            cell = ctk.CTkFrame(flow, corner_radius=8, border_width=0)
            cell.grid(row=r, column=c, padx=3, pady=3, sticky="n")

            name = os.path.basename(img_path)
            try:
                with PILImage.open(img_path) as p:
                    pw, ph = p.size
                    ratio = min(80 / pw, 80 / ph)
                    thumb_size = (max(int(pw * ratio), 1), max(int(ph * ratio), 1))
                    p.thumbnail(thumb_size, PILImage.LANCZOS)
                    tk_img = ctk.CTkImage(p, size=p.size)
            except Exception:
                tk_img = None

            label_img = ctk.CTkLabel(cell, text="", image=tk_img)
            label_img.pack(padx=6, pady=(6, 0))

            label_name = ctk.CTkLabel(
                cell, text=name, font=ctk.CTkFont(size=10),
                wraplength=90, justify="center",
            )
            label_name.pack(padx=4, pady=(2, 6))

            self._preview_cells.append(cell)

        if len(images) > max_shown:
            ctk.CTkLabel(
                self._preview_container,
                text=f"+{len(images) - max_shown} more images",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color=("gray", "#667788"),
            ).pack(pady=(2, 0))

    def _build_settings_card(self, parent, pad):
        card = self._card(parent, pad)
        self._section_title(card, "⚙️", "Video Settings")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(row, text="FPS", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(0, 4))
        self._entry_fps = ctk.CTkEntry(row, width=60, corner_radius=8, justify="center")
        self._entry_fps.pack(side="left", padx=(0, 18))
        self._entry_fps.insert(0, "24")

        ctk.CTkLabel(row, text="Duration (s)", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(0, 4))
        self._entry_duration = ctk.CTkEntry(row, width=64, corner_radius=8, justify="center")
        self._entry_duration.pack(side="left", padx=(0, 18))
        self._entry_duration.insert(0, "30")

        ctk.CTkLabel(row, text="Output", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(0, 4))
        self._entry_output = ctk.CTkEntry(row, width=180, corner_radius=8)
        self._entry_output.pack(side="left", padx=(0, 6))
        self._entry_output.insert(0, self.output_file)

        ctk.CTkButton(
            row, text="…", width=32, corner_radius=8,
            command=self._browse_output,
        ).pack(side="left")

    def _build_progress_card(self, parent, pad):
        card = self._card(parent, pad)
        self._section_title(card, "🚀", "Conversion")

        prog_frame = ctk.CTkFrame(card, fg_color="transparent")
        prog_frame.pack(fill="x", pady=(6, 8))
        prog_frame.grid_columnconfigure(0, weight=1)

        self._progress = ctk.CTkProgressBar(
            prog_frame, height=10, corner_radius=5,
            border_width=0,
            progress_color="#3b82f6",
        )
        self._progress.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self._progress.set(0)

        self._progress_label = ctk.CTkLabel(
            prog_frame, text="0%", font=ctk.CTkFont(size=13, weight="bold"),
            width=44, anchor="e",
        )
        self._progress_label.grid(row=0, column=1, sticky="e")

        self._btn_convert = ctk.CTkButton(
            card,
            text="🚀  Convert",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white",
            command=self._start_conversion,
        )
        self._btn_convert.pack(fill="x", pady=(0, 2))

    def _build_log_card(self, parent, pad):
        card = self._card(parent, pad)
        self._section_title(card, "📄", "Operation Log")

        self._log = ctk.CTkTextbox(
            card,
            height=110,
            corner_radius=8,
            border_width=0,
            font=ctk.CTkFont(family="SF Mono", size=11),
            activate_scrollbars=True,
        )
        self._log.pack(fill="x")
        self._log.insert("0.0", "Ready. Select a folder and press Convert.\n")
        self._log.configure(state="disabled")

    def _build_footer(self, parent, pad):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=pad, pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="v1.1  ·  Made with ❤️  using MoviePy & CustomTkinter",
            font=ctk.CTkFont(size=11),
            text_color=("gray", "#556677"),
        ).pack(side="left")

        def _open_github():
            import webbrowser
            webbrowser.open("https://github.com/Antonino-Ivan/jpg-to-mp4")

        ctk.CTkButton(
            frame,
            text="GitHub",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color=("#3b82f6", "#60a5fa"),
            hover=False,
            command=_open_github,
            cursor="hand2",
        ).pack(side="right")

    def _log_msg(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.configure(state="normal")
        self._log.insert("end", f"[{ts}] {msg}\n")
        self._log.see("end")
        self._log.configure(state="disabled")
        self.update_idletasks()

    def _update_progress(self, value):
        self._progress.set(value)
        pct = int(value * 100)
        self._progress_label.configure(text=f"{pct}%")
        self.update_idletasks()

    def _set_status(self, state, color=None):
        labels = {
            "ready": ("● Ready", "#22c55e"),
            "loading": ("● Loading…", "#3b82f6"),
            "converting": ("● Converting…", "#f59e0b"),
            "done": ("● Done", "#22c55e"),
            "error": ("● Error", "#ef4444"),
            "empty": ("● No images", "#6b7280"),
        }
        text, dot_color = labels.get(state, ("●", "#6b7280"))
        c = color or dot_color
        self._status_dot.configure(text=text, text_color=c)

    def _browse_input(self):
        d = os.path.dirname(self._entry_input.get()) or "."
        path = filedialog.askdirectory(title="Select image folder", initialdir=d)
        if path:
            self._entry_input.delete(0, "end")
            self._entry_input.insert(0, path)
            self._refresh_image_list()

    def _browse_output(self):
        d = os.path.dirname(self._entry_output.get()) or "."
        path = filedialog.asksaveasfilename(
            title="Save video as",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")],
            initialdir=d,
        )
        if path:
            self._entry_output.delete(0, "end")
            self._entry_output.insert(0, path)
            self.output_file = path

    def _on_input_changed(self, event=None):
        self._refresh_image_list()

    def _refresh_image_list(self):
        path = self._entry_input.get().strip()

        if not os.path.isdir(path):
            self._lbl_count.configure(text="Invalid folder")
            self._lbl_size.configure(text="")
            self._status_dot.configure(text="● Invalid folder", text_color="#ef4444")
            self._preview_container.pack_forget()
            return

        images = find_images(path)

        if not images:
            self._lbl_count.configure(text="No JPG/JPEG images found")
            self._lbl_size.configure(text="")
            self._set_status("empty")
            self._preview_container.pack_forget()
            return

        self._lbl_count.configure(text=f"📷  {len(images)} images found")
        try:
            with PILImage.open(images[0]) as first:
                w, h = first.size
            self._lbl_size.configure(text=f"  ·  {w}×{h}px")
        except Exception:
            self._lbl_size.configure(text="")

        self._set_status("ready")
        self._preview_container.pack(fill="x", pady=(0, 4))
        self._refresh_preview(images)

    def _start_conversion(self):
        if self._running:
            return
        self._running = True
        self._btn_convert.configure(state="disabled", text="⏳  Converting…")
        self._set_status("converting")
        self._progress.set(0)
        self._progress_label.configure(text="0%")
        self._log.configure(state="normal")
        self._log.delete("0.0", "end")
        self._log.configure(state="disabled")
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        input_dir = self._entry_input.get().strip()
        output_file = self._entry_output.get().strip()
        try:
            fps = int(self._entry_fps.get().strip())
        except ValueError:
            self._log_msg("Error: invalid FPS.")
            self._reset_button()
            return
        try:
            total_duration = float(self._entry_duration.get().strip())
        except ValueError:
            self._log_msg("Error: invalid Duration.")
            self._reset_button()
            return

        success = convert_images_to_video(
            input_dir=input_dir,
            output_file=output_file,
            fps=fps,
            total_duration=total_duration,
            progress_callback=self._update_progress,
            log_callback=self._log_msg,
        )
        if success:
            self._log_msg("✅ Conversion completed successfully!")
            self._set_status("done")
        else:
            self._set_status("error")
        self._reset_button()

    def _reset_button(self):
        self._running = False
        self._btn_convert.configure(state="normal", text="🚀  Convert")


if __name__ == "__main__":
    from tkinter import filedialog
    app = ConverterApp()
    app._refresh_image_list()
    app.mainloop()
