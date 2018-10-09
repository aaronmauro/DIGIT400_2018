import pymysql

def connection():
    conn = pymysql.connect(host='localhost',
                            user='root',
                            passwd = 'english4',
                            db='demo')
    c = conn.cursor()

    return c, conn