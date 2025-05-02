from fastapi import APIRouter
from app.models.feedbacks import FeedbackCreate, FeedbackOut
from app.crud import feedbacks as crud_feedbacks

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])

@router.post("/", response_model=FeedbackOut)
def insertar_feedback(feedback: FeedbackCreate):
    id_feedback = crud_feedbacks.insertar_feedback(
        id_mensaje=feedback.id_mensaje,
        puntuacion=feedback.puntuacion,
        comentario=feedback.comentario
    )
    return FeedbackOut(id_feedback=id_feedback, id_mensaje=feedback.id_mensaje, puntuacion=feedback.puntuacion, comentario=feedback.comentario, fecha=None)
