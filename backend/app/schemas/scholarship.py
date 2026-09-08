# -*- coding: utf-8 -*-
"""
Esquemas Pydantic: Convocatorias, Requisitos y Catálogo Ciudadano
Sprint 2 - HU-002, HU-003, HU-004, HU-005, HU-006
"""
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# ----------------- REQUISITOS -----------------
class CallRequirementBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    descripcion: Optional[str] = None
    es_obligatorio: bool = True
    tipo_documento: str = Field("PDF", description="PDF, IMAGEN")
    peso_maximo_mb: int = Field(5, ge=1, le=25)
    orden: int = Field(1, ge=1)

class CallRequirementCreate(CallRequirementBase):
    pass

class CallRequirementResponse(CallRequirementBase):
    id: UUID
    convocatoria_id: UUID

    class Config:
        from_attributes = True


# ----------------- CONVOCATORIAS -----------------
class ScholarshipCallBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=255)
    descripcion: str = Field(..., min_length=10)
    tipo_beca_id: UUID
    nivel_educativo_id: UUID
    departamento_id: Optional[UUID] = None # Null = Nacional
    cupos_disponibles: int = Field(..., ge=1, description="Mínimo 1 cupo disponible")
    presupuesto_total: float = Field(0.0, ge=0.0)
    monto_individual: float = Field(0.0, ge=0.0)
    promedio_minimo_requerido: float = Field(..., ge=0.0, le=100.0)
    fecha_inicio: datetime
    fecha_cierre: datetime
    bases_url: Optional[str] = None
    cronograma_detalle: Optional[Any] = None

class ScholarshipCallCreate(ScholarshipCallBase):
    codigo: Optional[str] = Field(None, description="Código personalizado o generado automáticamente")
    requisitos_iniciales: Optional[List[CallRequirementCreate]] = []

class ScholarshipCallUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_beca_id: Optional[UUID] = None
    nivel_educativo_id: Optional[UUID] = None
    departamento_id: Optional[UUID] = None
    cupos_disponibles: Optional[int] = Field(None, ge=1)
    presupuesto_total: Optional[float] = Field(None, ge=0.0)
    monto_individual: Optional[float] = Field(None, ge=0.0)
    promedio_minimo_requerido: Optional[float] = Field(None, ge=0.0, le=100.0)
    fecha_inicio: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    bases_url: Optional[str] = None
    cronograma_detalle: Optional[Any] = None


# ----------------- CATÁLOGO PÚBLICO MÓVIL (HU-004 y HU-006) -----------------
class ScholarshipCallPublicSummary(BaseModel):
    """Esquema ultraligero optimizado para baja conectividad móvil"""
    id: UUID
    codigo: str
    titulo: str
    tipo_beca: str
    nivel_educativo: str
    departamento_cobertura: str
    cupos_disponibles: int
    monto_individual: float
    promedio_minimo_requerido: float
    fecha_cierre: datetime
    estado: str
    dias_restantes: int

    class Config:
        from_attributes = True

class PaginatedCallResponse(BaseModel):
    """Estructura paginada para listas eficientes"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ScholarshipCallPublicSummary]


# ----------------- FICHA TÉCNICA DETALLADA (HU-005) -----------------
class ScholarshipCallDetailResponse(ScholarshipCallBase):
    id: UUID
    codigo: str
    estado: str
    tipo_beca_nombre: str
    nivel_educativo_nombre: str
    departamento_nombre: Optional[str] = "Cobertura Nacional"
    creado_en: datetime
    actualizado_en: datetime
    requisitos: List[CallRequirementResponse] = []

    class Config:
        from_attributes = True
