# 🔐 Ứng dụng Chữ ký số RSA

> **Môn học:** An toàn và Bảo mật Thông tin  
> **Chủ đề:** Demo thuật toán Chữ ký số RSA  
> **Công nghệ:** Python 3.10+ · PyQt6 · hashlib · python-docx

Ứng dụng mô phỏng trực quan quá trình trao đổi khóa, ký số và xác thực chữ ký RSA theo giao diện 2 cột (Người gửi – Người nhận).

---

## ⚡ Chạy nhanh (sau khi pull về)

```bash
# 1. Di chuyển vào thư mục ứng dụng
cd rsa_app

# 2. Tạo môi trường ảo
python3 -m venv .venv

# 3. Kích hoạt môi trường ảo
source .venv/bin/activate

# 4. Cài đặt thư viện
pip install -r requirements.txt

# 5. Chạy ứng dụng
python3 main.py
```

> ✅ Từ lần sau, chỉ cần kích hoạt lại venv rồi chạy:
> ```bash
> cd rsa_app && source .venv/bin/activate && python3 main.py
> ```

---

## 📁 Cấu trúc dự án

```
atbmtt/
├── README.md
└── rsa_app/
    ├── main.py                  # Điểm khởi động ứng dụng
    ├── requirements.txt         # Danh sách thư viện cần cài
    ├── core/
    │   └── rsa_engine.py        # Lõi thuật toán RSA (tự implement)
    ├── utils/
    │   └── file_manager.py      # Lưu/đọc file .txt và .docx
    └── ui/
        └── main_window.py       # Giao diện 2 cột chính
```

---

## 🔧 Hướng dẫn sử dụng

### 👤 Cột Trái – Người gửi (Khóa bí mật)

1. **Sinh khóa:**
   - Tự nhập `P`, `Q`, `E` rồi bấm **"Xác nhận"**, hoặc
   - Bấm **"Sinh khóa tự động"** để tạo bộ khóa 512-bit an toàn.  
     → Hệ thống tự tính `N`, `Phi(N)` và khóa bí mật `d`.

2. **Ký số:**
   - Nhập nội dung vào ô **"Văn bản gốc cần gửi"**.
   - Chọn thuật toán băm (SHA-256, MD5, ...).
   - Bấm **"Ký số (Mã hóa)"** → hiển thị **Mã băm H(M)** và **Chữ ký S**.

3. **Truyền tin:**
   - Bấm **"Chuyển tiếp ➔"** để gửi văn bản, chữ ký và khóa công khai sang cột Người nhận.
   - Hoặc chọn **"Lưu file"** để xuất ra `.txt` / `.docx`.

### 👥 Cột Phải – Người nhận (Khóa công khai)

1. Bấm **"Nhận khóa"** nếu nhập thủ công `N` và `E` (bỏ qua nếu đã dùng Chuyển tiếp).
2. **Xác thực chữ ký:**
   - Bấm **"Kiểm tra chữ ký"**.
   - Kết quả: ✅ **Hợp lệ (xanh)** hoặc ❌ **Không hợp lệ (đỏ)**.
3. **Giả lập tấn công:**
   - Bấm **"⚠️ Giả lập sửa đổi"** → ứng dụng thay đổi 1 ký tự trong văn bản.
   - Kiểm tra lại sẽ thấy mã băm lệch nhau → chứng minh tính toàn vẹn của chữ ký số.

---

## 📐 Tóm tắt thuật toán RSA

```
SINH KHÓA:
  1. Chọn 2 số nguyên tố: p, q
  2. N = p × q
  3. φ(N) = (p−1) × (q−1)
  4. Chọn E sao cho gcd(E, φ(N)) = 1
  5. d = E⁻¹ mod φ(N)
  → Khóa công khai: (E, N)
  → Khóa bí mật:   (d, N)

KÝ SỐ (Người gửi):
  H = Hash(M)       ← Băm thông điệp gốc
  S = H^d mod N     ← Ký bằng khóa bí mật

XÁC MINH (Người nhận):
  H' = S^E mod N    ← Giải mã chữ ký bằng khóa công khai
  H  = Hash(M')     ← Băm lại văn bản nhận được
  H' == H  →  Hợp lệ ✅
```
