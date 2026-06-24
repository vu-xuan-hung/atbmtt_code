"""
main_window.py
==============
Giao diện chính – theo layout 2 cột đơn giản nhưng bổ sung chi tiết:
  - Hiển thị N, Phi(N) khi sinh khóa.
  - Tùy chọn hàm băm (Hash) & hiển thị mã băm.
  - Nút giả lập tấn công sửa đổi văn bản.
  - Hiển thị chi tiết mã băm giải mã từ chữ ký vs băm từ văn bản.
"""

import sys, os, random
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QFileDialog, QMessageBox, QFrame, QApplication, QGroupBox,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QDialogButtonBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QTimer

from rsa_app.core import (
    generate_rsa_keys, sign_message, verify_signature,
    HASH_ALGORITHMS
)
from rsa_app.utils import save_signature_file, read_file
from rsa_app.utils.file_manager import read_signature_csv, read_sig, PANDAS_AVAILABLE


STYLE = """
QMainWindow, QWidget {
    background-color: #f4f4f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #222222;
}
QLabel {
    font-size: 13px;
    color: #222222;
}
QLabel#header {
    font-size: 15px;
    font-weight: bold;
    color: #222222;
}
QLabel#subheader {
    font-size: 13px;
    font-weight: bold;
    color: #333333;
    margin-top: 4px;
}
QLineEdit {
    background: #ffffff;
    border: 1px solid #aaaaaa;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 13px;
}
QTextEdit {
    background: #ffffff;
    border: 1px solid #aaaaaa;
    border-radius: 3px;
    padding: 4px;
    font-size: 12px;
    font-family: Consolas, monospace;
}
QPushButton {
    background-color: #e07060;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}
QPushButton:hover { background-color: #cc5a4a; }
QPushButton:pressed { background-color: #b84a3a; }
QPushButton:disabled { background-color: #e8b8b0; color: #aaaaaa; }
QComboBox {
    background: #ffffff;
    border: 1px solid #aaaaaa;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 13px;
    min-height: 28px;
}
QComboBox::drop-down { border: none; }
QFrame#divider { color: #cccccc; background: #cccccc; }
"""


class KeyGenWorker(QThread):
    done  = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, bits=512):
        super().__init__()
        self.bits = bits

    def run(self):
        try:
            self.done.emit(generate_rsa_keys(self.bits))
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chữ ký số RSA - Chi tiết")
        self.setMinimumSize(1200, 720)
        self.resize(1280, 780)
        self.setStyleSheet(STYLE)

        self._key_pair   = None
        self._sign_data  = {}
        self._worker     = None

        self._build_ui()
        self._center()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main_row = QHBoxLayout(root)
        main_row.setContentsMargins(18, 14, 18, 14)
        main_row.setSpacing(0)

        main_row.addLayout(self._build_left(), stretch=1)
        
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedWidth(1)
        main_row.addWidget(div)
        main_row.addSpacing(18)
        
        main_row.addLayout(self._build_right(), stretch=1)

    # ── Cột trái: Người gửi ───────────────────────────────────
    def _build_left(self):
        lay = QVBoxLayout()
        lay.setSpacing(8)

        # --- Khu vực Tạo Khóa (Group Box) ---
        group_key = QGroupBox("Tạo Khóa")
        group_key.setStyleSheet("""
            QGroupBox {
                background-color: #e8e9eb;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        lay_key = QVBoxLayout()
        lay_key.setSpacing(0)
        lay_key.setContentsMargins(10, 15, 10, 10)

        sub_pub = QLabel("Khóa công khai (n,e)")
        sub_pub.setStyleSheet("font-weight: bold; color: #333;")
        lay_key.addWidget(sub_pub)
        lay_key.addSpacing(4)

        lay_pub_fields = QVBoxLayout()
        lay_pub_fields.setSpacing(2)
        lay_pub_fields.setContentsMargins(20, 0, 15, 0) # Thụt lề trái 20px, phải 15px

        lay_pub_fields.addWidget(QLabel("Số nguyên tố p:"))
        self.inp_p = QLineEdit()
        self.inp_p.setStyleSheet("font-family: Consolas; font-size: 12px;")
        lay_pub_fields.addWidget(self.inp_p)
        lay_pub_fields.addSpacing(6)

        lay_pub_fields.addWidget(QLabel("Số nguyên tố q:"))
        self.inp_q = QLineEdit()
        self.inp_q.setStyleSheet("font-family: Consolas; font-size: 12px;")
        lay_pub_fields.addWidget(self.inp_q)
        lay_pub_fields.addSpacing(6)

        lay_pub_fields.addWidget(QLabel("Số e:"))
        self.inp_e = QLineEdit()
        self.inp_e.setStyleSheet("font-family: Consolas; font-size: 12px;")
        lay_pub_fields.addWidget(self.inp_e)
        lay_pub_fields.addSpacing(6)

        lay_pub_fields.addWidget(QLabel("Số n:"))
        self.inp_n = QLineEdit()
        self.inp_n.setReadOnly(True)
        self.inp_n.setStyleSheet("background:#fcfcfc; color:#555; font-family: Consolas; font-size: 12px;")
        lay_pub_fields.addWidget(self.inp_n)
        
        lay_key.addLayout(lay_pub_fields)

        self.inp_phi = QLineEdit()
        self.inp_phi.setVisible(False)

        lay_key.addSpacing(10)
        
        sub_priv = QLabel("Khóa bí mật (n,d)")
        sub_priv.setStyleSheet("font-weight: bold; color: #333;")
        lay_key.addWidget(sub_priv)
        lay_key.addSpacing(4)

        lay_priv_fields = QVBoxLayout()
        lay_priv_fields.setSpacing(2)
        lay_priv_fields.setContentsMargins(20, 0, 15, 0)

        lay_priv_fields.addWidget(QLabel("Số d:"))
        self.inp_d = QLineEdit()
        self.inp_d.setReadOnly(True)
        self.inp_d.setStyleSheet("background:#fcfcfc; color:#555; font-family: Consolas; font-size: 12px;")
        lay_priv_fields.addWidget(self.inp_d)

        lay_key.addLayout(lay_priv_fields)

        lay_key.addSpacing(12)
        
        row_btn = QHBoxLayout()
        self.btn_gen = QPushButton("Sinh khóa tự động")
        self.btn_gen.clicked.connect(self._on_auto_gen)
        row_btn.addWidget(self.btn_gen)
        
        self.combo_bits = QComboBox()
        self.combo_bits.addItems(["64", "128", "256", "512", "1024", "2048"])
        self.combo_bits.setCurrentText("512")
        row_btn.addWidget(self.combo_bits)
        row_btn.addWidget(QLabel("bits"))


        row_btn.addStretch()
        lay_key.addLayout(row_btn)
        
        group_key.setLayout(lay_key)
        lay.addWidget(group_key)
        
        lay.addSpacing(5)

        lay.addSpacing(10)

        lbl_msg = QLabel("Văn bản gốc cần gửi:")
        lay.addWidget(lbl_msg)
        self.txt_message = QTextEdit()
        self.txt_message.setPlaceholderText("Nhập thông điệp cần ký vào đây...")
        self.txt_message.setFixedHeight(70)
        lay.addWidget(self.txt_message)

        # Hash và Nút Mã hóa
        row_mh = QHBoxLayout()
        row_mh.addWidget(QLabel("Hàm Băm:"))
        self.combo_hash = QComboBox()
        self.combo_hash.addItems(["MD5"])
        self.combo_hash.setCurrentText("MD5")
        row_mh.addWidget(self.combo_hash)
        row_mh.addStretch()
        self.btn_load_file_sign = QPushButton("📂 Thêm file")
        self.btn_load_file_sign.setObjectName("btnGray")
        # [PDF] Khi bat ho tro PDF, doi tooltip thanh: "Mo file (.txt, .docx, .pdf) de ky so"
        self.btn_load_file_sign.setToolTip("Mở file (.txt, .docx) để ký số")
        self.btn_load_file_sign.clicked.connect(self._on_load_file_to_sign)
        row_mh.addWidget(self.btn_load_file_sign)
        row_mh.addSpacing(6)
        self.btn_maHoa = QPushButton("Ký số (Mã hóa)")
        self.btn_maHoa.setEnabled(False)
        self.btn_maHoa.clicked.connect(self._on_sign)
        row_mh.addWidget(self.btn_maHoa)
        lay.addLayout(row_mh)

        lbl_hash = QLabel("Mã Băm H")
        lay.addWidget(lbl_hash)
        self.txt_hash = QLineEdit()
        self.txt_hash.setReadOnly(True)
        self.txt_hash.setPlaceholderText("(Mã băm của văn bản trước khi mã hóa)")
        self.txt_hash.setStyleSheet("background:#eeeeee; color:#555;")
        lay.addWidget(self.txt_hash)

        lbl_enc = QLabel("Chữ ký số")
        lay.addWidget(lbl_enc)
        self.txt_signature = QTextEdit()
        self.txt_signature.setReadOnly(True)
        self.txt_signature.setPlaceholderText("(Chữ ký số sẽ hiển thị ở đây)")
        self.txt_signature.setFixedHeight(70)
        lay.addWidget(self.txt_signature)

        row_bottom = QHBoxLayout()
        row_bottom.addStretch()
        self.btn_save_sig = QPushButton("💾 Lưu chữ ký (.sig)")
        self.btn_save_sig.setObjectName("btnGray")
        self.btn_save_sig.setEnabled(False)
        self.btn_save_sig.setToolTip("Lưu toàn bộ thông tin chữ ký ra file .sig (JSON – chuẩn cryptography)")
        self.btn_save_sig.clicked.connect(self._on_save_sig)
        row_bottom.addWidget(self.btn_save_sig)
        lay.addLayout(row_bottom)
        
        lay.addStretch()
        return lay

    # ── Cột phải: Người nhận ──────────────────────────────────
    def _build_right(self):
        lay = QVBoxLayout()
        lay.setSpacing(8)
        lay.addSpacing(2)

        hdr = QLabel("Khóa công khai (Người nhận)")
        hdr.setObjectName("header")
        lay.addWidget(hdr)

        row_n = QHBoxLayout()
        row_n.addWidget(QLabel("Số N "))
        self.inp_recv_n = QLineEdit()
        self.inp_recv_n.setPlaceholderText("Nhập số N từ người gửi...")
        row_n.addWidget(self.inp_recv_n)
        lay.addLayout(row_n)

        row_da = QHBoxLayout()
        row_da.addWidget(QLabel("Số E"))
        self.inp_recv_e = QLineEdit()
        self.inp_recv_e.setPlaceholderText("Nhập số E từ người gửi...")
        row_da.addWidget(self.inp_recv_e)
        lay.addLayout(row_da)

        row_nhank = QHBoxLayout()
        row_nhank.addStretch()
        self.btn_recv_key = QPushButton("Nhận khóa")
        self.btn_recv_key.clicked.connect(self._on_recv_key)
        row_nhank.addWidget(self.btn_recv_key)
        lay.addLayout(row_nhank)
        
        lay.addSpacing(10)

        row_sig_hdr = QHBoxLayout()
        row_sig_hdr.addWidget(QLabel("Chữ ký nhận được"))
        row_sig_hdr.addStretch()
        self.btn_load_sig_file = QPushButton("📂 Mở file chữ ký")
        self.btn_load_sig_file.setObjectName("btnGray")
        self.btn_load_sig_file.setToolTip("Mở file chữ ký số (.sig, .csv, .txt, .docx)")
        self.btn_load_sig_file.clicked.connect(self._on_load_sig_file)
        row_sig_hdr.addWidget(self.btn_load_sig_file)
        lay.addLayout(row_sig_hdr)

        self.txt_recv_sig = QTextEdit()
        self.txt_recv_sig.setReadOnly(False)
        self.txt_recv_sig.setPlaceholderText("(Chữ ký số từ người gửi – mở file hoặc nhập trực tiếp)")
        self.txt_recv_sig.setFixedHeight(70)
        lay.addWidget(self.txt_recv_sig)

        row_mof = QHBoxLayout()
        row_mof.addWidget(QLabel("Văn bản nhận được"))
        row_mof.addStretch()

        self.btn_tamper = QPushButton("Giả lập sửa đổi")
        self.btn_tamper.setObjectName("btnWarning")
        self.btn_tamper.setEnabled(False)
        self.btn_tamper.setToolTip("Thay đổi 1 ký tự ngẫu nhiên trong văn bản để xem kết quả kiểm tra")
        self.btn_tamper.clicked.connect(self._on_tamper)
        row_mof.addWidget(self.btn_tamper)
        row_mof.addSpacing(6)

        self.btn_load_msg_file = QPushButton("📂 Mở file văn bản")
        self.btn_load_msg_file.setObjectName("btnGray")
        # [PDF] Khi bat ho tro PDF, doi tooltip thanh: "Mo file van ban nhan duoc (.txt, .docx, .pdf)"
        self.btn_load_msg_file.setToolTip("Mở file văn bản nhận được (.txt, .docx)")
        self.btn_load_msg_file.clicked.connect(self._on_load_msg_file)
        row_mof.addWidget(self.btn_load_msg_file)
        lay.addLayout(row_mof)

        self.txt_recv_msg = QTextEdit()
        self.txt_recv_msg.setReadOnly(False)
        self.txt_recv_msg.setPlaceholderText("(Thông điệp nhận được – có thể chỉnh sửa để giả lập tấn công)")
        self.txt_recv_msg.setFixedHeight(70)
        self.txt_recv_msg.textChanged.connect(lambda: self.lbl_verify_result.clear())
        lay.addWidget(self.txt_recv_msg)

        row_vhash = QHBoxLayout()
        row_vhash.addWidget(QLabel("Hàm Băm:"))
        self.combo_recv_hash = QComboBox()
        self.combo_recv_hash.addItems(["MD5"])
        self.combo_recv_hash.setCurrentText("MD5")
        row_vhash.addWidget(self.combo_recv_hash)
        row_vhash.addStretch()
        self.btn_verify = QPushButton("Kiểm tra chữ ký")
        self.btn_verify.setEnabled(False)
        self.btn_verify.clicked.connect(self._on_verify)
        row_vhash.addWidget(self.btn_verify)
        lay.addLayout(row_vhash)

        lbl_details = QLabel("Chi tiết kiểm tra nội dung:")
        lay.addWidget(lbl_details)
        self.txt_verify_details = QTextEdit()
        self.txt_verify_details.setReadOnly(True)
        self.txt_verify_details.setStyleSheet("background:#eeeeee; font-size:11px;")
        self.txt_verify_details.setPlaceholderText("(Kết quả tính toán mã băm sẽ hiển thị ở đây...)")
        self.txt_verify_details.setFixedHeight(65)
        lay.addWidget(self.txt_verify_details)

        self.lbl_verify_result = QLabel("")
        self.lbl_verify_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_verify_result.setFixedHeight(28)
        lay.addWidget(self.lbl_verify_result)

        lay.addStretch()
        return lay

    # ──────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────
    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)

    def _alert(self, title, msg, icon=QMessageBox.Icon.Warning):
        mb = QMessageBox(self)
        mb.setWindowTitle(title)
        mb.setText(msg)
        mb.setIcon(icon)
        mb.exec()

    # ──────────────────────────────────────────────────────────
    #  Slots
    # ──────────────────────────────────────────────────────────
    @pyqtSlot()
    def _on_auto_gen(self):
        bits = int(self.combo_bits.currentText())
        self.btn_gen.setEnabled(False)
        self.btn_gen.setText("Đang sinh khóa...")
        self._worker = KeyGenWorker(bits=bits)
        self._worker.done.connect(self._on_keys_done)
        self._worker.error.connect(self._on_keys_error)
        self._worker.start()

    @pyqtSlot(object)
    def _on_keys_done(self, kp):
        self._key_pair = kp
        self.inp_p.setText(str(kp.p))
        self.inp_q.setText(str(kp.q))
        self.inp_e.setText(str(kp.public_key.e))
        self.inp_d.setText(str(kp.private_key.d))
        self.inp_n.setText(str(kp.public_key.n))
        self.inp_phi.setText(str(kp.phi_n))
        self.btn_gen.setEnabled(True)
        self.btn_gen.setText("Sinh khóa tự động")
        self.btn_maHoa.setEnabled(True)
    @pyqtSlot(str)
    def _on_keys_error(self, msg):
        self.btn_gen.setEnabled(True)
        self.btn_gen.setText("Sinh khóa tự động")
        self._alert("Lỗi", f"Không thể sinh khóa:\n{msg}")

    @pyqtSlot()
    def _on_load_file_to_sign(self):
        """Mo file .txt hoac .docx de dua noi dung vao o van ban ky so.
        Nguoi dung can bam 'Ky so (Ma hoa)' de thuc hien ky – khong tu dong ky.
        """
        fp, _ = QFileDialog.getOpenFileName(
            self, "Chọn file cần ký", "",
            "Supported Files (*.txt *.docx *.pdf);;Text (*.txt);;Word (*.docx);;PDF (*.pdf)"
        )
        if not fp:
            return
        try:
            content = read_file(fp)
            self.txt_message.setPlainText(content)
            # Khong tu dong ky – nguoi dung phai bam "Ky so (Ma hoa)" thu cong
        except Exception as ex:
            self._alert("Lỗi mở file", str(ex))

    @pyqtSlot()
    def _on_sign(self):
        msg = self.txt_message.toPlainText().strip()
        if not msg:
            self._alert("Thiếu thông điệp", "Vui lòng nhập thông điệp cần ký."); return
        if self._key_pair is None:
            self._alert("Chưa có khóa", "Vui lòng sinh khóa trước."); return

        algo = self.combo_hash.currentText()
        try:
            h_hex, sig_hex, _ = sign_message(msg, self._key_pair.private_key, algo)
        except Exception as ex:
            self._alert("Lỗi ký", str(ex)); return

        self.txt_hash.setText(h_hex)
        self.txt_signature.setPlainText(sig_hex)
        self._sign_data = {
            "message": msg,
            "hash_algorithm": algo,
            "hash_hex": h_hex,
            "signature_hex": sig_hex,
            "public_key_e": self._key_pair.public_key.e,
            "public_key_n": self._key_pair.public_key.n,
            "private_key_d": self._key_pair.private_key.d,
        }

        # Cập nhật trạng thái nút lưu
        self.btn_save_sig.setEnabled(True)


    @pyqtSlot()
    def _on_save_sig(self):
        """Luu toan bo thong tin chu ky ra file .sig (JSON – chuan cryptography)."""
        if not self._sign_data:
            self._alert("Chưa có chữ ký", "Vui lòng ký số trước khi lưu.")
            return
        fp, selected_filter = QFileDialog.getSaveFileName(
            self, "Lưu chữ ký số", "chu_ky.sig",
            "Signature files (*.sig);;CSV – DataFrame (*.csv);;Text files (*.txt);;PDF files (*.pdf)"
        )
        if not fp: return
        # Tự động thêm đuôi .sig nếu thiếu
        if not any(fp.endswith(ext) for ext in (".sig", ".csv", ".txt", ".pdf")):
            fp += ".sig"
        try:
            save_signature_file(fp, self._sign_data)
            fmt_note = {
                ".sig": "Định dạng: SIG / JSON (chuẩn cryptography, có đầy đủ metadata)",
                ".csv": "Định dạng: CSV (mỗi lần ký sẽ thêm 1 dòng mới vào file)",
            }.get(fp[fp.rfind("."):], "")
            QMessageBox.information(self, "Thành công",
                f"Đã lưu chữ ký số ra file:\n{fp}\n\n{fmt_note}"
            )
        except Exception as ex:
            self._alert("Lỗi lưu file", str(ex))

    @pyqtSlot()
    def _on_recv_key(self):
        """Tự động lấy khóa công khai (N, e) từ cặp khóa đã sinh bên trái."""
        if self._key_pair is None:
            self._alert("Chưa có khóa", "Vui lòng sinh khóa tự động ở cột bên trái trước."); return

        n_val = self._key_pair.public_key.n
        e_val = self._key_pair.public_key.e
        self.inp_recv_n.setText(str(n_val))
        self.inp_recv_e.setText(str(e_val))
        self.btn_verify.setEnabled(True)
        self.btn_tamper.setEnabled(True)
        self.lbl_verify_result.clear()
        self.txt_verify_details.clear()
        QMessageBox.information(self, "Nhận khóa", f"Đã nhận khóa công khai thành công!\nN = {str(n_val)[:30]}...\nE = {e_val}\n\nCó thể tiến hành kiểm tra chữ ký.")

    @pyqtSlot()
    def _on_load_sig_file(self):
        """Mo file chu ky so vao o ben phai.
        - File .sig: doc JSON, tu dong dien chu ky + khoa cong khai + van ban.
        - File .csv: hien dialog xem truoc DataFrame, chon 1 dong de dien day du thong tin.
        - File .txt / .docx: doc raw va dien vao o chu ky.
        """
        fp, _ = QFileDialog.getOpenFileName(
            self, "Mở file chữ ký", "",
            "Signature files (*.sig);;CSV – DataFrame (*.csv);;Text (*.txt);;Word (*.docx);;PDF (*.pdf);;All files (*)"
        )
        if not fp: return
        try:
            if fp.lower().endswith(".sig"):
                self._load_sig_from_sig(fp)
            elif fp.lower().endswith(".csv"):
                self._load_sig_from_csv(fp)
            else:
                content = read_file(fp)
                self.txt_recv_sig.setPlainText(content.strip())
        except Exception as ex:
            self._alert("Lỗi mở file chữ ký", str(ex))

    def _load_sig_from_sig(self, filepath: str):
        """Doc file .sig (JSON) va tu dong dien day du thong tin vao cac o."""
        data = read_sig(filepath)

        sig_hex  = data.get("signature_hex", "").strip()
        msg_val  = data.get("message", "").strip()
        hash_alg = data.get("hash_algorithm", "").strip()
        pub      = data.get("public_key", {})
        n_val    = pub.get("n", "").strip()
        e_val    = pub.get("e", "").strip()

        self.txt_recv_sig.setPlainText(sig_hex)
        if n_val:
            self.inp_recv_n.setText(n_val)
        if e_val:
            self.inp_recv_e.setText(e_val)
        if msg_val:
            self.txt_recv_msg.setPlainText(msg_val)
        if hash_alg and self.combo_recv_hash.findText(hash_alg) >= 0:
            self.combo_recv_hash.setCurrentText(hash_alg)

        if sig_hex and n_val and e_val:
            self.btn_verify.setEnabled(True)
            self.btn_tamper.setEnabled(bool(msg_val))

        QMessageBox.information(self, "Đã tải file .sig",
            f"Đã nạp thông tin từ:\n{filepath}\n\n"
            f"Chữ ký, khóa công khai (N, e){' và văn bản' if msg_val else ''} đã được điền tự động.\n"
            "Có thể kiểm tra chữ ký ngay bây giờ."
        )

    def _load_sig_from_csv(self, filepath: str):
        """Doc file CSV va hien dialog chon dong, sau do tu dong dien thong tin vao cac o."""
        rows = read_signature_csv(filepath)

        # Chuyen sang list[dict] neu la DataFrame
        if PANDAS_AVAILABLE:
            try:
                import pandas as pd
                if isinstance(rows, pd.DataFrame):
                    rows = rows.to_dict(orient="records")
            except Exception:
                pass

        if not rows:
            self._alert("File trống", "File CSV không có dữ liệu chữ ký.")
            return

        # --- Dialog xem truoc ---
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Chọn bản ghi chữ ký – {os.path.basename(filepath)}")
        dlg.setMinimumSize(900, 400)
        dlg_lay = QVBoxLayout(dlg)

        info = QLabel(f"📄 File: <b>{filepath}</b>  |  Số bản ghi: <b>{len(rows)}</b>  –  Chọn 1 dòng rồi nhấn <b>Chọn</b>")
        info.setWordWrap(True)
        dlg_lay.addWidget(info)

        cols = list(rows[0].keys()) if rows else []
        tbl = QTableWidget(len(rows), len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setAlternatingRowColors(True)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tbl.setStyleSheet("font-size: 11px; font-family: Consolas;")

        for r, row_data in enumerate(rows):
            for c, col in enumerate(cols):
                val = str(row_data.get(col, ""))
                item = QTableWidgetItem(val[:80] + "..." if len(val) > 80 else val)
                item.setToolTip(val)
                tbl.setItem(r, c, item)

        tbl.selectRow(len(rows) - 1)  # Mac dinh chon dong cuoi
        dlg_lay.addWidget(tbl)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Chọn")
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        dlg_lay.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        selected = tbl.currentRow()
        if selected < 0:
            selected = len(rows) - 1
        record = rows[selected]

        # --- Dien thong tin vao cac o ---
        sig_hex  = record.get("signature_hex", "").strip()
        n_val    = record.get("public_key_n", "").strip()
        e_val    = record.get("public_key_e", "").strip()
        msg_val  = record.get("message", "").strip()
        hash_alg = record.get("hash_algorithm", "").strip()

        self.txt_recv_sig.setPlainText(sig_hex)
        if n_val:
            self.inp_recv_n.setText(n_val)
        if e_val:
            self.inp_recv_e.setText(e_val)
        if msg_val:
            self.txt_recv_msg.setPlainText(msg_val)
        if hash_alg and self.combo_recv_hash.findText(hash_alg) >= 0:
            self.combo_recv_hash.setCurrentText(hash_alg)

        # Kich hoat nut kiem tra neu du thong tin
        if sig_hex and n_val and e_val:
            self.btn_verify.setEnabled(True)
            self.btn_tamper.setEnabled(bool(msg_val))

        QMessageBox.information(self, "Đã tải từ CSV",
            f"Đã nạp bản ghi #{selected + 1} từ file CSV.\n"
            f"Chữ ký, khóa công khai (N, e){' và văn bản' if msg_val else ''} đã được điền tự động.\n"
            "Có thể kiểm tra chữ ký ngay bây giờ."
        )

    @pyqtSlot()
    def _on_load_msg_file(self):
        """Mo file van ban nhan duoc vao o ben phai."""
        fp, _ = QFileDialog.getOpenFileName(
            self, "Mở file văn bản", "",
            "Supported Files (*.txt *.docx *.pdf);;Text (*.txt);;Word (*.docx);;PDF (*.pdf)"
        )
        if not fp: return
        try:
            content = read_file(fp)
            self.txt_recv_msg.setPlainText(content)
            self.btn_tamper.setEnabled(True)
        except Exception as ex:
            self._alert("Lỗi mở file văn bản", str(ex))
            
    @pyqtSlot()
    def _on_tamper(self):
        """Sửa đổi ngẫu nhiên 1 ký tự trong văn bản nhận được."""
        msg = self.txt_recv_msg.toPlainText()
        if not msg: return
        
        pos = random.randint(0, len(msg)-1)
        # Thay đổi ký tự (ví dụ: cộng thêm 1 giá trị ascii nhỏ)
        new_char = chr(ord(msg[pos]) ^ 1) 
        if new_char == msg[pos]: new_char = 'X' # Fallback
        
        tampered_msg = msg[:pos] + new_char + msg[pos+1:]
        self.txt_recv_msg.setPlainText(tampered_msg)
        self.txt_recv_msg.setStyleSheet("background-color: #ffcccc;") # Đánh dấu màu đỏ nhẹ
        # Reset màu sau 1.5s
        def reset_color():
            self.txt_recv_msg.setStyleSheet("background-color: #ffffff;")
        QTimer.singleShot(1500, reset_color)
        
        self.lbl_verify_result.clear()
        self.txt_verify_details.clear()

    @pyqtSlot()
    def _on_verify(self):
        msg = self.txt_recv_msg.toPlainText().strip()
        sig = self.txt_recv_sig.toPlainText().strip()
        n_s = self.inp_recv_n.text().strip()
        e_s = self.inp_recv_e.text().strip()

        if not all([msg, sig, n_s, e_s]):
            self._alert("Thiếu", "Cần có: thông điệp, chữ ký, Số N và Số E."); return

        algo = self.combo_recv_hash.currentText()
        try:
            from rsa_app.core.rsa_engine import RSAPublicKey
            pub = RSAPublicKey(e=int(e_s), n=int(n_s))
            ok, orig_h, dec_h = verify_signature(msg, sig, pub, algo)
        except Exception as ex:
            self._alert("Lỗi", str(ex)); return

        details = (
            f"- Mã băm tính từ văn bản hiện tại : {orig_h}\n"
            f"- Mã băm giải mã từ chữ ký số   : {dec_h}"
        )
        self.txt_verify_details.setPlainText(details)

        if ok:
            self.lbl_verify_result.setText("  VĂN BẢN HỢP LỆ VÀ NGUYÊN VẸN")
            self.lbl_verify_result.setStyleSheet("color: #228822; font-weight: bold; font-size:14px;")
            self.txt_verify_details.setStyleSheet("background:#e6ffe6; font-size:11px;")
        else:
            self.lbl_verify_result.setText(" VĂN BẢN KHÔNG HỢP LỆ HOẶC ĐÃ BỊ SỬA ĐỔI")
            self.lbl_verify_result.setStyleSheet("color: #cc2222; font-weight: bold; font-size:14px;")
            self.txt_verify_details.setStyleSheet("background:#ffe6e6; font-size:11px;")
