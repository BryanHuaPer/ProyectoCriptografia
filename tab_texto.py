import flet as ft
import asyncio
import time

import motor_cripto as mc
import historial_db as db
import ui_componentes as ui

def construir_tab_texto(page: ft.Page, estado: dict) -> ft.Container:
    campo_texto = ui.default_text_field(
        label="Texto a procesar", multiline=True, min_lines=5, max_lines=8, expand=True,
    )
    campo_clave_texto = ui.default_text_field(label="Clave (solo letras)", width=300)
    fortaleza_texto = ft.Text(value="", size=12)
    
    mensaje_texto = ft.Text(value="", size=13)
    barra_progreso_texto = ft.ProgressBar(width=400, visible=False)

    contenedor_comp, etiqueta_op, campo_izq, campo_der = ui.construir_vista_comparacion(
        titulo_izq="Texto Original", titulo_der="Resultado"
    )

    campo_clave_texto.on_change = lambda e: ui.crear_indicador_fortaleza(campo_clave_texto, fortaleza_texto, page)

    def procesar_texto(modo: str):
        mensaje_texto.value = ""
        mensaje_texto.color = ft.Colors.ERROR
        contenedor_comp.visible = False
        
        try:
            texto_actual = campo_texto.value or ""
            clave_actual = campo_clave_texto.value or ""
            if not texto_actual:
                raise ValueError("Ingresa un texto primero.")
            
            t0 = time.perf_counter()
            salida = mc.cifrar_mixto(texto_actual, clave_actual) if modo == "cifrar" else mc.descifrar_mixto(texto_actual, clave_actual)
            duracion = time.perf_counter() - t0
            
            campo_izq.value = ui.truncar_visual(texto_actual)
            campo_der.value = ui.truncar_visual(salida)
            
            etiqueta_op.value = f"[{'Cifrado Mixto' if modo == 'cifrar' else 'Descifrado Mixto'}] • Clave: {'●' * len(clave_actual)} • Tiempo: {duracion:.3f} s"
            etiqueta_op.visible = True
            contenedor_comp.visible = True
            
            prev = estado["texto"]
            if (prev["ultimo_texto"] != texto_actual or 
                prev["ultima_clave"] != clave_actual or 
                prev["ultimo_modo"] != modo):
                db.registrar_operacion(
                    accion="Cifrar" if modo == "cifrar" else "Descifrar",
                    metodo="Mixto (Vigenère progresivo + Transposición)", origen="Texto",
                )
                prev["ultimo_texto"] = texto_actual
                prev["ultima_clave"] = clave_actual
                prev["ultimo_modo"] = modo
                
        except ValueError as e:
            mensaje_texto.value = str(e)
        page.update()

    async def cifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        await asyncio.sleep(0.4)
        procesar_texto("cifrar")
        barra_progreso_texto.visible = False
        page.update()

    async def descifrar_texto_click(e):
        barra_progreso_texto.visible = True
        page.update()
        await asyncio.sleep(0.4)
        procesar_texto("descifrar")
        barra_progreso_texto.visible = False
        page.update()

    return ft.Container(
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
                contenedor_comp,
            ],
            spacing=12,
        ),
        padding=20,
    )
