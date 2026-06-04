"""
main.py – Entry point ứng dụng Chữ ký số RSA
Chạy: python main.py (từ thư mục atbmtt/)
      hoặc: ./venv/bin/python main.py (từ thư mục rsa_app/)
"""
import sys, os

_this = os.path.dirname(os.path.abspath(__file__))   # .../rsa_app
_parent = os.path.dirname(_this)                      # .../atbmtt
for _p in [_parent, _this]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from rsa_app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ứng dụng Chữ ký số RSA")
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
