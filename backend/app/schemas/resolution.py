# -*- coding: utf-8 -*-
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# --- SPRINT 5: ADJUDICACIÓN, RESOLUCIONES Y AUDITORÍA ---

class CommitteeActCreate(BaseModel):
    comite_id: UUID
    numero_acta: str
    resumen_deliberacion: str
    total_evaluados: int
    total_recomendados: int

class AwardResolutionCreate(BaseModel):
    convocatoria_id: UUID
    numero_resolucion: str
    titulo: str
    considerando: str
    por_tanto: str
    total_becarios_adjudicados: int
    monto_total_comprometido: float

class AwardResolutionResponse(BaseModel):
    id: UUID
    numero_resolucion: str
    convocatoria_id: UUID
    titulo: str
    total_becarios_adjudicados: int
    monto_total_comprometido: float
    estado: str
    fecha_resolucion: datetime

    class Config:
        from_attributes = True

class ApplicationEventResponse(BaseModel):
    id: UUID
    tipo_evento: str
    titulo: str
    descripcion: str
    creado_en: datetime

    class Config:
        from_attributes = True

class InternalNotificationResponse(BaseModel):
    id: UUID
    titulo: str
    mensaje: str
    tipo: str
    leida: bool
    creado_en: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: UUID
    usuario_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    modulo: str
    accion: str
    entidad: str
    entidad_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
