# -*- coding: utf-8 -*-
"""
Endpoints de la API: Comités Colegiados, Asignación de Expedientes y Rúbrica Digital (0-100 pts)
Sprint 4 - HU-001 a HU-006
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user, require_roles
from app.infrastructure.models.user import User
from app.infrastructure.models.evaluation import EvaluationCommittee, CommitteeMember, ApplicationAssignment, EvaluationScore
from app.infrastructure.models.application import Application
from app.schemas.evaluation import (
    CommitteeCreate, CommitteeMemberAdd, ConflictDeclarationRequest,
    AssignApplicationsRequest, EvaluationRubricScoreRequest,
    EvaluationScoreResponse, CommitteeConsolidationResponse
)
from app.services.evaluation_service import EvaluationService
from app.services.pdf_report_service import PdfReportService

router = APIRouter()

@router.get(
    "/committees",
    summary="Listar Comités Colegiados",
    dependencies=[Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "EVALUADOR", "SYSADMIN", "ADMIN_BECAS"]))]
)
def list_committees(db: Session = Depends(get_db)):
    committees = db.query(EvaluationCommittee).order_by(EvaluationCommittee.creado_en.desc()).all()
    results = []
    for c in committees:
        members = []
        for m in (c.miembros or []):
            u = m.usuario
            p = u.persona if u else None
            members.append({
                "id": str(m.id),
                "usuario_id": str(m.usuario_id),
                "nombre": p.nombre_completo if p else (u.email if u else "Usuario"),
                "email": u.email if u else "",
                "rol_comite": m.rol_comite,
                "declaracion_conflicto": m.declaracion_conflicto
            })
        results.append({
            "id": str(c.id),
            "codigo": c.codigo,
            "nombre": c.nombre,
            "convocatoria_id": str(c.convocatoria_id),
            "convocatoria_titulo": c.convocatoria.titulo if c.convocatoria else "",
            "estado": c.estado,
            "fecha_creacion": c.creado_en.isoformat() if c.creado_en else None,
            "miembros": members,
            "total_asignados": len(c.asignaciones) if c.asignaciones else 0
        })
    return results

@router.post("/committees", summary="HU-002: Constituir Comité Colegiado")
def create_committee(
    req: CommitteeCreate,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN", "ADMIN_BECAS"])),
    db: Session = Depends(get_db)
):

    c = EvaluationService.create_committee(db, req.codigo, req.nombre, req.convocatoria_id)
    return {"id": c.id, "codigo": c.codigo, "nombre": c.nombre, "estado": c.estado}

@router.post("/committees/{comite_id}/members", summary="HU-002: Incorporar Miembro al Comité")
def add_member(
    comite_id: UUID,
    req: CommitteeMemberAdd,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    m = EvaluationService.add_committee_member(db, comite_id, req.usuario_id, req.rol_comite)
    return {"id": m.id, "comite_id": m.comite_id, "usuario_id": m.usuario_id, "rol_comite": m.rol_comite}

@router.post("/committees/{comite_id}/conflict-declaration", summary="HU-004: Declaración Jurada de No Conflicto de Interés")
def declare_conflict(
    comite_id: UUID,
    req: ConflictDeclarationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    m = EvaluationService.declare_conflict(db, comite_id, current_user.id, req.acepta_terminos)
    return {"message": "Declaración jurada de ausencia de conflicto aceptada y registrada digitalmente.", "fecha": m.fecha_declaracion}

@router.post("/committees/{comite_id}/assign", summary="HU-003: Asignar Expedientes Admitidos a Comité")
def assign_applications(
    comite_id: UUID,
    req: AssignApplicationsRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    total = EvaluationService.assign_applications_to_committee(db, comite_id, req.solicitud_ids)
    return {"message": f"Se asignaron exitosamente {total} expedientes admisibles al comité."}

@router.post("/scores", response_model=EvaluationScoreResponse, summary="HU-005: Registrar Calificación de Rúbrica Digital (0-100 pts)")
def submit_score(
    req: EvaluationRubricScoreRequest,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "EVALUADOR", "DIRECTOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    score = EvaluationService.submit_rubric_score(
        db=db,
        evaluador_id=current_user.id,
        solicitud_id=req.solicitud_id,
        puntaje_academico=req.puntaje_academico,
        puntaje_socioeconomico=req.puntaje_socioeconomico,
        puntaje_ensayo_atestados=req.puntaje_ensayo_atestados,
        dictamen_individual=req.dictamen_individual,
        observaciones=req.observaciones
    )
    return EvaluationScoreResponse(
        id=score.id,
        solicitud_id=score.solicitud_id,
        evaluador_id=score.evaluador_id,
        puntaje_academico=score.puntaje_academico,
        puntaje_socioeconomico=score.puntaje_socioeconomico,
        puntaje_ensayo_atestados=score.puntaje_ensayo_atestados,
        puntaje_total=score.puntaje_total,
        dictamen_individual=score.dictamen_individual,
        observaciones=score.observaciones,
        fecha_evaluacion=score.fecha_evaluacion
    )

@router.post("/committees/{comite_id}/consolidate/{solicitud_id}", response_model=CommitteeConsolidationResponse, summary="HU-006: Consolidación Colegiada y Dictamen")
def consolidate_scores(
    comite_id: UUID,
    solicitud_id: UUID,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "EVALUADOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    res = EvaluationService.consolidate_committee_scores(db, solicitud_id)
    return CommitteeConsolidationResponse(**res)

@router.get("/committees/{comite_id}/applications", summary="Expedientes Asignados para Evaluación")
def list_committee_applications(
    comite_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    asignaciones = db.query(ApplicationAssignment).filter(ApplicationAssignment.comite_id == comite_id).all()
    results = []
    for a in asignaciones:
        s = a.solicitud
        p = s.postulante
        results.append({
            "solicitud_id": s.id,
            "numero_expediente": s.numero_expediente,
            "postulante_nombre": p.nombre_completo if p else "Postulante",
            "promedio_postulacion": s.promedio_postulacion,
            "estado": s.estado,
            "puntaje_ponderado_comite": s.puntaje_ponderado_comite,
            "dictamen_comite": s.dictamen_comite
        })
    return results

@router.post("/committees/auto-assign", summary="HU-002: Asignación Automática de Evaluadores y Expedientes a Comités")
def auto_assign_all_committees(
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN", "ADMIN_BECAS", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    """Asigna automáticamente evaluadores disponibles y expedientes admisibles a todos los comités activos."""
    res = EvaluationService.auto_assign_evaluators_to_committees(db)
    return {
        "success": True,
        "message": f"Se procesaron {res['comites_procesados']} comités: {res['miembros_asignados']} miembros y {res['solicitudes_asignadas']} expedientes vinculados exitosamente.",
        "detalles": res
    }

@router.post("/committees/{comite_id}/auto-assign", summary="Asignación Automática para un Comité Específico")
def auto_assign_single_committee(
    comite_id: UUID,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "SYSADMIN", "ADMIN_BECAS", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    res = EvaluationService.auto_assign_evaluators_to_committees(db, comite_id=comite_id)
    return {
        "success": True,
        "message": f"Comité configurado exitosamente: {res['miembros_asignados']} evaluadores y {res['solicitudes_asignadas']} expedientes enlazados.",
        "detalles": res
    }

@router.get("/committees/{comite_id}/acta-dictamen-pdf", summary="HU-024: Emitir y Descargar Acta Colegiada de Dictamen Técnico en PDF")
def download_acta_dictamen_pdf(
    comite_id: UUID,
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "EVALUADOR", "ADMIN_BECAS", "AUDITOR", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    """
    HU-024: Permite al Coordinador o miembros del Comité cerrar la fase de evaluación,
    generar el cuadro de mérito oficial y emitir el acta de dictamen técnico de recomendación en formato PDF.
    """
    acta_data = EvaluationService.get_committee_acta_data(db, comite_id)
    pdf_bytes = PdfReportService.generate_acta_dictamen_pdf(
        comite=acta_data["comite"],
        convocatoria=acta_data["convocatoria"],
        miembros=acta_data["miembros"],
        ranking_data=acta_data["ranking_data"]
    )
    codigo_comite = acta_data["comite"].codigo.replace(" ", "_")
    filename = f"Acta_Dictamen_{codigo_comite}_2026.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Type": "ActaDictamenTecnico-HU024"
        }
    )
