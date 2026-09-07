
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path


def _obtener_db_path() -> Path:
    """
    Devuelve la ruta de la base de datos.
    - En desarrollo: usa %LOCALAPPDATA%/CryptoVA/cryptova.db (o junto al .py si falla)
    - Empaquetado (flet build): misma lógica, LOCALAPPDATA siempre existe en Windows
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        carpeta = Path(local_app_data) / "CryptoVA"
    else:
        # Fallback: junto al archivo fuente (Linux/Mac o entorno atípico)
        carpeta = Path(__file__).parent
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta / "cryptova.db"


DB_PATH = _obtener_db_path()


def inicializar_db():
    """Crea la base de datos y la tabla de historial si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            accion TEXT NOT NULL,
            metodo TEXT NOT NULL,
            origen TEXT NOT NULL
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
    """Borra todo el historial."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial")
    conn.commit()
    conn.close()