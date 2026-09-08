# -*- coding: utf-8 -*-
"""
Endpoints de la API: Estudiantes y Perfil Socioeconómico
Sprint 2 - HU-001
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user
from app.infrastructure.models.user import User
from app.schemas.student_profile import StudentProfileUpdate, StudentProfileResponse
from app.services.student_profile_service import StudentProfileService

router = APIRouter()

@router.get("/me/profile", response_model=StudentProfileResponse, summary="HU-001: Consultar Perfil Propio")
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Permite al postulante autenticado consultar su ficha socioeconómica y académica."""
    return StudentProfileService.get_or_create_profile(db, current_user.id)

@router.put("/me/profile", response_model=StudentProfileResponse, summary="HU-001: Actualizar Perfil Propio")
def update_my_profile(req: StudentProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Permite al postulante actualizar su información socioeconómica y académica."""
    return StudentProfileService.update_profile(db, current_user.id, req)
