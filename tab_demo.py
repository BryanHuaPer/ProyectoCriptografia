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
            demo_limite.value = "40" if num > 40 else str(num)
        else:
            demo_limite.value = ""
        page.update()

    demo_limite = ui.default_text_field(
        label="Límite pasos", value="15", width=100,
        keyboard_type=ft.KeyboardType.NUMBER, on_change=validar_limite,
    )
    demo_modo = ft.Dropdown(
        label="Modo", width=150, value="cifrar", border_color=ft.Colors.OUTLINE,
        options=[ft.dropdown.Option("cifrar"), ft.dropdown.Option("descifrar")],
    )
    mostrar_todo_checkbox = ft.Checkbox(label="Mostrar todo de inmediato", value=False)

    demo_mensaje            = ft.Text(value="", size=14, color=ft.Colors.ERROR)
    demo_mensaje_truncamiento = ft.Text(value="", size=13, color=ft.Colors.OUTLINE, italic=True)
    demo_resultado_final    = ft.Text(value="", size=20, weight=ft.FontWeight.BOLD)

    # ── Widgets para Etapa A (la que va primero según el modo) ─────────────────
    etiq_a     = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color="#00BCD4", visible=False)
    etiq_a_sub = ft.Text("", size=12, italic=True, color=ft.Colors.OUTLINE,       visible=False)
    # Cabecera de tabla (solo visible en etapa de sustitución)
    cabecera_tabla = ft.Row(
        controls=[
            ui.crear_celda_demo("#",         bold=True),
            ui.crear_celda_demo("Letra",     bold=True),
            ui.crear_celda_demo("Clave",     bold=True),
            ui.crear_celda_demo("Ciclo",     bold=True),
            ui.crear_celda_demo("Pos.",      bold=True),
            ui.crear_celda_demo("Pos.Clave", bold=True),
            ui.crear_celda_demo("Op.",       bold=True),
            ui.crear_celda_demo("Resultado", bold=True),
        ],
        visible=False,
    )
    cuerpo_a = ft.Column()

    texto_intermedio_label = ft.Text(
        value="", size=14, italic=True, color=ui.COLOR_EXITO, visible=False,
    )

    # ── Widgets para Etapa B (la que va segunda) ───────────────────────────────
    etiq_b     = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color="#FFA726", visible=False)
    etiq_b_sub = ft.Text("", size=12, italic=True, color=ft.Colors.OUTLINE,       visible=False)
    cuerpo_b   = ft.Column()

    # ── Helpers cuadrícula ──────────────────────────────────────────────────────
    def _fila_cuadricula(celdas: list, bg=None) -> ft.Row:
        return ft.Row(controls=[
            ft.Container(
                content=ft.Text(c, size=13, text_align=ft.TextAlign.CENTER),
                expand=True, bgcolor=bg,
                border=ft.Border.all(1, ft.Colors.OUTLINE),
                padding=ft.Padding(top=4, bottom=4, left=2, right=2),
            )
            for c in celdas
        ])

    def _construir_filas_cuadricula(texto_in: str, clave: str) -> list:
        datos = mc.cuadricula_transposicion(texto_in, clave)
        filas = []
        filas.append(_fila_cuadricula(datos["clave"], bg="#1A3A5C"))
        filas.append(_fila_cuadricula([str(r) for r in datos["rango"]], bg="#1A2E3A"))
        for fila in datos["filas"]:
            celdas = list(fila) + [""] * (len(datos["clave"]) - len(fila))
            filas.append(_fila_cuadricula(celdas))
        return filas

    # ── Handler principal ───────────────────────────────────────────────────────
    async def ejecutar_demo_async(e):
        if e is not None:
            demo_mensaje.value = ""

        demo_resultado_final.value = ""
        demo_mensaje_truncamiento.value = ""
        texto_intermedio_label.value   = ""
        texto_intermedio_label.visible = False

        cuerpo_a.controls.clear()
        cuerpo_b.controls.clear()

        for w in [etiq_a, etiq_a_sub, cabecera_tabla,
                  etiq_b, etiq_b_sub]:
            w.visible = False
        page.update()

        try:
            texto = demo_texto.value or ""
            clave = demo_clave.value or ""
            modo  = demo_modo.value or "cifrar"

            try:
                limite_val = int(demo_limite.value)
                limite_val = max(1, min(40, limite_val))
            except ValueError:
                limite_val = 15
            demo_limite.value = str(limite_val)

            inmediato = mostrar_todo_checkbox.value

            letras_totales = sum(1 for c in texto if c.upper() in mc.ALFABETO)
            if letras_totales > limite_val:
                demo_mensaje_truncamiento.value = (
                    f"Mostrando las primeras {limite_val} letras de {letras_totales} totales."
                )

            resultado_completo = (
                mc.cifrar_mixto(texto, clave) if modo == "cifrar"
                else mc.descifrar_mixto(texto, clave)
            )

            # ══════════════════════════════════════════════════════════════════
            if modo == "cifrar":
                # ─ Etapa A: Sustitución (tabla) ─
                etiq_a.value     = "Etapa 1 — Vigenère Progresivo (Sustitución)"
                etiq_a_sub.value = "Operación: (pos_letra + pos_clave + ciclo) % 26"
                pasos_a = mc.pasos_sustitucion(texto, clave, "cifrar", limite=limite_val)

                texto_intermedio = mc.sustitucion(texto, clave, "cifrar")

                # ─ Etapa B: Transposición (cuadrícula) ─
                etiq_b.value     = "Etapa 2 — Transposición Columnar"
                etiq_b_sub.value = "Las columnas se reordenan según el orden alfabético de la clave."
                texto_para_grid  = texto_intermedio

                etiq_a_es_tabla  = True

            else:
                # ─ Etapa A: Destransposición (cuadrícula) ─
                etiq_a.value     = "Etapa 1 — Transposición Columnar Inversa"
                etiq_a_sub.value = "Las columnas se reordenan de vuelta a su posición original."
                texto_destransp  = mc.transposicion(texto, clave, "descifrar")
                texto_para_grid  = texto_destransp

                texto_intermedio = texto_destransp

                # ─ Etapa B: Desustitución (tabla) ─
                etiq_b.value     = "Etapa 2 — Vigenère Progresivo Inverso (Desustitución)"
                etiq_b_sub.value = "Operación: (pos_letra − pos_clave − ciclo) % 26"
                pasos_a = mc.pasos_sustitucion(texto_destransp, clave, "descifrar", limite=limite_val)

                etiq_a_es_tabla  = False

            # ── Renderizar Etapa A ─────────────────────────────────────────────
            for w in [etiq_a, etiq_a_sub]:
                w.visible = True

            if etiq_a_es_tabla:
                # Tabla en A
                cabecera_tabla.visible = True
                page.update()
                filas_buf = []
                for i, p in enumerate(pasos_a, 1):
                    op_str = f"({p['pos_texto']} {p['operacion']} {p['pos_clave']} + {p['giro']}) % 26"
                    fila = ft.Row(controls=[
                        ui.crear_celda_demo(str(i)),
                        ui.crear_celda_demo(p["letra_original"], bold=True, color="#00BCD4"),
                        ui.crear_celda_demo(p["letra_clave"],    bold=True, color="#FFA726"),
                        ui.crear_celda_demo(str(p["giro"]),      color="#BB86FC"),
                        ui.crear_celda_demo(str(p["pos_texto"])),
                        ui.crear_celda_demo(str(p["pos_clave"])),
                        ui.crear_celda_demo(op_str, size=12),
                        ui.crear_celda_demo(p["resultado"], bold=True, color=ui.COLOR_EXITO),
                    ])
                    if inmediato:
                        filas_buf.append(fila)
                    else:
                        cuerpo_a.controls.append(fila)
                        page.update()
                        await asyncio.sleep(0.20)
                if inmediato:
                    cuerpo_a.controls.extend(filas_buf)
            else:
                # Cuadrícula en A
                page.update()
                filas_grid = _construir_filas_cuadricula(texto_para_grid, clave)
                if inmediato:
                    cuerpo_a.controls.extend(filas_grid)
                else:
                    for fg in filas_grid:
                        cuerpo_a.controls.append(fg)
                        page.update()
                        await asyncio.sleep(0.15)

            # Texto intermedio entre etapas
            texto_intermedio_label.value   = f"→ Texto que pasa a la siguiente etapa: {texto_intermedio}"
            texto_intermedio_label.visible = True
            page.update()

            # ── Renderizar Etapa B ─────────────────────────────────────────────
            for w in [etiq_b, etiq_b_sub]:
                w.visible = True
            page.update()

            if not etiq_a_es_tabla:
                # Tabla en B
                cabecera_tabla.visible = True
                page.update()
                filas_buf = []
                for i, p in enumerate(pasos_a, 1):
                    op_str = f"({p['pos_texto']} {p['operacion']} {p['pos_clave']} − {p['giro']}) % 26"
                    fila = ft.Row(controls=[
                        ui.crear_celda_demo(str(i)),
                        ui.crear_celda_demo(p["letra_original"], bold=True, color="#00BCD4"),
                        ui.crear_celda_demo(p["letra_clave"],    bold=True, color="#FFA726"),
                        ui.crear_celda_demo(str(p["giro"]),      color="#BB86FC"),
                        ui.crear_celda_demo(str(p["pos_texto"])),
                        ui.crear_celda_demo(str(p["pos_clave"])),
                        ui.crear_celda_demo(op_str, size=12),
                        ui.crear_celda_demo(p["resultado"], bold=True, color=ui.COLOR_EXITO),
                    ])
                    if inmediato:
                        filas_buf.append(fila)
                    else:
                        cuerpo_b.controls.append(fila)
                        page.update()
                        await asyncio.sleep(0.20)
                if inmediato:
                    cuerpo_b.controls.extend(filas_buf)
            else:
                # Cuadrícula en B
                filas_grid = _construir_filas_cuadricula(texto_para_grid, clave)
                if inmediato:
                    cuerpo_b.controls.extend(filas_grid)
                else:
                    for fg in filas_grid:
                        cuerpo_b.controls.append(fg)
                        page.update()
                        await asyncio.sleep(0.15)

            demo_resultado_final.value = f"Resultado completo: {resultado_completo}"

        except ValueError as ex:
            demo_mensaje.value = str(ex)
            demo_mensaje.color = ft.Colors.ERROR
        page.update()

    def usar_ultima_operacion(e):
        prev = estado["texto"]
        if prev["ultimo_texto"] and prev["ultima_clave"]:
            demo_texto.value = prev["ultimo_texto"].replace("\n", " ")[:50]
            demo_clave.value = prev["ultima_clave"]
            demo_modo.value  = prev["ultimo_modo"]
            demo_mensaje.value = "✔ Cargado desde la pestaña Texto."
            demo_mensaje.color = ui.COLOR_EXITO
            asyncio.create_task(ejecutar_demo_async(None))
        else:
            demo_mensaje.value = "Aún no hay una operación previa en la pestaña Texto."
            demo_mensaje.color = ui.COLOR_ADVERTENCIA
        page.update()

    return ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Modo Demostración — Paso a paso",
                        size=20, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Visualiza cómo el algoritmo Mixto transforma cada letra (sustitución) "
                    "y reordena el texto (transposición). El orden de las etapas se invierte al descifrar.",
                    size=14, italic=True, color=ft.Colors.OUTLINE,
                ),
                ft.Divider(height=10),
                ft.Row(
                    [ft.Button("Usar mi última operación", icon=ft.Icons.SYNC,
                               on_click=usar_ultima_operacion)],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Row(
                    [demo_texto, demo_clave, demo_limite, demo_modo],
                    alignment=ft.MainAxisAlignment.CENTER, wrap=True,
                ),
                ft.Row(
                    [
                        ft.Button("Ejecutar demostración", icon=ft.Icons.PLAY_ARROW,
                                  on_click=ejecutar_demo_async),
                        mostrar_todo_checkbox,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                demo_mensaje,
                demo_mensaje_truncamiento,
                # ── Etapa A ──
                etiq_a,
                etiq_a_sub,
                cabecera_tabla,
                cuerpo_a,
                texto_intermedio_label,
                ft.Divider(height=4),
                # ── Etapa B ──
                etiq_b,
                etiq_b_sub,
                cuerpo_b,
                ft.Divider(height=5),
                demo_resultado_final,
            ],
            spacing=10,
        ),
        padding=20,
    )
