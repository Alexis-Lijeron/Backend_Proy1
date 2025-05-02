import re
from typing import Dict, List


class filtro_palabras:
    def __init__(self):
        # -------------------- EXPRESIONES COMPLETAS --------------------
        self.expresiones = {
            "me pusieron una multa": "multa",
            "me dieron un ticket": "multa",
            "me hicieron una boleta": "multa",
            "me sacaron una papeleta": "multa",
            "me hicieron un comparendo": "multa",
            "me cobraron una sanción": "multa",
            "me chocaron": "accidente",
            "choqué contra otro carro": "accidente",
            "tuve un percance": "accidente",
            "sufrí un siniestro": "accidente",
            "me quitaron el carro": "confiscación del vehículo",
            "me pararon en un retén": "control policial",
            "me hicieron alcoholemia": "prueba de alcohol en sangre",
            "voy a apelar la multa": "recurso contra sanción",
            "me citaron a audiencia vial": "audiencia de tránsito",
            "me pasé el rojo": "infracción por semáforo",
            "no tenía casco": "infracción por falta de casco",
            "me pidieron los papeles del carro": "documentos del vehículo",
        }

        # -------------------- SINONIMOS INDIVIDUALES --------------------
        self.sinonimos = {
            # Licencia
            "brevete": "licencia de conducir",
            "brevet": "licencia de conducir",
            "carnet de manejo": "licencia de conducir",
            "licencia de manejo": "licencia de conducir",
            "permiso de conducir": "licencia de conducir",
            "carnet de chofer": "licencia de conducir",
            "registro de conducir": "licencia de conducir",
            "pase de conducir": "licencia de conducir",
            "carné de conducción": "licencia de conducir",
            "carnet de conducción": "licencia de conducir",
            "permiso de manejo": "licencia de conducir",
            "licencia para conducir": "licencia de conducir",
            # Policía
            "paco": "policía",
            "policia": "policía",
            "canas": "policía",
            "yuta": "policía",
            "tombos": "policía",
            "oficial": "policía",
            "agente de tránsito": "policía",
            "guardia civil": "policía",
            "carabinero": "policía",
            "autoridad vial": "policía",
            "agente vial": "policía",
            # Accidentes
            "choque": "accidente",
            "colisión": "accidente",
            "percance": "accidente",
            "sinestro": "accidente",
            "impacto": "accidente",
            "crash": "accidente",
            "evento vial": "accidente",
            "incidente vehicular": "accidente",
            # Multa
            "boleta": "multa",
            "infracción": "multa",
            "sanción": "multa",
            "ticket": "multa",
            "citación": "multa",
            "papeleta": "multa",
            "parte": "multa",
            "penalización": "multa",
            "boleto": "multa",
            "comparendo": "multa",
            # Documentos
            "tarjeta de propiedad": "tarjeta de circulación",
            "tarjeta verde": "tarjeta de circulación",
            "documentación vehicular": "tarjeta de circulación",
            "papeles del carro": "documentos del vehículo",
            "papeles del auto": "documentos del vehículo",
            "papeles del coche": "documentos del vehículo",
            "tarjeta de rodaje": "tarjeta de circulación",
            "permiso de circulación": "tarjeta de circulación",
            # Seguro
            "seguro obligatorio": "seguro vehicular",
            "póliza vehicular": "seguro vehicular",
            "seguro automotriz": "seguro vehicular",
            "seguro del carro": "seguro vehicular",
            "seguro del auto": "seguro vehicular",
            # Vehículo
            "carro": "vehículo",
            "auto": "vehículo",
            "coche": "vehículo",
            "automóvil": "vehículo",
            "carruaje": "vehículo",
            "máquina": "vehículo",
            "nave": "vehículo",
            "motorizado": "vehículo",
            "motocicleta": "vehículo",
            "moto": "vehículo",
            # Infracciones específicas
            "exceso de velocidad": "infracción por velocidad",
            "pasarse el rojo": "infracción por semáforo",
            "cruze prohibido": "infracción por cruce prohibido",
            "cruce prohibido": "infracción por cruce prohibido",
            "pasarse el semáforo": "infracción por semáforo",
            "no respetar señal": "infracción de señalización",
            "conducir ebrio": "conducir bajo influencia del alcohol",
            "manejar borracho": "conducir bajo influencia del alcohol",
            "alcoholemia": "prueba de alcohol en sangre",
            # Procesos y autoridades
            "juzgado de tránsito": "tribunal de tránsito",
            "corte de tráfico": "tribunal de tránsito",
            "audiencia vial": "audiencia de tránsito",
            "apelación de multa": "recurso contra sanción",
            "recurso de multa": "recurso contra sanción",
            "impugnación": "recurso contra sanción",
            "departamento de tránsito": "autoridad de tránsito",
            "dirección de tránsito": "autoridad de tránsito",
            # Términos legales
            "decreto ley": "normativa legal",
            "reglamento vial": "código de tránsito",
            "código de tráfico": "código de tránsito",
            "ley de tránsito": "código de tránsito",
            "ordenanza municipal": "normativa local",
            "disposición legal": "normativa legal",
            "acta": "documento oficial",
            "testificación": "testimonio",
            "declaración jurada": "declaración bajo juramento",
            # Situaciones
            "control vehicular": "revisión vehicular",
            "operativo": "control policial",
            "retén": "control policial",
            "punto de control": "control policial",
            "decomiso": "confiscación",
            "incautación": "confiscación",
            "retirada del vehículo": "confiscación del vehículo",
            "grúa": "servicio de remolque",
            "depósito vehicular": "corralón",
            "corralón": "depósito oficial de vehículos",
            "detención vehicular": "inmovilización del vehículo",
            # Verbos
            "revasar": "adelantar",
            "rebasar": "adelantar",
        }

        # -------------------- CATEGORIAS AMPLIAS --------------------
        self.categorias = {
            
            "Licencias": ["licencia", "brevete", "permiso de conducir"],
            "Policía / Tránsito": [
                "paco",
                "policía",
                "tránsito",
                "control",
                "agente de tránsito",
            ],
            "Sanciones / Multas": ["multa", "sanción", "ticket", "penalización"],
            "Accidentes / Siniestros": [
                "accidente",
                "choque",
                "colisión",
                "impacto",
                "siniestro",
            ],
            "Vehículos": ["vehículo", "auto", "coche", "motorizado"],
            "Infracciones": ["infracción", "contravención", "falta"],
            "Peatones": ["peatón", "transeúnte", "persona"],
            "Seguro": ["seguro vehicular", "soat"],
            "Normativa / Leyes": [
                "ley",
                "artículo",
                "código de tránsito",
                "decreto",
                "reglamento",
            ],
            # Puedes seguir añadiendo más categorías si quieres
        }

    def reemplazar_palabras(self, texto: str) -> str:
        texto = texto.lower()

        # 1️⃣ Reemplazar expresiones completas primero
        for expresion, concepto in self.expresiones.items():
            texto = texto.replace(expresion, concepto)

        # 2️⃣ Reemplazar sinónimos individuales
        for palabra, base in self.sinonimos.items():
            texto = re.sub(rf"\b{re.escape(palabra)}\b", base, texto)

        # 3️⃣ Reemplazar categorías amplias
        for categoria, palabras in self.categorias.items():
            for palabra in palabras:
                texto = re.sub(rf"\b{re.escape(palabra)}\b", categoria.lower(), texto)

        return texto


# ---------------- CACHE SIMPLE ---------------------


class ContextCache:
    def __init__(self):
        self.cache: Dict[str, List[Dict[str, str]]] = {}

    def add_entry(self, usuario_id: str, pregunta: str, respuesta: str, contexto: str):
        if usuario_id not in self.cache:
            self.cache[usuario_id] = []
        self.cache[usuario_id].append(
            {"pregunta": pregunta, "respuesta": respuesta, "contexto": contexto}
        )

    def get_history(self, usuario_id: str) -> List[Dict[str, str]]:
        return self.cache.get(usuario_id, [])

    def clear_user_history(self, usuario_id: str):
        if usuario_id in self.cache:
            del self.cache[usuario_id]
