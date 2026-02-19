
from app.packages import os,Path,shutil
from flask import Flask
from flask import Blueprint,request
from app.helpers.handlerResponse import *
from app.helpers.mdl import *
import logging
from pathlib import Path
from datetime import datetime
from app.helpers.mdl import setup_logger

logger = setup_logger(name="spread_dt9")



spread_dt9_bp = Blueprint("spread_dt9", __name__)
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
                dt9Date = parse_dt9_filename(file)
                dt9Date = dt9Date.strftime("%d%m%Y")

                last_5 = file[-5:]          # ambil 5 karakter terakhir
                kodeToko = last_5.replace('.', '')  # hapus titik

                # Buat path Target Folder Kode Toko
                print("KODE_TOKO :", kodeToko)
                directoryTargetKodeToko = baseDirectory.joinpath(kodeToko, "in")
                print("✨directoryTargetKodeToko :", directoryTargetKodeToko)
                
                # CHECK FOLDER EXIST KALAU TIDAK MAKA LOG DAN SKIP
                if not directoryTargetKodeToko.exists():
                    logger.error(f"⛔ Folder toko tidak ada: {directoryTargetKodeToko} → SKIP")
                    continue

                # BUAT PATH BACKUP TOKO SORT BY DT9 DATE, ABISITU MAKA BUAT FOLDER BARU KALAU NGGA ADA
                directoryBackupTokoByDate = directoryBackupToko.joinpath(dt9Date)
                if not directoryBackupTokoByDate.exists():
                    os.makedirs(directoryBackupTokoByDate, exist_ok=True)


                # os.makedirs(directoryTargetKodeToko, exist_ok=True)

                
                # FULL PATH SOURCE
                source_path = os.path.join(directoryDT9, file)

                shutil.copy(source_path, directoryTargetKodeToko)
                # logger.info(f"📂 File copied to subfolder {directoryTargetKodeToko}")
                move_replace(Path(source_path), directoryBackupTokoByDate, logger)
                # logger.info(f"📂 File moved to backupToko {directoryBackupTokoByDate}")
                logger.info("\n")

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

