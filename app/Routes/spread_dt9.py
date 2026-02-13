
from app.packages import os,Path,shutil
from flask import Flask
from flask import Blueprint,request
from app.helpers.handlerResponse import *
import logging
from pathlib import Path
from datetime import datetime

# CHECK FOLDER LOGNYA
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# BUAT FORMAT TANGGAL YYYY-MM-DD UNTUK NAMA FILE LOGNYA
today_str = datetime.now().strftime("%Y-%m-%d")
log_file = log_dir / f"Spread_dt9_job_{today_str}.log"

# SETUP LOGGERNYA
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)



spread_dt9_bp = Blueprint("master_rak", __name__)
@spread_dt9_bp.route('/proced-spread-dt9')
def spread_dt9():
   return proced_spread_dt9()

def proced_spread_dt9():
    try:
        print("Job penyebaran DT9 dijalankan")

        directoryDT9 = Path(os.getenv("DIRECTORY_DT9"))
        baseDirectory = Path(os.getenv("PUBLIC_DIR"))

        directoryBackupToko = baseDirectory.joinpath("dt9_backup")
        if not directoryBackupToko.exists():
            os.makedirs(directoryBackupToko, exist_ok=True)

        files = [f for f in directoryDT9.iterdir() if f.is_file()]

        for file in files:
            
            try:
                file = file.name
                    
                last_5 = file[-5:]          # ambil 5 karakter terakhir
                kodeToko = last_5.replace('.', '')  # hapus titik

                # Buat path Target Folder Kode Toko
                print("KODE_TOKO :", kodeToko)
                directoryTargetKodeToko = baseDirectory.joinpath(kodeToko, "in")
                
                # CHECK FOLDER EXIST KALAU TIDAK MAKA LOG DAN SKIP
                if not directoryTargetKodeToko.exists():
                    print(f"⛔ Folder toko tidak ada: {directoryTargetKodeToko} → SKIP")
                    logger.error(f"Folder toko tidak ada: {directoryTargetKodeToko} → SKIP")
                    continue

                print("✨directoryTargetKodeToko :", directoryTargetKodeToko)

                # os.makedirs(directoryTargetKodeToko, exist_ok=True)
                # os.makedirs(directoryBackupToko, exist_ok=True)

                # FULL PATH SOURCE
                source_path = os.path.join(directoryDT9, file)

                shutil.copy(source_path, directoryTargetKodeToko)
                print(f"📂 File copied to subfolder {directoryTargetKodeToko}")
                shutil.move(source_path, directoryBackupToko)
                print(f"📂 File moved to backupToko {directoryBackupToko}")
                print("\n")

            except Exception as e:
                logger.error(f"Gagal proses file {file} | {str(e)}")
                continue

        return "Success: File copied to all toko and subfolders!"

    except Exception as e:
        print(f"Error during copy: {e}")
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )

