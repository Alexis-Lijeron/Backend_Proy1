1. Crear entorno virtual
    python -m venv venv
2. Activar entorno virtual
    source venv/bin/activate        # (Linux/Mac)
    venv\Scripts\activate           # (Windows)
3. Instalar las dependencias
    pip install -r requirements.txt
4. Levantar contenedor de base de datos
    docker-compose up -d
5. Ejecutar 
    uvicorn app.main:app --reload
