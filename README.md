# Gửi File QR

App desktop Python gửi một file từ máy tính sang điện thoại trong cùng mạng nội bộ. Điện thoại quét mã QR rồi tải file bằng trình duyệt.

## Chạy trên Windows

Cài Python 3.10 trở lên kèm Tcl/Tk. Trên trang GitHub của dự án, bấm **Code** → **Download ZIP**, rồi giải nén thư mục vừa tải.

Nếu đã cài Git, có thể chạy hai lệnh sau trong Terminal.

```powershell
git clone https://github.com/TDUmii/GuiFileQR.git
cd GuiFileQR
```

| Phiên bản | Cách mở | Dành cho |
| --- | --- | --- |
| Cơ bản | Nhấp đúp `ChayBanCoBan.cmd` | Dạy trên lớp, tập trung vào chọn file, tạo mã QR và dừng chia sẻ. |
| Nâng cao | Nhấp đúp `ChayGuiFileQR.cmd` | Xem một giao diện hoàn chỉnh và học cách phát triển tiếp từ bản cơ bản. |

Hai bản dùng chung môi trường `.venv`. Lần chạy đầu cần Internet để cài Flask và thư viện tạo mã QR. Sau khi cài, có thể chạy trực tiếp từ PowerShell.

```powershell
.\.venv\Scripts\python.exe basic.py
.\.venv\Scripts\python.exe app.py
```

## Gửi một file

1. Kết nối điện thoại và máy tính vào cùng mạng nội bộ. Máy tính có thể cắm cáp Ethernet vào router phát Wi-Fi cho điện thoại.
2. Chọn một file rồi tạo mã QR. Nếu danh sách có nhiều địa chỉ mạng, dùng IPv4 của kết nối Wi-Fi hoặc Ethernet đang dùng. Có thể chạy `ipconfig` để xem địa chỉ.
3. Quét QR bằng camera điện thoại và mở liên kết. Bản nâng cao có nút **Sao chép liên kết** để mở cùng địa chỉ từ một thiết bị khác.
4. Giữ app mở trong lúc tải. Bấm **Dừng chia sẻ** khi xong để đóng liên kết.

Nếu điện thoại không mở được liên kết, kiểm tra IP đã chọn và thử lại trên mạng cho phép hai thiết bị kết nối với nhau. Wi-Fi khách có thể tách các thiết bị. Nếu hai thiết bị cùng mạng mà vẫn không kết nối được, kiểm tra xem tường lửa Windows có chặn kết nối tới Python trên mạng đó không.

## Lộ trình làm theo

1. **Bắt đầu với `basic.py`.** Chạy app, theo dấu từ nút chọn file đến lúc có đường dẫn tải, rồi quan sát mã QR được tạo từ đường dẫn đó. Thử đổi thông báo sau khi chọn file.
2. **Đọc `network.py` và `sharing.py`.** Xem cách chọn IP, tạo một đường dẫn tải cho file đã chọn và đóng phiên chia sẻ. Thử tải một file có tên tiếng Việt, bấm dừng, rồi mở lại liên kết cũ.
3. **Mở `app.py` để nâng cấp giao diện.** Chọn một cải tiến để làm theo, chẳng hạn hiện dung lượng file, thêm nút chép liên kết hoặc đổi trạng thái nút khi đang chia sẻ. Chạy lại từ lúc chọn file tới lúc dừng chia sẻ để kiểm tra cả hai trạng thái.

Kiểm tra phần tải file và đóng phiên trên chính máy tính bằng lệnh dưới đây khi đã chạy trình mở app ít nhất một lần.

```powershell
.\.venv\Scripts\python.exe -B test_sharing.py
```
