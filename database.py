import os
import mysql.connector

def conectar():
    banco = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "1005yukio"),
        database=os.environ.get("DB_NAME", "tt_performance"),
        port=int(os.environ.get("DB_PORT", 3306))
    )

    return banco