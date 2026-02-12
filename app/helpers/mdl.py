from app.packages import os, shutil
from app.helpers.handlerResponse import *
from app.helpers.createConnection import getPostgresConnection

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