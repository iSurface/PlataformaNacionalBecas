# -*- coding: utf-8 -*-
"""
Endpoints de la API: Solicitudes de Beca, Carga Documental SHA-256 y Admisibilidad
Sprint 3 - HU-001 a HU-006
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user, require_roles
from app.infrastructure.models.user import User
from app.infrastructure.models.application import Application, ApplicationDocument
from app.schemas.application import (
    ApplicationDraftCreate, ApplicationDraftUpdate, ApplicationWithdrawRequest,
    ApplicationSubmitResponse, ApplicationVerificationRequest,
    ApplicationDocumentResponse, ApplicationResponse
)
from app.services.application_service import ApplicationService
from app.services.document_service import DocumentService

router = APIRouter()

def _map_app(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        numero_expediente=app.numero_expediente,
        convocatoria_id=app.convocatoria_id,
        convocatoria_codigo=app.convocatoria.codigo if app.convocatoria else None,
        convocatoria_titulo=app.convocatoria.titulo if app.convocatoria else None,
        postulante_id=app.postulante_id,
        postulante_nombre=app.postulante.nombre_completo if app.postulante else None,
        estado=app.estado,
        promedio_postulacion=app.promedio_postulacion,
        datos_formulario=app.datos_formulario,
        motivo_desistimiento=app.motivo_desistimiento,
        observaciones_verificacion=app.observaciones_verificacion,
        puntaje_ponderado_comite=app.puntaje_ponderado_comite,
        dictamen_comite=app.dictamen_comite,
        fecha_creacion=app.fecha_creacion,
        fecha_envio=app.fecha_envio,
        documentos=[
            ApplicationDocumentResponse(
                id=d.id,
                requisito_id=d.requisito_id,
                nombre_archivo=d.nombre_archivo,
                archivo_hash_sha256=d.archivo_hash_sha256,
                mime_type=d.mime_type,
                tamano_bytes=d.tamano_bytes,
                estado_verificacion=d.estado_verificacion,
                observaciones=d.observaciones,
                fecha_subida=d.fecha_subida
            ) for d in (app.documentos or [])
        ]
    )

@router.post("/draft", response_model=ApplicationResponse, summary="HU-001: Crear o Recuperar Borrador")
def create_draft(
    req: ApplicationDraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = ApplicationService.create_or_get_draft(db, current_user.id, req.convocatoria_id)
    return _map_app(app)

@router.put("/{application_id}/draft", response_model=ApplicationResponse, summary="HU-001: Actualizar Datos de Borrador")
def update_draft(
    application_id: UUID,
    req: ApplicationDraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = ApplicationService.update_draft(db, application_id, current_user.id, req.datos_formulario)
    return _map_app(app)

@router.post("/{application_id}/documents", response_model=ApplicationDocumentResponse, summary="HU-004: Carga de Atestado PDF con SHA-256")
def upload_document(
    application_id: UUID,
    requisito_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = DocumentService.upload_document(db, application_id, requisito_id, file, current_user.id)
    return ApplicationDocumentResponse(
        id=doc.id,
        requisito_id=doc.requisito_id,
        nombre_archivo=doc.nombre_archivo,
        archivo_hash_sha256=doc.archivo_hash_sha256,
        mime_type=doc.mime_type,
        tamano_bytes=doc.tamano_bytes,
        estado_verificacion=doc.estado_verificacion,
        observaciones=doc.observaciones,
        fecha_subida=doc.fecha_subida
    )

@router.post("/{application_id}/submit", response_model=ApplicationSubmitResponse, summary="HU-002: Formalización y Generación de Expediente Inmutable")
def submit_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = ApplicationService.submit_application(db, application_id, current_user.id)
    return ApplicationSubmitResponse(
        success=True,
        numero_expediente=app.numero_expediente,
        estado=app.estado,
        fecha_envio=app.fecha_envio,
        message=f"Postulación formalizada con éxito. Correlativo oficial: {app.numero_expediente}"
    )

@router.post("/{application_id}/withdraw", response_model=ApplicationResponse, summary="HU-003: Desistimiento Voluntario de Postulación")
def withdraw_application(
    application_id: UUID,
    req: ApplicationWithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = ApplicationService.withdraw_application(db, application_id, current_user.id, req.motivo)
    return _map_app(app)

@router.post("/{application_id}/cure", response_model=ApplicationResponse, summary="HU-006: Subsanación de Expediente Observado")
def cure_observations(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = ApplicationService.cure_observations(db, application_id, current_user.id)
    return _map_app(app)

@router.get("/my-applications", response_model=List[ApplicationResponse], summary="Consultar Mis Solicitudes")
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.postulante_id == current_user.id).order_by(Application.fecha_creacion.desc()).all()
    return [_map_app(a) for a in apps]

@router.get("/admin/list", response_model=List[ApplicationResponse], summary="HU-005: Bandeja de Verificación Administrativa (MINEDUC)")
def list_applications_for_verification(
    convocatoria_id: Optional[UUID] = Query(None),
    estado: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    query = db.query(Application)
    if convocatoria_id:
        query = query.filter(Application.convocatoria_id == convocatoria_id)
    if estado:
        query = query.filter(Application.estado == estado)
    apps = query.order_by(Application.fecha_creacion.desc()).limit(limit).all()
    return [_map_app(a) for a in apps]

@router.get("/{application_id}", response_model=ApplicationResponse, summary="Consultar Detalle de Expediente")
def get_application_detail(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expediente no encontrado")
    
    # Validar que sea el postulante o personal MINEDUC
    is_admin = any(r.codigo in ["SYSADMIN", "ADMIN_MINEDUC", "EVALUADOR", "DIRECTOR"] for r in current_user.roles)
    if not is_admin and str(app.postulante_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    return _map_app(app)

@router.post("/{application_id}/verify", response_model=ApplicationResponse, summary="HU-005: Dictamen de Admisibilidad Administrativa")
def verify_application(
    application_id: UUID,
    req: ApplicationVerificationRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    app = ApplicationService.verify_admissibility(db, application_id, current_user.id, req.estado, req.observaciones)
    return _map_app(app)
