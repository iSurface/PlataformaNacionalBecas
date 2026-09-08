# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.infrastructure.models.user import Base
from app.infrastructure.models import catalog, student_profile, scholarship
from app.core.database import engine

# Crear tablas si no existen (en caso de despliegue directo en nube)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="API RESTful de la Plataforma Nacional de Becas (MINEDUC Guatemala) - Sprints 1 & 2"
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
    """Inicializa esquemas y siembra datos iniciales automáticamente en PostgreSQL de AWS al arrancar"""
    try:
        from app.infrastructure.seeders import seed_initial_data
        seed_initial_data()
    except Exception as ex:
        print(f"[STARTUP DB INIT] {ex}")

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
