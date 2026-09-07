import flet as ft
import asyncio

import motor_cripto as mc
import ui_componentes as ui

def construir_tab_demo(page: ft.Page, estado: dict) -> ft.Container:
    demo_texto = ui.default_text_field(
        label="Texto de ejemplo", value="HOLA MUNDO", width=250,
    )
    demo_clave = ui.default_text_field(
        label="Clave de ejemplo", value="CLAVE", width=150,
    )
    def validar_limite(e):
        valor = demo_limite.value
        solo_digitos = "".join(c for c in valor if c.isdigit())
        if solo_digitos:
            num = int(solo_digitos)
            if num > 40:
                demo_limite.value = "40"
            else:
                demo_limite.value = str(num)
        else:
            demo_limite.value = ""
        page.update()

    demo_limite = ui.default_text_field(
        label="Límite pasos", value="15", width=100, keyboard_type=ft.KeyboardType.NUMBER,
        on_change=validar_limite
    )
    demo_modo = ft.Dropdown(
        label="Modo", width=150, value="cifrar", border_color=ft.Colors.OUTLINE,
        options=[ft.dropdown.Option("cifrar"), ft.dropdown.Option("descifrar")],
    )
    
    mostrar_todo_checkbox = ft.Checkbox(
        label="Mostrar todo de inmediato", value=False
    )
    
    demo_mensaje = ft.Text(value="", size=14, color=ft.Colors.ERROR)
    demo_mensaje_truncamiento = ft.Text(value="", size=13, color=ft.Colors.OUTLINE, italic=True)
    demo_resultado_final = ft.Text(value="", size=22, weight=ft.FontWeight.BOLD)

    # Cabecera de la tabla manual
    demo_tabla_header = ft.Row(
        controls=[
            ui.crear_celda_demo("#", bold=True),
            ui.crear_celda_demo("Letra", bold=True),
            ui.crear_celda_demo("Clave", bold=True),
            ui.crear_celda_demo("Pos.", bold=True),
            ui.crear_celda_demo("Pos. Clave", bold=True),
            ui.crear_celda_demo("Op.", bold=True),
            ui.crear_celda_demo("Resultado", bold=True),
        ],
    )
    
    # Contenedor para las filas generadas dinámicamente
    demo_tabla_body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # Tabla completa envolviendo cabecera y filas
    demo_tabla_manual = ft.Column(
        controls=[
            demo_tabla_header,
            ft.Divider(height=1),
            demo_tabla_body
        ],
        expand=True
    )

    def usar_ultima_operacion(e):
        prev = estado["texto"]
        if prev["ultimo_texto"] and prev["ultima_clave"]:
            # Reemplazar saltos de línea por espacios para no romper el TextField unilínea
            texto_plano = prev["ultimo_texto"].replace("\n", " ")
            
            # Recortamos a 50 para la demo para no saturar si es muy largo
            demo_texto.value = texto_plano[:50]
            demo_clave.value = prev["ultima_clave"]
            demo_modo.value = prev["ultimo_modo"]
            demo_mensaje.value = "✔ Cargado desde la pestaña Texto."
            demo_mensaje.color = ui.COLOR_EXITO
            
            # Ejecutamos de forma asíncrona para la animación
            asyncio.create_task(ejecutar_demo_async(None))
        else:
            demo_mensaje.value = "Aún no hay una operación previa en la pestaña Texto."
            demo_mensaje.color = ui.COLOR_ADVERTENCIA
        page.update()

    async def ejecutar_demo_async(e):
        if e is not None:
            demo_mensaje.value = ""
        
        demo_resultado_final.value = ""
        demo_mensaje_truncamiento.value = ""
        demo_tabla_body.controls.clear()
        page.update()
        
        try:
            texto = demo_texto.value or ""
            clave = demo_clave.value or ""
            modo = demo_modo.value or "cifrar"
            
            # Validación de límite
            try:
                limite_val = int(demo_limite.value)
                limite_val = max(1, min(40, limite_val)) # Forzar entre 1 y 40
            except ValueError:
                limite_val = 15
            
            demo_limite.value = str(limite_val) # Actualizar UI al valor parseado seguro
            
            # Contar letras reales para el mensaje de truncamiento
            letras_totales = sum(1 for c in texto if c.upper() in mc.ALFABETO)

            pasos = mc.vigenere_pasos(texto, clave, modo, limite=limite_val)
            resultado_completo = mc.vigenere(texto, clave, modo)
            
            if letras_totales > limite_val:
                demo_mensaje_truncamiento.value = f"Mostrando las primeras {limite_val} letras de {letras_totales} totales."
                page.update()

            # Lógica de renderizado (animado o inmediato)
            inmediato = mostrar_todo_checkbox.value
            
            filas_a_agregar = []
            
            for i, p in enumerate(pasos, 1):
                fila = ft.Row(
                    controls=[
                        ui.crear_celda_demo(str(i)),
                        ui.crear_celda_demo(p["letra_original"], bold=True, color="#00BCD4"),
                        ui.crear_celda_demo(p["letra_clave"], bold=True, color="#FFA726"),
                        ui.crear_celda_demo(str(p["pos_texto"])),
                        ui.crear_celda_demo(str(p["pos_clave"])),
                        ui.crear_celda_demo(f"({p['pos_texto']} {p['operacion']} {p['pos_clave']}) % 26", size=14),
                        ui.crear_celda_demo(p["resultado"], bold=True, color=ui.COLOR_EXITO),
                    ]
                )
                
                if inmediato:
                    filas_a_agregar.append(fila)
                else:
                    demo_tabla_body.controls.append(fila)
                    page.update()
                    await asyncio.sleep(0.25) # Animación progresiva

            if inmediato:
                demo_tabla_body.controls.extend(filas_a_agregar)

            demo_resultado_final.value = f"Resultado completo: {resultado_completo}"

        except ValueError as ex:
            demo_mensaje.value = str(ex)
            demo_mensaje.color = ft.Colors.ERROR
        page.update()

    return ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
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
                    [demo_texto, demo_clave, demo_limite, demo_modo],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                ),
                ft.Row(
                    [
                        ft.Button("Ejecutar demostración", icon=ft.Icons.PLAY_ARROW,
                               on_click=ejecutar_demo_async),
                        mostrar_todo_checkbox
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                demo_mensaje,
                demo_tabla_manual,
                demo_mensaje_truncamiento,
                ft.Divider(height=5),
                demo_resultado_final,
            ],
            spacing=10,
        ),
        padding=20,
    )
