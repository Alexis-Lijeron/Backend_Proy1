import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

CHUNKS_PATH = "chunks_con_etiquetas.json"
FAISS_OUTPUT_DIR = "faiss_index_transito"

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

textos = [chunk["text"] for chunk in chunks]

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = FAISS.from_texts(textos, embedding_model)

vectorstore.save_local(FAISS_OUTPUT_DIR)

print(f"✅ Índice FAISS guardado en: {FAISS_OUTPUT_DIR}/")
