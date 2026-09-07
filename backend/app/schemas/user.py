# -*- coding: utf-8 -*-
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

class RoleResponse(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    es_activo: bool

    class Config:
        from_attributes = True

class UserDetailResponse(BaseModel):
    id: UUID
    cui: str
    email: EmailStr
    estado: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    nombre_completo: str
    telefono: Optional[str]
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]
    roles: List[str]

    class Config:
        from_attributes = True

class AssignRolesRequest(BaseModel):
    roles_codigos: List[str]
