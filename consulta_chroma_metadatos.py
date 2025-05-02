import requests

BASE_URL = "http://127.0.0.1:8000/chroma_metadatos"


def hacer_pregunta():
    pregunta = input("\n👉 Escribe tu pregunta: ")
    documento = input("📄 Filtrar por documento (deja vacío para todos): ").strip()
    articulo = input("📑 Filtrar por artículo (deja vacío para todos): ").strip()

    payload = {
        "pregunta": pregunta,
        "k": 5,
        "documento": documento if documento else None,
        "articulo": articulo if articulo else None,
    }

    response = requests.post(f"{BASE_URL}/search", json=payload)

    if response.status_code == 200:
        data = response.json()
        print("\n✅ Respuesta:")
        print(data["respuesta"])

        print("\n🔎 Metadatos de los resultados relevantes:")
        for res in data["resultados"]:
            print(
                f"- Documento: {res['documento']}, Capítulo: {res['capitulo']}, Artículo: {res['articulo']}"
            )
            print(f"  → Texto: {res['contenido'][:200]}...\n")

        # Usamos solo los metadatos del primer resultado (el más relevante)
        if data["resultados"]:
            metadatos = data["resultados"][0]
        else:
            metadatos = {}

        return pregunta, data["respuesta"], metadatos
    else:
        print("❌ Error en la búsqueda:", response.text)
        return None, None, None


def dar_feedback(pregunta, respuesta, metadatos):
    try:
        puntuacion = int(
            input("\n🔎 Del 1 al 5, ¿qué puntuación le das a la respuesta? ")
        )
        comentario = input("💬 Escribe un comentario (opcional): ")

        payload = {
            "query": pregunta,
            "response": respuesta,
            "rating": puntuacion,
            "comentario": comentario,
            "metadatos": metadatos,  # 👈 incluimos los metadatos del chunk
        }

        response = requests.post("http://127.0.0.1:8000/chroma/feedback", json=payload)

        if response.status_code == 200:
            data = response.json()
            print("✅ Feedback guardado.")
        else:
            print("❌ Error al guardar el feedback:", response.text)

    except ValueError:
        print("❌ La puntuación debe ser un número entre 1 y 5.")


def main():
    while True:
        pregunta, respuesta = hacer_pregunta()
        if pregunta and respuesta:
            dar_feedback(pregunta, respuesta)

        continuar = input("\n¿Quieres hacer otra pregunta? (s/n): ").lower()
        if continuar != "s":
            break


if __name__ == "__main__":
    main()
