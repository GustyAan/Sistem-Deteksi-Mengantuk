"""
Script sederhana untuk start aplikasi
"""
import sys
import os

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import dan jalankan
    from app.main import main
    print("Starting Sistem Deteksi Mengantuk...")
    main()
except Exception as e:
    print(f"Failed to start: {e}")
    input("Press Enter to exit...")