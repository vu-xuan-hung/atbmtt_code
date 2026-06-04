"""
file_manager.py
===============
Module quản lý file:
- Lưu chữ ký ra .txt
- Lưu chữ ký ra .docx
- Đọc file chữ ký
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_as_txt(filepath: str, data: dict) -> None:
    """
    Lưu thông tin chữ ký ra file .txt.

    data dict chứa các key:
        message, hash_algorithm, hash_hex, signature_hex,
        public_key_e, public_key_n, private_key_d (tuỳ chọn)
    """
    lines = [
        "=" * 60,
        "  ỨNG DỤNG CHỮ KÝ SỐ RSA",
        "  An toàn và Bảo mật Thông tin",
        "=" * 60,
        f"  Thời gian: {_timestamp()}",
        "=" * 60,
        "",
        "[THÔNG ĐIỆP GỐC]",
        data.get("message", ""),
        "",
        "[THUẬT TOÁN HASH]",
        data.get("hash_algorithm", "SHA-256"),
        "",
        "[GIÁ TRỊ HASH (H(m))]",
        data.get("hash_hex", ""),
        "",
        "[CHỮ KÝ SỐ (S = H^d mod n)]",
        data.get("signature_hex", ""),
        "",
        "[KHÓA CÔNG KHAI]",
        f"  e = {data.get('public_key_e', '')}",
        f"  n = {data.get('public_key_n', '')}",
        "",
    ]

    if data.get("include_private", False):
        lines += [
            "[KHÓA BÍ MẬT]",
            f"  d = {data.get('private_key_d', '')}",
            f"  n = {data.get('public_key_n', '')}",
            "",
        ]

    lines += [
        "=" * 60,
        "  [Kết thúc file chữ ký]",
        "=" * 60,
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def save_as_docx(filepath: str, data: dict) -> None:
    """Lưu thông tin chữ ký ra file .docx."""
    if not DOCX_AVAILABLE:
        raise RuntimeError("Thư viện python-docx chưa được cài đặt.")

    doc = Document()

    # Title
    title = doc.add_heading("ỨNG DỤNG CHỮ KÝ SỐ RSA", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph("An toàn và Bảo mật Thông tin")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Thời gian tạo: {_timestamp()}")
    doc.add_paragraph("─" * 50)

    def add_section(title: str, content: str):
        p = doc.add_paragraph()
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(11)
        doc.add_paragraph(content or "(trống)")
        doc.add_paragraph("")

    add_section("THÔNG ĐIỆP GỐC", data.get("message", ""))
    add_section("THUẬT TOÁN HASH", data.get("hash_algorithm", "SHA-256"))
    add_section("GIÁ TRỊ HASH  H(m)", data.get("hash_hex", ""))
    add_section("CHỮ KÝ SỐ  S = H^d mod n", data.get("signature_hex", ""))

    doc.add_paragraph("").add_run("KHÓA CÔNG KHAI").bold = True
    doc.add_paragraph(f"  e = {data.get('public_key_e', '')}")
    doc.add_paragraph(f"  n = {data.get('public_key_n', '')}")

    if data.get("include_private", False):
        doc.add_paragraph("").add_run("KHÓA BÍ MẬT").bold = True
        doc.add_paragraph(f"  d = {data.get('private_key_d', '')}")
        doc.add_paragraph(f"  n = {data.get('public_key_n', '')}")

    doc.save(filepath)


def save_signature_file(filepath: str, data: dict) -> None:
    """Lưu file chữ ký (tự động chọn định dạng theo extension)."""
    ext = Path(filepath).suffix.lower()
    if ext == ".docx":
        save_as_docx(filepath, data)
    else:
        save_as_txt(filepath, data)


def read_file(filepath: str) -> str:
    """Đọc nội dung file chữ ký (txt hoặc docx) và trả về chuỗi."""
    ext = Path(filepath).suffix.lower()
    if ext == ".docx":
        if not DOCX_AVAILABLE:
            raise RuntimeError("Thư viện python-docx chưa được cài đặt.")
        doc = Document(filepath)
        lines = [para.text for para in doc.paragraphs]
        return "\n".join(lines)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
