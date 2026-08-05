"""Emite un JWT de desarrollo para hablar con FastAPI sin BFF.

Uso:
    JWT_SECRET_KEY=... python generar_token.py

Imprime unicamente el token. El secreto nunca se imprime: es la credencial
compartida entre el BFF y FastAPI (arquitectura, seccion 10.4), y la terminal
termina en scrollback, capturas y sesiones compartidas.
"""

import os
import sys

import jwt

ACTOR_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

secret = os.getenv("JWT_SECRET_KEY")
if not secret:
    sys.exit("JWT_SECRET_KEY no esta definida; no se puede firmar el token.")

token = jwt.encode({"sub": ACTOR_ID}, secret, algorithm="HS256")

print(token)
