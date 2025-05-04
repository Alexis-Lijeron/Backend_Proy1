import requests

# ------------------ CONFIGURA TU SERVIDOR ------------------
BASE_URL = "http://127.0.0.1:8000/chroma"
# ----------------------------------------------------------


def hacer_pregunta():
    pregunta = input("\n👉 Escribe tu pregunta: ")

    payload = {"pregunta": pregunta, "k": 5}

    response = requests.post(f"{BASE_URL}/search1", json=payload)

    if response.status_code == 200:
        data = response.json()
        print("\n✅ Respuesta:")
        print(data["respuesta"])
        return pregunta, data["respuesta"]
    else:
        print("❌ Error en la búsqueda:", response.text)
        return None, None


def dar_feedback(pregunta, respuesta):
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
        }

        response = requests.post(f"{BASE_URL}/feedback1", json=payload)

        if response.status_code == 200:
            data = response.json()
            print("✅ Feedback guardado. ID:", data["id_feedback"])
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
