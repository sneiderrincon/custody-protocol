#!/usr/bin/env bash

export JWT_SECRET_KEY="mi_clave_secreta_para_desarrollo"
export CORS_ALLOWED_ORIGINS="http://localhost:5500"

source .venv/Scripts/activate
python -m uvicorn api.main:app --reload