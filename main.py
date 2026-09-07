# pyrefly: ignore [missing-import]
import flet as ft
import historial_db as db

from tab_texto import construir_tab_texto
from tab_archivo import construir_tab_archivo
from tab_historial import construir_tab_historial
from tab_demo import construir_tab_demo

def main(page: ft.Page):
    page.title = "CryptoVA — Cifrado Vigenère"
    page.window.width = 850
    page.window.height = 760
    page.window.resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # ── Tema centralizado ──
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed="#0D47A1",
        color_scheme=ft.ColorScheme(
            primary="#0D47A1",
            secondary="#00BCD4",
            surface="#1E1E2E",
            on_surface="#E0E0E0",
            error="#EF5350",
            on_error="#FFFFFF",
            primary_container="#1A5276",
            on_primary="#FFFFFF",
            surface_container="#252540",
            surface_container_high="#2D2D4A",
            outline="#555577", # Borde visible por defecto
        ),
        font_family="Segoe UI",
    )
    page.dark_theme = page.theme  # mismo tema en modo oscuro

    db.inicializar_db()

    # Variables de estado para evitar historiales duplicados y para la demo
    estado = {
        "texto": {"ultimo_texto": "", "ultima_clave": "", "ultimo_modo": ""},
        "archivo": {"ultimo_texto": "", "ultima_clave": "", "ultimo_modo": ""}
    }

    # Inicializar componentes de pestañas modulares
    tab_historial_view, refrescar_historial_fn = construir_tab_historial(page)
    
    tab_texto_view = construir_tab_texto(page, estado)
    tab_archivo_view = construir_tab_archivo(page, estado)
    tab_demo_view = construir_tab_demo(page, estado)

    # ================================================================
    #  LAYOUT FINAL — 4 pestañas
    # ================================================================
    tabs = ft.Tabs(
        length=4,
        selected_index=0,
        expand=True,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Texto", icon=ft.Icons.TEXT_FIELDS),
                        ft.Tab(label="Archivo", icon=ft.Icons.FOLDER),
                        ft.Tab(label="Historial", icon=ft.Icons.HISTORY),
                        ft.Tab(label="Demostración", icon=ft.Icons.SCHOOL),
                    ],
                ),
                ft.TabBarView(
                    controls=[tab_texto_view, tab_archivo_view, tab_historial_view, tab_demo_view],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        on_change=lambda e: refrescar_historial_fn() if tabs.selected_index == 2 else None,
    )

    # Contenedor central para evitar que se estire demasiado en pantallas anchas
    contenedor_principal = ft.Container(
        width=1100,
        expand=True,
        content=ft.Column(
            [
                ft.Text("CryptoVA — Cifrado Vigenère", size=26,
                        weight=ft.FontWeight.BOLD, color="#00BCD4"),
                tabs,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        alignment=ft.Alignment.TOP_CENTER
    )

    page.add(contenedor_principal)

    refrescar_historial_fn()


if __name__ == "__main__":
    ft.run(main)