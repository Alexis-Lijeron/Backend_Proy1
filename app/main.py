from fastapi import FastAPI
from app.api import users, chats, contextos, mensajes, feedbacks
from app.rag import chroma_routes, rag_routes, chroma_metadatos_routes

app = FastAPI(
    title="Sistema de Chats Multi-Contexto",
    description="API para gestionar usuarios, chats, contextos, mensajes y feedbacks",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(chats.router)
app.include_router(contextos.router)
app.include_router(mensajes.router)
app.include_router(feedbacks.router)
app.include_router(chroma_routes.router)
app.include_router(rag_routes.router)
app.include_router(chroma_metadatos_routes.router)
