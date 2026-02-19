import sys
from app.packages import os, shutil
from datetime import datetime
from app.helpers.handlerResponse import *
from app.helpers.createConnection import getPostgresConnection
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import logging

#GET CONNECTION
oConn = getPostgresConnection()
pgCursor = oConn.cursor()

class CustomError(Exception):
    pass

# def extract_zip_to_temp(zipPath, temp_dir):
#     try:
#         print(f"FILE ZIP : '{zipPath}'")
#         with zipfile.ZipFile(zipPath, 'r') as zip_ref:
#             zip_ref.extractall(temp_dir)
#             print("     EXTRACTION SUCCEED")
            
#     except Exception as e:
#         raise

def fixFolderFormatToZIP_ExpectFullPath(old_file_path):
    try:

        ext = ".Zip"
        file_path, oldFileName = os.path.split(old_file_path)

        if oldFileName.endswith(".zip"):
            print(old_file_path)
            return {"path" : old_file_path, "kodeToko" : (oldFileName.rsplit('.', 1)[0])[-4:]}
        
        if "." in oldFileName:
            oldFileName = oldFileName.replace(".", "")

        newFileName = oldFileName + ext
        new_file_path = os.path.join(file_path, newFileName)
        os.rename(old_file_path, new_file_path)
        return {"path" : new_file_path, "kodeToko" : (oldFileName.rsplit('.', 1)[0])[-4:]}
    
    except FileNotFoundError:
        print("File tidak ditemukan.")
        raise
    except OSError as e:
        print("Terjadi kesalahan saat mengubah nama file:", e)
        raise

def findingFileWithPrefix(folder, prefix):

    files = []
    for file in os.listdir(folder):
        if file.startswith(prefix):
            files.append(os.path.join(folder, file))
    return files

def deleteFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
        print(f"File {filePath} berhasil dihapus.")
    else:
        print(f"File {filePath} tidak ditemukan.")

def deleteFolder(folderPath):
    if os.path.exists(folderPath):
        shutil.rmtree(folderPath)
        print(f"Folder {folderPath} berhasil dihapus.")
    else:
        print(f"Folder {folderPath} tidak ditemukan.")

def fields(cursor):
  
    results = {}
    column = 0
    for d in cursor.description:
        results[d[0]] = column
        column = column + 1
 
    return results

def queryDataFound(tableName, condition, db="pg"):
    try:

        if db == "pg" :
            cursor = pgCursor
        else :
            cursor = pgCursor


        querySelect = f"""
            SELECT COUNT(*) AS JUMLAH FROM {tableName} WHERE {condition}
            """
        cursor.execute(querySelect)
        result =  cursor.fetchone()

        if db == "oracle" :
            field_map = fields(cursor)
            jumlah = result[field_map['JUMLAH']]
        else:
            jumlah = result['JUMLAH']

        if jumlah > 0 :
            return True
        else :
            return False
    except Exception as e:
        return create_error_response(
            message="Terjadi Kesalahan", error_message=f"Error: {e}"
        )


def getEnvVariable(key, default=None):
    return os.getenv(key, default)

# def insertSqlFailedJobLog(listData, typeJob):

#     failedProcess_json = json.dumps(listData)

#     query = """
#         INSERT INTO tbtr_failed_job_log (type_job, data)
#         VALUES (%s, %s)
#     """

#     sqlCursor.execute(query, (typeJob, failedProcess_json))
#     connection.commit()

#     sqlCursor.close()
#     connection.close()


def parse_dt9_filename(filename: str) -> datetime:
    try:
        # contoh: DT96219O.5CH

        # FIX karena slicing harus jelas
        year_last_digit = filename[3]
        month_hex = filename[4]
        day = filename[5:7] #5:7 artinya ambil 5 sampai 6

        # convert HEX ke DEC
        month = int(month_hex, 16)

        # asumsi abad sekarang (2000–2099)
        current_year = datetime.now().year
        year = int(str(current_year)[:3] + year_last_digit)

        result = datetime(year, month, int(day))
        print("DT9 TANGGAL= ",result.strftime("%d%m%Y"))
        return result

    except Exception as e:
        raise ValueError(f"Format filename tidak valid: {filename}")
    
def move_replace(src: Path, dst_dir: Path,  logger: logging.Logger):
    try:
        dst_file = dst_dir / src.name

        if dst_file.exists():
            dst_file.unlink()
            logger.warning(f"⚠ File sudah ada, dihapus dari : {dst_dir}")

        shutil.move(str(src), str(dst_file))

        return dst_file
    except Exception as e:
        raise

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # mode exe
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        else:
            return Path(sys.executable).parent
    else:
        # mode python normal
        return Path(__file__).resolve().parent.parent
    
def setup_logger(name: str = "spread_dt9") -> logging.Logger:
    base_dir = get_base_dir()

    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "Spread_dt9_job.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # prevent duplicate handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=90,
        encoding="utf-8"
    )

    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger

