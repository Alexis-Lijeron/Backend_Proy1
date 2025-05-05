import os
from typing import Optional
from fastapi import APIRouter, HTTPException
import re

router = APIRouter(prefix="/consulta_txt", tags=["Consulta TXT"])

DIRECTORIO_TXT = "documentos_txt"


def numero_a_romano(numero: int) -> str:
    valores = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    resultado = ""
    for valor, romano in valores:
        while numero >= valor:
            resultado += romano
            numero -= valor
    return resultado


def cargar_documento(nombre_archivo):
    ruta = os.path.join(DIRECTORIO_TXT, nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {nombre_archivo}")
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def normalizar(texto):
    return (
        texto.lower()
        .strip()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def buscar_contenido(documento, capitulo=None, articulo=None):
    documento = documento.lower().strip()
    archivos = os.listdir(DIRECTORIO_TXT)
    archivo_encontrado = None
    for archivo in archivos:
        if documento in archivo.lower():
            archivo_encontrado = archivo
            break

    if not archivo_encontrado:
        raise ValueError("No se encontró el documento solicitado.")

    texto = cargar_documento(archivo_encontrado)
    lineas = texto.split("\n")
    resultado = []

    capitulo_romano = None
    if capitulo:
        capitulo = str(capitulo)
        capitulo_romano = (
            numero_a_romano(int(capitulo)) if capitulo.isdigit() else capitulo.upper()
        )

    # ----- Caso 1: Todo el documento -----
    if not capitulo and not articulo:
        return texto

    # ----- Caso 2: Solo capítulo -----
    if capitulo and not articulo:
        capturando = False
        for i, linea in enumerate(lineas):
            linea_norm = normalizar(linea)

            # Detectar CAPÍTULO exacto
            if (
                f"capitulo {capitulo}" in linea_norm
                or f"capitulo {capitulo_romano}".lower() in linea_norm
            ) and not capturando:
                capturando = True
                resultado.append(linea)
                continue

            if capturando:
                # Detener captura si aparece otro capítulo o un título
                if re.match(r"^\s*(cap[íi]tulo|titulo)\s", linea_norm):
                    break
                resultado.append(linea)

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el capítulo {capitulo} en el documento."

    # ----- Caso 3: Capítulo + Artículo -----
    if capitulo and articulo:
        capturando = False
        cap_actual = None
        for linea in lineas:
            linea_norm = normalizar(linea)

            # Detectar CAPÍTULO
            if re.match(r"^\s*cap[íi]tulo\s", linea_norm):
                cap_actual = linea_norm
                capturando = False

            if cap_actual and (
                f"capitulo {capitulo}" in cap_actual
                or f"capitulo {capitulo_romano}".lower() in cap_actual
            ):
                # Detectar ARTÍCULO dentro del capítulo
                if f"articulo {articulo}" in linea_norm:
                    capturando = True
                    resultado.append(linea)
                    continue

                if capturando:
                    if (
                        re.match(r"^\s*art[íi]culo\s", linea_norm)
                        and f"{articulo}" not in linea_norm
                    ):
                        break
                    resultado.append(linea)

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el artículo {articulo} en el capítulo {capitulo} del documento."

    # ----- Caso 4: Solo Artículo -----
    if not capitulo and articulo:
        capturando = False
        for linea in lineas:
            linea_norm = normalizar(linea)

            if f"articulo {articulo}" in linea_norm:
                capturando = True
                resultado.append(linea)
                continue

            if capturando:
                if (
                    re.match(r"^\s*art[íi]culo\s", linea_norm)
                    and f"{articulo}" not in linea_norm
                ):
                    break
                resultado.append(linea)

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el artículo {articulo} en el documento."

    return "No se encontró contenido con los parámetros especificados."


@router.get("/buscar")
def buscar(
    documento: str, capitulo: Optional[int] = None, articulo: Optional[int] = None
):
    try:
        resultado = buscar_contenido(documento, capitulo, articulo)
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
