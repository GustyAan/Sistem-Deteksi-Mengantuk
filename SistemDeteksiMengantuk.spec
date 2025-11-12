# SistemDeteksiMengantuk.spec
# SPEC file final yang sudah include modul MediaPipe

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# ===== PATH MEDIAPIPE ANDA =====
mediapipe_path = r"C:\Users\pc\Documents\aan_pens\Tugas Sem 7\Pengolahan citra\Sistem_Deteksi_Mengantuk\venv\lib\site-packages\mediapipe"

# ===== DATA YANG IKUT DICOPY =====
datas = [
    (os.path.join(mediapipe_path, "modules"), "mediapipe/modules"),
    ("app/resources", "app/resources"),
    ("data", "data"),
]

hiddenimports = collect_submodules("mediapipe") + collect_submodules("app")

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SistemDeteksiMengantuk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,     # Tidak muncul console
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='SistemDeteksiMengantuk'
)
