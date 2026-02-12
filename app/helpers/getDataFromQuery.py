from app.helpers.createConnection import getPostgresConnection
from app.helpers.mdl import fields
def selectMasterToko():
    try:
        connection = getPostgresConnection()
        cursor = connection.cursor()

        cursor.execute("""
            select * FROM tbmaster_tokoigr_interface
            join tbmaster_cabang on cab_kodecabang = tko_kodecabang 
            where tko_namasbu = 'OMI'
            AND tko_tgltutup IS null;
            """)
        items = cursor.fetchall()
        dataFields = fields(cursor)

        return {"records":items,"fields":dataFields}
    except Exception as e:
        raise