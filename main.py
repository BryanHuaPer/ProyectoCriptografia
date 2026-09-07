# pyrefly: ignore [missing-import]
import flet as ft
import string

ALFABETO = string.ascii_uppercase  # A-Z


def limpiar_clave(clave: str) -> str:
    """Deja solo letras en la clave y la pone en mayúsculas."""
    return "".join(c for c in clave.upper() if c in ALFABETO)


def vigenere(texto: str, clave: str, modo: str) -> str:
    """
    Cifra o descifra texto usando Vigenère.
    modo: 'cifrar' o 'descifrar'
    Los caracteres que no son letras (espacios, números, símbolos) se dejan igual.
    """
    clave = limpiar_clave(clave)
    if not clave:
        raise ValueError("La clave debe contener al menos una letra.")

    resultado = []
    indice_clave = 0

    for char in texto:
        char_upper = char.upper()
        if char_upper in ALFABETO:
            pos_texto = ALFABETO.index(char_upper)
            pos_clave = ALFABETO.index(clave[indice_clave % len(clave)])

            if modo == "cifrar":
                nueva_pos = (pos_texto + pos_clave) % 26
            else:  # descifrar
                nueva_pos = (pos_texto - pos_clave) % 26

            nueva_letra = ALFABETO[nueva_pos]
            # Mantener mayúscula/minúscula original
            resultado.append(nueva_letra if char.isupper() else nueva_letra.lower())
            indice_clave += 1
        else:
            # No es letra: se deja tal cual (espacios, números, puntuación)
            resultado.append(char)

    return "".join(resultado)


def main(page: ft.Page):
    page.title = "Cifrado Vigenère"
    page.window.width = 700
    page.window.height = 650
    page.window.resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # ---------- ESTADO PARA MANEJO DE ARCHIVOS ----------
    contenido_archivo = {"texto": None, "nombre": None}

    # ---------- COMPONENTES: PESTAÑA DE TEXTO ----------
    campo_texto = ft.TextField(
        label="Texto a procesar",
        multiline=True,
        min_lines=5,
        max_lines=8,
        expand=True,
    )
    campo_clave_texto = ft.TextField(
        label="Clave (solo letras)",
        width=300,
    )
    resultado_texto = ft.TextField(
        label="Resultado",
        multiline=True,
        min_lines=5,
        max_lines=8,
        read_only=True,
        expand=True,
    )
    mensaje_texto = ft.Text(value="", color=ft.Colors.RED)

    def procesar_texto(modo: str):
        mensaje_texto.value = ""
        try:
            if not campo_texto.value:
                raise ValueError("Ingresa un texto primero.")
            salida = vigenere(campo_texto.value, campo_clave_texto.value, modo)
            resultado_texto.value = salida
        except ValueError as e:
            mensaje_texto.value = str(e)
            resultado_texto.value = ""
        page.update()

    barra_progreso_texto = ft.ProgressBar(width=400, visible=False)

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
                ft.Row(
                    [
                        ft.Button(
                            "Cifrar",
                            icon=ft.Icons.LOCK,
                            on_click=cifrar_texto_click,
                        ),
                        ft.Button(
                            "Descifrar",
                            icon=ft.Icons.LOCK_OPEN,
                            on_click=descifrar_texto_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                barra_progreso_texto,
                mensaje_texto,
                resultado_texto,
            ],
            spacing=15,
        ),
        padding=20,
    )

    # ---------- COMPONENTES: PESTAÑA DE ARCHIVO ----------
    nombre_archivo_txt = ft.Text(value="Ningún archivo seleccionado", italic=True)
    campo_clave_archivo = ft.TextField(label="Clave (solo letras)", width=300)
    resultado_archivo = ft.TextField(
        label="Resultado",
        multiline=True,
        min_lines=6,
        max_lines=10,
        read_only=True,
        expand=True,
    )
    mensaje_archivo = ft.Text(value="", color=ft.Colors.RED)
    barra_progreso_archivo = ft.ProgressBar(width=400, visible=False)

    file_picker = ft.FilePicker()

    def procesar_archivo(modo: str):
        mensaje_archivo.value = ""
        try:
            if not contenido_archivo["texto"]:
                raise ValueError("Primero selecciona un archivo .txt")
            salida = vigenere(contenido_archivo["texto"], campo_clave_archivo.value, modo)
            resultado_archivo.value = salida
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

    async def seleccionar_archivo_click(e):
        archivos = await file_picker.pick_files(
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

    async def guardar_resultado_click(e):
        if resultado_archivo.value:
            ruta_guardado = await save_picker.save_file(
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

    save_picker = ft.FilePicker()

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
                        ft.Button(
                            "Cifrar",
                            icon=ft.Icons.LOCK,
                            on_click=cifrar_archivo_click,
                        ),
                        ft.Button(
                            "Descifrar",
                            icon=ft.Icons.LOCK_OPEN,
                            on_click=descifrar_archivo_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                barra_progreso_archivo,
                mensaje_archivo,
                resultado_archivo,
                ft.Button(
                    "Guardar resultado como .txt",
                    icon=ft.Icons.SAVE,
                    on_click=guardar_resultado_click,
                ),
            ],
            spacing=15,
        ),
        padding=20,
    )

    # ---------- LAYOUT FINAL CON PESTAÑAS ----------
    tabs = ft.Tabs(
        length=2,
        selected_index=0,
        expand=True,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Texto", icon=ft.Icons.TEXT_FIELDS),
                        ft.Tab(label="Archivo", icon=ft.Icons.FOLDER),
                    ]
                ),
                ft.TabBarView(
                    controls=[tab_texto, tab_archivo],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )

    page.add(
        ft.Text(
            "Cifrado y Descifrado Vigenère",
            size=26,
            weight=ft.FontWeight.BOLD,
        ),
        tabs,
    )


ft.run(main)