# -*- coding: utf-8 -*-
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.catalog import (
    DepartmentResponse, MunicipalityResponse, EducationLevelResponse, 
    ScholarshipTypeResponse, CreateCatalogItemRequest, ToggleCatalogStatusRequest
)
from app.schemas.auth import GenericResponse
from app.services.catalog_service import CatalogService
from app.api.middlewares.auth_guard import require_roles

router = APIRouter(prefix="/catalogs", tags=["Catálogos Maestros (Sprint 1)"])

@router.get("/departments", response_model=List[DepartmentResponse], summary="Listar Departamentos de Guatemala")
def list_departments(only_active: bool = Query(True), db: Session = Depends(get_db)):
    """Retorna los 22 departamentos oficiales de Guatemala."""
    return CatalogService.get_departments(db, only_active=only_active)

@router.get("/municipalities", response_model=List[MunicipalityResponse], summary="Listar Municipios")
def list_municipalities(department_id: Optional[UUID] = Query(None), only_active: bool = Query(True), db: Session = Depends(get_db)):
    """Retorna los municipios de Guatemala (filtrables por departamento)."""
    return CatalogService.get_municipalities(db, department_id=department_id, only_active=only_active)

@router.get("/education-levels", response_model=List[EducationLevelResponse], summary="Listar Niveles Educativos")
def list_education_levels(only_active: bool = Query(True), db: Session = Depends(get_db)):
    """Retorna los niveles académicos (Básico, Diversificado, Licenciatura, Maestría, Doctorado)."""
    return CatalogService.get_education_levels(db, only_active=only_active)

@router.get("/scholarship-types", response_model=List[ScholarshipTypeResponse], summary="Listar Tipos de Beca")
def list_scholarship_types(only_active: bool = Query(True), db: Session = Depends(get_db)):
    """Retorna los tipos de beca del sistema."""
    return CatalogService.get_scholarship_types(db, only_active=only_active)

@router.post("/scholarship-types", response_model=ScholarshipTypeResponse, status_code=status.HTTP_201_CREATED, summary="HU-004: Crear Tipo de Beca (Admin)")
def create_scholarship_type(
    req: CreateCatalogItemRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["SYSADMIN", "ADMIN_BECAS"]))
):
    """Permite al administrador agregar un nuevo tipo de beca."""
    return CatalogService.create_scholarship_type(db, req)

@router.patch("/scholarship-types/{item_id}/status", response_model=ScholarshipTypeResponse, summary="HU-004: Borrado Lógico de Catálogo (Admin)")
def toggle_scholarship_type(
    item_id: UUID,
    req: ToggleCatalogStatusRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["SYSADMIN", "ADMIN_BECAS"]))
):
    """RB-025: Inactiva o activa lógicamente un elemento de catálogo para preservar integridad histórica."""
    return CatalogService.toggle_scholarship_type_status(db, item_id, req.es_activo)
