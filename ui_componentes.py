import flet as ft
import motor_cripto as mc


COLOR_EXITO = "#4CAF50"
COLOR_ADVERTENCIA = "#FFA726"

def default_text_field(**kwargs):
    return ft.TextField(border_color=ft.Colors.OUTLINE, **kwargs)

def crear_indicador_fortaleza(campo_clave: ft.TextField, fortaleza_texto: ft.Text, page: ft.Page):
    """Evalúa la clave actual y actualiza el texto/color de fortaleza."""
    info = mc.evaluar_fortaleza_clave(campo_clave.value)
    fortaleza_texto.value = f"Fortaleza: {info['nivel']} — {info['detalle']}"
    mapa = {
        "grey": ft.Colors.OUTLINE, 
        "red": ft.Colors.ERROR,
        "orange": COLOR_ADVERTENCIA, 
        "green": COLOR_EXITO
    }
    fortaleza_texto.color = mapa.get(info["color"], ft.Colors.ON_SURFACE)
    page.update()

def truncar_visual(texto: str, limite: int = 5000) -> str:
    if not texto: return ""
    return (texto[:limite] + f"\n\n... (Texto truncado a {limite} caracteres para visualización)") if len(texto) > limite else texto

def construir_vista_comparacion(titulo_izq="Contenido Original", titulo_der="Resultado"):
    """
    Construye y retorna los elementos para una vista de comparación de dos columnas.
    Retorna: (contenedor_general, etiqueta_operacion, campo_izq, campo_der)
    """
    etiqueta_operacion = ft.Text(value="", size=18, weight=ft.FontWeight.W_900, color=ft.Colors.PRIMARY, visible=False)
    
    campo_izq = default_text_field(
        label=titulo_izq, multiline=True, min_lines=6, max_lines=10,
        read_only=True, expand=True
    )
    campo_der = default_text_field(
        label=titulo_der, multiline=True, min_lines=6, max_lines=10,
        read_only=True, expand=True
    )
    
    fila_campos = ft.Row(
        controls=[campo_izq, campo_der],
        expand=True
    )
    
    contenedor_general = ft.Column(
        controls=[
            ft.Row([etiqueta_operacion], alignment=ft.MainAxisAlignment.CENTER),
            fila_campos
        ],
        expand=True,
        visible=False
    )
    
    return contenedor_general, etiqueta_operacion, campo_izq, campo_der

def crear_celda_demo(texto, bold=False, color=None, size=16):
    return ft.Container(
        content=ft.Text(texto, size=size, weight=ft.FontWeight.BOLD if bold else None, color=color),
        expand=True,
        alignment=ft.Alignment.CENTER_LEFT
    )
