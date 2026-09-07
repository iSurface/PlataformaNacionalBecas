# -*- coding: utf-8 -*-
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class DepartmentResponse(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    es_activo: bool

    class Config:
        from_attributes = True

class MunicipalityResponse(BaseModel):
    id: UUID
    departamento_id: UUID
    codigo: str
    nombre: str
    es_activo: bool

    class Config:
        from_attributes = True

class EducationLevelResponse(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    es_activo: bool

    class Config:
        from_attributes = True

class ScholarshipTypeResponse(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    es_activo: bool

    class Config:
        from_attributes = True

class CreateCatalogItemRequest(BaseModel):
    codigo: str = Field(..., max_length=30)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    departamento_id: Optional[UUID] = None  # Requerido solo si el catálogo es Municipio

class ToggleCatalogStatusRequest(BaseModel):
    es_activo: bool
