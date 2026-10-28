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
    ApplicationDocumentResponse, ApplicationResponse,
    FirstApprovalRequest, SecondApprovalRequest
)
from app.services.application_service import ApplicationService
from app.services.document_service import DocumentService

router = APIRouter()

def _map_app(app: Application) -> ApplicationResponse:
    monto = app.monto_solicitado or (app.convocatoria.monto_individual if app.convocatoria else 0.0)
    requiere_2da = app.requiere_segunda_aprobacion or (monto > 10000.0)
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
        monto_solicitado=monto,
        requiere_segunda_aprobacion=requiere_2da,
        datos_formulario=app.datos_formulario,
        motivo_desistimiento=app.motivo_desistimiento,
        observaciones_verificacion=app.observaciones_verificacion,
        puntaje_ponderado_comite=app.puntaje_ponderado_comite,
        dictamen_comite=app.dictamen_comite,
        primera_aprobacion_por_id=app.primera_aprobacion_por_id,
        primera_aprobacion_por_nombre=app.primera_aprobacion_por.nombre_completo if app.primera_aprobacion_por else None,
        fecha_primera_aprobacion=app.fecha_primera_aprobacion,
        observaciones_primera_aprobacion=app.observaciones_primera_aprobacion,
        segunda_aprobacion_por_id=app.segunda_aprobacion_por_id,
        segunda_aprobacion_por_nombre=app.segunda_aprobacion_por.nombre_completo if app.segunda_aprobacion_por else None,
        fecha_segunda_aprobacion=app.fecha_segunda_aprobacion,
        observaciones_segunda_aprobacion=app.observaciones_segunda_aprobacion,
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
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR", "ADMIN_BECAS", "DIRECTOR", "AUDITOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    query = db.query(Application)
    if convocatoria_id:
        query = query.filter(Application.convocatoria_id == convocatoria_id)
    if estado:
        query = query.filter(Application.estado == estado)
    apps = query.order_by(Application.fecha_creacion.desc()).limit(limit).all()
    return [_map_app(a) for a in apps]

# =========================================================================
# SPRINT 6: GOBERNANZA, DOBLE APROBACIÓN Y AUDITORÍA FORENSE
# =========================================================================

@router.get("/pending-second-approval", response_model=List[ApplicationResponse], summary="HU-001: Listado de Expedientes Pendientes de Segunda Aprobación (> Q10,000)")
def list_pending_second_approval(
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    """Retorna solicitudes de beca con monto > Q 10,000.00 que requieren ratificación de Dirección Ministerial."""
    apps = db.query(Application).filter(Application.estado == "PENDIENTE_SEGUNDA_APROBACION").order_by(Application.fecha_actualizacion.desc()).all()
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
    is_admin = any(r.codigo in ["SYSADMIN", "ADMIN_MINEDUC", "EVALUADOR", "DIRECTOR", "ADMIN_BECAS", "AUDITOR"] for r in current_user.roles)
    if not is_admin and str(app.postulante_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    return _map_app(app)

@router.post("/{application_id}/verify", response_model=ApplicationResponse, summary="HU-005: Dictamen de Admisibilidad Administrativa")
def verify_application(
    application_id: UUID,
    req: ApplicationVerificationRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR", "ADMIN_BECAS", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    app = ApplicationService.verify_admissibility(db, application_id, current_user.id, req.estado, req.observaciones)
    return _map_app(app)

@router.post("/{application_id}/approve-first", response_model=ApplicationResponse, summary="HU-001: Primera Aprobación (Evaluador / Coordinador)")
def approve_first(
    application_id: UUID,
    req: FirstApprovalRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Emite la primera aprobación del expediente.
    Si el monto > Q 10,000.00, transiciona a PENDIENTE_SEGUNDA_APROBACION.
    Si el monto <= Q 10,000.00, se adjudica directamente.
    """
    app = ApplicationService.approve_first_phase(
        db=db,
        solicitud_id=application_id,
        approver=current_user,
        monto_aprobado=req.monto_aprobado,
        observaciones=req.observaciones
    )
    return _map_app(app)

@router.post("/{application_id}/approve-second", response_model=ApplicationResponse, summary="HU-001: Segunda Aprobación Ministerial Obligatoria (> Q10,000)")
def approve_second(
    application_id: UUID,
    req: SecondApprovalRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Segunda aprobación obligatoria emitida por Dirección Ministerial.
    Aplica RB-014: Se deniega si el usuario es el mismo que realizó la primera aprobación.
    """
    app = ApplicationService.approve_second_phase(
        db=db,
        solicitud_id=application_id,
        approver=current_user,
        observaciones=req.observaciones
    )
    return _map_app(app)

@router.post("/{application_id}/reject", response_model=ApplicationResponse, summary="HU-003: Rechazo Formal de Expediente con Asiento Forense")
def reject_application(
    application_id: UUID,
    motivo: str = Query(..., min_length=3, description="Causa o justificación legal del rechazo"),
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR", "DIRECTOR", "ADMIN_BECAS", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    """Rechaza el expediente y asienta el registro inmutable en bitácora de auditoría."""
    app = ApplicationService.reject_application(
        db=db,
        solicitud_id=application_id,
        reviewer=current_user,
        motivo=motivo
    )
    return _map_app(app)
