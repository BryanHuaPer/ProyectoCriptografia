# pyrefly: ignore [missing-import]
import flet as ft
import asyncio

import motor_cripto as mc
import historial_db as db

# ── Paleta centralizada (para los pocos lugares que necesitan color manual) ──
_COLOR_EXITO = "#4CAF50"
_COLOR_ADVERTENCIA = "#FFA726"


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

    # Helper para estandarizar bordes
    def default_text_field(**kwargs):
        return ft.TextField(border_color=ft.Colors.OUTLINE, **kwargs)

    # ================================================================
    #  PESTAÑA 1: TEXTO
    # ================================================================
    campo_texto = default_text_field(
        label="Texto a procesar", multiline=True, min_lines=5, max_lines=8, expand=True,
    )
    campo_clave_texto = default_text_field(label="Clave (solo letras)", width=300)
    fortaleza_texto = ft.Text(value="", size=12)
    resultado_texto = default_text_field(
        label="Resultado", multiline=True, min_lines=5, max_lines=8, read_only=True, expand=True,
    )
    mensaje_texto = ft.Text(value="", size=13)
    barra_progreso_texto = ft.ProgressBar(width=400, visible=False)

    def actualizar_fortaleza_texto(e):
        info = mc.evaluar_fortaleza_clave(campo_clave_texto.value)
        fortaleza_texto.value = f"Fortaleza: {info['nivel']} — {info['detalle']}"
        mapa = {"grey": ft.Colors.OUTLINE, "red": ft.Colors.ERROR,
                "orange": _COLOR_ADVERTENCIA, "green": _COLOR_EXITO}
        fortaleza_texto.color = mapa.get(info["color"], ft.Colors.ON_SURFACE)
        page.update()

    campo_clave_texto.on_change = actualizar_fortaleza_texto

    def procesar_texto(modo: str):
        mensaje_texto.value = ""
        mensaje_texto.color = ft.Colors.ERROR
        try:
            texto_actual = campo_texto.value or ""
            clave_actual = campo_clave_texto.value or ""
            if not texto_actual:
                raise ValueError("Ingresa un texto primero.")
            salida = mc.vigenere(texto_actual, clave_actual, modo)
            resultado_texto.value = salida
            
            # Registrar solo si cambió algo respecto a la última vez
            prev = estado["texto"]
            if (prev["ultimo_texto"] != texto_actual or 
                prev["ultima_clave"] != clave_actual or 
                prev["ultimo_modo"] != modo):
                db.registrar_operacion(
                    accion="Cifrar" if modo == "cifrar" else "Descifrar",
                    metodo="Vigenère", origen="Texto",
                )
                prev["ultimo_texto"] = texto_actual
                prev["ultima_clave"] = clave_actual
                prev["ultimo_modo"] = modo

        except ValueError as e:
            mensaje_texto.value = str(e)
            resultado_texto.value = ""
        page.update()

    async def cifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        await asyncio.sleep(0.4) # Pausa para UX de carga
        procesar_texto("cifrar")
        barra_progreso_texto.visible = False
        page.update()

    async def descifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        await asyncio.sleep(0.4) # Pausa para UX de carga
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

    # ================================================================
    #  PESTAÑA 2: ARCHIVO
    # ================================================================
    contenido_archivo = {"texto": None, "nombre": None}
    nombre_archivo_txt = ft.Text(value="Ningún archivo seleccionado", italic=True)
    campo_clave_archivo = default_text_field(label="Clave (solo letras)", width=300)
    resultado_archivo = default_text_field(
        label="Resultado", multiline=True, min_lines=6, max_lines=10,
        read_only=True, expand=True,
    )
    mensaje_archivo = ft.Text(value="", size=13)
    barra_progreso_archivo = ft.ProgressBar(width=400, visible=False)

    def procesar_archivo(modo: str):
        mensaje_archivo.value = ""
        mensaje_archivo.color = ft.Colors.ERROR
        try:
            texto_actual = contenido_archivo["texto"]
            clave_actual = campo_clave_archivo.value or ""
            if not texto_actual:
                raise ValueError("Primero selecciona un archivo .txt")
            salida = mc.vigenere(texto_actual, clave_actual, modo)
            resultado_archivo.value = salida

            prev = estado["archivo"]
            if (prev["ultimo_texto"] != texto_actual or 
                prev["ultima_clave"] != clave_actual or 
                prev["ultimo_modo"] != modo):
                db.registrar_operacion(
                    accion="Cifrar" if modo == "cifrar" else "Descifrar",
                    metodo="Vigenère", origen="Archivo",
                )
                prev["ultimo_texto"] = texto_actual
                prev["ultima_clave"] = clave_actual
                prev["ultimo_modo"] = modo

        except ValueError as e:
            mensaje_archivo.value = str(e)
            resultado_archivo.value = ""
        page.update()

    async def cifrar_archivo_click(e):
        barra_progreso_archivo.visible = True
        page.update()
        await asyncio.sleep(0.4)
        procesar_archivo("cifrar")
        barra_progreso_archivo.visible = False
        page.update()

    async def descifrar_archivo_click(e):
        barra_progreso_archivo.visible = True
        page.update()
        await asyncio.sleep(0.4)
        procesar_archivo("descifrar")
        barra_progreso_archivo.visible = False
        page.update()

    async def seleccionar_archivo_click(e):
        archivos = await ft.FilePicker().pick_files(
            allow_multiple=False, allowed_extensions=["txt"],
        )
        if archivos:
            ruta = archivos[0].path
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido_archivo["texto"] = f.read()
                contenido_archivo["nombre"] = archivos[0].name
                nombre_archivo_txt.value = f"✔ {archivos[0].name}"
                mensaje_archivo.value = ""
            except Exception as ex:
                mensaje_archivo.value = f"Error al leer: {ex}"
                contenido_archivo["texto"] = None
        page.update()

    async def guardar_resultado_click(e):
        if resultado_archivo.value:
            ruta = await ft.FilePicker().save_file(
                dialog_title="Guardar resultado como...", file_name="resultado.txt",
            )
            if ruta:
                try:
                    with open(ruta, "w", encoding="utf-8") as f:
                        f.write(resultado_archivo.value)
                    mensaje_archivo.value = "✔ Archivo guardado correctamente."
                    mensaje_archivo.color = _COLOR_EXITO
                except Exception as ex:
                    mensaje_archivo.value = f"Error al guardar: {ex}"
                    mensaje_archivo.color = ft.Colors.ERROR
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
                ft.Button("Guardar resultado como .txt", icon=ft.Icons.SAVE,
                          on_click=guardar_resultado_click),
            ],
            spacing=12,
        ),
        padding=20,
    )

    # ================================================================
    #  PESTAÑA 3: HISTORIAL
    # ================================================================
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

    # ================================================================
    #  PESTAÑA 4: DEMOSTRACIÓN (paso a paso del algoritmo)
    # ================================================================
    demo_texto = default_text_field(
        label="Texto de ejemplo", value="HOLA MUNDO", width=350,
    )
    demo_clave = default_text_field(
        label="Clave de ejemplo", value="CLAVE", width=250,
    )
    demo_modo = ft.Dropdown(
        label="Modo", width=180, value="cifrar", border_color=ft.Colors.OUTLINE,
        options=[ft.dropdown.Option("cifrar"), ft.dropdown.Option("descifrar")],
    )
    demo_mensaje = ft.Text(value="", size=14, color=ft.Colors.ERROR)
    demo_resultado_final = ft.Text(value="", size=22, weight=ft.FontWeight.BOLD)

    demo_tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("#", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Letra", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Clave", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Pos.", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Pos. Clave", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Op.", size=16, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Resultado", size=16, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        column_spacing=20,
    )

    def usar_ultima_operacion(e):
        prev = estado["texto"]
        if prev["ultimo_texto"] and prev["ultima_clave"]:
            # Recortamos el texto a 50 caracteres máximo para la demo para no saturar
            demo_texto.value = prev["ultimo_texto"][:50]
            demo_clave.value = prev["ultima_clave"]
            demo_modo.value = prev["ultimo_modo"]
            demo_mensaje.value = "✔ Cargado desde la pestaña Texto."
            demo_mensaje.color = _COLOR_EXITO
            ejecutar_demo(None)
        else:
            demo_mensaje.value = "Aún no hay una operación previa en la pestaña Texto."
            demo_mensaje.color = _COLOR_ADVERTENCIA
        page.update()

    def ejecutar_demo(e):
        if e is not None:
            # Si el usuario hace clic en el botón de Ejecutar, reseteamos mensajes previos
            demo_mensaje.value = ""
        
        demo_resultado_final.value = ""
        demo_tabla.rows = []
        try:
            texto = demo_texto.value or ""
            clave = demo_clave.value or ""
            modo = demo_modo.value or "cifrar"

            pasos = mc.vigenere_pasos(texto, clave, modo, limite=15)
            resultado_completo = mc.vigenere(texto, clave, modo)

            for i, p in enumerate(pasos, 1):
                demo_tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(i), size=16)),
                        ft.DataCell(ft.Text(p["letra_original"], size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color="#00BCD4")),
                        ft.DataCell(ft.Text(p["letra_clave"], size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color="#FFA726")),
                        ft.DataCell(ft.Text(str(p["pos_texto"]), size=16)),
                        ft.DataCell(ft.Text(str(p["pos_clave"]), size=16)),
                        ft.DataCell(ft.Text(
                            f"({p['pos_texto']} {p['operacion']} {p['pos_clave']}) % 26",
                            size=14,
                        )),
                        ft.DataCell(ft.Text(p["resultado"], size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=_COLOR_EXITO)),
                    ])
                )

            demo_resultado_final.value = f"Resultado completo: {resultado_completo}"

        except ValueError as ex:
            demo_mensaje.value = str(ex)
            demo_mensaje.color = ft.Colors.ERROR
        page.update()

    tab_demo = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Modo Demostración — Paso a paso",
                    size=20, weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Visualiza cómo el algoritmo Vigenère transforma cada letra.",
                    size=14, italic=True, color=ft.Colors.OUTLINE,
                ),
                ft.Divider(height=10),
                ft.Row(
                    [
                        ft.Button("Usar mi última operación", icon=ft.Icons.SYNC, on_click=usar_ultima_operacion)
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Row(
                    [demo_texto, demo_clave, demo_modo],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                ),
                ft.Row(
                    [ft.Button("Ejecutar demostración", icon=ft.Icons.PLAY_ARROW,
                               on_click=ejecutar_demo)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                demo_mensaje,
                ft.Column(
                    [demo_tabla],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                ft.Divider(height=5),
                demo_resultado_final,
            ],
            spacing=10,
        ),
        padding=20,
    )

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
                    controls=[tab_texto, tab_archivo, tab_historial, tab_demo],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        on_change=lambda e: refrescar_historial() if tabs.selected_index == 2 else None,
    )

    page.add(
        ft.Text("CryptoVA — Cifrado Vigenère", size=26,
                weight=ft.FontWeight.BOLD, color="#00BCD4"),
        tabs,
    )

    refrescar_historial()


if __name__ == "__main__":
    ft.run(main)