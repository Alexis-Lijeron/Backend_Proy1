import os
from typing import Optional
from fastapi import APIRouter, HTTPException
import re

import openai
from langchain_openai import ChatOpenAI
from app.core.config import settings

router = APIRouter(prefix="/consulta_txt", tags=["Consulta TXT"])

DIRECTORIO_TXT = "documentos_txt"


# Convertir números a romanos
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


# Cargar el documento desde el sistema de archivos
def cargar_documento1(nombre_archivo):
    ruta = os.path.join(DIRECTORIO_TXT, nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {nombre_archivo}")
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


# Normalizar texto (convertir todo a minúsculas y eliminar tildes)
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


# Buscar contenido dentro del documento (capítulo o artículo específico)
def buscar_contenido(documento, titulo=None, capitulo=None, articulo=None):
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

    # Caso 1: Solo Título - Devolver todo lo que está en el título (capítulos y artículos)
    if titulo and not capitulo and not articulo:
        capturando = False
        for linea in lineas:
            linea_norm = normalizar(linea)

            if titulo.lower() in linea_norm:
                capturando = True
            if capturando:
                if re.match(r"^\s*(cap[íi]tulo|titulo)\s", linea_norm):
                    break
                resultado.append(linea)

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el título {titulo} en el documento."

    # Caso 2: Título + Capítulo - Devolver todo lo que está en el capítulo del título
    if titulo and capitulo and not articulo:
        capturando = False
        capitulo_actual = None
        for linea in lineas:
            linea_norm = normalizar(linea)

            # Detectar Título
            if titulo.lower() in linea_norm:
                capturando = True
            if capturando:
                # Detectar CAPÍTULO
                if (
                    f"capitulo {capitulo}" in linea_norm
                    or f"capitulo {capitulo_romano}".lower() in linea_norm
                ):
                    capitulo_actual = linea.strip()
                    resultado.append(capitulo_actual)
                    continue
                # Si el capítulo ya fue capturado, añadir contenido
                if capitulo_actual:
                    if re.match(
                        r"^\s*(cap[íi]tulo|titulo)\s", linea_norm
                    ):  # Fin de capítulo
                        break
                    resultado.append(linea)

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el capítulo {capitulo} en el título {titulo}."

    # Caso 3: Título + Capítulo + Artículo - Devolver solo el artículo
    if titulo and capitulo and articulo:
        capturando = False
        capitulo_actual = None
        for linea in lineas:
            linea_norm = normalizar(linea)

            # Detectar Título
            if titulo.lower() in linea_norm:
                capturando = True
            if capturando:
                # Detectar CAPÍTULO
                if (
                    f"capitulo {capitulo}" in linea_norm
                    or f"capitulo {capitulo_romano}".lower() in linea_norm
                ):
                    capitulo_actual = linea.strip()
                    continue
                # Detectar ARTÍCULO dentro del capítulo
                if f"articulo {articulo}" in linea_norm:
                    resultado.append(linea.strip())
                    capturando = False
                    break

        if resultado:
            return "\n".join(resultado).strip()
        else:
            return f"No se encontró el artículo {articulo} en el capítulo {capitulo} del título {titulo}."

    return "No se encontró contenido con los parámetros especificados."


# Obtener el resultado de búsqueda
@router.get("/buscar")
def buscar(
    documento: str,
    titulo: Optional[str] = None,
    capitulo: Optional[int] = None,
    articulo: Optional[int] = None,
):
    try:
        resultado = buscar_contenido(documento, titulo, capitulo, articulo)
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estructura")
def analizar_estructura(documento: str):
    try:
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

        estructura = []
        titulo_actual = None
        capitulo_actual = None

        for linea in lineas:
            linea_norm = normalizar(linea)

            match_titulo = re.match(r"^\s*t[ií]tulo\s+([^\n]*)", linea_norm)
            if match_titulo:
                titulo_actual = {"titulo": linea.strip(), "capitulos": []}
                estructura.append(titulo_actual)
                capitulo_actual = None  
                continue

            match_cap = re.match(r"^\s*cap[íi]tulo\s+([^\n]*)", linea_norm)
            if match_cap:
                if not titulo_actual:
                    titulo_actual = {"titulo": "Sin Título", "capitulos": []}
                    estructura.append(titulo_actual)

                capitulo_actual = {"capitulo": linea.strip(), "articulos": []}
                titulo_actual["capitulos"].append(capitulo_actual)
                continue

            match_art = re.match(r"^\s*art[íi]culo\s+\d+", linea_norm)
            if match_art:
                if not capitulo_actual:
                    capitulo_actual = {"capitulo": "Sin Capítulo", "articulos": []}
                    if not titulo_actual:
                        titulo_actual = {"titulo": "Sin Título", "capitulos": []}
                        estructura.append(titulo_actual)
                    titulo_actual["capitulos"].append(capitulo_actual)

                capitulo_actual["articulos"].append(linea.strip())

        return {"estructura": estructura}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documentos")
def listar_documentos():
    try:
        archivos = os.listdir(DIRECTORIO_TXT)
        documentos = [archivo for archivo in archivos if archivo.endswith(".txt")]
        return {"documentos": documentos}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estructura_resumida")
def analizar_estructura_resumida(documento: str):
    try:
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
        titulo_actual = ""
        capitulo_actual = ""
        articulos = []

        def agregar_capitulo_con_rangos():
            if capitulo_actual:
                resultado.append(f"  - {capitulo_actual}")
                if articulos:
                    rangos = calcular_rangos_articulos(articulos)
                    for r in rangos:
                        resultado.append(f"    - {r}")

        def calcular_rangos_articulos(lista_articulos):
            numeros = []
            for art in lista_articulos:
                match = re.search(r"\d+", art)
                if match:
                    numeros.append(int(match.group()))
            numeros = sorted(set(numeros))
            if not numeros:
                return ["Artículos no especificados"]

            rangos = []
            inicio = fin = numeros[0]
            for n in numeros[1:]:
                if n == fin + 1:
                    fin = n
                else:
                    if inicio == fin:
                        rangos.append(f"Artículo {inicio}")
                    else:
                        rangos.append(f"Artículos {inicio} a {fin}")
                    inicio = fin = n
            if inicio == fin:
                rangos.append(f"Artículo {inicio}")
            else:
                rangos.append(f"Artículos {inicio} a {fin}")
            return rangos

        for linea in lineas:
            linea_norm = normalizar(linea)

            match_titulo = re.match(r"^\s*t[ií]tulo\s+[^\n]*", linea_norm)
            if match_titulo:
                if capitulo_actual or articulos:
                    agregar_capitulo_con_rangos()
                    capitulo_actual = ""
                    articulos = []

                if titulo_actual:
                    resultado.append("")  
                titulo_actual = linea.strip()
                resultado.append(titulo_actual)
                continue

            match_cap = re.match(r"^\s*cap[íi]tulo\s+[^\n]*", linea_norm)
            if match_cap:
                if capitulo_actual or articulos:
                    agregar_capitulo_con_rangos()
                    articulos = []
                capitulo_actual = linea.strip()
                continue

            match_art = re.match(r"^\s*art[íi]culo\s+\d+", linea_norm)
            if match_art:
                articulos.append(linea.strip())

        if capitulo_actual or articulos:
            agregar_capitulo_con_rangos()

        return {"estructura_resumida": resultado}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/buscar_con_openai")
async def buscar_con_openai(documento: str, consulta: str):
    try:
        documento_contenido = cargar_documento(documento)

        prompt = f"""
        El siguiente es el contenido de un documento legal:

        {documento_contenido}

        Consulta: {consulta}

        Caso 1: Si la consulta menciona un título específico, devolver todo el contenido de ese título, incluyendo sus capítulos y artículos.
        Caso 2: Si la consulta menciona un título, capítulo y artículo específicos, devolver el contenido exacto de ese artículo dentro del capítulo y título solicitados.
        Caso 3: Si la consulta menciona un artículo específico, devolver el fragmento exacto de ese artículo del documento.
        Después de dar la respuesta, proporciona una breve explicación sobre el contenido devuelto, en pocas palabras, para contextualizar el fragmento que se extrae del documento.
        """

        chat_model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        response = chat_model.predict(prompt)

        return {"respuesta": response}

    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Error de OpenAI: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la consulta: {str(e)}"
        )


def cargar_documento(nombre_archivo):
    ruta = os.path.join("documentos_txt", nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {nombre_archivo}")
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()
