import psycopg

try:
    conn = psycopg.connect(
        dbname="dictionary",
        user="postgres",
        password="123321",
        host="localhost",
        port="5432",
        connect_timeout=3
    )
    print("Bog'landi!")
except Exception as e:
    print("Xato:", e)
