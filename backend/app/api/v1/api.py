# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, catalogs, admin, students, scholarships,
    applications, evaluations, resolutions, dashboard, reports
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(catalogs.router)
api_router.include_router(admin.router)
api_router.include_router(students.router, prefix="/students", tags=["Estudiantes y Perfil (Sprint 2)"])
api_router.include_router(scholarships.router, prefix="/scholarships", tags=["Convocatorias de Becas (Sprint 2)"])
api_router.include_router(applications.router, prefix="/applications", tags=["Solicitudes y Expedientes (Sprint 3)"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Comités y Evaluaciones (Sprint 4)"])
api_router.include_router(resolutions.router, prefix="/resolutions", tags=["Resoluciones y Trazabilidad (Sprint 5)"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Tablero Gerencial y Transparencia (Sprint 5)"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reportes Consolidados (Sprint 5 - HU29)"])

