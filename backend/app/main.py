"""Entry point de la aplicación FastAPI - Tracker Dinámico."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routers import diary, plans, recalc, users


# Crea tablas al arrancar (en producción se usaría Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Tracker Dinámico de Nutrición y Gimnasio",
    description=(
        "API del producto Tracker Dinámico (Taller 4). Implementa las funcionalidades:\n"
        "- **F2** Cálculo Inicial de Objetivos Nutricionales (Mifflin-St Jeor).\n"
        "- **F3** Registro Diario de Alimentos con integración a OpenFoodFacts.\n"
        "- **F4** Motor de Recálculo Dinámico (CORE)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(diary.router)
app.include_router(recalc.router)
app.include_router(plans.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Tracker Dinámico",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
