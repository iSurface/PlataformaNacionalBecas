# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# --- SPRINT 3: SOLICITUDES Y DOCUMENTOS ---

class ApplicationDraftCreate(BaseModel):
    convocatoria_id: UUID

class ApplicationDraftUpdate(BaseModel):
    datos_formulario: Optional[Dict[str, Any]] = None

class ApplicationWithdrawRequest(BaseModel):
    motivo: str = Field(..., min_length=5, max_length=255, description="Motivo del desistimiento voluntario")

class ApplicationSubmitResponse(BaseModel):
    success: bool
    numero_expediente: str
    estado: str
    fecha_envio: datetime
    message: str

class ApplicationVerificationRequest(BaseModel):
    estado: str = Field(..., description="ADMISIBLE, OBSERVADA, NO_ADMISIBLE")
    observaciones: Optional[str] = None

class ApplicationDocumentResponse(BaseModel):
    id: UUID
    requisito_id: UUID
    nombre_archivo: str
    archivo_hash_sha256: str
    mime_type: str
    tamano_bytes: int
    estado_verificacion: str
    observaciones: Optional[str] = None
    fecha_subida: datetime

    class Config:
        from_attributes = True

class ApplicationResponse(BaseModel):
    id: UUID
    numero_expediente: Optional[str] = None
    convocatoria_id: UUID
    convocatoria_codigo: Optional[str] = None
    convocatoria_titulo: Optional[str] = None
    postulante_id: UUID
    postulante_nombre: Optional[str] = None
    estado: str
    promedio_postulacion: float
    datos_formulario: Optional[Dict[str, Any]] = None
    motivo_desistimiento: Optional[str] = None
    observaciones_verificacion: Optional[str] = None
    puntaje_ponderado_comite: Optional[float] = None
    dictamen_comite: Optional[str] = None
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None
    documentos: List[ApplicationDocumentResponse] = []

    class Config:
        from_attributes = True
