import flet as ft
import historial_db as db

def construir_tab_historial(page: ft.Page):
    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha y hora")),
            ft.DataColumn(ft.Text("Acción")),
            ft.DataColumn(ft.Text("Método")),
            ft.DataColumn(ft.Text("Origen")),
        ],
        rows=[],
    )

    def refrescar_historial(e=None):
        filas = db.obtener_historial()
        tabla_historial.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(fecha)),
                ft.DataCell(ft.Text(accion)),
                ft.DataCell(ft.Text(metodo)),
                ft.DataCell(ft.Text(origen)),
            ])
            for fecha, accion, metodo, origen in filas
        ]
        page.update()

    def limpiar_historial_click(e):
        db.limpiar_historial()
        refrescar_historial()

    contenedor = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button("Actualizar", icon=ft.Icons.REFRESH,
                                  on_click=refrescar_historial),
                        ft.Button("Limpiar historial", icon=ft.Icons.DELETE_OUTLINE,
                                  on_click=limpiar_historial_click, color=ft.Colors.ERROR),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Column([tabla_historial], scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=12,
        ),
        padding=20,
    )
    
    return contenedor, refrescar_historial
