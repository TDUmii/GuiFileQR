"""Bản cơ bản để học cách chia sẻ file qua mã QR."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import qrcode
from PIL import ImageTk

from network import local_addresses
from sharing import ShareSession


def main():
    window = tk.Tk()
    window.title("Gửi File QR - Bản cơ bản")
    window.resizable(False, False)
    frame = ttk.Frame(window, padding=20)
    frame.pack()

    chosen_file = None
    session = None
    file_name = tk.StringVar(value="Chưa chọn file")
    status = tk.StringVar(value="Chọn file và kết nối hai thiết bị vào cùng mạng.")
    addresses = local_addresses()

    def choose_file():
        nonlocal chosen_file
        selected = filedialog.askopenfilename(parent=window, title="Chọn một file")
        if selected:
            chosen_file = Path(selected)
            file_name.set(chosen_file.name)
            status.set("Bấm Tạo mã QR để chia sẻ.")

    def start_sharing():
        nonlocal session
        if chosen_file is None:
            status.set("Hãy chọn một file trước.")
            return
        if not address_box.get():
            status.set("Chưa tìm thấy địa chỉ mạng. Kết nối mạng rồi mở lại app.")
            return

        try:
            # Máy chủ tạo link tải. Mã QR chứa chính đường dẫn này.
            session = ShareSession(chosen_file, address_box.get())
            qr = qrcode.make(session.url, box_size=5)
            qr_image = ImageTk.PhotoImage(qr.get_image(), master=window)
        except (OSError, ValueError, tk.TclError) as error:
            stop_sharing()
            if isinstance(error, (FileNotFoundError, PermissionError)):
                status.set("Không đọc được file. Hãy chọn lại file.")
            else:
                status.set("Chưa thể chia sẻ. Kiểm tra địa chỉ mạng rồi thử lại.")
            return

        qr_label.configure(image=qr_image, text="")
        qr_label.image = qr_image  # Tkinter cần giữ tham chiếu đến ảnh QR.
        choose_button.configure(state="disabled")
        address_box.configure(state="disabled")
        start_button.configure(state="disabled")
        stop_button.configure(state="normal")
        stop_button.focus_set()
        status.set("Quét mã bằng camera điện thoại. Giữ cửa sổ mở khi tải.")

    def stop_sharing():
        nonlocal session
        if session is not None:
            session.close()
            session = None
        qr_label.configure(image="", text="Mã QR sẽ hiện ở đây")
        qr_label.image = None
        choose_button.configure(state="normal")
        address_box.configure(state="readonly")
        start_button.configure(state="normal")
        stop_button.configure(state="disabled")
        start_button.focus_set()
        status.set("Đã dừng chia sẻ.")

    def close_window():
        if session is not None:
            session.close()
        window.destroy()

    choose_button = ttk.Button(frame, text="Chọn file…", command=choose_file)
    choose_button.pack(anchor="w")
    ttk.Label(frame, textvariable=file_name, wraplength=375).pack(anchor="w", pady=(6, 12))
    ttk.Label(frame, text="Địa chỉ mạng").pack(anchor="w")
    address_box = ttk.Combobox(frame, values=addresses, state="readonly", width=20)
    address_box.pack(anchor="w", pady=(4, 12))
    if addresses:
        address_box.current(0)
    else:
        status.set("Chưa tìm thấy địa chỉ mạng. Kết nối mạng rồi mở lại app.")

    actions = ttk.Frame(frame)
    actions.pack(anchor="w")
    start_button = ttk.Button(actions, text="Tạo mã QR", command=start_sharing)
    start_button.pack(side="left")
    stop_button = ttk.Button(actions, text="Dừng chia sẻ", command=stop_sharing, state="disabled")
    stop_button.pack(side="left", padx=(8, 0))
    qr_label = ttk.Label(frame, text="Mã QR sẽ hiện ở đây", anchor="center")
    qr_label.pack(fill="x", pady=12)
    ttk.Label(frame, textvariable=status, wraplength=375).pack(anchor="w")

    window.protocol("WM_DELETE_WINDOW", close_window)
    choose_button.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()
