# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.infrastructure.models.user import Base
from app.infrastructure.models import catalog, student_profile, scholarship, application, evaluation, resolution
from app.core.database import engine

# Crear tablas si no existen (en caso de despliegue directo en nube)
try:
    Base.metadata.create_all(bind=engine)
except Exception as ex:
    print(f"[MODULE INIT WARNING] DB not reachable at import time: {ex}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="API RESTful de la Plataforma Nacional de Becas (MINEDUC Guatemala) - Sprints 1 a 5 (Completo)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todas las rutas del Sprint 1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_db_init():
    """Inicializa esquemas, aplica migraciones DDL y siembra datos iniciales automáticamente"""
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS google_id VARCHAR(100) UNIQUE;"))
            conn.execute(text("ALTER TABLE usuarios ALTER COLUMN password_hash DROP NOT NULL;"))

            # Sprint 6 - HU-001: Doble Aprobación y Gobernanza Financiera (> Q10k)
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS monto_solicitado FLOAT DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS requiere_segunda_aprobacion BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS primera_aprobacion_por_id UUID REFERENCES usuarios(id);"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS fecha_primera_aprobacion TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS observaciones_primera_aprobacion TEXT;"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS segunda_aprobacion_por_id UUID REFERENCES usuarios(id);"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS fecha_segunda_aprobacion TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE solicitudes_beca ADD COLUMN IF NOT EXISTS observaciones_segunda_aprobacion TEXT;"))

            # Sprint 6 - HU-003: Bitácora Forense de 4 Dimensiones
            conn.execute(text("ALTER TABLE bitacora_auditoria ADD COLUMN IF NOT EXISTS usuario_nombre VARCHAR(150);"))
            conn.execute(text("ALTER TABLE bitacora_auditoria ADD COLUMN IF NOT EXISTS usuario_rol VARCHAR(50);"))
            conn.execute(text("ALTER TABLE bitacora_auditoria ADD COLUMN IF NOT EXISTS operacion VARCHAR(100);"))
            conn.execute(text("ALTER TABLE bitacora_auditoria ADD COLUMN IF NOT EXISTS resultado VARCHAR(30) DEFAULT 'EXITOSO';"))
            conn.execute(text("ALTER TABLE bitacora_auditoria ADD COLUMN IF NOT EXISTS detalles TEXT;"))

            # Sprint 6 - Flexibilización CUI y Documentos Extranjeros
            conn.execute(text("ALTER TABLE usuarios ALTER COLUMN cui TYPE VARCHAR(50);"))
    except Exception as ex:
        print(f"[STARTUP DDL MIGRATION] {ex}")

    try:
        from app.infrastructure.seeders import seed_initial_data
        seed_initial_data()
    except Exception as ex:
        print(f"[STARTUP DB INIT] {ex}")

@app.get("/", summary="Página de Pruebas Frontend", tags=["Frontend"])
def serve_frontend_page():
    """Sirve la interfaz de usuario web interactiva para pruebas de inicio de sesión y registro"""
    import os
    from fastapi.responses import FileResponse
    static_file = os.path.join(os.path.dirname(__file__), "app", "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file, media_type="text/html")
    return {"message": "Plataforma Nacional de Becas API - Visite /docs para Swagger UI"}

@app.get("/health", tags=["Salud del Sistema"])
def health_check():
    """Endpoint de verificación de estado y salud de la API"""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "sprint": "Sprint 1 - Cimientos de Identidad, Seguridad y Catálogos",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
