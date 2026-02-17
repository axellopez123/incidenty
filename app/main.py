from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes.auth import router as auth_router
from app.company.routes.company import router as company_router
from app.database import database, init_db

from typing import List

import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "*"
]

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

app.include_router(auth_router, prefix="/api")
app.include_router(company_router, prefix="/api")


# # Crear el directorio media si no existe
# os.makedirs("media", exist_ok=True)

# # Montar la carpeta media en /media
# app.mount("/media", StaticFiles(directory="media"), name="media")
