import os
import re
import hashlib
import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

# Configuraciones
CARPETA_TXT = "documentos_txt"  # Carpeta donde tienes tus TXT
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHROMA_DIR = "chroma_db_metadatos"

# Inicializar embeddings
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)


def detectar_metadatos(texto):
    """Detecta capítulo, título y artículo si existe en el texto."""
    capitulo = None
    titulo = None
    articulo = None

    cap_match = re.search(r"Cap[ií]tulo\s+[^\n]+", texto, re.IGNORECASE)
    titulo_match = re.search(r"T[ií]tulo\s+[^\n]+", texto, re.IGNORECASE)
    art_match = re.search(r"Art[ií]culo\s+\d+", texto, re.IGNORECASE)

    if cap_match:
        capitulo = cap_match.group()
    if titulo_match:
        titulo = titulo_match.group()
    if art_match:
        articulo = art_match.group()

    return capitulo, titulo, articulo


def cargar_documentos():
    """Carga y divide los documentos, añadiendo metadatos."""
    documentos = []

    archivos = [f for f in os.listdir(CARPETA_TXT) if f.endswith(".txt")]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )

    for archivo in archivos:
        path = os.path.join(CARPETA_TXT, archivo)
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()

        chunks = splitter.split_documents(docs)

        for chunk in chunks:
            texto = chunk.page_content

            capitulo, titulo, articulo = detectar_metadatos(texto)

            chunk.metadata = {
                "documento": archivo,
                "capitulo": capitulo or "No detectado",
                "titulo": titulo or "No detectado",
                "articulo": articulo or "No detectado",
            }

            documentos.append(chunk)

        logging.info(f"Procesado {archivo}: {len(chunks)} chunks")

    return documentos


def crear_vectorstore():
    """Crea la base vectorial Chroma."""
    logging.info("📂 Cargando documentos y creando metadatos...")
    documentos = cargar_documentos()

    if not documentos:
        logging.error("❌ No se encontraron documentos para procesar.")
        return

    logging.info(f"📊 Total chunks: {len(documentos)}")

    # Crear Chroma
    vectorstore = Chroma.from_documents(
        documents=documentos, embedding=embeddings, persist_directory=CHROMA_DIR
    )

    logging.info("✅ Base de datos Chroma creada con éxito.")
    logging.info(f"Ubicación: {CHROMA_DIR}")


if __name__ == "__main__":
    crear_vectorstore()
