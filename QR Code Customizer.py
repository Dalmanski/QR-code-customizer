#!/usr/bin/env python3
"""
Requirements:
- Python 3
- pip install qrcode pillow
"""

import qrcode
from tkinter import Tk, Label, Entry, Button, StringVar, IntVar, Spinbox, messagebox, Canvas
from tkinter import filedialog
from PIL import Image, ImageTk

DEFAULT_SIZE = 40
DEFAULT_BORDER = 1
PREVIEW_MAX = 200

DARK_BG = "#2b2b2b"
DARK_PANEL = "#232323"
FG = "#f2f2f2"
ENTRY_BG = "#333333"
ENTRY_FG = "#ffffff"
BTN_BG = "#3a7bd5"
BTN_FG = "#ffffff"
STATUS_BG = DARK_BG


def ask_save_path(default_ext=".png"):
    path = filedialog.asksaveasfilename(defaultextension=default_ext,
                                        filetypes=[("PNG Image", "*.png")],
                                        title="Save QR Code As")
    return path


def generate_qr_image(data: str, desired_size: int, border: int) -> Image.Image:
    if not data:
        raise ValueError("No data provided for QR code")

    tmp_qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=border,
    )
    tmp_qr.add_data(data)
    tmp_qr.make(fit=True)
    modules_count = len(tmp_qr.get_matrix())

    total_boxes = modules_count + border * 2
    if total_boxes <= 0:
        raise ValueError("Computed total boxes is invalid")

    box_size = max(1, desired_size // total_boxes)

    qr = qrcode.QRCode(
        version=tmp_qr.version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    final_size = img.size[0]

    if final_size != desired_size:
        img = img.resize((desired_size, desired_size), Image.NEAREST)

    return img


class QRGui:
    def __init__(self, root):
        self.root = root
        root.title("QR Code Customizer")
        root.configure(bg=DARK_BG)

        Label(root, text="Text / URL:", bg=DARK_BG, fg=FG).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.data_var = StringVar()
        self.data_entry = Entry(root, textvariable=self.data_var, width=48, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.data_entry.grid(row=0, column=1, columnspan=3, padx=8, pady=6)

        Label(root, text="Pixel size:", bg=DARK_BG, fg=FG).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.size_var = StringVar(value=str(DEFAULT_SIZE))
        self.size_entry = Entry(root, textvariable=self.size_var, width=10, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.size_entry.grid(row=1, column=1, sticky="w", padx=8, pady=6)
        Label(root, text="(final image will be WxW pixels)", bg=DARK_BG, fg=FG).grid(row=1, column=2, columnspan=2, sticky="w")

        Label(root, text="White edge (quiet zone) size:", bg=DARK_BG, fg=FG).grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.border_var = IntVar(value=DEFAULT_BORDER)
        self.border_spin = Spinbox(root, from_=0, to=10, textvariable=self.border_var, width=6, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.border_spin.grid(row=2, column=1, sticky="w", padx=8)
        Label(root, text="(0 = none; 4 is typical)", bg=DARK_BG, fg=FG).grid(row=2, column=2, columnspan=2, sticky="w")

        self.gen_btn = Button(root, text="Generate & Save PNG", command=self.on_generate, bg=BTN_BG, fg=BTN_FG)
        self.gen_btn.grid(row=3, column=0, columnspan=3, pady=12, padx=8, sticky="w")

        Label(root, text="Preview:", bg=DARK_BG, fg=FG).grid(row=0, column=4, sticky="sw", padx=8)
        self.preview_frame = Label(root, bg=DARK_PANEL)
        self.preview_frame.grid(row=1, column=4, rowspan=3, padx=8, pady=6)
        self.preview_canvas = Canvas(self.preview_frame, width=PREVIEW_MAX, height=PREVIEW_MAX, bg=DARK_PANEL, highlightthickness=0)
        self.preview_canvas.pack()
        self.preview_image_id = None
        self.preview_image_ref = None

        self.status_label = Label(root, text="Ready", anchor="w", bg=STATUS_BG, fg=FG)
        self.status_label.grid(row=4, column=0, columnspan=4, sticky="we", padx=8, pady=6)

        self.credits_label = Label(root, text="Created by Dalmanski", bg=DARK_BG, fg=FG)
        self.credits_label.grid(row=4, column=4, sticky="e", padx=8, pady=6)

        try:
            self.data_var.trace_add('write', lambda *args: self.update_preview())
            self.size_var.trace_add('write', lambda *args: self.update_preview())
            self.border_var.trace_add('write', lambda *args: self.update_preview())
        except Exception:
            self.data_var.trace('w', lambda *args: self.update_preview())
            self.size_var.trace('w', lambda *args: self.update_preview())
            self.border_var.trace('w', lambda *args: self.update_preview())

    def update_preview(self):
        data = self.data_var.get().strip()
        if not data:
            self.preview_canvas.delete("all")
            self.status_label.config(text='Ready')
            return

        try:
            desired_size = int(self.size_var.get())
            if desired_size <= 0:
                desired_size = DEFAULT_SIZE
        except Exception:
            desired_size = DEFAULT_SIZE

        preview_size = PREVIEW_MAX  # show preview at fixed 200x200 regardless of final size
        border = int(self.border_var.get()) if self.border_var.get() is not None else DEFAULT_BORDER

        try:
            img = generate_qr_image(data, preview_size, border)
            tk_img = ImageTk.PhotoImage(img)
            self.preview_image_ref = tk_img
            self.preview_canvas.delete("all")
            self.preview_image_id = self.preview_canvas.create_image(PREVIEW_MAX//2, PREVIEW_MAX//2, image=tk_img)
            self.status_label.config(text=f'Preview updated ({preview_size}x{preview_size}px, border={border})')
        except Exception as e:
            self.preview_canvas.delete("all")
            self.status_label.config(text=f'Preview error: {e}')

    def on_generate(self):
        data = self.data_var.get().strip()
        if not data:
            messagebox.showerror("Error", "Please enter text or a URL to encode.")
            return

        try:
            desired_size = int(self.size_var.get())
            if desired_size <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Error", "Pixel size must be a positive integer.")
            return

        border = int(self.border_var.get())
        if border < 0:
            messagebox.showerror("Error", "Border must be 0 or greater.")
            return

        save_path = ask_save_path(".png")
        if not save_path:
            self.status_label.config(text="Save canceled.")
            return

        self.status_label.config(text="Generating...")
        self.root.update_idletasks()

        try:
            img = generate_qr_image(data, desired_size, border)
            img.save(save_path, format="PNG")
            self.status_label.config(text=f"✅ Saved: {save_path} ({desired_size}x{desired_size}px, border={border})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate or save QR: {e}")
            self.status_label.config(text=f"Error: {e}")


def main():
    root = Tk()
    try:
        root.eval('tk::PlaceWindow . center')
    except Exception:
        pass
    try:
        root.iconbitmap('icon.ico')
    except Exception:
        try:
            root.iconphoto(False, ImageTk.PhotoImage(file='icon.ico'))
        except Exception:
            pass
    QRGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
