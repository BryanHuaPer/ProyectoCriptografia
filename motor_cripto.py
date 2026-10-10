import string

ALFABETO = string.ascii_uppercase  # A-Z


def limpiar_clave(clave: str) -> str:
    """Deja solo letras en la clave y la pone en mayúsculas."""
    return "".join(c for c in clave.upper() if c in ALFABETO)


def vigenere(texto: str, clave: str, modo: str) -> str:
    """Cifra o descifra texto usando el algoritmo Vigenère."""
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
            else:
                nueva_pos = (pos_texto - pos_clave) % 26

            nueva_letra = ALFABETO[nueva_pos]
            resultado.append(nueva_letra if char.isupper() else nueva_letra.lower())
            indice_clave += 1
        else:
            resultado.append(char)

    return "".join(resultado)


def vigenere_pasos(texto: str, clave: str, modo: str, limite: int = 12) -> list[dict]:
    clave = limpiar_clave(clave)
    if not clave:
        raise ValueError("La clave debe contener al menos una letra.")

    pasos = []
    indice_clave = 0

    for char in texto:
        if len(pasos) >= limite:
            break

        char_upper = char.upper()
        if char_upper in ALFABETO:
            pos_texto = ALFABETO.index(char_upper)
            letra_clave = clave[indice_clave % len(clave)]
            pos_clave = ALFABETO.index(letra_clave)

            if modo == "cifrar":
                nueva_pos = (pos_texto + pos_clave) % 26
            else:
                nueva_pos = (pos_texto - pos_clave) % 26

            nueva_letra = ALFABETO[nueva_pos]

            pasos.append({
                "letra_original": char_upper,
                "letra_clave": letra_clave,
                "pos_texto": pos_texto,
                "pos_clave": pos_clave,
                "operacion": "+" if modo == "cifrar" else "-",
                "resultado": nueva_letra,
            })
            indice_clave += 1

    return pasos


def evaluar_fortaleza_clave(clave: str) -> dict:
    clave_limpia = limpiar_clave(clave)
    largo = len(clave_limpia)
    letras_unicas = len(set(clave_limpia))

    if largo == 0:
        return {"nivel": "Sin clave", "color": "grey", "detalle": "Ingresa una clave"}
    elif largo < 4 or letras_unicas <= 1:
        return {"nivel": "Débil", "color": "red", "detalle": "Usa una clave más larga y variada"}
    elif largo < 8 or letras_unicas < largo * 0.5:
        return {"nivel": "Media", "color": "orange", "detalle": "Aceptable, pero puede mejorar"}
    else:
        return {"nivel": "Fuerte", "color": "green", "detalle": "Buena longitud y variedad"}




def _validar_clave(clave: str) -> str:
    clave = limpiar_clave(clave)
    if not clave:
        raise ValueError("La clave debe contener al menos una letra.")
    return clave


def sustitucion(texto: str, clave: str, modo: str) -> str:
    clave = _validar_clave(clave)
    n = len(clave)
    salida, i = [], 0
    for ch in texto:
        u = ch.upper()
        if len(u) == 1 and u in ALFABETO:
            desplazamiento = ALFABETO.index(clave[i % n]) + (i // n)
            p = ALFABETO.index(u)
            nueva = (p + desplazamiento) % 26 if modo == "cifrar" else (p - desplazamiento) % 26
            letra = ALFABETO[nueva]
            salida.append(letra if ch.isupper() else letra.lower())
            i += 1
        else:
            salida.append(ch)
    return "".join(salida)


def orden_columnas(clave: str) -> list:
    clave = _validar_clave(clave)
    return sorted(range(len(clave)), key=lambda j: (clave[j], j))


def transposicion(texto: str, clave: str, modo: str) -> str:
    clave = _validar_clave(clave)
    n, L = len(clave), len(texto)
    orden = orden_columnas(clave)
    if modo == "cifrar":
        return "".join(texto[j::n] for j in orden)
    largos = [(L - j + n - 1) // n for j in range(n)]
    res, pos = [""] * L, 0
    for j in orden:
        segmento = texto[pos:pos + largos[j]]
        pos += largos[j]
        for r, ch in enumerate(segmento):
            res[j + r * n] = ch
    return "".join(res)


def cifrar_mixto(texto: str, clave: str) -> str:
    return transposicion(sustitucion(texto, clave, "cifrar"), clave, "cifrar")


def descifrar_mixto(texto: str, clave: str) -> str:
    return sustitucion(transposicion(texto, clave, "descifrar"), clave, "descifrar")


def pasos_sustitucion(texto: str, clave: str, modo: str, limite: int = 15) -> list:
    clave = _validar_clave(clave)
    n, pasos, i = len(clave), [], 0
    for ch in texto:
        if len(pasos) >= limite:
            break
        u = ch.upper()
        if len(u) == 1 and u in ALFABETO:
            base = ALFABETO.index(clave[i % n])
            giro = i // n
            p = ALFABETO.index(u)
            d = base + giro
            nueva = (p + d) % 26 if modo == "cifrar" else (p - d) % 26
            pasos.append({
                "letra_original": u,
                "letra_clave": clave[i % n],
                "pos_texto": p,
                "pos_clave": base,
                "giro": giro,
                "operacion": "+" if modo == "cifrar" else "-",
                "resultado": ALFABETO[nueva],
            })
            i += 1
    return pasos


def cuadricula_transposicion(texto: str, clave: str) -> dict:
    clave = _validar_clave(clave)
    n = len(clave)
    rango = [0] * n
    for r, j in enumerate(orden_columnas(clave)):
        rango[j] = r + 1
    filas = [texto[k:k + n] for k in range(0, len(texto), n)]
    return {"clave": list(clave), "rango": rango, "filas": filas}