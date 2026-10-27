# -*- coding: utf-8 -*-
"""
Endpoints de la API: Actas Colegiadas, Resoluciones Ministeriales y Trazabilidad Estudiantil
Sprint 5 - HU-001, HU-002, HU-003, HU-004, HU-005
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user, require_roles
from app.infrastructure.models.user import User
from app.infrastructure.models.resolution import CommitteeAct, AwardResolution
from app.schemas.resolution import (
    CommitteeActCreate, AwardResolutionCreate, AwardResolutionResponse,
    ApplicationEventResponse, InternalNotificationResponse
)
from app.services.resolution_service import ResolutionService

router = APIRouter()

@router.post("/acts", summary="HU-001: Emitir Acta Colegiada de Dictamen")
def create_committee_act(
    req: CommitteeActCreate,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    act = ResolutionService.create_committee_act(
        db=db,
        comite_id=req.comite_id,
        numero_acta=req.numero_acta,
        resumen_deliberacion=req.resumen_deliberacion,
        total_evaluados=req.total_evaluados,
        total_recomendados=req.total_recomendados,
        firmado_por_id=current_user.id
    )
    return {"id": act.id, "numero_acta": act.numero_acta, "fecha_emision": act.fecha_emision}

@router.post("/awards", response_model=AwardResolutionResponse, summary="HU-002: Emitir Resolución Ministerial de Adjudicación")
def issue_award_resolution(
    req: AwardResolutionCreate,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR"])),
    db: Session = Depends(get_db)
):
    res = ResolutionService.issue_award_resolution(
        db=db,
        convocatoria_id=req.convocatoria_id,
        numero_resolucion=req.numero_resolucion,
        titulo=req.titulo,
        considerando=req.considerando,
        por_tanto=req.por_tanto,
        total_becarios=req.total_becarios_adjudicados,
        monto_total=req.monto_total_comprometido,
        emitida_por_id=current_user.id
    )
    return AwardResolutionResponse(
        id=res.id,
        numero_resolucion=res.numero_resolucion,
        convocatoria_id=res.convocatoria_id,
        titulo=res.titulo,
        total_becarios_adjudicados=res.total_becarios_adjudicados,
        monto_total_comprometido=res.monto_total_comprometido,
        estado=res.estado,
        fecha_resolucion=res.fecha_resolucion
    )

@router.get("/timeline/{solicitud_id}", response_model=List[ApplicationEventResponse], summary="HU-003 & HU-004: Trazabilidad en Tiempo Real del Expediente")
def get_application_timeline(
    solicitud_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = any(r.codigo in ["SYSADMIN", "ADMIN_MINEDUC", "DIRECTOR", "EVALUADOR"] for r in current_user.roles)
    events = ResolutionService.get_events_for_application(db, solicitud_id, current_user.id, is_admin)
    return [
        ApplicationEventResponse(
            id=e.id,
            tipo_evento=e.tipo_evento,
            titulo=e.titulo,
            descripcion=e.descripcion,
            creado_en=e.creado_en
        ) for e in events
    ]

@router.get("/notifications", response_model=List[InternalNotificationResponse], summary="HU-005: Bandeja de Notificaciones Internas")
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = ResolutionService.get_user_notifications(db, current_user.id)
    return [
        InternalNotificationResponse(
            id=n.id,
            titulo=n.titulo,
            mensaje=n.mensaje,
            tipo=n.tipo,
            leida=n.leida,
            creado_en=n.creado_en
        ) for n in notifs
    ]

@router.put("/notifications/{notif_id}/read", summary="HU-005: Marcar Notificación como Leída")
def mark_read(
    notif_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = ResolutionService.mark_notification_read(db, notif_id, current_user.id)
    return {"message": "Notificación marcada como leída", "id": notif.id}
