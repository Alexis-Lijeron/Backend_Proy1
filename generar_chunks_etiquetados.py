import os
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
CARPETA_TXT = "./documentos_txt"

with open("categorias_sinonimos_bolivia.json", "r", encoding="utf-8") as f:
    CATEGORIAS_SINONIMOS_BOLIVIA = json.load(f)

def etiquetar_chunk(texto):
    texto_lower = texto.lower()
    etiquetas = []

    for categoria, sinonimos in CATEGORIAS_SINONIMOS_BOLIVIA.items():
        if any(s in texto_lower for s in sinonimos):
            etiquetas.append(categoria)

    return etiquetas

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "]
)

chunks_etiquetados = []

for archivo in os.listdir(CARPETA_TXT):
    if archivo.endswith(".txt"):
        ruta = os.path.join(CARPETA_TXT, archivo)
        texto = Path(ruta).read_text(encoding="utf-8")
        partes = splitter.split_text(texto)

        for i, chunk in enumerate(partes):
            etiquetas = etiquetar_chunk(chunk)
            chunks_etiquetados.append({
                "source": archivo,
                "chunk_id": i,
                "text": chunk,
                "etiquetas": etiquetas
            })

with open("chunks_con_etiquetas.json", "w", encoding="utf-8") as f:
    json.dump(chunks_etiquetados, f, ensure_ascii=False, indent=2)

print("✅ chunks_con_etiquetas.json generado con éxito.")
