# -*- coding: utf-8 -*-
"""
Servicio de Dominio: Perfil del Estudiante
Sprint 2 - HU-001: Gestión del perfil socioeconómico y académico
"""
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.models.student_profile import StudentProfile
from app.infrastructure.models.user import User
from app.schemas.student_profile import StudentProfileUpdate, StudentProfileResponse

class StudentProfileService:

    @staticmethod
    def get_or_create_profile(db: Session, user_id: UUID) -> StudentProfileResponse:
        """Obtiene o inicializa la ficha socioeconómica y académica del postulante."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        profile = db.query(StudentProfile).filter(StudentProfile.usuario_id == user_id).first()
        if not profile:
            profile = StudentProfile(usuario_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # Construir respuesta con datos de identidad
        persona = user.persona
        nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}" if persona else "Estudiante"

        res = StudentProfileResponse.model_validate(profile)
        res.nombre_completo = nombre_completo
        res.email = user.email
        res.cui = user.cui
        return res

    @staticmethod
    def update_profile(db: Session, user_id: UUID, req: StudentProfileUpdate) -> StudentProfileResponse:
        """Actualiza los datos del perfil y evalúa si cumple la completitud requerida."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        profile = db.query(StudentProfile).filter(StudentProfile.usuario_id == user_id).first()
        if not profile:
            profile = StudentProfile(usuario_id=user_id)
            db.add(profile)

        # Actualizar campos enviados
        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)

        # Validar completitud de perfil (Campos mínimos esenciales para poder postular a una beca)
        tiene_socio = bool(profile.departamento_residencia_id and profile.tipo_vivienda and profile.ingreso_mensual_familiar is not None)
        tiene_academico = bool(profile.nivel_educativo_id and profile.institucion_origen and profile.promedio_general and profile.promedio_general > 0)
        profile.perfil_completo = (tiene_socio and tiene_academico)

        db.commit()
        db.refresh(profile)

        persona = user.persona
        nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}" if persona else "Estudiante"

        res = StudentProfileResponse.model_validate(profile)
        res.nombre_completo = nombre_completo
        res.email = user.email
        res.cui = user.cui
        return res
