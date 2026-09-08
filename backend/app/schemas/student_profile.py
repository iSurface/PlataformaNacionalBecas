# -*- coding: utf-8 -*-
"""
Esquemas Pydantic: Perfil Socioeconómico y Académico del Estudiante
Sprint 2 - HU-001
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class StudentProfileBase(BaseModel):
    # Socioeconómicos
    direccion_residencia: Optional[str] = Field(None, max_length=255)
    departamento_residencia_id: Optional[UUID] = None
    municipio_residencia_id: Optional[UUID] = None
    tipo_vivienda: Optional[str] = Field(None, max_length=50, description="PROPIA, ALQUILADA, PRESTADA, ASENTAMIENTO")
    ingreso_mensual_familiar: Optional[float] = Field(0.0, ge=0.0, description="Ingreso familiar mensual en Quetzales")
    dependientes_hogar: Optional[int] = Field(1, ge=1, le=30, description="Número de personas que dependen de dicho ingreso")
    tiene_empleo: Optional[bool] = False
    ingreso_propio: Optional[float] = Field(0.0, ge=0.0)

    # Académicos
    nivel_educativo_id: Optional[UUID] = None
    institucion_origen: Optional[str] = Field(None, max_length=200)
    carrera_o_grado: Optional[str] = Field(None, max_length=150)
    promedio_general: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Promedio de notas de 0 a 100")
    carnet_estudiantil: Optional[str] = Field(None, max_length=50)

    observaciones: Optional[str] = None

class StudentProfileUpdate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    id: UUID
    usuario_id: UUID
    perfil_completo: bool
    creado_en: datetime
    actualizado_en: datetime

    # Datos adicionales informativos
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    cui: Optional[str] = None

    class Config:
        from_attributes = True
