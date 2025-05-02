import os
import time
import hashlib
import logging
from typing import List, Dict, Any

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, file_path: str, persist_dir: str = "chroma_db", chunk_size: int = 500, chunk_overlap: int = 50):
        self.file_path = file_path
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings(openai_api_key="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")
        self.vectorstore = None

        os.makedirs(self.persist_dir, exist_ok=True)

    def get_file_hash(self) -> str:
        with open(self.file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_documents(self) -> List[Document]:
        logger.info("📄 Cargando y dividiendo documentos en chunks...")
        loader = TextLoader(self.file_path, encoding="utf-8")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        texts = text_splitter.split_documents(documents)
        logger.info(f"✅ {len(texts)} chunks generados.")
        return texts

    def initialize(self) -> None:
        """Inicializar o cargar la base vectorial (Chroma) según cambios en el archivo."""
        hash_path = os.path.join(self.persist_dir, "hash.txt")
        current_hash = self.get_file_hash()

        if os.path.exists(self.persist_dir) and os.path.exists(hash_path):
            with open(hash_path, "r") as f:
                previous_hash = f.read().strip()
            if previous_hash == current_hash:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
                logger.info("✅ Reutilizando embeddings existentes.")
                return

        logger.info("🔄 Archivo modificado, regenerando embeddings...")
        documents = self.load_documents()
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        with open(hash_path, "w") as f:
            f.write(current_hash)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.vectorstore:
            raise ValueError("⚠️ Vectorstore no inicializado. Ejecuta initialize() primero.")
        docs = self.vectorstore.similarity_search(query, k=k)
        return [{"id": i + 1, "content": d.page_content, "metadata": d.metadata} for i, d in enumerate(docs)]
