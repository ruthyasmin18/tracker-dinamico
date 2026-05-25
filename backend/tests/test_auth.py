"""Tests de Autenticación (F1) + integración F4 auto-recálculo desde diario.

Cubre:
- Registro con email + contraseña → JWT.
- Validación de fortaleza de contraseña (mayúscula, número, especial).
- Login correcto / incorrecto (401).
- Email duplicado (409).
- Contraseña hasheada con bcrypt (nunca texto plano).
- JWT decodificable con user_id correcto.
- Refresh de token.
- Logout invalida el token (blacklist).
- Endpoints de diario requieren auth (401 sin token, 403 con token ajeno).
- Auto-recálculo: devuelve adjusted=False si plan en ruta.
"""
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.main import app


# BD en memoria compartida (StaticPool evita pérdida entre conexiones)
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Base.metadata.create_all(bind=_engine)


def override_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)

# ---------- Fixtures ----------

BASE_PAYLOAD = {
    "name": "Mateo",
    "email": "mateo@test.com",
    "password": "Segura123!",
    "age": 24,
    "weight_kg": 75,
    "height_cm": 175,
    "gender": "male",
    "activity_level": "moderate",
    "goal": "maintain",
}


def _register(email: str = BASE_PAYLOAD["email"]) -> dict:
    payload = {**BASE_PAYLOAD, "email": email}
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code in (201, 409), res.json()
    if res.status_code == 409:
        res = client.post("/api/auth/login", json={"email": email, "password": BASE_PAYLOAD["password"]})
    return res.json()


# ---------- Registro ----------

class TestRegister:
    def test_returns_token(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "reg1@test.com"})
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data

    def test_token_contains_user_id(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "reg2@test.com"})
        data = res.json()
        decoded = jwt.decode(data["access_token"], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert decoded["sub"] == data["user_id"]

    def test_duplicate_email_409(self):
        client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "dup@test.com"})
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "dup@test.com"})
        assert res.status_code == 409

    def test_weak_password_no_uppercase(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "w1@test.com", "password": "segura123!"})
        assert res.status_code == 422

    def test_weak_password_no_number(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "w2@test.com", "password": "Segura!!!"})
        assert res.status_code == 422

    def test_weak_password_no_special(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "w3@test.com", "password": "Segura123"})
        assert res.status_code == 422

    def test_too_short_password(self):
        res = client.post("/api/auth/register", json={**BASE_PAYLOAD, "email": "w4@test.com", "password": "Ab1!"})
        assert res.status_code == 422


# ---------- Login ----------

class TestLogin:
    def setup_method(self):
        self.email = "login@test.com"
        _register(self.email)

    def test_correct_credentials(self):
        res = client.post("/api/auth/login", json={"email": self.email, "password": BASE_PAYLOAD["password"]})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_wrong_password_401(self):
        res = client.post("/api/auth/login", json={"email": self.email, "password": "Wrong123!"})
        assert res.status_code == 401

    def test_unknown_email_401(self):
        res = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "Any1thing!"})
        assert res.status_code == 401


# ---------- Refresh & Logout ----------

class TestRefreshLogout:
    def setup_method(self):
        data = _register("session@test.com")
        self.token = data["access_token"]
        self.user_id = data["user_id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_refresh_returns_valid_token(self):
        res = client.post("/api/auth/refresh", json={"access_token": self.token})
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        # El nuevo token debe ser decodificable y contener el mismo user_id
        decoded = jwt.decode(data["access_token"], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert decoded["sub"] == self.user_id

    def test_logout_blacklists_token(self):
        # Logout
        res = client.post("/api/auth/logout", headers=self.headers)
        assert res.status_code == 204
        # El token ya no debe ser válido para acceder al diario
        import datetime
        res2 = client.get(
            f"/api/users/{self.user_id}/diary",
            params={"on": datetime.date.today().isoformat()},
            headers=self.headers,
        )
        assert res2.status_code == 401


# ---------- Seguridad: endpoints protegidos ----------

class TestEndpointProtection:
    def setup_method(self):
        data = _register("prot@test.com")
        self.token = data["access_token"]
        self.user_id = data["user_id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_diary_without_token_401(self):
        import datetime
        res = client.get(
            f"/api/users/{self.user_id}/diary",
            params={"on": datetime.date.today().isoformat()},
        )
        assert res.status_code == 401

    def test_diary_with_valid_token_200(self):
        import datetime
        res = client.get(
            f"/api/users/{self.user_id}/diary",
            params={"on": datetime.date.today().isoformat()},
            headers=self.headers,
        )
        assert res.status_code == 200

    def test_diary_wrong_user_403(self):
        # Registra otro usuario
        other = _register("other_prot@test.com")
        other_headers = {"Authorization": f"Bearer {other['access_token']}"}
        import datetime
        # Intenta acceder al diario del primer usuario con el token del segundo
        res = client.get(
            f"/api/users/{self.user_id}/diary",
            params={"on": datetime.date.today().isoformat()},
            headers=other_headers,
        )
        assert res.status_code == 403


# ---------- Seguridad de contraseña ----------

class TestPasswordSecurity:
    def test_password_stored_as_bcrypt_hash(self):
        from sqlalchemy.orm import Session
        from app.models import User
        _register("bcrypt@test.com")
        db: Session = _SessionLocal()
        try:
            user = db.query(User).filter(User.email == "bcrypt@test.com").first()
            assert user is not None
            assert user.password_hash != BASE_PAYLOAD["password"]
            assert user.password_hash.startswith("$2b$")
        finally:
            db.close()


# ---------- Auto-recálculo sin registros ----------

class TestAutoRecalc:
    def setup_method(self):
        data = _register("autorecalc@test.com")
        self.token = data["access_token"]
        self.user_id = data["user_id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_auto_recalc_no_entries_returns_not_adjusted(self):
        import datetime
        res = client.post(
            "/api/recalc/auto",
            json={"user_id": self.user_id, "target_date": datetime.date.today().isoformat()},
            headers=self.headers,
        )
        assert res.status_code == 200
        assert res.json()["adjusted"] is False
