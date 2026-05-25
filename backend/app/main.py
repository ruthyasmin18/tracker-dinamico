"""Entry point de la aplicación FastAPI - Tracker Dinámico."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db import Base, engine
from app.routers import auth, dashboard, diary, plans, recalc, routines, users


def _migrate_db() -> None:
    """Agrega columnas de F1 si la BD ya existía sin ellas (SQLite-safe)."""
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE users ADD COLUMN email TEXT",
            "ALTER TABLE users ADD COLUMN password_hash TEXT",
            "ALTER TABLE users ADD COLUMN last_login_at DATETIME",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # columna ya existe


# Crea tablas al arrancar y aplica migración incremental
Base.metadata.create_all(bind=engine)
_migrate_db()


app = FastAPI(
    title="Tracker Dinámico de Nutrición y Gimnasio",
    description=(
        "API del producto Tracker Dinámico (Taller 4). Implementa las funcionalidades:\n"
        "- **F1** Gestión de Usuario y Sesión Persistente (bcrypt + JWT HS256 60 días).\n"
        "- **F2** Cálculo Inicial de Objetivos Nutricionales (Mifflin-St Jeor).\n"
        "- **F3** Registro Diario de Alimentos — búsqueda híbrida local + OpenFoodFacts.\n"
        "- **F4** Motor de Recálculo Dinámico (CORE) con auto-detección desde diario.\n"
        "- **F5** Generador de Rutinas Express adaptado a tiempo y equipo disponible.\n"
        "- **F6** Dashboard de Progreso y Analítica semanal."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_allow_all else settings.cors_origins,
    allow_credentials=not settings.cors_allow_all,  # * incompatible con credentials=True
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(diary.router)
app.include_router(recalc.router)
app.include_router(plans.router)
app.include_router(routines.router)   # F5 — Generador de Rutinas Express
app.include_router(dashboard.router)  # F6 — Dashboard de Progreso


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
