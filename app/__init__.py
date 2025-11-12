"""
Package Sistem Deteksi Mengantuk
Aplikasi deteksi kantuk menggunakan EAR (Eye Aspect Ratio)
"""

__version__ = "1.0.0"
__author__ = "Politeknik Elektronika Negeri Surabaya"
__description__ = "Sistem Deteksi Mengantuk berbasis EAR (Eye Aspect Ratio)"

# Import ringan (tidak memanggil modul berat secara langsung)
from .utils import resource_path, ensure_directories

def init_package():
    """Inisialisasi package (membuat direktori, dsb)."""
    print(f"Initializing {__description__} v{__version__}")
    ensure_directories()

# Jalankan inisialisasi dasar
init_package()

# Ekspor modul (LAZY IMPORT untuk menghindari import-recursion)
__all__ = [
    "resource_path",
    "ensure_directories",
    "FaceDetector",
    "EarLogger",
    "Plotter",
    "MainApplication",
    "main"
]

def __getattr__(name):
    """
    Lazy import untuk modul berat seperti GUI, Plotter, FaceDetector.
    Tidak akan di-import sebelum benar-benar dipakai.
    """
    if name == "FaceDetector":
        from .face_detector import FaceDetector
        return FaceDetector
    elif name == "EarLogger":
        from .ear_logger import EarLogger
        return EarLogger
    elif name == "Plotter":
        from .plotter import Plotter
        return Plotter
    elif name == "MainApplication":
        from .gui import MainApplication
        return MainApplication
    elif name == "main":
        from .main import main
        return main
    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")
