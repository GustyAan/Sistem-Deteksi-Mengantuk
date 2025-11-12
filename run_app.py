"""
Script untuk menjalankan aplikasi Sistem Deteksi Mengantuk
"""
import sys
import os

# Tambahkan root directory ke Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import dari package app
    from app import main
    print("Berhasil import package app")
    
    # Jalankan aplikasi
    main()
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Mencoba alternatif import...")
    
    # Alternatif: import langsung
    try:
        from app.main import main
        main()
    except Exception as e2:
        print(f"Error: {e2}")
        input("Press Enter to exit...")
        
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")