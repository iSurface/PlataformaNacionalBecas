# -*- coding: utf-8 -*-
"""
Modelos de Dominio: Convocatorias y Requisitos de Becas
Sprint 2 - HU-002, HU-003, HU-004, HU-005
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Numeric, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScholarshipCall(Base):
    """
    Tabla: convocatorias
    Define los programas de becas ofertados por el MINEDUC, sus cupos,
    requisitos mínimos y fechas de vigencia.
    """
    __tablename__ = "convocatorias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), unique=True, nullable=False, index=True) # Ej: "BEC-2026-MEDIO-01"
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    
    # Parametrización
    tipo_beca_id = Column(UUID(as_uuid=True), ForeignKey("cat_tipos_beca.id"), nullable=False)
    nivel_educativo_id = Column(UUID(as_uuid=True), ForeignKey("cat_niveles_educativos.id"), nullable=False)
    departamento_id = Column(UUID(as_uuid=True), ForeignKey("cat_departamentos.id"), nullable=True) # Null = Cobertura Nacional

    cupos_disponibles = Column(Integer, nullable=False, default=1)
    presupuesto_total = Column(Numeric(12, 2), nullable=False, default=0.0)
    monto_individual = Column(Numeric(10, 2), nullable=False, default=0.0)
    promedio_minimo_requerido = Column(Float, nullable=False, default=70.0)

    # Fechas de Vigencia
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=False)

    # Máquina de Estados: BORRADOR, PUBLICADA, CERRADA, EN_EVALUACION, FINALIZADA
    estado = Column(String(30), nullable=False, default="BORRADOR", index=True)
    
    bases_url = Column(String(500), nullable=True)
    cronograma_detalle = Column(JSON, nullable=True) # Fechas clave en JSON
    
    creado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    es_activo = Column(Boolean, nullable=False, default=True)

    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    tipo_beca = relationship("ScholarshipType")
    nivel_educativo = relationship("EducationLevel")
    departamento = relationship("Department")
    creado_por = relationship("User")
    requisitos = relationship("CallRequirement", back_populates="convocatoria", cascade="all, delete-orphan")


class CallRequirement(Base):
    """
    Tabla: requisitos_convocatoria
    Documentos y atestados obligatorios u opcionales solicitados para postular.
    """
    __tablename__ = "requisitos_convocatoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    convocatoria_id = Column(UUID(as_uuid=True), ForeignKey("convocatorias.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), nullable=False) # Ej: "Certificado de notas ciclo 2025"
    descripcion = Column(Text, nullable=True)
    es_obligatorio = Column(Boolean, nullable=False, default=True)
    tipo_documento = Column(String(50), nullable=False, default="PDF") # PDF, IMAGEN
    peso_maximo_mb = Column(Integer, nullable=False, default=5)
    orden = Column(Integer, nullable=False, default=1)

    convocatoria = relationship("ScholarshipCall", back_populates="requisitos")
