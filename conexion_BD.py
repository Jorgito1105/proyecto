import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "")
        )
        return conexion
    except mysql.connector.Error as error:
        print(f"Falla de conexión al servidor: {error}")
        return None