
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "cryptova.db"


def inicializar_db():
    """Crea la base de datos y la tabla de historial si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            accion TEXT NOT NULL,      -- 'Cifrar' o 'Descifrar'
            metodo TEXT NOT NULL,      -- 'Vigenère', etc.
            origen TEXT NOT NULL       -- 'Texto' o 'Archivo'
        )
    """)
    conn.commit()
    conn.close()


def registrar_operacion(accion: str, metodo: str, origen: str):
    """Inserta una nueva fila en el historial. No recibe ni guarda datos sensibles."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historial (fecha_hora, accion, metodo, origen) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), accion, metodo, origen),
    )
    conn.commit()
    conn.close()


def obtener_historial(limite: int = 100) -> list[tuple]:
    """Devuelve las últimas `limite` operaciones, más recientes primero."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fecha_hora, accion, metodo, origen FROM historial "
        "ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    filas = cursor.fetchall()
    conn.close()
    return filas


def limpiar_historial():
    """Borra todo el historial (útil para pruebas o para reiniciar antes de la demo)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial")
    conn.commit()
    conn.close()