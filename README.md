# 🔐 RSA Digital Signature — Demo App

> **Môn:** An toàn và Bảo mật Thông tin &nbsp;|&nbsp; **Stack:** Python 3.10 · PyQt6 · hashlib

Ứng dụng mô phỏng trực quan toàn bộ quy trình **ký số và xác thực RSA** — từ sinh khóa, ký thông điệp, đến phát hiện giả mạo — qua giao diện 2 cột (Người gửi ↔ Người nhận).

---

## 🚀 Chạy nhanh

### ✅ Cách duy nhất cần nhớ — Docker Compose (1 lệnh)

> Yêu cầu: cài [Docker Desktop](https://www.docker.com/products/docker-desktop/). Không cần Python, không cần Qt.

```bash
docker compose up
```

Mở trình duyệt → **[http://localhost:8080](http://localhost:8080)** → nhấn **Connect** ✅

> Lần đầu build mất ~15 phút (tải thư viện hệ thống). Lần sau chỉ mất vài giây nhờ Docker cache.

**Dừng:**
```bash
docker compose down
```

---

### Cách khác — Python trực tiếp

> Yêu cầu: [Python 3.10+](https://www.python.org/downloads/) — **Windows phải tích "Add to PATH"** khi cài.

**Windows (Command Prompt / PowerShell):**
```bat
cd rsa_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Linux / macOS (Terminal):**
```bash
cd rsa_app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

> ⚠️ PyQt6 trên Windows yêu cầu **Visual C++ Redistributable** (thường đã có sẵn). Nếu lỗi, tải tại [aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

## 📁 Cấu trúc dự án

```
atbmtt/
├── Dockerfile              # Build image: Xvfb + noVNC + PyQt6
├── entrypoint.sh           # Khởi động VNC stack + ứng dụng
├── .dockerignore
├── README.md
└── rsa_app/
    ├── main.py             # Entry point
    ├── requirements.txt
    ├── core/
    │   └── rsa_engine.py   # Toàn bộ RSA tự implement từ đầu
    ├── utils/
    │   └── file_manager.py # Đọc/ghi .txt và .docx
    └── ui/
        └── main_window.py  # Giao diện PyQt6 — layout 2 cột
```

---

## 🖥️ Hướng dẫn sử dụng

### 👤 Cột trái — Người gửi

| Bước | Thao tác |
|------|----------|
| **1. Sinh khóa** | Nhấn **"Sinh khóa tự động"**, chọn số bit (512 bit cho demo nhanh). Hệ thống tính `p, q, n, e, d`. |
| **2. Nhập văn bản** | Gõ trực tiếp hoặc nhấn **📂 Thêm file** để mở `.txt`/`.docx`. |
| **3. Ký số** | Nhấn **"Ký số (Mã hóa)"** → hiện **Mã băm H(M)** và **Chữ ký số S**. |
| **4. Lưu** | Nhấn **💾 Lưu chữ ký** để xuất file `.txt`. |

### 👥 Cột phải — Người nhận

| Bước | Thao tác |
|------|----------|
| **5. Nhận khóa** | Nhấn **"Nhận khóa"** để lấy `(N, E)` từ cột trái, hoặc nhập thủ công. |
| **6. Tải dữ liệu** | Nhấn **📂 Mở file chữ ký** và **📂 Mở file văn bản**. |
| **7. Xác thực** | Nhấn **"Kiểm tra chữ ký"** → ✅ Hợp lệ (xanh) hoặc ❌ Không hợp lệ (đỏ). |
| **8. Giả lập tấn công** | Nhấn **"Giả lập sửa đổi"** → thay 1 ký tự ngẫu nhiên → kiểm tra lại → bị phát hiện ngay. |

---

## 🔄 Workflow & Dataflow

```
NGƯỜI GỬI                              NGƯỜI NHẬN
─────────────────────────────────────────────────────────
[p, q, e]
    │
    ▼
n = p×q,  φ(n) = (p−1)(q−1)
d = e⁻¹ mod φ(n)
    │
    ├── (e, n) ──────────────────────► nhận khóa công khai
    │    [kênh công khai]
    │
[Thông điệp M]
    │
    ▼
H   = Hash(M)          ← băm
S   = H^d mod n        ← ký bằng khóa bí mật
    │
    └── (M, S) ─────────────────────► nhận thông điệp + chữ ký
         [kênh truyền thông]              │
                                          ▼
                                     H'  = S^e mod n   ← giải mã chữ ký
                                     H   = Hash(M')    ← băm lại
                                          │
                                     H' == H ?
                                       ✅ Khớp   → Hợp lệ
                                       ❌ Lệch   → Bị giả mạo
```

---

## 📐 Thuật toán RSA

Toàn bộ được **tự implement** trong `rsa_engine.py` — không dùng thư viện mã hóa bên ngoài.

```
SINH KHÓA:
  p, q  → số nguyên tố ngẫu nhiên (kiểm tra bằng Miller-Rabin)
  n     = p × q
  φ(n)  = (p−1) × (q−1)
  e     = 65537            [gcd(e, φ(n)) = 1]
  d     = e⁻¹ mod φ(n)    [Extended Euclidean Algorithm]

  Khóa công khai  :  (e, n)
  Khóa bí mật    :  (d, n)

KÝ SỐ:
  H = Hash(M) mod n
  S = H^d mod n            [fast modular exponentiation]

XÁC MINH:
  H' = S^e mod n
  H  = Hash(M') mod n
  H' == H  →  ✅ Hợp lệ
```

---

## 🛡️ Tính bảo mật

| Tính chất | Cơ chế |
|-----------|--------|
| **Xác thực** | Chỉ người có `d` mới tạo được `S = H^d mod n` hợp lệ |
| **Toàn vẹn** | Sửa 1 ký tự → `Hash(M') ≠ Hash(M)` → xác thực thất bại ngay |
| **Không phủ nhận** | Chữ ký gắn với `d` duy nhất; bên thứ 3 xác minh được bằng `(e, n)` công khai |
| **Độ khó phá** | Dựa trên bài toán phân tích thừa số nguyên tố (IFP) — khả thi với 2048-bit+ |

> ⚠️ App này phục vụ **mục đích giáo dục**. Production nên dùng thư viện chuẩn như `cryptography` hoặc OpenSSL.
