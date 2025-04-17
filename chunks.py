from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import json
import os

documentos_txt = [
    "57_L_259.txt",
    "58_DS_1347.txt",
    "DS_27295.txt",
    "Ley_1883.txt",
    "Ley_completo.txt",
    "ley-nº-145.txt",
    "reglamentotecnicooperativo.txt"
]
carpeta = "./documentos_txt"  
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "]
)
chunks = []

for archivo in documentos_txt:
    ruta = os.path.join(carpeta, archivo)
    texto = Path(ruta).read_text(encoding="utf-8")

    partes = splitter.split_text(texto)
    for i, chunk in enumerate(partes):
        chunks.append({
            "source": archivo,
            "chunk_id": i,
            "text": chunk
        })

with open("chunks_codigo_transito_completo.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print("✅ Chunks generados y guardados en 'chunks_codigo_transito_completo.json'")
