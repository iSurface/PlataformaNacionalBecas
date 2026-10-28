# -*- coding: utf-8 -*-
"""
Modelos de Dominio: Solicitudes de Beca y Atestados Digitales
Sprint 3 - HU-001 a HU-006
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    """
    Tabla: solicitudes_beca
    Expediente digital de postulación ciudadana a convocatorias del MINEDUC.
    """
    __tablename__ = "solicitudes_beca"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_expediente = Column(String(50), unique=True, nullable=True, index=True) # Ej: EXP-2026-MEDIO-00001
    
    postulante_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    convocatoria_id = Column(UUID(as_uuid=True), ForeignKey("convocatorias.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Máquina de Estados:
    # BORRADOR, ENVIADA, EN_VERIFICACION, OBSERVADA, SUBSANADA, ADMISIBLE, NO_ADMISIBLE,
    # ASIGNADA_COMITE, EN_EVALUACION, DICTAMINADA, PENDIENTE_SEGUNDA_APROBACION, ADJUDICADA, RECHAZADA, DESISTIDA
    estado = Column(String(40), nullable=False, default="BORRADOR", index=True)

    promedio_postulacion = Column(Float, nullable=False, default=0.0)
    monto_solicitado = Column(Float, nullable=True, default=0.0) # Monto financiero del beneficio
    requiere_segunda_aprobacion = Column(Boolean, nullable=False, default=False) # True si monto > Q10,000 (HU-001)

    datos_formulario = Column(JSON, nullable=True) # Respuestas y formulario complementario

    motivo_desistimiento = Column(String(255), nullable=True)
    observaciones_verificacion = Column(Text, nullable=True)
    verificado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Puntajes consolidados del comité (Sprint 4 & 5)
    puntaje_ponderado_comite = Column(Float, nullable=True)
    dictamen_comite = Column(String(30), nullable=True) # RECOMENDADO, NO_RECOMENDADO

    # Doble Aprobación y Gobernanza (Sprint 6 - HU-001)
    primera_aprobacion_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_primera_aprobacion = Column(DateTime(timezone=True), nullable=True)
    observaciones_primera_aprobacion = Column(Text, nullable=True)

    segunda_aprobacion_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_segunda_aprobacion = Column(DateTime(timezone=True), nullable=True)
    observaciones_segunda_aprobacion = Column(Text, nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_envio = Column(DateTime(timezone=True), nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    postulante = relationship("User", foreign_keys=[postulante_id], backref="solicitudes")
    convocatoria = relationship("ScholarshipCall", backref="solicitudes")
    verificado_por = relationship("User", foreign_keys=[verificado_por_id])
    primera_aprobacion_por = relationship("User", foreign_keys=[primera_aprobacion_por_id])
    segunda_aprobacion_por = relationship("User", foreign_keys=[segunda_aprobacion_por_id])
    documentos = relationship("ApplicationDocument", back_populates="solicitud", cascade="all, delete-orphan")
    historial = relationship("ApplicationStatusHistory", back_populates="solicitud", cascade="all, delete-orphan", order_by="ApplicationStatusHistory.fecha_cambio.desc()")


class ApplicationDocument(Base):
    """
    Tabla: documentos_solicitud
    Atestados probatorios en PDF cargados con resumen criptográfico SHA-256 (HU-004).
    """
    __tablename__ = "documentos_solicitud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_beca.id", ondelete="CASCADE"), nullable=False, index=True)
    requisito_id = Column(UUID(as_uuid=True), ForeignKey("requisitos_convocatoria.id", ondelete="RESTRICT"), nullable=False)

    nombre_archivo = Column(String(255), nullable=False)
    archivo_ruta = Column(String(500), nullable=False)
    archivo_hash_sha256 = Column(String(64), nullable=False, index=True) # Integridad digital
    mime_type = Column(String(100), nullable=False, default="application/pdf")
    tamano_bytes = Column(Integer, nullable=False)

    # Estados de Verificación Documental: PENDIENTE, CONFORME, OBSERVADO, SUBSANADO
    estado_verificacion = Column(String(30), nullable=False, default="PENDIENTE")
    observaciones = Column(Text, nullable=True)

    fecha_subida = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_subsanacion = Column(DateTime(timezone=True), nullable=True)

    solicitud = relationship("Application", back_populates="documentos")
    requisito = relationship("CallRequirement")


class ApplicationStatusHistory(Base):
    """
    Tabla: historial_estados_solicitud
    Auditoría interna de transiciones de estado del expediente.
    """
    __tablename__ = "historial_estados_solicitud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_beca.id", ondelete="CASCADE"), nullable=False, index=True)
    estado_anterior = Column(String(40), nullable=False)
    estado_nuevo = Column(String(40), nullable=False)
    cambiado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_cambio = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    solicitud = relationship("Application", back_populates="historial")
    cambiado_por = relationship("User")
