from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json

with open("chunks_codigo_transito_completo.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

textos = [chunk["text"] for chunk in chunks]
modelo = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts(textos, embedding=modelo)
vectorstore.save_local("indice_codigo_transito")

print("✅ Embeddings creados y guardados en la carpeta 'indice_codigo_transito'")
