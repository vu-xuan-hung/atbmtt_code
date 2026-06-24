"""Utils module: file manager & helpers."""
from .file_manager import (
    save_signature_file, read_file,
    read_signature_csv, save_as_csv,
    DOCX_AVAILABLE, PANDAS_AVAILABLE,
)

__all__ = [
    "save_signature_file", "read_file",
    "read_signature_csv", "save_as_csv",
    "DOCX_AVAILABLE", "PANDAS_AVAILABLE",
]
