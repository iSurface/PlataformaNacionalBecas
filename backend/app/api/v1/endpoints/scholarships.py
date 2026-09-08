# -*- coding: utf-8 -*-
"""
Endpoints de la API: Convocatorias de Becas y Catálogo Ciudadano
Sprint 2 - HU-002, HU-003, HU-004, HU-005, HU-006
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user, require_roles
from app.infrastructure.models.user import User
from app.schemas.scholarship import (
    ScholarshipCallCreate, ScholarshipCallUpdate, CallRequirementCreate,
    CallRequirementResponse, PaginatedCallResponse, ScholarshipCallDetailResponse
)
from app.schemas.auth import GenericResponse
from app.services.scholarship_service import ScholarshipService

router = APIRouter()

# ----------------- ENDPOINTS PÚBLICOS (CIUDADANOS) -----------------

@router.get("/calls", response_model=PaginatedCallResponse, summary="HU-004 & HU-006: Catálogo Público de Becas")
def list_public_calls(
    q: Optional[str] = Query(None, description="Búsqueda libre por título o descripción"),
    tipo_id: Optional[UUID] = Query(None, description="Filtrar por tipo de beca"),
    nivel_id: Optional[UUID] = Query(None, description="Filtrar por nivel educativo"),
    depto_id: Optional[UUID] = Query(None, description="Filtrar por departamento de cobertura"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Cantidad de elementos por página"),
    db: Session = Depends(get_db)
):
    """
    Catálogo público ciudadano sin autenticación.
    Retorna solo convocatorias PUBLICADAS, ordenadas por fecha de cierre próxima,
    optimizadas para baja transferencia de datos móviles.
    """
    return ScholarshipService.list_public_calls(
        db=db,
        q=q,
        tipo_id=tipo_id,
        nivel_id=nivel_id,
        depto_id=depto_id,
        page=page,
        page_size=page_size
    )

@router.get("/calls/{call_id}", response_model=ScholarshipCallDetailResponse, summary="HU-005: Ficha Técnica y Bases de Convocatoria")
def get_call_detail(call_id: UUID, db: Session = Depends(get_db)):
    """
    Consulta pública de la ficha técnica completa de una convocatoria con sus bases,
    requisitos documentales obligatorios y cronograma oficial.
    """
    return ScholarshipService.get_public_call_detail(db, call_id)


# ----------------- ENDPOINTS ADMINISTRATIVOS (MINEDUC) -----------------

@router.post(
    "/calls",
    response_model=ScholarshipCallDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["ADMIN_BECAS", "SYSADMIN"]))],
    summary="HU-002: Creación de Convocatoria (Borrador)"
)
def create_scholarship_call(
    req: ScholarshipCallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite al Administrador de Becas crear una nueva convocatoria en estado BORRADOR."""
    call = ScholarshipService.create_call(db, current_user.id, req)
    return ScholarshipService.get_public_call_detail(db, call.id)

@router.put(
    "/calls/{call_id}",
    response_model=ScholarshipCallDetailResponse,
    dependencies=[Depends(require_roles(["ADMIN_BECAS", "SYSADMIN"]))],
    summary="HU-002: Modificar Convocatoria en Borrador"
)
def update_scholarship_call(
    call_id: UUID,
    req: ScholarshipCallUpdate,
    db: Session = Depends(get_db)
):
    """Permite modificar parámetros de una convocatoria únicamente mientras permanezca en BORRADOR."""
    call = ScholarshipService.update_call(db, call_id, req)
    return ScholarshipService.get_public_call_detail(db, call.id)

@router.post(
    "/calls/{call_id}/requirements",
    response_model=CallRequirementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["ADMIN_BECAS", "SYSADMIN"]))],
    summary="HU-002: Agregar Requisito a Convocatoria"
)
def add_call_requirement(
    call_id: UUID,
    req: CallRequirementCreate,
    db: Session = Depends(get_db)
):
    """Agrega un requisito documental o atestado obligatorio a una convocatoria en borrador."""
    return ScholarshipService.add_requirement(db, call_id, req)

@router.post(
    "/calls/{call_id}/publish",
    response_model=GenericResponse,
    dependencies=[Depends(require_roles(["ADMIN_BECAS", "SYSADMIN"]))],
    summary="HU-003: Publicación Oficial de Convocatoria"
)
def publish_scholarship_call(
    call_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Publica oficialmente la convocatoria haciéndola visible en el catálogo ciudadano.
    Valida requisitos mínimos, cupos y vigencia de fechas.
    """
    call = ScholarshipService.publish_call(db, call_id)
    return GenericResponse(
        success=True,
        message=f"La convocatoria '{call.titulo}' ({call.codigo}) ha sido publicada exitosamente."
    )

@router.post(
    "/calls/{call_id}/close",
    response_model=GenericResponse,
    dependencies=[Depends(require_roles(["ADMIN_BECAS", "SYSADMIN"]))],
    summary="HU-003: Cierre Formal de Convocatoria"
)
def close_scholarship_call(
    call_id: UUID,
    db: Session = Depends(get_db)
):
    """Cierra la recepción de postulaciones para la convocatoria seleccionada."""
    call = ScholarshipService.close_call(db, call_id)
    return GenericResponse(
        success=True,
        message=f"La convocatoria '{call.titulo}' ({call.codigo}) ha sido cerrada para nuevas postulaciones."
    )
