from pg8000.dbapi import connect

def get_postgres_conn():
    return connect(
        user="postgres",
        password="123456",
        host="localhost",
        port=5432,
        database="ADM_New_Project"
    )
