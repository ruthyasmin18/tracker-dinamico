# Tracker Dinámico de Nutrición y Gimnasio

Implementación fullstack del producto definido en el Taller 4 - Ciclo de Vida del Producto Ágil.

---

## 🚀 Para probar el proyecto (Windows — un solo click)

### Prerrequisitos (una sola vez)

1. **Python 3.11+** → https://www.python.org/downloads/ — al instalar marca **"Add Python to PATH"**.
2. **Node.js 18+** (versión LTS) → https://nodejs.org/.
3. **Git** (opcional) → https://git-scm.com/download/win.

### Pasos

```bash
git clone https://github.com/ruthyasmin18/tracker-dinamico.git
cd tracker-dinamico
start.bat
```

> **Sin Git**: descarga el ZIP desde [aquí](https://github.com/ruthyasmin18/tracker-dinamico/archive/refs/heads/main.zip) → descomprime → doble click en `start.bat`.

La **primera ejecución** tarda 2-3 minutos (instala dependencias automáticamente). Las siguientes arrancan en segundos.

Se abrirá:

- Ventana **Tracker - Backend** → API en http://127.0.0.1:8000 (docs interactivas en `/docs`).
- Ventana **Tracker - Frontend** → app en http://localhost:5173.
- Tu navegador con la app lista para usar.

Para **detener**: doble click en `stop.bat` o cierra las dos ventanas.

---

Desarrolla las funcionalidades:

- **F2** Cálculo Inicial de Objetivos Nutricionales (fórmula Mifflin-St Jeor + distribución de macros).
- **F3** Registro Diario de Alimentos con integración a la API pública de OpenFoodFacts.
- **F4** Motor de Recálculo Dinámico (CORE) — redistribuye macros y propaga ajustes a próximos días cuando ocurre un imprevisto.
- **Plan semanal personalizado** generado a partir del perfil:
  - Plan de comidas con 4 ítems/día que se aproximan al objetivo de macros.
  - Rutina de gimnasio (Full Body / Upper-Lower / Push-Pull-Legs) según nivel de actividad y objetivo.

## Stack

| Capa | Tecnología |
|------|------------|
| Frontend | React 18 + TypeScript + Vite + TailwindCSS + TanStack Query + Recharts |
| Backend | Python 3.11+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + NumPy |
| Base de datos | SQLite (zero-config) — fácilmente cambiable a PostgreSQL vía `DATABASE_URL` |
| API externa | OpenFoodFacts (`world.openfoodfacts.org`) |
| Tests | pytest |

## Estructura

```
tracker-dinamico/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── users.py        # F2
│   │   │   ├── diary.py        # F3
│   │   │   └── recalc.py       # F4
│   │   └── services/
│   │       ├── nutrition.py    # Mifflin-St Jeor + distribución macros
│   │       ├── openfoodfacts.py
│   │       └── recalc_engine.py # CORE
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Onboarding.tsx
    │   │   ├── Diary.tsx
    │   │   ├── Recalc.tsx       # estrella del producto
    │   │   └── Profile.tsx
    │   ├── components/
    │   ├── lib/
    │   └── App.tsx
    └── package.json
```

## Setup rápido (un solo click — Windows)

**Doble click sobre `start.bat`** en la carpeta `tracker-dinamico/`.

El script:
1. Verifica que Python y Node estén instalados.
2. Crea el entorno virtual e instala dependencias si es la primera ejecución.
3. Abre el backend en una ventana (`http://127.0.0.1:8000`).
4. Abre el frontend en otra ventana (`http://localhost:5173`).
5. Abre el navegador automáticamente.

Para detener: ejecuta `stop.bat` o cierra las dos ventanas `Tracker - Backend` y `Tracker - Frontend`.

## Setup manual

### Requisitos

- Python 3.11 o superior
- Node.js 18 o superior
- npm

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1            # Windows PowerShell
# o:   .venv/Scripts/activate          # Git Bash

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

El backend queda en `http://127.0.0.1:8000`.

- **Documentación interactiva (Swagger):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend en `http://localhost:5173`. Vite ya está configurado para proxyear `/api` hacia el backend.

### 3. Tests del backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
pytest -v
```

Cubre 15 tests del servicio nutricional y del motor de recálculo (incluyendo escenarios de proteína intacta, propagación de desviaciones severas y déficit máximo de seguridad).

## Demo flow

1. **Onboarding** (`/onboarding`) → ingresa nombre, edad, peso, altura, género, nivel de actividad y objetivo. Al guardar, el sistema calcula kcal y macros con Mifflin-St Jeor + factor de actividad (PAL).
2. **Mi Plan** (`/plan`) — pantalla inicial después del onboarding:
   - Pestaña **Alimentación**: plan semanal de 7 días con 4 comidas/día (desayuno, almuerzo, cena, snack), seleccionadas de una biblioteca curada de alimentos para aproximarse al objetivo de macros.
   - Pestaña **Entrenamiento**: rutina semanal adaptada (Full Body para sedentarios, Upper/Lower para moderados, Push/Pull/Legs para activos), con series, repeticiones y descansos ajustados al objetivo.
3. **Diario** (`/diary`) → busca alimentos en OpenFoodFacts (ej. "huevo", "yogur"), selecciona porción en gramos y agrégalos a desayuno / almuerzo / cena / snack. Las barras de macros y el total diario se actualizan en tiempo real.
4. **Recálculo** (`/recalc`) — el corazón del producto:
   - Elige un preset (`Comí algo extra` / `Salté una comida` / `Menos tiempo de gym`) o ajusta el delta manualmente.
   - El motor calcula la desviación, redistribuye macros (proteína intacta, ajustando carbs primero y luego grasa) y, si la desviación supera el 30% del objetivo, propaga el ajuste a los próximos 2 días.
   - Se muestra un gráfico Original vs Ajustado y el detalle de cada día.
5. **Perfil** (`/profile`) → muestra TMB, TDEE, objetivos calculados y permite recalcular.

## Decisiones clave del algoritmo CORE (F4)

1. **Proteína intacta**: nunca se reduce — es el macro de soporte para retención muscular.
2. **Redistribución 50/50**: el delta de kcal se reparte 50% en carbs y 50% en grasa (en gramos equivalentes según 4 y 9 kcal/g).
3. **Propagación**: si `|delta| > 30%` del objetivo, el ajuste se reparte con pesos `[0.5, 0.3, 0.2]` en los días `T`, `T+1`, `T+2`.
4. **Déficit máximo de seguridad**: si tras el ajuste el plan caería bajo 70% del objetivo, el sistema rellena con carbs hasta el mínimo seguro.
5. **Lenguaje positivo**: los mensajes nunca culpabilizan al usuario (validado en tests).

## Endpoints clave

| Método | Ruta | Funcionalidad |
|--------|------|---------------|
| POST | `/api/users` | Crear usuario y calcular plan inicial (F2) |
| GET | `/api/users/{id}/goal` | Obtener plan actual |
| POST | `/api/users/{id}/goal/recalculate` | Recalcular plan |
| GET | `/api/foods/search?q={q}` | Buscar en OpenFoodFacts (F3) |
| POST | `/api/users/{id}/diary` | Registrar comida del día (F3) |
| GET | `/api/users/{id}/diary?on=YYYY-MM-DD` | Diario del día con totales |
| **POST** | **`/api/recalc/event`** | **Reportar imprevisto y recibir plan recalibrado (F4 CORE)** |
| GET | `/api/recalc/users/{id}/logs` | Histórico de eventos de recálculo |
| GET | `/api/users/{id}/meal-plan` | Plan semanal de comidas (7 días × 4 comidas) |
| GET | `/api/users/{id}/workout-plan` | Rutina semanal de gimnasio adaptada al perfil |

## Configuración (opcional)

Crea un archivo `.env` en `backend/` para sobrescribir configuración:

```env
DATABASE_URL=postgresql://user:pass@localhost/tracker
CORS_ORIGINS=["http://localhost:5173"]
```

## Producto

Producto definido en el documento `Informe_Taller_4.docx`. Esta implementación es un MVP funcional de las funcionalidades F2 + F3 + F4 (la columna vertebral diferenciadora del producto).
