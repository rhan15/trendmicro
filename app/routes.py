
from app.packages import os,Path,shutil
from flask import Flask
from flask import Blueprint,request
from app.helpers.handlerResponse import *
from app.helpers.createConnection import getPostgresConnection
from app.helpers.getDataFromQuery import selectMasterToko
import logging
from pathlib import Path
from datetime import datetime

# CHECK FOLDER LOGNYA
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# BUAT FORMAT TANGGAL YYYY-MM-DD UNTUK NAMA FILE LOGNYA
today_str = datetime.now().strftime("%Y-%m-%d")
log_file = log_dir / f"dt9_job_{today_str}.log"

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


main = Blueprint('main', __name__)

@main.route('/')
def home():
    try:
        print("Job dijalankan")
        conn = getPostgresConnection()
        if conn:
            print("PostgreSQL Connected Successfully!")
            conn.close()
        else:
            print("PostgreSQL Connection Failed.")
            raise Exception("Connection Failed")

        current_directory = Path.cwd()
        tempDir = current_directory.joinpath(os.getenv("PUBLIC_DIR"))
        print("Default directory:", tempDir)
        os.makedirs(tempDir, exist_ok=True)
        return "Succedd Create Temp KodeToko Directory!!"
    except Exception as e:
        # connection.rollback()
        # DELETE FOLDER TEMP
        return create_error_response(
            message="Terjadi Kesalahan", error_message=f"Error: {e}"
        )


@main.route('/create-store-directory')
def create_store_directory():
    try:
        print("Job create-store-directory dijalankan")

        result = selectMasterToko()
        fields = result["fields"]
        records = result["records"]

        base_dir = Path(os.getenv("PUBLIC_DIR"))

        for record in records:
            cabang = record[fields['cab_singkatancabang']]
            kode_omi = record[fields['tko_kodeomi']]

            tempDir = base_dir.joinpath(cabang, kode_omi)

            os.makedirs(tempDir.joinpath("in/history"), exist_ok=True)
            os.makedirs(tempDir.joinpath("out/Backup"), exist_ok=True)
            os.makedirs(tempDir.joinpath("out/Finance"), exist_ok=True)
            os.makedirs(tempDir.joinpath("out/PB"), exist_ok=True)
            os.makedirs(tempDir.joinpath("out/QV"), exist_ok=True)
            os.makedirs(tempDir.joinpath("lhost"), exist_ok=True)
            os.makedirs(tempDir.joinpath("lremote"), exist_ok=True)

            print(f"Success create store directory: {tempDir}")

        return "Success Create All Store Directories!"

    except Exception as e:
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )


# @main.route('/transfer-files')
# def trnsfer_file():
#     try:
#         print("Job copy-file dijalankan")
#         current_directory = Path.cwd()

#         oldServer = Path(os.getenv("PUBLIC_DIR_OLD")) 
#         newServer = Path(os.getenv("PUBLIC_DIR")) 

#         for root, dirs, files in os.walk(oldServer):
#             # print("ROOT:", root)
#             # print("DIRS:", dirs)
#             # print("FILES:", files)
#             # print("------------")
#             for d in dirs:
#                 # subfolder = Path(root) / d
#                 # shutil.copy(source_file, subfolder)
#                 # shutil.copy(source_file2, subfolder)
#                 # print(f"📂 File copied to subfolder {subfolder}")
#                 for f in files:
#                     print(f"📂 File copied to subfolder {current_directory.joinpath(root,d,f)}")
#                     print(f"📂 File copied to subfolder {current_directory.joinpath(newServer,d)}")
#                     filesOnOldServer = current_directory.joinpath(newServer,d,f)
#                     pathNewServer = current_directory.joinpath(newServer,d)
#                     # shutil.copy(filesOnOldServer, pathNewServer)

#         return "Success: File copied to all toko and subfolders!"

#     except Exception as e:
#         print(f"Error during copy: {e}")
#         return create_error_response(
#             message="Terjadi Kesalahan",
#             error_message=f"Error: {e}"
#         )

@main.route('/transfer-files')
def transfer_files():
    try:
        print("Job transfer-files dijalankan")

        oldServer = Path(os.getenv("PUBLIC_DIR_OLD")).resolve()
        newServer = Path(os.getenv("PUBLIC_DIR")).resolve()

        print(f"Source: {oldServer}")
        print(f"Destination: {newServer}")

        result = selectMasterToko()
        fields = result["fields"]
        records = result["records"]
        toko_map = {record[fields['tko_kodeomi']]: record[fields['cab_singkatancabang']] for record in records}
        # print(f"Toko Map: {toko_map}")
        # return "haloo"

        # cek semua file dan folder di oldServer
        for root, dirs, files in os.walk(oldServer):
            root_path = Path(root)

            # Buat path relatif dari oldServer
            relative_path = root_path.relative_to(oldServer)

            # Ambil kode_toko omi (folder toko)
            parts = relative_path.parts
            if not parts:
                continue

            kode_omi = parts[0]
            if kode_omi not in toko_map:
                print(f"Folder {kode_omi} tidak terdaftar di database, dilewati.")
                continue

            # Ambil nama cabang berdasarkan kode_omi
            cabang = toko_map[kode_omi]

            # Path tujuan (mirror structure di newServer)
            dest_dir = newServer / cabang / relative_path

            # Pastikan folder tujuan ada
            os.makedirs(dest_dir, exist_ok=True)
            print(f"DESTINATION DIR: {dest_dir}")

            # Salin semua file di folder ini
            for f in files:
                src_file = root_path / f
                dest_file = dest_dir / f

                shutil.copy2(src_file, dest_file)  # copy dengan metadata
                print(f"Copied: {src_file} → {dest_file}")

            print(f"=========================================================")
        return "Success: Semua file berhasil ditransfer dari OLD ke NEW server!"

    except Exception as e:
        print(f"Error during transfer: {e}")
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )


@main.route('/copy-file')
def copy_file():
    try:
        print("Job copy-file dijalankan")

        source_file = os.getenv("SOURCE_FILE")
        source_file2 = os.getenv("SOURCE_FILE2")

        # hasil query PostgreSQL
        result = selectMasterToko()
        fields = result["fields"]
        records = result["records"]

        # direktori utama tempat toko disimpan
        public_dir_old = Path(os.getenv("PUBLIC_DIR_OLD"))

        for record in records:
            kode_omi = record[fields['tko_kodeomi']]
            tempDir = public_dir_old.joinpath(kode_omi)

            if not tempDir.exists():
                print(f"Folder {tempDir} tidak ditemukan, dilewati.")
                continue

            # --- copy ke folder utama toko ---
            shutil.copy(source_file, tempDir)
            shutil.copy(source_file2, tempDir)
            print(f"File copied to {tempDir}")

            # --- copy ke semua subfolder yang sudah ada ---
            for root, dirs, files in os.walk(tempDir):
                # print("ROOT:", root)
                # print("DIRS:", dirs)
                # print("FILES:", files)
                # print("------------")
                for d in dirs:
                    subfolder = Path(root) / d
                    shutil.copy(source_file, subfolder)
                    shutil.copy(source_file2, subfolder)
                    print(f"File copied to subfolder {subfolder}")

        return "Success: File copied to all toko and subfolders!"

    except Exception as e:
        print(f"Error during copy: {e}")
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )
    

