# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.api.v1.endpoints import auth, catalogs, admin, students, scholarships

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(catalogs.router)
api_router.include_router(admin.router)
api_router.include_router(students.router, prefix="/students", tags=["Estudiantes y Perfil (Sprint 2)"])
api_router.include_router(scholarships.router, prefix="/scholarships", tags=["Convocatorias de Becas (Sprint 2)"])
