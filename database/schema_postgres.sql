CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE,
    contrasena TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chats (
    id_chat SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    titulo TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contextos_chat (
    id_contexto SERIAL PRIMARY KEY,
    id_chat INTEGER NOT NULL,
    contexto_numero INTEGER NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_chat) REFERENCES chats(id_chat) ON DELETE CASCADE,
    UNIQUE (id_chat, contexto_numero)
);

CREATE TABLE IF NOT EXISTS mensajes (
    id_mensaje SERIAL PRIMARY KEY,
    id_chat INTEGER NOT NULL,
    id_contexto INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('pregunta', 'respuesta')),
    contenido TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_chat) REFERENCES chats(id_chat) ON DELETE CASCADE,
    FOREIGN KEY (id_contexto) REFERENCES contextos_chat(id_contexto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
    id_feedback SERIAL PRIMARY KEY,
    id_mensaje INTEGER NOT NULL,
    puntuacion INTEGER NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_mensaje) REFERENCES mensajes(id_mensaje) ON DELETE CASCADE
);
