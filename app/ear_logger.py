"""
Modul untuk logging data EAR ke CSV
Kompatibel dengan GUI Sistem Deteksi Mengantuk (developer & user)
"""

import pandas as pd
import os
from datetime import datetime
import csv

class EarLogger:
    """Kelas untuk menangani logging data EAR"""

    def __init__(self, filename="data/ear_log.csv"):
        self.filename = filename
        self.ensure_directory_exists()

        # Jika file belum ada → buat baru dengan header standar
        if not os.path.exists(self.filename):
            self.create_csv_file()

    def ensure_directory_exists(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def create_csv_file(self):
        """Buat CSV baru dengan header sesuai struktur GUI"""
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'ear', 'status'])

    def append(self, ear, status="Normal"):
        """
        Tambah satu data EAR
        
        Args:
            ear (float): Nilai EAR
            status (str): Status ("Normal" / "Mengantuk")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, ear, status])

    def read_all(self):
        """Membaca seluruh data"""

        try:
            df = pd.read_csv(self.filename)

            # Backward Compatibility:
            # Jika file lama pakai ear_value, rename agar GUI tidak error
            if "ear" not in df.columns:
                if "ear_value" in df.columns:
                    df.rename(columns={"ear_value": "ear"}, inplace=True)
                else:
                    raise KeyError("Kolom 'ear' tidak ditemukan.")

            return df

        except Exception as e:
            print(f"Error reading CSV: {e}")
            return pd.DataFrame(columns=['timestamp', 'ear', 'status'])

    def get_recent_data(self, minutes=10):
        """Mengambil data terbaru dalam rentang menit tertentu"""

        df = self.read_all()
        if df.empty:
            return df

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = pd.Timestamp.now() - pd.Timedelta(minutes=minutes)
        return df[df['timestamp'] >= cutoff]
