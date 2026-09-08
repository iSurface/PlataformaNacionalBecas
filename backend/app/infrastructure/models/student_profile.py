# -*- coding: utf-8 -*-
"""
Modelo de Dominio: Perfil del Estudiante (Socioeconómico y Académico)
Sprint 2 - HU-001: Gestión del perfil del estudiante
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentProfile(Base):
    """
    Tabla: perfiles_estudiantes
    Contiene la ficha socioeconómica y académica del postulante a becas.
    Relación 1 a 1 con el usuario (User).
    """
    __tablename__ = "perfiles_estudiantes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 1. Datos Socioeconómicos
    direccion_residencia = Column(String(255), nullable=True)
    departamento_residencia_id = Column(UUID(as_uuid=True), ForeignKey("cat_departamentos.id"), nullable=True)
    municipio_residencia_id = Column(UUID(as_uuid=True), ForeignKey("cat_municipios.id"), nullable=True)
    tipo_vivienda = Column(String(50), nullable=True)  # PROPIA, ALQUILADA, PRESTADA, ASENTAMIENTO
    ingreso_mensual_familiar = Column(Numeric(10, 2), nullable=True, default=0.0)
    dependientes_hogar = Column(Integer, nullable=True, default=1)
    tiene_empleo = Column(Boolean, nullable=False, default=False)
    ingreso_propio = Column(Numeric(10, 2), nullable=True, default=0.0)

    # 2. Datos Académicos
    nivel_educativo_id = Column(UUID(as_uuid=True), ForeignKey("cat_niveles_educativos.id"), nullable=True)
    institucion_origen = Column(String(200), nullable=True)
    carrera_o_grado = Column(String(150), nullable=True)
    promedio_general = Column(Float, nullable=True, default=0.0)
    carnet_estudiantil = Column(String(50), nullable=True)

    # 3. Estado del Perfil
    perfil_completo = Column(Boolean, nullable=False, default=False)
    observaciones = Column(Text, nullable=True)
    
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    usuario = relationship("User", backref="perfil_estudiante")
    departamento = relationship("Department")
    municipio = relationship("Municipality")
    nivel_educativo = relationship("EducationLevel")
