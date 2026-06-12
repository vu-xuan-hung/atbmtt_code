
## ⚙️ Cài đặt & Chạy ứng dụng

Trên các hệ điều hành Linux (như Ubuntu), Python yêu cầu sử dụng môi trường ảo (virtual environment) để cài đặt thư viện. Hãy làm theo các bước sau:

### 1. Tạo môi trường ảo (Virtual Environment)


```bash
cd atbmtt
cd rsa_app
python -m venv .venv
```

### 2. Kích hoạt môi trường ảo và cài thư viện
```bash
# Kích hoạt môi trường ảo
.venv\Scripts\activate
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 3. Khởi động ứng dụng

```bash
python main.py
```

---

## 🔧 Hướng dẫn sử dụng

Giao diện được chia làm 2 phần mô phỏng quá trình truyền tin:

### 👤 Cột Trái: Người gửi (Khóa bí mật)
1. **Sinh khóa:** 
   - Bạn có thể tự nhập số nguyên tố `P`, `Q` và số `E` rồi bấm **"Xác nhận"**.
   - Hoặc bấm **"Sinh khóa tự động"** để ứng dụng tự tạo bộ khóa an toàn (512-bit). Lúc này Số `N`, `Phi(N)` và `dₐ` (Khóa bí mật) sẽ được tính toán tự động.
2. **Ký số văn bản:**
   - Nhập nội dung vào ô **"Văn bản gốc cần gửi"**.
   - Chọn thuật toán băm (SHA-256, MD5...).
   - Bấm **"Ký số (Mã hóa)"**. Ứng dụng sẽ hiển thị **Mã Băm H(M)** và **Chữ ký S**.
3. **Truyền tin:**
   - Bấm **"Chuyển tiếp ➔"** để gửi văn bản, chữ ký và khóa công khai sang cột Người nhận.
   - Bạn cũng có thể chọn **"Lưu file"** để lưu chữ ký ra định dạng `.txt` hoặc `.docx`.

### 👥 Cột Phải: Người nhận (Khóa công khai)
1. Bấm **"Nhận khóa"** nếu bạn tự nhập thủ công `N` và `E`. (Nếu dùng nút Chuyển tiếp, bước này đã tự động hoàn tất).
2. **Xác thực chữ ký:**
   - Bấm **"Kiểm tra chữ ký"**. 
   - Ứng dụng sẽ tính toán lại mã băm từ văn bản nhận được và so sánh với mã băm giải mã từ chữ ký số. 
   - Kết quả sẽ báo **Hợp lệ (Màu xanh)** hoặc **Không hợp lệ (Màu đỏ)**.
3. **Giả lập tấn công:**
   - Bấm nút **"⚠️ Giả lập sửa đổi"**, ứng dụng sẽ cố tình thay đổi 1 ký tự trong văn bản nhận được. 
   - Bấm kiểm tra lại, bạn sẽ thấy mã băm lệch nhau hoàn toàn, mô phỏng việc kẻ tấn công sửa đổi nội dung trên đường truyền.

---

## 🔄 Workflow & Dataflow

### Workflow tổng quan

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NGƯỜI GỬI (Sender)                          │
│                                                                     │
│  [Chọn p, q, e]                                                     │
│       │                                                             │
│       ▼                                                             │
│  Tính n = p×q,  φ(n) = (p−1)(q−1),  d = e⁻¹ mod φ(n)             │
│       │                                                             │
│       ├──── Khóa công khai (e, n) ────► Gửi cho Người nhận         │
│       │                                 (kênh công khai)            │
│       │                                                             │
│  [Soạn thông điệp M]                                                │
│       │                                                             │
│       ▼                                                             │
│  H = Hash(M)          ← Băm thông điệp                             │
│       │                                                             │
│       ▼                                                             │
│  S = H^d mod n        ← Ký bằng khóa bí mật d                     │
│       │                                                             │
│       └──── (M, S) ──────────────────► Gửi cho Người nhận          │
│                                         (kênh truyền thông)         │
└─────────────────────────────────────────────────────────────────────┘
                               │
                     Kênh truyền thông
                (có thể bị nghe lén / sửa đổi)
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                        NGƯỜI NHẬN (Receiver)                        │
│                                                                     │
│  Nhận: (M', S) và khóa công khai (e, n)                            │
│       │                                                             │
│       ▼                                                             │
│  H' = S^e mod n       ← Giải mã chữ ký bằng khóa công khai         │
│       │                                                             │
│       ▼                                                             │
│  H  = Hash(M')        ← Băm lại văn bản nhận được                  │
│       │                                                             │
│       ▼                                                             │
│  H' == H ?                                                          │
│    ├── ✅ KHỚP    → Văn bản nguyên vẹn, chữ ký hợp lệ             │
│    └── ❌ LỆCH    → Văn bản đã bị sửa đổi HOẶC chữ ký giả mạo     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Dataflow chi tiết (trong ứng dụng)

```
User Input (p, q, e)
        │
        ▼
┌──────────────────────┐
│   generate_rsa_keys  │  rsa_engine.py
│                      │
│  1. is_prime(p, q)   │  ← Miller-Rabin (k=20 vòng)
│  2. n = p * q        │
│  3. φ(n) = (p−1)(q−1)│
│  4. gcd(e, φ(n)) = 1 │  ← Kiểm tra bằng Euclid
│  5. d = e⁻¹ mod φ(n) │  ← Extended Euclidean Algorithm
└──────────┬───────────┘
           │
     RSAKeyPair(pub, priv)
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
 (e, n)        (d, n)
Pub Key       Priv Key
    │             │
    │       ┌─────┴──────────────────┐
    │       │     sign_message()     │
    │       │                        │
    │       │  H_hex = Hash(M)       │  ← hashlib.md5 / sha256...
    │       │  H_int = int(H_hex,16) │
    │       │  H_int = H_int % n     │  ← Đảm bảo H < n
    │       │  S = H_int^d mod n     │  ← power_mod() – O(log d)
    │       │  S_hex = hex(S)        │
    │       └─────┬──────────────────┘
    │             │
    │           (M, S_hex)
    │             │
    └──────┐      │
           ▼      ▼
    ┌─────────────────────────────┐
    │     verify_signature()      │
    │                             │
    │  S_int = int(S_hex, 16)     │
    │  H'_int = S_int^e mod n     │  ← Giải mã chữ ký
    │  H'_hex = hex(H'_int)       │
    │                             │
    │  H_hex  = Hash(M')          │  ← Băm văn bản nhận được
    │  H_int  = int(H_hex,16) % n │
    │  H_hex_mod = hex(H_int)     │
    │                             │
    │  H'_hex == H_hex_mod ?      │
    │    ✅ True  → Hợp lệ        │
    │    ❌ False → Không hợp lệ  │
    └─────────────────────────────┘
```

---

## 📐 Thuật toán RSA — Chi tiết kỹ thuật

Toàn bộ RSA được **tự implement từ đầu** trong `rsa_engine.py`, không dùng thư viện mã hóa bên ngoài.

### 1. Các thành phần cốt lõi

| Thành phần | Hàm | Mô tả |
|---|---|---|
| Kiểm tra số nguyên tố | `is_prime(n, k=20)` | Miller-Rabin probabilistic test |
| Sinh số nguyên tố | `generate_prime(bits)` | Sinh ngẫu nhiên, kiểm tra đến khi pass |
| Nghịch đảo modular | `mod_inverse(e, φ)` | Extended Euclidean Algorithm |
| Lũy thừa modular | `power_mod(base, exp, mod)` | Fast exponentiation — O(log exp) |
| Ký số | `sign_message(M, priv)` | S = Hash(M)^d mod n |
| Xác minh | `verify_signature(M, S, pub)` | H' = S^e mod n; kiểm tra H' == Hash(M) |

### 2. Các công thức toán học

```
SINH KHÓA:
  p, q  → hai số nguyên tố lớn (Miller-Rabin)
  n     = p × q                        (modulus)
  φ(n)  = (p−1) × (q−1)               (Euler's totient)
  e     = 65537  [nếu gcd(e,φ(n))=1]  (public exponent)
  d     = e⁻¹ mod φ(n)                (private exponent)

  Khóa công khai  : (e, n)
  Khóa bí mật    : (d, n)

KÝ SỐ (Người gửi):
  H = Hash(M)            ← MD5 / SHA-256 / SHA-512
  H = H mod n            ← Đảm bảo H < n
  S = H^d mod n          ← Chữ ký số

XÁC MINH (Người nhận):
  H' = S^e mod n         ← Giải mã chữ ký
  H  = Hash(M') mod n    ← Băm văn bản nhận được
  H' == H  →  ✅ Hợp lệ
  H' ≠  H  →  ❌ Không hợp lệ
```

---

## 🛡️ Chứng minh tính bảo mật

### 1. Tính xác thực (Authentication)

Chữ ký `S = H^d mod n` chỉ có thể được tạo ra bởi người **nắm khóa bí mật `d`**.  
Bất kỳ ai cũng có thể xác minh bằng khóa công khai `(e, n)`:

```
S^e mod n = (H^d)^e mod n = H^(d×e) mod n = H mod n  ✅
```

Điều này đúng nhờ định lý Euler: `H^(e×d) ≡ H (mod n)` khi `e×d ≡ 1 (mod φ(n))`.

### 2. Tính toàn vẹn (Integrity)

Nếu văn bản bị sửa đổi từ `M` thành `M'`:

```
Hash(M') ≠ Hash(M)   (tính kháng xung đột của hàm băm)
     ↓
S^e mod n ≠ Hash(M') mod n
     ↓
❌ Xác thực THẤT BẠI — phát hiện giả mạo
```

Ứng dụng minh họa điều này qua nút **"Giả lập sửa đổi"**.

### 3. Tính không thể phủ nhận (Non-repudiation)

Người gửi **không thể phủ nhận** việc đã ký, vì:
- Chữ ký `S` chỉ có thể được tạo bởi `d` (khóa bí mật — chỉ người gửi biết).
- Bất kỳ bên thứ ba nào cũng xác minh được `S` bằng khóa công khai `(e, n)`.

### 4. Độ khó phá khóa — Bài toán IFP

Bảo mật của RSA dựa trên **Integer Factorization Problem (IFP)**:

> Cho `n = p × q`, rất khó để tìm lại `p` và `q` khi `n` đủ lớn.
'git
