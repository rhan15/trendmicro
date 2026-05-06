
from flask import Blueprint,request
from app.helpers.handlerResponse import *
from app.helpers.mdl import *
from app.helpers.mdl import setup_logger
from ftplib import FTP

logger = setup_logger(name="absensi_dt9")



absensi_dt9_bp = Blueprint("absensi_dt9", __name__)
@absensi_dt9_bp.route('/proced-absensi-dt9')
def absensi_dt9():
   return proced_absensi_dt9()

def proced_absensi_dt9():
   try:
    
    print("Job penyebaran DT9 dijalankan")
    # CONFIG FTP
    FTP_HOST = "172.20.28.245"
    FTP_USER = "omiho"
    FTP_PASS = "omihoftp"
    FTP_DIR = f"/igrcpg/dt9bak/{datetime.now():%d%m}2016"

    # CONNECT FTP
    ftp = FTP(FTP_HOST, timeout=30)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)
    print("Connected to FTP")
    # PINDAH DIRECTORY
    ftp.cwd(FTP_DIR)
    # AMBIL LIST FILE
    files = ftp.nlst()

    FTP_dt9Files = [f for f in files if f.startswith("DT9")]

    baseDirectory = Path(os.getenv("PUBLIC_DIR"))
    directoryBackupToko = baseDirectory.joinpath(F"dt9_backup/{datetime.now():%d%m%Y}")
    if not directoryBackupToko.exists():
        logger.error(f"⛔ Folder toko tidak ada: {directoryBackupToko} → SKIP")
        return f"⛔ Folder toko tidak ada: {directoryBackupToko} → SKIP"
    
    SFTP_dt9Files = [
        f.name for f in directoryBackupToko.iterdir() if f.is_file() and f.name.startswith("DT9")
    ]

    missing_toko = list(set(FTP_dt9Files) - set(SFTP_dt9Files))

    return {
        "status": "success",
        "toko_kurang": missing_toko,
        "total_toko_kurang": len(missing_toko),
        "total_dt9_ftp": len(FTP_dt9Files),
        "total_dt9_sftp": len(SFTP_dt9Files),
    }


   except Exception as e:
        print(f"Error during Proced ABSENSI DT9: {e}")
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )
        