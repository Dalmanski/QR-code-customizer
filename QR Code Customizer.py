#!/usr/bin/env python3
import qrcode
from tkinter import Tk, Label, Entry, Button, StringVar, IntVar, Spinbox, messagebox, Canvas, colorchooser
from tkinter import filedialog
from PIL import Image, ImageTk, ImageColor

VERSION = "1.1.0"
CREATED_BY = "Created by: Dalmanski"

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

QR_FG_DEFAULT = "#000000"
QR_BG_DEFAULT = "#ffffff"


def ask_save_path(default_ext=".png"):
    return filedialog.asksaveasfilename(defaultextension=default_ext,
                                        filetypes=[("PNG Image", "*.png")],
                                        title="Save QR Code As")


def generate_qr_image(data: str, desired_size: int, border: int,
                      fill_color: str = QR_FG_DEFAULT, back_color: str = QR_BG_DEFAULT) -> Image.Image:
    if not data:
        raise ValueError("No data provided for QR code")
    tmp_qr = qrcode.QRCode(version=None,
                           error_correction=qrcode.constants.ERROR_CORRECT_H,
                           box_size=1,
                           border=border)
    tmp_qr.add_data(data)
    tmp_qr.make(fit=True)
    modules_count = len(tmp_qr.get_matrix())
    total_boxes = modules_count + border * 2
    if total_boxes <= 0:
        raise ValueError("Computed total boxes is invalid")
    box_size = max(1, desired_size // total_boxes)
    qr = qrcode.QRCode(version=tmp_qr.version,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=box_size,
                       border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    final_size = img.size[0]
    if final_size != desired_size:
        img = img.resize((desired_size, desired_size), Image.NEAREST)
    return img


def _to_rgb(color_str):
    try:
        return ImageColor.getrgb(color_str)
    except Exception:
        try:
            h = color_str.lstrip('#')
            if len(h) == 3:
                h = ''.join([c*2 for c in h])
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            return (r, g, b)
        except Exception:
            return (0, 0, 0)


def _contrasting_text(hex_color: str) -> str:
    try:
        r, g, b = _to_rgb(hex_color)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return "#000000" if luminance > 186 else "#ffffff"
    except Exception:
        return "#ffffff"


class QRGui:
    def __init__(self, root):
        self.root = root
        root.title("QR Code Customizer")
        root.configure(bg=DARK_BG)

        Label(root, text="Text / URL:", bg=DARK_BG, fg=FG).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.data_var = StringVar()
        self.data_entry = Entry(root, textvariable=self.data_var, width=48,
                                bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.data_entry.grid(row=0, column=1, columnspan=4, padx=8, pady=6)

        Label(root, text="Pixel size:", bg=DARK_BG, fg=FG).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.size_var = StringVar(value=str(DEFAULT_SIZE))
        self.size_entry = Entry(root, textvariable=self.size_var, width=10,
                                bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.size_entry.grid(row=1, column=1, sticky="w", padx=8, pady=6)
        Label(root, text="(final image will be WxW pixels)", bg=DARK_BG, fg=FG)\
            .grid(row=1, column=2, columnspan=3, sticky="w")

        Label(root, text="White edge (quiet zone) size:", bg=DARK_BG, fg=FG)\
            .grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.border_var = IntVar(value=DEFAULT_BORDER)
        self.border_spin = Spinbox(root, from_=0, to=10, textvariable=self.border_var, width=6,
                                   bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG)
        self.border_spin.grid(row=2, column=1, sticky="w", padx=8)
        Label(root, text="(0 = none; 4 is typical)", bg=DARK_BG, fg=FG)\
            .grid(row=2, column=2, columnspan=3, sticky="w")

        Label(root, text="QR Foreground:", bg=DARK_BG, fg=FG).grid(row=3, column=0, sticky="w", padx=8, pady=6)
        self.fg_color_var = StringVar(value=QR_FG_DEFAULT)
        self.fg_color_btn = Button(root, text=self.fg_color_var.get(), command=self.pick_fg_color,
                                   bg=self.fg_color_var.get(), fg=_contrasting_text(self.fg_color_var.get()), width=10)
        self.fg_color_btn.grid(row=3, column=1, sticky="w", padx=8, pady=6)

        Label(root, text="QR Background:", bg=DARK_BG, fg=FG).grid(row=4, column=0, sticky="w", padx=8, pady=6)
        self.bg_color_var = StringVar(value=QR_BG_DEFAULT)
        self.bg_color_btn = Button(root, text=self.bg_color_var.get(), command=self.pick_bg_color,
                                   bg=self.bg_color_var.get(), fg=_contrasting_text(self.bg_color_var.get()), width=10)
        self.bg_color_btn.grid(row=4, column=1, sticky="w", padx=8, pady=6)

        self.gen_btn = Button(root, text="Generate & Save PNG", command=self.on_generate, bg=BTN_BG, fg=BTN_FG)
        self.gen_btn.grid(row=5, column=0, columnspan=3, pady=12, padx=8, sticky="w")

        Label(root, text="Preview:", bg=DARK_BG, fg=FG).grid(row=0, column=5, sticky="sw", padx=8)
        self.preview_frame = Label(root, bg=DARK_PANEL)
        self.preview_frame.grid(row=1, column=5, rowspan=6, padx=8, pady=6)
        self.preview_canvas = Canvas(self.preview_frame, width=PREVIEW_MAX, height=PREVIEW_MAX,
                                    bg=DARK_PANEL, highlightthickness=0)
        self.preview_canvas.pack(padx=6, pady=(6, 2))
        self.preview_image_ref = None

        self.status_label = Label(root, text="Ready", anchor="w", bg=STATUS_BG, fg=FG)
        self.status_label.grid(row=6, column=0, columnspan=5, sticky="we", padx=8, pady=6)

        self.created_label = Label(root, text=CREATED_BY, bg=DARK_BG, fg=FG)
        self.created_label.grid(row=7, column=5, sticky="n", padx=8, pady=(6, 0))
        self.version_label = Label(root, text=f"Version: {VERSION}", bg=DARK_BG, fg=FG)
        self.version_label.grid(row=8, column=5, sticky="n", padx=8, pady=(0, 8))

        try:
            self.data_var.trace_add('write', lambda *args: self.update_preview())
            self.size_var.trace_add('write', lambda *args: self.update_preview())
            self.border_var.trace_add('write', lambda *args: self.update_preview())
            self.fg_color_var.trace_add('write', lambda *args: self.update_preview())
            self.bg_color_var.trace_add('write', lambda *args: self.update_preview())
        except Exception:
            self.data_var.trace('w', lambda *args: self.update_preview())
            self.size_var.trace('w', lambda *args: self.update_preview())
            self.border_var.trace('w', lambda *args: self.update_preview())
            self.fg_color_var.trace('w', lambda *args: self.update_preview())
            self.bg_color_var.trace('w', lambda *args: self.update_preview())

    def pick_fg_color(self):
        rgb, hx = colorchooser.askcolor(color=self.fg_color_var.get(), title="Choose QR foreground color")
        if hx:
            self.fg_color_var.set(hx)
            self.fg_color_btn.configure(text=hx, bg=hx, fg=_contrasting_text(hx))

    def pick_bg_color(self):
        rgb, hx = colorchooser.askcolor(color=self.bg_color_var.get(), title="Choose QR background color")
        if hx:
            self.bg_color_var.set(hx)
            self.bg_color_btn.configure(text=hx, bg=hx, fg=_contrasting_text(hx))

    def update_preview(self):
        data_raw = self.data_var.get().strip()
        if not data_raw:
            self.preview_canvas.delete("all")
            self.status_label.config(text='Ready')
            return
        try:
            preview_size = PREVIEW_MAX
            border = int(self.border_var.get()) if self.border_var.get() is not None else DEFAULT_BORDER
            fg = self.fg_color_var.get() or QR_FG_DEFAULT
            bg = self.bg_color_var.get() or QR_BG_DEFAULT
            img = generate_qr_image(data_raw, preview_size, border, fill_color=fg, back_color=bg)
            tk_img = ImageTk.PhotoImage(img)
            self.preview_image_ref = tk_img
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(PREVIEW_MAX//2, PREVIEW_MAX//2, image=tk_img)
            self.created_label.configure(text=CREATED_BY)
            self.version_label.configure(text=f"Version: {VERSION}")
            self.status_label.config(text=f'Preview updated ({preview_size}x{preview_size}px, border={border})')
        except Exception as e:
            self.preview_canvas.delete("all")
            self.status_label.config(text=f'Preview error: {e}')

    def on_generate(self):
        data_raw = self.data_var.get().strip()
        if not data_raw:
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
        fg = self.fg_color_var.get() or QR_FG_DEFAULT
        bg = self.bg_color_var.get() or QR_BG_DEFAULT
        try:
            qr_img = generate_qr_image(data_raw, desired_size, border, fill_color=fg, back_color=bg)
            qr_img.save(save_path, format="PNG")
            self.status_label.config(text=f"✅ Saved: {save_path} ({desired_size}x{desired_size}px, border={border}, fg={fg}, bg={bg})")
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
