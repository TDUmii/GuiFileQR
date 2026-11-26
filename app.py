"""Giao diện nâng cao của Gửi File QR."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import qrcode
from PIL import ImageTk

from network import local_addresses
from sharing import ShareSession


PAGE = "#f5f7fc"
WHITE = "#ffffff"
INK = "#14223b"
MUTED = "#465877"
LINE = "#dce4f1"
BLUE = "#244dd8"
SOFT_BLUE = "#eaf0ff"
NAVY = "#142856"
PALE_BLUE = "#c9d7ff"
GREEN = "#a7ebce"
ERROR = "#9c1833"
QR_SIZE = 248
FONT = "Segoe UI"


def label(parent, text="", *, size=11, bold=False, bg=PAGE, fg=INK, **options):
    return tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"),
                    background=bg, foreground=fg, padx=0, pady=0, **options)


class ShareWindow:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.session = None
        self.qr_image = None
        self.host = tk.StringVar()
        self.filename = tk.StringVar(value="Chưa chọn file")
        self.file_details = tk.StringVar(value="Chọn một file trên máy tính.")
        self.status = tk.StringVar()

        root.title("Gửi File QR")
        root.configure(background=PAGE)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Control-o>", lambda event: self.choose_file())
        self.setup_styles()
        self.build()
        self.refresh_addresses()
        root.update_idletasks()
        width = max(850, root.winfo_reqwidth())
        height = root.winfo_reqheight()
        root.minsize(width, height)
        root.geometry(f"{max(952, width)}x{max(575, height)}")
        self.choose_button.focus_set()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        buttons = (
            ("TButton", "#edf2fc", INK, LINE, "#e2ebff", "#d3e1ff"),
            ("Primary.TButton", BLUE, WHITE, BLUE, "#1d42c0", "#163496"),
            ("Stop.TButton", "#fff0f2", ERROR, "#f0ccd4", "#fbe1e7", "#f8d5de"),
            ("Copy.TButton", "#213c78", WHITE, "#5171b1", "#304e96", "#193268"),
        )
        for name, bg, fg, border, hover, pressed in buttons:
            disabled_bg, disabled_fg = ("#213666", "#a2b4da") if name == "Copy.TButton" else ("#edf1f8", "#617390")
            style.configure(name, font=(FONT, 10, "bold"), padding=(14, 9),
                            background=bg, foreground=fg, bordercolor=border,
                            lightcolor=bg, darkcolor=bg, relief="flat")
            style.map(name, background=[("disabled", disabled_bg), ("pressed", pressed), ("active", hover)],
                      foreground=[("disabled", disabled_fg)],
                      bordercolor=[("focus", "#ffcb6b" if name == "Copy.TButton" else BLUE)])
        style.configure("TCombobox", padding=6, bordercolor=LINE, arrowsize=13)
        style.map("TCombobox", fieldbackground=[("readonly", WHITE)],
                  bordercolor=[("focus", BLUE)])

    def build(self):
        page = tk.Frame(self.root, bg=PAGE, padx=30, pady=22)
        page.pack(fill="both", expand=True)
        label(page, "Gửi File QR", size=30, bold=True).pack(anchor="w")
        label(page, "Gửi một file từ máy tính sang điện thoại qua Wi-Fi.", fg=MUTED).pack(anchor="w", pady=(2, 20))

        workspace = tk.Frame(page, bg=WHITE, highlightthickness=1, highlightbackground=LINE)
        workspace.pack(fill="both", expand=True)
        workspace.columnconfigure(0, weight=5, uniform="workspace")
        workspace.columnconfigure(1, weight=6, uniform="workspace")
        workspace.rowconfigure(0, weight=1)
        settings = tk.Frame(workspace, bg=WHITE, padx=25, pady=19)
        settings.grid(row=0, column=0, sticky="nsew")
        receiver = tk.Frame(workspace, bg=NAVY, padx=20, pady=15)
        receiver.grid(row=0, column=1, sticky="nsew")

        self.build_settings(settings)
        self.build_receiver(receiver)
        self.status_label = label(page, textvariable=self.status, fg=MUTED,
                                  anchor="w", justify="left", height=2)
        self.status_label.pack(fill="x", pady=(12, 0))
        page.bind("<Configure>", lambda event: self.status_label.configure(wraplength=max(1, event.width - 60)))

    def build_settings(self, parent):
        label(parent, "Chọn file để gửi", size=15, bold=True, bg=WHITE).pack(anchor="w")
        file_card = tk.Frame(parent, bg=PAGE, padx=12, pady=10)
        file_card.pack(fill="x", pady=(10, 10))
        icon = tk.Canvas(file_card, width=40, height=40, bg=SOFT_BLUE, highlightthickness=0)
        icon.pack(side="left", padx=(0, 10), anchor="n")
        icon.create_line(12, 9, 24, 9, 29, 14, 29, 31, 12, 31, 12, 9, fill=BLUE, width=2)
        icon.create_line(24, 9, 24, 14, 29, 14, fill=BLUE, width=2)
        icon.create_line(17, 21, 24, 21, fill=BLUE, width=2)
        icon.create_line(17, 26, 24, 26, fill=BLUE, width=2)

        file_info = tk.Frame(file_card, bg=PAGE)
        file_info.pack(side="left", fill="x", expand=True)
        label(file_info, textvariable=self.filename, bold=True, anchor="w",
              justify="left", wraplength=238, height=2).pack(fill="x")
        label(file_info, textvariable=self.file_details, size=10, fg=MUTED,
              anchor="w").pack(fill="x", pady=(2, 0))

        self.choose_button = ttk.Button(parent, text="Chọn file…", command=self.choose_file)
        self.choose_button.pack(anchor="w")
        ttk.Separator(parent).pack(fill="x", pady=(15, 13))

        label(parent, "Địa chỉ mạng của máy tính", size=11, bold=True, bg=WHITE).pack(anchor="w")
        network = tk.Frame(parent, bg=WHITE)
        network.pack(fill="x", pady=(6, 5))
        self.address_box = ttk.Combobox(network, textvariable=self.host, width=15,
                                        font=("Consolas", 11), state="readonly")
        self.address_box.pack(side="left", fill="x", expand=True)
        self.address_box.bind("<<ComboboxSelected>>", lambda event: self.update_action())
        self.refresh_button = ttk.Button(network, text="Tìm lại", command=self.refresh_addresses)
        self.refresh_button.pack(side="left", padx=(8, 0))
        label(parent, "Hai thiết bị cần dùng cùng mạng nội bộ.", size=10, bg=WHITE, fg=MUTED).pack(anchor="w")

        self.share_button = ttk.Button(parent, text="Tạo mã QR", style="Primary.TButton", command=self.toggle)
        self.share_button.pack(fill="x", side="bottom", pady=(12, 0))

    def build_receiver(self, parent):
        label(parent, "Quét để tải file", size=17, bold=True, bg=NAVY, fg=WHITE).pack()
        self.receiver_hint = label(parent, "Tạo mã QR để bắt đầu.", size=10, bg=NAVY, fg=PALE_BLUE)
        self.receiver_hint.pack(pady=(2, 8))

        paper = tk.Canvas(parent, width=QR_SIZE, height=QR_SIZE, bg=WHITE,
                          highlightthickness=0, takefocus=False)
        paper.pack()
        self.qr_canvas = paper
        for x, y, dx, dy in ((82, 80, 1, 1), (166, 80, -1, 1),
                             (82, 156, 1, -1), (166, 156, -1, -1)):
            paper.create_line(x + dx * 21, y, x, y, x, y + dy * 21, fill=BLUE,
                              width=3, tags="placeholder")
        paper.create_text(QR_SIZE // 2, 184, text="Mã QR sẽ hiện ở đây", font=(FONT, 10),
                          fill=MUTED, tags="placeholder")
        self.qr_item = paper.create_image(QR_SIZE // 2, QR_SIZE // 2)

        self.copy_button = ttk.Button(parent, text="Sao chép liên kết", style="Copy.TButton",
                                      command=self.copy_url, state="disabled")
        self.copy_button.pack(pady=(10, 0))

    def show_status(self, text, *, error=False):
        self.status.set(text)
        self.status_label.configure(fg=ERROR if error else MUTED)

    def refresh_addresses(self):
        addresses = local_addresses()
        self.address_box.configure(values=addresses)
        if self.host.get() not in addresses:
            self.host.set(addresses[0] if addresses else "")
        self.show_status("Chưa chia sẻ." if addresses else
                         "Chưa tìm thấy mạng nội bộ. Kết nối mạng rồi bấm Tìm lại.", error=not addresses)
        self.update_action()

    def choose_file(self):
        if self.session:
            return
        filename = filedialog.askopenfilename(parent=self.root, title="Chọn file để chia sẻ")
        if filename:
            self.file_path = Path(filename)
            name = self.file_path.name
            self.filename.set(name if len(name) <= 48 else name[:28] + "…" + name[-16:])
            try:
                size = self.file_path.stat().st_size
            except OSError:
                self.file_details.set("Không đọc được thông tin file.")
            else:
                self.file_details.set(f"{size:,}".replace(",", ".") + " byte")
            if self.host.get():
                self.show_status("File đã sẵn sàng. Bấm Tạo mã QR.")
            self.update_action()

    def update_action(self):
        enabled = self.file_path is not None and bool(self.host.get())
        self.share_button.configure(state="normal" if enabled else "disabled")

    def toggle(self):
        if self.session:
            self.stop_sharing()
        else:
            self.start_sharing()

    def start_sharing(self):
        if self.file_path is None or not self.host.get():
            return
        session = None
        try:
            session = ShareSession(self.file_path, self.host.get())
            qr = qrcode.QRCode(border=4)
            qr.add_data(session.url)
            qr.make(fit=True)
            qr.box_size = QR_SIZE // (qr.modules_count + 2 * qr.border)
            self.qr_image = ImageTk.PhotoImage(qr.make_image().get_image(), master=self.root)
        except (OSError, ValueError, tk.TclError, RuntimeError) as error:
            if session is not None:
                session.close()
            if isinstance(error, (FileNotFoundError, PermissionError, IsADirectoryError)):
                self.show_status("Không mở được file. Kiểm tra quyền đọc hoặc chọn lại file.", error=True)
            else:
                self.show_status("Không thể mở chia sẻ. Bấm Tìm lại hoặc chọn địa chỉ mạng khác.", error=True)
            return

        self.session = session
        self.show_sharing_state(True)
        self.show_status("Đang chia sẻ. Giữ cửa sổ mở trong khi điện thoại tải.")
        self.share_button.focus_set()

    def show_sharing_state(self, active):
        self.qr_canvas.itemconfigure("placeholder", state="hidden" if active else "normal")
        self.qr_canvas.itemconfigure(self.qr_item, image=self.qr_image if active else "")
        self.receiver_hint.configure(text="Dùng camera điện thoại để quét." if active else "Tạo mã QR để bắt đầu.",
                                     fg=GREEN if active else PALE_BLUE)
        self.share_button.configure(text="Dừng chia sẻ" if active else "Tạo mã QR",
                                    style="Stop.TButton" if active else "Primary.TButton")
        self.copy_button.configure(state="normal" if active else "disabled")
        self.choose_button.configure(state="disabled" if active else "normal")
        self.refresh_button.configure(state="disabled" if active else "normal")
        self.address_box.configure(state="disabled" if active else "readonly")

    def copy_url(self):
        if self.session:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.session.url)
            self.show_status("Đang chia sẻ. Đã sao chép liên kết tải file.")

    def stop_sharing(self):
        self.session.close()
        self.session = None
        self.show_sharing_state(False)
        self.qr_image = None
        self.show_status("Đã dừng chia sẻ. Mã QR cũ hết hiệu lực.")

    def close(self):
        if self.session:
            self.session.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ShareWindow(root)
    root.mainloop()
