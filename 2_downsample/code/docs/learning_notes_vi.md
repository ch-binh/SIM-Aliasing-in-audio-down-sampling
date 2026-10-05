# Mô phỏng aliasing của PCM: 64 → 32 kHz

- Ngày thực hiện: 2026-10-05 (Asia/Saigon).
- PCM mono: 3, 10 và 31 kHz; mỗi thành phần có biên độ 0,12 FS.
- Thời lượng: 4 giây. Fade 10 ms ở đầu/cuối để giảm tiếng click khi playback.
- Downsample: `after = before[::2]`, không lọc thông thấp.
- File sau được ghi ở **32 kHz**, không phát sai tốc độ ở 64 kHz.
- Giữ nguyên thang biên độ giữa hai file; không normalize riêng.

| Trước (64 kHz) | Sau (32 kHz) |
|---|---|
| 3 kHz | 3 kHz |
| 10 kHz | 10 kHz |
| 31 kHz | **1 kHz** |

Thành phần 31 kHz vượt Nyquist mới 16 kHz, nên gập xuống
`abs(31 - 32) = 1 kHz`. File sau xuất hiện âm 1 kHz dù file trước
không có thành phần 1 kHz đáng kể.

## Chạy với venv có sẵn

```powershell
.\.venv314\Scripts\python.exe 1_demo_audio/code/run_demo.py
```

Nếu dựng môi trường mới:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r 1_demo_audio/code/requirements.txt
.\.venv\Scripts\python.exe 1_demo_audio/code/run_demo.py
```

## Xem và nghe

Mở `1_demo_audio/output/index.html` để xem hai biểu đồ và nghe
hai file WAV. Bắt đầu ở âm lượng nhỏ vì đây là các âm đơn liên tục.

FFT được tính từ **PCM 16-bit đọc lại từ chính file WAV**, dùng 2 giây
ở giữa bản ghi (bỏ vùng fade). Phổ biên độ một phía được chuẩn hóa theo
số mẫu; hai biểu đồ dùng cùng thang biên độ. Dạng sóng phóng to 1 ms.

Browser/OS có thể resample trước khi đưa âm thanh ra thiết bị. Loa thông
thường không thể tái tạo trung thực 31 kHz. Vì vậy, WAV và FFT là bằng
chứng về thành phần 31 kHz; playback giúp nghe thành phần alias 1 kHz
xuất hiện sau downsample. FFT không được tính từ tín hiệu đã qua loa.

Script tự kiểm tra tốc độ mẫu, thời lượng, quy tắc giữ mẫu xen kẽ,
không clipping, ba đỉnh FFT và biên độ tại 1 kHz trước/sau.

Tài liệu: [MathWorks — downsample](https://www.mathworks.com/help/signal/ref/downsample.html).
