import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
load_dotenv()
CHUNKS_PATH = "chunks_con_etiquetas.json"
CATEGORIAS_PATH = "categorias_sinonimos_bolivia.json"
FAISS_INDEX_DIR = "faiss_index_transito"
FAISS_TOP_K = 15       
MAX_CHUNKS_GPT = 15   

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(CATEGORIAS_PATH, "r", encoding="utf-8") as f:
    categorias_sinonimos = json.load(f)

def detectar_categorias_pregunta(pregunta, categorias_dict):
    pregunta_lower = pregunta.lower()
    return [cat for cat, palabras in categorias_dict.items() if any(p in pregunta_lower for p in palabras)]

def filtrar_chunks_por_categorias(chunks, categorias_objetivo):
    return [
        chunk for chunk in chunks
        if any(c in chunk.get("etiquetas", []) for c in categorias_objetivo)
    ]

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    FAISS_INDEX_DIR,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True 
)
retriever = vectorstore.as_retriever(search_kwargs={"k": FAISS_TOP_K})

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

pregunta = "¿Cual es la multa si avanzo cuando el semaforo señala luz roja?"

categorias_detectadas = detectar_categorias_pregunta(pregunta, categorias_sinonimos)
chunks_filtrados = filtrar_chunks_por_categorias(chunks, categorias_detectadas)

resultados_faiss = retriever.invoke(pregunta)

textos_finales = [
    doc.page_content for doc in resultados_faiss
    if any(
        any(cat in chunk["etiquetas"] for cat in categorias_detectadas)
        for chunk in chunks if chunk["text"] == doc.page_content
    )
]

if not textos_finales:
    textos_finales = [doc.page_content for doc in resultados_faiss[:MAX_CHUNKS_GPT]]

textos_finales = textos_finales[:MAX_CHUNKS_GPT]

contexto = "\n\n".join(textos_finales)
prompt = f"Basado en la siguiente normativa del tránsito boliviano:\n\n{contexto}\n\nResponde legalmente: {pregunta}"

respuesta = llm.invoke([
    {"role": "system", "content": "Eres un experto legal en normativa boliviana de tránsito."},
    {"role": "user", "content": prompt}
])

print("🧠 Pregunta:", pregunta)
print("✅ Respuesta:", respuesta.content)
