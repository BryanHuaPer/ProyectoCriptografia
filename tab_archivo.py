import flet as ft
import asyncio
import time

import motor_cripto as mc
import historial_db as db
import ui_componentes as ui

def construir_tab_archivo(page: ft.Page, estado: dict) -> ft.Container:
    contenido_archivo = {"texto": None, "nombre": None, "resultado_completo": None}
    
    nombre_archivo_txt = ft.Text(value="Ningún archivo seleccionado", italic=True)
    campo_clave_archivo = ui.default_text_field(label="Clave (solo letras)", width=300)
    fortaleza_archivo = ft.Text(value="", size=12)
    
    mensaje_archivo = ft.Text(value="", size=13)
    barra_progreso_archivo = ft.ProgressBar(width=400, visible=False)

    contenedor_comp, etiqueta_op, campo_izq, campo_der = ui.construir_vista_comparacion(
        titulo_izq="Contenido Original", titulo_der="Resultado"
    )

    campo_clave_archivo.on_change = lambda e: ui.crear_indicador_fortaleza(campo_clave_archivo, fortaleza_archivo, page)

    def procesar_archivo(modo: str):
        mensaje_archivo.value = ""
        mensaje_archivo.color = ft.Colors.ERROR
        contenedor_comp.visible = False
        
        try:
            texto_actual = contenido_archivo["texto"]
            clave_actual = campo_clave_archivo.value or ""
            if not texto_actual:
                raise ValueError("Primero selecciona un archivo .txt")
            
            t0 = time.perf_counter()
            salida = mc.cifrar_mixto(texto_actual, clave_actual) if modo == "cifrar" else mc.descifrar_mixto(texto_actual, clave_actual)
            duracion = time.perf_counter() - t0
            contenido_archivo["resultado_completo"] = salida
            
            campo_izq.value = ui.truncar_visual(texto_actual)
            campo_der.value = ui.truncar_visual(salida)
            
            etiqueta_op.value = f"[{'Cifrado Mixto' if modo == 'cifrar' else 'Descifrado Mixto'}] • Clave: {'●' * len(clave_actual)} • Tiempo: {duracion:.3f} s"
            etiqueta_op.visible = True
            contenedor_comp.visible = True

            prev = estado["archivo"]
            if (prev["ultimo_texto"] != texto_actual or 
                prev["ultima_clave"] != clave_actual or 
                prev["ultimo_modo"] != modo):
                db.registrar_operacion(
                    accion="Cifrar" if modo == "cifrar" else "Descifrar",
                    metodo="Mixto (Vigenère progresivo + Transposición)", origen="Archivo",
                )
                prev["ultimo_texto"] = texto_actual
                prev["ultima_clave"] = clave_actual
                prev["ultimo_modo"] = modo

        except ValueError as e:
            mensaje_archivo.value = str(e)
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
                contenido_archivo["resultado_completo"] = None
                
                texto_cargado = contenido_archivo["texto"]
                preview = (texto_cargado[:100] + "...") if len(texto_cargado) > 100 else texto_cargado
                preview_escaped = preview.replace('\n', ' ')
                nombre_archivo_txt.value = f"✔ {archivos[0].name}\nVista previa: {preview_escaped}"
                
                mensaje_archivo.value = ""
                contenedor_comp.visible = False
            except Exception as ex:
                mensaje_archivo.value = f"Error al leer: {ex}"
                contenido_archivo["texto"] = None
                contenido_archivo["resultado_completo"] = None
        page.update()

    async def guardar_resultado_click(e):
        if contenido_archivo["resultado_completo"]:
            ruta = await ft.FilePicker().save_file(
                dialog_title="Guardar resultado como...", file_name="resultado.txt",
            )
            if ruta:
                try:
                    with open(ruta, "w", encoding="utf-8") as f:
                        f.write(contenido_archivo["resultado_completo"])
                    mensaje_archivo.value = "✔ Archivo guardado correctamente."
                    mensaje_archivo.color = ui.COLOR_EXITO
                except Exception as ex:
                    mensaje_archivo.value = f"Error al guardar: {ex}"
                    mensaje_archivo.color = ft.Colors.ERROR
                page.update()

    return ft.Container(
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
                fortaleza_archivo,
                ft.Row(
                    [
                        ft.Button("Cifrar", icon=ft.Icons.LOCK, on_click=cifrar_archivo_click),
                        ft.Button("Descifrar", icon=ft.Icons.LOCK_OPEN, on_click=descifrar_archivo_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                barra_progreso_archivo,
                mensaje_archivo,
                contenedor_comp,
                ft.Button("Guardar resultado como .txt", icon=ft.Icons.SAVE,
                          on_click=guardar_resultado_click),
            ],
            spacing=12,
        ),
        padding=20,
    )
