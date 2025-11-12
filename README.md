# Sistem-Deteksi-Mengantuk
Sistem ini menggunakan metode **Eye Aspect Ratio (EAR)** berbasis **MediaPipe FaceMesh** untuk mendeteksi kondisi mengantuk secara real-time. Ketika nilai EAR berada di bawah ambang batas selama beberapa frame berturut-turut, sistem menampilkan **peringatan otomatis** agar pengguna tetap waspada. 

# Pengembang
Nama: 
- Alwansyah Muhammad M.E. (2122600031)  
- Balqis Sofi Nurani (2122600034)  
- Gusty Anugrah (2122600040)  
- Dikri Sadam Panca Sakti (2122600049)  
- Wildan Aldi Nugroho (2122600055)  

Institusi: [Politeknik Elektronika Negeri Surabaya / Teknik Elektronika]

# Fitur Utama
🔹 Deteksi kondisi mata secara real-time dengan **MediaPipe FaceMesh**.  

🔹 Perhitungan **Eye Aspect Ratio (EAR)** untuk membedakan kondisi “Normal” dan “Mengantuk”.  

🔹 Ambang batas EAR = **0.21** dengan deteksi beruntun minimal **3 frame** agar tidak salah mendeteksi kedipan alami.  

🔹 Popup peringatan otomatis ketika kondisi mengantuk terdeteksi.  

🔹 Dua mode tampilan: **User Mode** (sederhana) dan **Developer Mode** (grafik & data historis).  

🔹 Penyimpanan nilai EAR dan status pengguna ke file **CSV** untuk analisis lebih lanjut.  

🔹 Grafik tren EAR real-time menggunakan **Matplotlib**.  

🔹 Pembuatan file .exe dengan **PyInstaller** untuk kemudahan distribusi.

# Arsitektur Sistem
<img width="734" height="425" alt="Image" src="https://github.com/user-attachments/assets/5358b386-5fbe-4a10-8c63-8acec72b8546" />

# Teknologi yang Digunakan
🔹 Python versi 3 + (lebih dari 3)  

🔹 OpenCV – pengambilan dan pemrosesan video dari kamera.  

🔹 MediaPipe – pendeteksian titik wajah (FaceMesh).  

🔹 Tkinter – antarmuka pengguna (GUI).  

🔹 Matplotlib – visualisasi grafik nilai EAR.  

🔹 Pandas – pengelolaan data dan penyimpanan CSV.  

🔹 Threading – eksekusi paralel kamera & logika deteksi.

# Cara Menjalankan Program
1. Pastikan Python 3 dan pustaka berikut telah terpasang:

    pip install opencv-python tk matplotlib


2. Jalankan program utama:

    python main.py


3. Pilih mode User atau Developer dari antarmuka utama.

4. Izinkan akses kamera saat diminta.

5. Aplikasi akan mulai mendeteksi dan menampilkan waktu penggunaan layar.
