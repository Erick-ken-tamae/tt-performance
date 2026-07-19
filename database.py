import mysql.connector

def conectar():
    banco =  mysql.connector.connect(
        host="localhost",
        user = "root",
        password = "1005yukio",
        database="tt_performance"
    )
    
    return banco