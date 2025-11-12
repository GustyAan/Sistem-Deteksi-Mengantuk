"""
Modul utilitas untuk kompatibilitas PyInstaller dan fungsi helper
"""
import os
import sys

def resource_path(relative_path):
    """
    Mendapatkan absolute path ke resource, bekerja untuk development dan PyInstaller
    
    Args:
        relative_path (str): Path relatif ke resource
        
    Returns:
        str: Absolute path ke resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def ensure_directories():
    """Memastikan semua directory yang diperlukan tersedia"""
    directories = [
        "app/resources",
        "data",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def check_camera_permission():
    """
    Memeriksa apakah aplikasi memiliki akses ke kamera
    
    Returns:
        bool: True jika kamera dapat diakses
    """
    import cv2
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            return ret
        return False
    except:
        return False