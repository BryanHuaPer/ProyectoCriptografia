# pyrefly: ignore [missing-import]
import flet as ft

import motor_cripto as mc
import historial_db as db


def main(page: ft.Page):
    page.title = "Cifrado Vigenère"
    page.window.width = 750
    page.window.height = 700
    page.window.resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    db.inicializar_db()

    # ========== PESTAÑA: TEXTO ==========
    campo_texto = ft.TextField(
        label="Texto a procesar", multiline=True, min_lines=5, max_lines=8, expand=True,
    )
    campo_clave_texto = ft.TextField(label="Clave (solo letras)", width=300)
    fortaleza_texto = ft.Text(value="", size=12)
    resultado_texto = ft.TextField(
        label="Resultado", multiline=True, min_lines=5, max_lines=8, read_only=True, expand=True,
    )
    mensaje_texto = ft.Text(value="", color=ft.Colors.RED)
    barra_progreso_texto = ft.ProgressBar(width=400, visible=False)

    def actualizar_fortaleza_texto(e):
        info = mc.evaluar_fortaleza_clave(campo_clave_texto.value)
        fortaleza_texto.value = f"Fortaleza de clave: {info['nivel']} — {info['detalle']}"
        fortaleza_texto.color = info["color"]
        page.update()

    campo_clave_texto.on_change = actualizar_fortaleza_texto

    def procesar_texto(modo: str):
        mensaje_texto.value = ""
        try:
            if not campo_texto.value:
                raise ValueError("Ingresa un texto primero.")
            salida = mc.vigenere(campo_texto.value, campo_clave_texto.value, modo)
            resultado_texto.value = salida
            db.registrar_operacion(
                accion="Cifrar" if modo == "cifrar" else "Descifrar",
                metodo="Vigenère",
                origen="Texto",
            )
        except ValueError as e:
            mensaje_texto.value = str(e)
            resultado_texto.value = ""
        page.update()

    def cifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        procesar_texto("cifrar")
        barra_progreso_texto.visible = False
        page.update()

    def descifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        procesar_texto("descifrar")
        barra_progreso_texto.visible = False
        page.update()

    tab_texto = ft.Container(
        content=ft.Column(
            [
                campo_texto,
                campo_clave_texto,
                fortaleza_texto,
                ft.Row(
                    [
                        ft.Button("Cifrar", icon=ft.Icons.LOCK, on_click=cifrar_texto_click),
                        ft.Button("Descifrar", icon=ft.Icons.LOCK_OPEN, on_click=descifrar_texto_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                barra_progreso_texto,
                mensaje_texto,
                resultado_texto,
            ],
            spacing=12,
        ),
        padding=20,
    )

    # ========== PESTAÑA: ARCHIVO ==========
    contenido_archivo = {"texto": None, "nombre": None}
    nombre_archivo_txt = ft.Text(value="Ningún archivo seleccionado", italic=True)
    campo_clave_archivo = ft.TextField(label="Clave (solo letras)", width=300)
    resultado_archivo = ft.TextField(
        label="Resultado", multiline=True, min_lines=6, max_lines=10, read_only=True, expand=True,
    )
    mensaje_archivo = ft.Text(value="", color=ft.Colors.RED)
    barra_progreso_archivo = ft.ProgressBar(width=400, visible=False)

    def procesar_archivo(modo: str):
        mensaje_archivo.value = ""
        try:
            if not contenido_archivo["texto"]:
                raise ValueError("Primero selecciona un archivo .txt")
            salida = mc.vigenere(contenido_archivo["texto"], campo_clave_archivo.value, modo)
            resultado_archivo.value = salida
            db.registrar_operacion(
                accion="Cifrar" if modo == "cifrar" else "Descifrar",
                metodo="Vigenère",
                origen="Archivo",
            )
        except ValueError as e:
            mensaje_archivo.value = str(e)
            resultado_archivo.value = ""
        page.update()

    def cifrar_archivo_click(e):
        barra_progreso_archivo.visible = True
        page.update()
        procesar_archivo("cifrar")
        barra_progreso_archivo.visible = False
        page.update()

    def descifrar_archivo_click(e):
        barra_progreso_archivo.visible = True
        page.update()
        procesar_archivo("descifrar")
        barra_progreso_archivo.visible = False
        page.update()

    # --- FilePicker: seleccionar archivo (async, sin on_result ni overlay) ---
    async def seleccionar_archivo_click(e):
        archivos = await ft.FilePicker().pick_files(
            allow_multiple=False,
            allowed_extensions=["txt"],
        )
        if archivos:
            ruta = archivos[0].path
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido_archivo["texto"] = f.read()
                contenido_archivo["nombre"] = archivos[0].name
                nombre_archivo_txt.value = f"Archivo cargado: {archivos[0].name}"
                mensaje_archivo.value = ""
            except Exception as ex:
                mensaje_archivo.value = f"Error al leer el archivo: {ex}"
                contenido_archivo["texto"] = None
        page.update()

    # --- FilePicker: guardar resultado (async, sin on_result ni overlay) ---
    async def guardar_resultado_click(e):
        if resultado_archivo.value:
            ruta_guardado = await ft.FilePicker().save_file(
                dialog_title="Guardar resultado como...",
                file_name="resultado.txt",
            )
            if ruta_guardado:
                try:
                    with open(ruta_guardado, "w", encoding="utf-8") as f:
                        f.write(resultado_archivo.value)
                    mensaje_archivo.value = "Archivo guardado correctamente."
                    mensaje_archivo.color = ft.Colors.GREEN
                except Exception as ex:
                    mensaje_archivo.value = f"Error al guardar: {ex}"
                    mensaje_archivo.color = ft.Colors.RED
                page.update()

    tab_archivo = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button(
                            "Seleccionar archivo .txt",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=seleccionar_archivo_click,
                        ),
                        nombre_archivo_txt,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                campo_clave_archivo,
                ft.Row(
                    [
                        ft.Button("Cifrar", icon=ft.Icons.LOCK, on_click=cifrar_archivo_click),
                        ft.Button("Descifrar", icon=ft.Icons.LOCK_OPEN, on_click=descifrar_archivo_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                barra_progreso_archivo,
                mensaje_archivo,
                resultado_archivo,
                ft.Button("Guardar resultado como .txt", icon=ft.Icons.SAVE, on_click=guardar_resultado_click),
            ],
            spacing=12,
        ),
        padding=20,
    )

    # ========== PESTAÑA: HISTORIAL ==========
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

    tab_historial = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Button("Actualizar", icon=ft.Icons.REFRESH, on_click=refrescar_historial),
                        ft.Button(
                            "Limpiar historial",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=limpiar_historial_click,
                            color=ft.Colors.RED,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Column([tabla_historial], scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            spacing=12,
        ),
        padding=20,
    )

    # ========== LAYOUT FINAL ==========
    tabs = ft.Tabs(
        length=3,
        selected_index=0,
        expand=True,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Texto", icon=ft.Icons.TEXT_FIELDS),
                        ft.Tab(label="Archivo", icon=ft.Icons.FOLDER),
                        ft.Tab(label="Historial", icon=ft.Icons.HISTORY),
                    ],
                ),
                ft.TabBarView(
                    controls=[tab_texto, tab_archivo, tab_historial],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        on_change=lambda e: refrescar_historial() if tabs.selected_index == 2 else None,
    )

    page.add(
        ft.Text("Cifrado y Descifrado Vigenère", size=26, weight=ft.FontWeight.BOLD),
        tabs,
    )

    refrescar_historial()


ft.run(main)