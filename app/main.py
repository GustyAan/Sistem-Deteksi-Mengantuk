"""
Entry point utama aplikasi Sistem Deteksi Mengantuk
"""
import tkinter as tk
from app.gui import MainApplication

def main():
    """Fungsi utama untuk menjalankan aplikasi GUI"""
    root = tk.Tk()
    root.title("Sistem Deteksi Mengantuk - PENS")
    root.geometry("800x600")
    root.resizable(True, True)
    
    app = MainApplication(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()