# -*- coding: utf-8 -*-
"""
Modelos de Dominio: Comités Evaluadores y Rúbricas Digitales
Sprint 4 - HU-001 a HU-006
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class EvaluationCommittee(Base):
    """
    Tabla: comites_evaluadores
    Comités colegiados constituidos para calificar expedientes de becas (HU-002).
    """
    __tablename__ = "comites_evaluadores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), unique=True, nullable=False, index=True) # Ej: COM-2026-MEDIO-01
    nombre = Column(String(150), nullable=False)
    convocatoria_id = Column(UUID(as_uuid=True), ForeignKey("convocatorias.id", ondelete="RESTRICT"), nullable=False)

    estado = Column(String(30), nullable=False, default="ACTIVO") # ACTIVO, EN_EVALUACION, FINALIZADO
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    convocatoria = relationship("ScholarshipCall", backref="comites")
    miembros = relationship("CommitteeMember", back_populates="comite", cascade="all, delete-orphan")
    asignaciones = relationship("ApplicationAssignment", back_populates="comite", cascade="all, delete-orphan")


class CommitteeMember(Base):
    """
    Tabla: miembros_comite
    Integrantes del comité evaluador con declaración ética de no conflicto (HU-002, HU-004).
    """
    __tablename__ = "miembros_comite"
    __table_args__ = (UniqueConstraint("comite_id", "usuario_id", name="uq_comite_usuario"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comite_id = Column(UUID(as_uuid=True), ForeignKey("comites_evaluadores.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    rol_comite = Column(String(30), nullable=False, default="EVALUADOR") # PRESIDENTE, SECRETARIO, VOCAL, EVALUADOR
    declaracion_conflicto = Column(Boolean, nullable=False, default=False)
    fecha_declaracion = Column(DateTime(timezone=True), nullable=True)

    comite = relationship("EvaluationCommittee", back_populates="miembros")
    usuario = relationship("User")


class ApplicationAssignment(Base):
    """
    Tabla: asignaciones_expediente
    Asignación de expedientes admitidos a comités evaluadores (HU-003).
    """
    __tablename__ = "asignaciones_expediente"
    __table_args__ = (UniqueConstraint("solicitud_id", "comite_id", name="uq_solicitud_comite"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_beca.id", ondelete="CASCADE"), nullable=False)
    comite_id = Column(UUID(as_uuid=True), ForeignKey("comites_evaluadores.id", ondelete="CASCADE"), nullable=False)

    estado = Column(String(30), nullable=False, default="ASIGNADO") # ASIGNADO, EN_EVALUACION, EVALUADO
    fecha_asignacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    solicitud = relationship("Application", backref="asignacion_comite")
    comite = relationship("EvaluationCommittee", back_populates="asignaciones")


class EvaluationScore(Base):
    """
    Tabla: calificaciones_evaluador
    Evaluación individual mediante rúbrica digital estandarizada (0-100 pts) (HU-005, HU-006).
    """
    __tablename__ = "calificaciones_evaluador"
    __table_args__ = (UniqueConstraint("solicitud_id", "evaluador_id", name="uq_solicitud_evaluador"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_beca.id", ondelete="CASCADE"), nullable=False)
    evaluador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    comite_id = Column(UUID(as_uuid=True), ForeignKey("comites_evaluadores.id", ondelete="CASCADE"), nullable=False)

    # Rúbrica estándar: Académico (40 pts) + Socioeconómico (40 pts) + Ensayo/Atestados (20 pts)
    puntaje_academico = Column(Float, nullable=False, default=0.0)
    puntaje_socioeconomico = Column(Float, nullable=False, default=0.0)
    puntaje_ensayo_atestados = Column(Float, nullable=False, default=0.0)
    puntaje_total = Column(Float, nullable=False, default=0.0)

    dictamen_individual = Column(String(30), nullable=False, default="FAVORABLE") # FAVORABLE, NO_FAVORABLE, RESERVA
    observaciones = Column(Text, nullable=True)
    criterios_detalle = Column(JSON, nullable=True) # Calificaciones detalladas por criterio

    fecha_evaluacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    solicitud = relationship("Application", backref="calificaciones")
    evaluador = relationship("User")
    comite = relationship("EvaluationCommittee")
