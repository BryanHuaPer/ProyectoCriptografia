import string

ALFABETO = string.ascii_uppercase  # A-Z


def limpiar_clave(clave: str) -> str:
    """Deja solo letras en la clave y la pone en mayúsculas."""
    return "".join(c for c in clave.upper() if c in ALFABETO)


def vigenere(texto: str, clave: str, modo: str) -> str:
    """
    Cifra o descifra texto usando el algoritmo Vigenère.

    modo: 'cifrar' o 'descifrar'
    Los caracteres que no son letras (espacios, números, símbolos)
    se dejan sin modificar.
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
            resultado.append(nueva_letra if char.isupper() else nueva_letra.lower())
            indice_clave += 1
        else:
            resultado.append(char)

    return "".join(resultado)


def vigenere_pasos(texto: str, clave: str, modo: str, limite: int = 12) -> list[dict]:
    """
    Igual que vigenere(), pero devuelve el detalle paso a paso de cada
    letra procesada (para el 'Modo Demostración' de la interfaz).
    Solo procesa hasta `limite` letras para no saturar la pantalla.

    Devuelve una lista de diccionarios:
    [{"letra_original": "H", "letra_clave": "C", "pos_texto": 7,
      "pos_clave": 2, "resultado": "J"}, ...]
    """
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
    """
    Evalúa qué tan fuerte es una clave según longitud y variedad.
    Devuelve {"nivel": "Débil"|"Media"|"Fuerte", "color": "...", "detalle": "..."}
    """
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