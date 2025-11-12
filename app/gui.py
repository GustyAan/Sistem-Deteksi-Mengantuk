"""
app/gui.py (FINAL - GUI_FULL)
Sistem Deteksi Mengantuk - GUI lengkap (Home / Developer / User)
Kompatibel dengan:
 - face_detector.FaceDetector (process_frame -> (frame, ear, status))
 - ear_logger.EarLogger (append(ear,status), read_all())
 - plotter.Plotter (generate_plot -> writes ear_plot.png)
 - utils.resource_path, ensure_directories, check_camera_permission
"""

import os
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import cv2                                # OpenCV: wajib untuk akses kamera
from PIL import Image, ImageTk

from app.face_detector import FaceDetector
from app.ear_logger import EarLogger
from app.plotter import Plotter
from app.utils import (
    resource_path,
    ensure_directories,
    check_camera_permission
)



class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master or tk.Tk()
        self.master.title("Sistem Deteksi Mengantuk - PENS")
        self.master.geometry("1100x700")
        self.pack(fill=tk.BOTH, expand=True)

        # Pastikan direktori data/resources ada
        ensure_directories()

        # Core components (dependensi harus ada)
        self.face_detector = FaceDetector()                        # process_frame(frame) -> (frame, ear, status)
        self.ear_logger = EarLogger(os.path.join("data", "ear_log.csv"))
        self.plotter = Plotter(self.ear_logger, out_path="ear_plot.png")

        # Camera / thread control
        self.cap = None
        self.camera_thread = None
        self.is_camera_running = False
        self.current_frame = None    # "home" / "developer" / "user"
        self.last_alert_time = 0
        self.alert_cooldown = 30     # detik, cooldown popup
        self.low_ear_counter = 0
        self.consecutive_threshold = 3  # butuh 3 frame berturut-turut (atau sampling) untuk alert

        # Tk placeholders
        self.logo_photo = None
        self.dev_logo_photo = None
        self.user_logo_photo = None

        # Build UI & show home
        self._build_base_ui()
        self.show_home_page()

        # Handle close
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------------------------------------------------
    # Base UI
    # ---------------------------------------------------------------------
    def _build_base_ui(self):
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------------------
    # Pages: Home / Developer / User
    # ---------------------------------------------------------------------
    def show_home_page(self):
        """Tampilan utama pilihan mode"""
        self._stop_camera_if_running()
        self._clear_container()
        self.current_frame = "home"
        self.low_ear_counter = 0

        # Logo (resource_path untuk PyInstaller)
        logo_path = resource_path(os.path.join("app", "resources", "logo_pens.png"))
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((120, 120), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.container, image=self.logo_photo)
                lbl.pack(pady=10)
            except Exception as e:
                print("Logo load error:", e)

        title = tk.Label(self.container, text="SISTEM DETEKSI MENGANTUK", font=("Arial", 22, "bold"))
        title.pack(pady=8)

        sub = tk.Label(self.container, text="Politeknik Elektronika Negeri Surabaya", font=("Arial", 12))
        sub.pack(pady=2)

        btn_frame = tk.Frame(self.container)
        btn_frame.pack(pady=30)

        dev_btn = tk.Button(btn_frame, text="Developer", width=20, height=2,
                            bg="#4CAF50", fg="white", font=("Arial", 12),
                            command=self.authenticate_developer)
        dev_btn.grid(row=0, column=0, padx=10, pady=6)

        user_btn = tk.Button(btn_frame, text="User", width=20, height=2,
                             bg="#2196F3", fg="white", font=("Arial", 12),
                             command=self.show_user_page)
        user_btn.grid(row=0, column=1, padx=10, pady=6)

        exit_btn = tk.Button(btn_frame, text="Keluar", width=44, height=2,
                             bg="#f44336", fg="white", font=("Arial", 12),
                             command=self._on_close)
        exit_btn.grid(row=1, column=0, columnspan=2, pady=8)

    def authenticate_developer(self):
        pw = simpledialog.askstring("Authentication", "Masukkan Password Developer:", show='*')
        if pw is None:
            return
        if pw == "Kakikudaada4":
            self.show_developer_page()
        else:
            messagebox.showerror("Authentication", "Password salah!")

    def show_developer_page(self):
        """Halaman Developer lengkap: status, histori, kamera besar, grafik"""
        self._stop_camera_if_running()
        self._clear_container()
        self.current_frame = "developer"
        self.low_ear_counter = 0

        # Header
        header = tk.Frame(self.container)
        header.pack(fill=tk.X, padx=10, pady=6)

        # logo small
        logo_path = resource_path(os.path.join("app", "resources", "logo_pens.png"))
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((80, 80), Image.Resampling.LANCZOS)
                self.dev_logo_photo = ImageTk.PhotoImage(img)
                logo_lbl = tk.Label(header, image=self.dev_logo_photo)
                logo_lbl.pack(side="left", padx=6)
            except Exception as e:
                print("Dev logo load error:", e)

        title = tk.Label(header, text="MODE DEVELOPER - SISTEM DETEKSI MENGANTUK",
                         font=("Arial", 16, "bold"))
        title.pack(side="left", padx=10)

        # Layout main split
        main_frame = tk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left_panel = tk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        right_panel = tk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left: status & history
        status_frame = tk.LabelFrame(left_panel, text="Status & Waktu")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = tk.Label(status_frame, text="Status: --", font=("Arial", 12), fg="gray")
        self.status_label.pack(anchor="w", padx=6, pady=2)

        self.time_label = tk.Label(status_frame, text="", font=("Arial", 12))
        self.time_label.pack(anchor="w", padx=6, pady=2)

        history_frame = tk.LabelFrame(left_panel, text="Histori Kondisi (20 Terakhir)")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ("Timestamp", "EAR", "Status")
        self.history_tree = ttk.Treeview(history_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.history_tree.heading(c, text=c)
            self.history_tree.column(c, width=110, anchor="center")

        scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scroll.set)
        self.history_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scroll.pack(side="right", fill="y")

        # Left control buttons
        control_frame = tk.Frame(left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=8)

        back_btn = tk.Button(control_frame, text="Kembali ke Home", command=self.show_home_page,
                             bg="#607D8B", fg="white", width=18)
        back_btn.pack(side="left", padx=4)

        refresh_btn = tk.Button(control_frame, text="Refresh Grafik", command=self.update_plot,
                                bg="#FF9800", fg="white", width=18)
        refresh_btn.pack(side="left", padx=4)

        # Right: camera display and plot
        camera_frame = tk.LabelFrame(right_panel, text="Kamera Live - Deteksi Wajah")
        camera_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.camera_label = tk.Label(camera_frame, text="Kamera tidak aktif", bg="black", fg="white")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        plot_frame = tk.LabelFrame(right_panel, text="Grafik EAR Realtime")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.plot_label = tk.Label(plot_frame, text="Grafik akan muncul di sini", bg="white")
        self.plot_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Start camera + UI updates
        self._start_camera_thread()
        self._schedule_update_time()
        self.update_plot()

    def show_user_page(self):
        """Halaman User: indikator besar, preview kecil, tombol data"""
        self._stop_camera_if_running()
        self._clear_container()
        self.current_frame = "user"
        self.low_ear_counter = 0

        header = tk.Frame(self.container)
        header.pack(pady=(6, 12))

        logo_path = resource_path(os.path.join("app", "resources", "logo_pens.png"))
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((60, 60), Image.Resampling.LANCZOS)
                self.user_logo_photo = ImageTk.PhotoImage(img)
                logo_lbl = tk.Label(header, image=self.user_logo_photo)
                logo_lbl.pack(side="left", padx=6)
            except Exception as e:
                print("User logo load error:", e)

        title = tk.Label(header, text="MODE PENGGUNA", font=("Arial", 18, "bold"))
        title.pack(side="left", padx=6)

        # Time label
        self.user_time_label = tk.Label(self.container, text="", font=("Arial", 14))
        self.user_time_label.pack(pady=6)

        # Big status indicator
        self.status_indicator = tk.Label(self.container, text="--", font=("Arial", 18, "bold"),
                                         bg="gray", fg="white", width=30, height=4, bd=3, relief="raised")
        self.status_indicator.pack(pady=10)

        self.ear_label = tk.Label(self.container, text="EAR: --", font=("Arial", 14))
        self.ear_label.pack(pady=6)

        # Preview small camera
        cam_frame = tk.LabelFrame(self.container, text="Preview Kamera")
        cam_frame.pack(pady=8)
        self.user_camera_label = tk.Label(cam_frame, text="Kamera belum aktif", bg="black", fg="white",
                                          width=40, height=10)
        self.user_camera_label.pack(padx=6, pady=6)

        # Buttons
        btn_frame = tk.Frame(self.container)
        btn_frame.pack(pady=12)

        back = tk.Button(btn_frame, text="Kembali ke Home", command=self.show_home_page,
                         bg="#607D8B", fg="white", width=16)
        back.grid(row=0, column=0, padx=8)

        data_btn = tk.Button(btn_frame, text="Lihat Data & Grafik", command=self.show_user_data,
                             bg="#4CAF50", fg="white", width=16)
        data_btn.grid(row=0, column=1, padx=8)

        # Start camera and user-time update
        self._start_camera_thread()
        self._schedule_update_user_time()

    def show_user_data(self):
        """Popup yang menampilkan grafik & log terbaru (Mode user)"""
        try:
            self.plotter.generate_plot()
            win = tk.Toplevel(self.master)
            win.title("Data Deteksi Mengantuk - Mode User")
            win.geometry("760x560")

            header = tk.Label(win, text="DATA HISTORIS DETEKSI MENGANTUK", font=("Arial", 14, "bold"))
            header.pack(pady=8)

            if os.path.exists("ear_plot.png"):
                img = Image.open("ear_plot.png").resize((720, 360), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(win, image=photo)
                lbl.image = photo
                lbl.pack(pady=6)
            else:
                lbl = tk.Label(win, text="Grafik tidak tersedia", font=("Arial", 12))
                lbl.pack(pady=12)

            # show recent log entries
            df = self.ear_logger.read_all()
            txt = tk.Text(win, height=8, width=90)
            txt.pack(pady=6)
            if df is not None and not df.empty:
                # ensure timestamp format is string for display
                if 'timestamp' in df.columns:
                    df['timestamp'] = df['timestamp'].astype(str)
                for idx, row in df.tail(30).iterrows():
                    ear_val = row.get('ear', row.get('ear_value', None))
                    status = row.get('status', 'Unknown')
                    if ear_val is None:
                        txt.insert("end", f"{row.get('timestamp','-')} - (no ear)\n")
                    else:
                        txt.insert("end", f"{row.get('timestamp','-')} - {float(ear_val):.3f} - {status}\n")
            else:
                txt.insert("end", "Tidak ada data.")

            close = tk.Button(win, text="Tutup", command=win.destroy)
            close.pack(pady=8)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan data: {e}")

    # ---------------------------------------------------------------------
    # Camera management & loop
    # ---------------------------------------------------------------------
    def _start_camera_thread(self):
        """Start camera thread kalau belum jalan"""
        if self.is_camera_running:
            return

        # quick camera permission check
        if not check_camera_permission():
            messagebox.showerror("Error Kamera", "Tidak dapat mengakses kamera. Tutup aplikasi lain yang menggunakan kamera atau cek permission.")
            return

        try:
            # CAP_DSHOW lebih stabil di Windows
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                messagebox.showerror("Error Kamera", "Gagal membuka kamera.")
                return

            self.is_camera_running = True
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            print("Camera thread started")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai kamera: {e}")
            self.is_camera_running = False

    def _stop_camera_if_running(self):
        """Stop camera safely when switching pages"""
        if self.is_camera_running:
            self.is_camera_running = False
            # Wait a little for thread to finish
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            # Release capture
            try:
                if self.cap:
                    self.cap.release()
            except Exception:
                pass
            self.cap = None
            print("Camera stopped via _stop_camera_if_running")

    def _camera_loop(self):
        """Loop capture & processing. Menjalankan face_detector dan update UI via master.after"""
        last_plot_update = 0

        while self.is_camera_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    # kalau read gagal, coba delay dan ulang
                    print("Camera read failed")
                    time.sleep(0.1)
                    continue

                processed, ear_value, status = self.face_detector.process_frame(frame)

                # Logging & alert logic
                if ear_value is not None:
                    # Append to CSV (include status)
                    try:
                        self.ear_logger.append(ear_value, status)
                    except Exception as e:
                        print("Logger append error:", e)

                    # Consecutive logic (menggunakan status agar lebih robust)
                    if status == "Mengantuk":
                        self.low_ear_counter += 1
                    else:
                        self.low_ear_counter = 0

                    # Trigger alert only when threshold of consecutive frames reached and cooldown passed
                    now_ts = time.time()
                    if self.low_ear_counter >= self.consecutive_threshold and (now_ts - self.last_alert_time) >= self.alert_cooldown:
                        # schedule alert on main thread
                        self.master.after(0, self._trigger_alert_ui)
                        self.last_alert_time = now_ts
                        self.low_ear_counter = 0

                    # schedule GUI status update
                    self.master.after(0, self._update_status_ui, ear_value, status)

                # Prepare image for display (RGB)
                try:
                    rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb)
                except Exception as e:
                    print("Error converting frame for display:", e)
                    time.sleep(0.05)
                    continue

                # size selection by mode
                if self.current_frame == "developer":
                    img = img.resize((480, 360), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((320, 240), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                # schedule image update in main thread
                self.master.after(0, self._update_camera_image, photo, self.current_frame)

                # periodic plot update (every 5 seconds)
                if time.time() - last_plot_update >= 5:
                    last_plot_update = time.time()
                    self.master.after(0, self.update_plot)

                # sleep to target ~10 Hz
                time.sleep(0.1)

            except Exception as e:
                print("Error in camera loop:", e)
                break

        # cleanup when loop ends
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        self.is_camera_running = False
        print("Camera loop ended")

    # ---------------------------------------------------------------------
    # GUI updates & helpers
    # ---------------------------------------------------------------------
    def _update_camera_image(self, photo, mode):
        """Update camera display depending on mode"""
        if mode != self.current_frame:
            # ignore old frame updates when mode switched
            return
        if mode == "developer":
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo
        elif mode == "user":
            self.user_camera_label.configure(image=photo)
            self.user_camera_label.image = photo

    def _update_status_ui(self, ear_value, status):
        """Update status labels and history tree"""
        if self.current_frame == "developer":
            # status label & time
            self.status_label.config(text=f"Status: {status}", fg="red" if status == "Mengantuk" else "green")
            # insert history top
            ts = datetime.now().strftime("%H:%M:%S")
            try:
                self.history_tree.insert("", 0, values=(ts, f"{ear_value:.3f}", status))
                # maintain only last 20 rows
                children = self.history_tree.get_children()
                if len(children) > 20:
                    self.history_tree.delete(children[-1])
            except Exception as e:
                print("History insert error:", e)
        elif self.current_frame == "user":
            try:
                self.ear_label.config(text=f"EAR: {ear_value:.3f}")
            except Exception:
                self.ear_label.config(text="EAR: --")
            if status == "Mengantuk":
                self.status_indicator.config(text="MENGANTUK!\nSEGERA ISTIRAHAT", bg="red")
            else:
                self.status_indicator.config(text="NORMAL\nSELAMAT BERKENDARA", bg="green")

    def _trigger_alert_ui(self):
        """Show alert popup on main thread"""
        if self.current_frame == "user":
            messagebox.showwarning("PERINGATAN MENGANTUK",
                                   "⚠️ KONDISI MENGANTUK TERDETEKSI! ⚠️\n\nSegera istirahat dan berhenti berkendara!")
        else:
            messagebox.showwarning("Peringatan Mengantuk", "Kondisi mengantuk terdeteksi! EAR ≤ threshold.")

    def _schedule_update_time(self):
        if self.current_frame == "developer":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=f"Waktu: {now}")
            self.master.after(1000, self._schedule_update_time)

    def _schedule_update_user_time(self):
        if self.current_frame == "user":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.user_time_label.config(text=f"Waktu: {now}")
            self.master.after(1000, self._schedule_update_user_time)

    def update_plot(self):
        """Regenerate plot and show on developer page (if open)"""
        try:
            self.plotter.generate_plot()
            if os.path.exists("ear_plot.png") and self.current_frame == "developer":
                img = Image.open("ear_plot.png").resize((380, 260), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.plot_label.configure(image=photo)
                self.plot_label.image = photo
        except Exception as e:
            print("Update plot error:", e)

    # -------------------------
    # Utilities
    # -------------------------
    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _on_close(self):
        """Cleanup and close application"""
        self._stop_camera_if_running()
        try:
            self.master.destroy()
        except Exception:
            os._exit(0)


# Entrypoint convenience
def run_app():
    root = tk.Tk()
    app = MainApplication(master=root)
    app.mainloop()


if __name__ == "__main__":
    run_app()
