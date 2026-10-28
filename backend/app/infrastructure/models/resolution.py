# -*- coding: utf-8 -*-
"""
Modelos de Dominio: Adjudicación, Trazabilidad, Auditoría y Transparencia
Sprint 5 - HU-001 a HU-009
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class CommitteeAct(Base):
    """
    Tabla: actas_dictamen_comite
    Emisión formal del acta colegiada de deliberación y recomendación (Sprint 5 - HU-001).
    """
    __tablename__ = "actas_dictamen_comite"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comite_id = Column(UUID(as_uuid=True), ForeignKey("comites_evaluadores.id"), nullable=False)
    numero_acta = Column(String(60), unique=True, nullable=False, index=True) # Ej: ACTA-COM-2026-001
    
    resumen_deliberacion = Column(Text, nullable=False)
    total_evaluados = Column(Integer, nullable=False, default=0)
    total_recomendados = Column(Integer, nullable=False, default=0)
    
    firmado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    fecha_emision = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    documento_acta_url = Column(String(500), nullable=True)

    comite = relationship("EvaluationCommittee")
    firmado_por = relationship("User")


class AwardResolution(Base):
    """
    Tabla: resoluciones_adjudicacion
    Resolución ministerial oficial de adjudicación de becas del Estado (Sprint 5 - HU-002).
    """
    __tablename__ = "resoluciones_adjudicacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_resolucion = Column(String(60), unique=True, nullable=False, index=True) # Ej: RES-MINEDUC-2026-0089
    convocatoria_id = Column(UUID(as_uuid=True), ForeignKey("convocatorias.id"), nullable=False)

    titulo = Column(String(255), nullable=False)
    considerando = Column(Text, nullable=False)
    por_tanto = Column(Text, nullable=False)

    total_becarios_adjudicados = Column(Integer, nullable=False, default=0)
    monto_total_comprometido = Column(Float, nullable=False, default=0.0)

    emitida_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    estado = Column(String(30), nullable=False, default="FIRMADA") # FIRMADA, PUBLICADA
    fecha_resolucion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    convocatoria = relationship("ScholarshipCall")
    emitida_por = relationship("User")


class ApplicationEvent(Base):
    """
    Tabla: trazabilidad_eventos_solicitud
    Registro cronológico de eventos para consulta del estudiante en tiempo real (HU-003, HU-004).
    """
    __tablename__ = "trazabilidad_eventos_solicitud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_beca.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo_evento = Column(String(50), nullable=False) # CREACION, ENVIO, VERIFICACION, ASIGNACION, EVALUACION, ADJUDICACION
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)

    actor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    visible_estudiante = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    solicitud = relationship("Application", backref="eventos_trazabilidad")
    actor = relationship("User")


class InternalNotification(Base):
    """
    Tabla: notificaciones_internas
    Bandeja de alertas y avisos en plataforma para estudiantes y evaluadores (HU-005).
    """
    __tablename__ = "notificaciones_internas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(30), nullable=False, default="INFO") # INFO, SUCCESS, WARNING, ACTION_REQUIRED
    leida = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    usuario = relationship("User", backref="notificaciones")


class AuditLog(Base):
    """
    Tabla: bitacora_auditoria
    Bitácora inmutable de eventos de seguridad y fiscalización pública (HU-008).
    """
    __tablename__ = "bitacora_auditoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Dimensión 1: ¿Quién realizó la acción?
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    usuario_nombre = Column(String(150), nullable=True) # Nombre capturado en el momento
    usuario_rol = Column(String(50), nullable=True) # Rol activo en la transacción
    ip_address = Column(String(50), nullable=True)
    
    # Dimensión 2: ¿Cuándo ocurrió?
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Dimensión 3: ¿Qué operación se ejecutó?
    modulo = Column(String(50), nullable=False) # IAM, POSTULACIONES, EVALUACIONES, ADJUDICACION
    accion = Column(String(100), nullable=False) # CREAR_SOLICITUD, ASIGNAR_COMITE, ADJUDICAR_BECA, etc.
    operacion = Column(String(100), nullable=True) # Operación explícita (HU-003)
    entidad = Column(String(50), nullable=False) # Application, EvaluationScore, etc.
    entidad_id = Column(String(100), nullable=True)

    # Dimensión 4: ¿Cuál fue el resultado?
    resultado = Column(String(30), nullable=False, default="EXITOSO") # EXITOSO, DENEGADO, ERROR
    detalles = Column(Text, nullable=True) # Justificación, motivo o causa del resultado

    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)

    usuario = relationship("User")
