
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
    FTP_DIR  = "/igrcpg/dt9bak/06052016"

    # CONNECT FTP
    ftp = FTP(FTP_HOST, timeout=30)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)
    print("Connected to FTP")
    # PINDAH DIRECTORY
    ftp.cwd(FTP_DIR)
    # AMBIL LIST FILE
    files = ftp.nlst()

    print("List file di FTP:")
    dt9Files = [f for f in files if f.startswith("DT9")]

    # for f in dt9Files:
    #     print(f)
    listKodeToko = [f.replace(".", "")[-4:] for f in dt9Files]  
    # for r in listKodeToko:
    #     print(r)

    PathFolderToko = Path(os.getenv("PUBLIC_DIR"))
    listKodeTokoSFTP = [
        f.name for f in PathFolderToko.iterdir() if f.is_dir()
    ]
    
    missing_toko = list(set(listKodeToko) - set(listKodeTokoSFTP))

    for m in missing_toko:
        print(f"Tidak ada di lokal: {m}")

    return {
        "status": "success",
        "toko_kurang": missing_toko,
        "total_toko_kurang": len(missing_toko),
        "total_toko_ftp": len(listKodeToko),
        "total_toko_sftp": len(listKodeTokoSFTP),
    }


   except Exception as e:
        print(f"Error during Proced ABSENSI DT9: {e}")
        return create_error_response(
            message="Terjadi Kesalahan",
            error_message=f"Error: {e}"
        )
        