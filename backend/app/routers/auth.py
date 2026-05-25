"""Router de Autenticación (F1) — Gestión de Usuario y Sesión Persistente.

Endpoints:
- POST /api/auth/register  → crea cuenta con email + contraseña, devuelve JWT.
- POST /api/auth/login     → valida credenciales, devuelve JWT 60 días.
- POST /api/auth/refresh   → emite nuevo token sin requerir contraseña.
- POST /api/auth/logout    → invalida el token actual (blacklist en memoria).

Seguridad:
- Contraseña hasheada con bcrypt cost=12 (nunca texto plano en BD).
- JWT HS256, expiración 60 días (sesión persistente sin reingreso).
- Blacklist en memoria para logout inmediato.
- Validación de fortaleza de contraseña (mayúscula + número + especial).
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import NutritionGoal, User
from app.schemas import AuthLogin, AuthRegister, RefreshTokenIn, TokenOut
from app.services.nutrition import calculate_nutrition_goal


router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------- Blacklist de logout (en memoria — suficiente para prototipo) ----------
_LOGOUT_BLACKLIST: set[str] = set()

# ---------- Security scheme ----------
_http_bearer = HTTPBearer(auto_error=False)


# ---------- Helpers ----------

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(days=settings.access_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ---------- Dependencia reutilizable ----------

def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_http_bearer)],
) -> str:
    """Valida el JWT Bearer y retorna el user_id.

    Inyectar con: user_id: str = Depends(get_current_user_id)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida — inicia sesión primero",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    if token in _LOGOUT_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión cerrada — vuelve a iniciar sesión",
        )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload["sub"]  # user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada — vuelve a iniciar sesión",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


# ---------- Endpoints ----------

@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y calcula su objetivo nutricional inicial."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        age=payload.age,
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        gender=payload.gender.value,
        activity_level=payload.activity_level.value,
        goal=payload.goal.value,
    )
    db.add(user)
    db.flush()

    result = calculate_nutrition_goal(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        activity_level=user.activity_level,
        goal=user.goal,
    )
    db.add(NutritionGoal(
        user_id=user.id,
        kcal=result.kcal,
        protein_g=result.protein_g,
        carbs_g=result.carbs_g,
        fat_g=result.fat_g,
        bmr=result.bmr,
        tdee=result.tdee,
    ))
    db.commit()
    db.refresh(user)

    return TokenOut(access_token=_create_token(user.id), user_id=user.id)


@router.post("/login", response_model=TokenOut)
def login(payload: AuthLogin, db: Session = Depends(get_db)):
    """Valida credenciales y devuelve un JWT de 60 días."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return TokenOut(access_token=_create_token(user.id), user_id=user.id)


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshTokenIn):
    """Emite un nuevo token sin requerir contraseña (sesión persistente).

    El token original sigue siendo válido hasta que expire o se haga logout.
    """
    if payload.access_token in _LOGOUT_BLACKLIST:
        raise HTTPException(status_code=401, detail="Token invalidado — inicia sesión de nuevo")
    try:
        decoded = jwt.decode(
            payload.access_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = decoded["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado — inicia sesión de nuevo")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return TokenOut(access_token=_create_token(user_id), user_id=user_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_http_bearer)],
):
    """Invalida el token actual — el usuario deberá volver a iniciar sesión."""
    if credentials:
        _LOGOUT_BLACKLIST.add(credentials.credentials)
