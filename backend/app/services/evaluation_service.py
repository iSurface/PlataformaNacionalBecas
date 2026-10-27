# -*- coding: utf-8 -*-
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infrastructure.models.application import Application, ApplicationStatusHistory
from app.infrastructure.models.evaluation import EvaluationCommittee, CommitteeMember, ApplicationAssignment, EvaluationScore
from app.infrastructure.models.resolution import ApplicationEvent, InternalNotification, AuditLog

class EvaluationService:
    @staticmethod
    def create_committee(db: Session, codigo: str, nombre: str, convocatoria_id: UUID) -> EvaluationCommittee:
        existing = db.query(EvaluationCommittee).filter(EvaluationCommittee.codigo == codigo).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un comité con ese código")

        committee = EvaluationCommittee(
            codigo=codigo,
            nombre=nombre,
            convocatoria_id=convocatoria_id,
            estado="ACTIVO"
        )
        db.add(committee)
        db.commit()
        db.refresh(committee)
        return committee

    @staticmethod
    def add_committee_member(db: Session, comite_id: UUID, usuario_id: UUID, rol_comite: str) -> CommitteeMember:
        comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).first()
        if not comite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comité no encontrado")

        existing = db.query(CommitteeMember).filter(
            CommitteeMember.comite_id == comite_id,
            CommitteeMember.usuario_id == usuario_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya es miembro de este comité")

        member = CommitteeMember(
            comite_id=comite_id,
            usuario_id=usuario_id,
            rol_comite=rol_comite,
            declaracion_conflicto=False
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def declare_conflict(db: Session, comite_id: UUID, usuario_id: UUID, acepta_terminos: bool) -> CommitteeMember:
        member = db.query(CommitteeMember).filter(
            CommitteeMember.comite_id == comite_id,
            CommitteeMember.usuario_id == usuario_id
        ).first()

        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Miembro del comité no encontrado")

        if not acepta_terminos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe declarar expresamente la ausencia de conflicto de interés")

        member.declaracion_conflicto = True
        member.fecha_declaracion = datetime.now(timezone.utc)

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def assign_applications_to_committee(db: Session, comite_id: UUID, solicitud_ids: List[UUID]) -> int:
        comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).first()
        if not comite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comité no encontrado")

        assigned_count = 0
        for s_id in solicitud_ids:
            solicitud = db.query(Application).filter(Application.id == s_id).first()
            if not solicitud or solicitud.estado != "ADMISIBLE":
                continue

            assignment = db.query(ApplicationAssignment).filter(
                ApplicationAssignment.solicitud_id == s_id,
                ApplicationAssignment.comite_id == comite_id
            ).first()

            if not assignment:
                assignment = ApplicationAssignment(
                    solicitud_id=s_id,
                    comite_id=comite_id,
                    estado="ASIGNADO"
                )
                db.add(assignment)
                solicitud.estado = "ASIGNADA_COMITE"
                
                event = ApplicationEvent(
                    solicitud_id=solicitud.id,
                    tipo_evento="ASIGNACION",
                    titulo="Asignación a Comité Evaluador",
                    descripcion=f"Expediente derivado al comité colegiado: {comite.nombre}",
                    visible_estudiante=True
                )
                db.add(event)
                assigned_count += 1

        db.commit()
        return assigned_count

    @staticmethod
    def submit_rubric_score(
        db: Session,
        evaluador_id: UUID,
        solicitud_id: UUID,
        puntaje_academico: float,
        puntaje_socioeconomico: float,
        puntaje_ensayo_atestados: float,
        dictamen_individual: str,
        observaciones: Optional[str]
    ) -> EvaluationScore:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        assignment = db.query(ApplicationAssignment).filter(
            ApplicationAssignment.solicitud_id == solicitud_id
        ).first()

        if not assignment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El expediente no está asignado a un comité evaluador")

        # Verificar que el usuario sea miembro del comité y haya firmado la no existencia de conflicto
        member = db.query(CommitteeMember).filter(
            CommitteeMember.comite_id == assignment.comite_id,
            CommitteeMember.usuario_id == evaluador_id
        ).first()

        if not member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No es miembro evaluador del comité asignado")

        if not member.declaracion_conflicto:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Debe completar su declaración ética de no conflicto antes de calificar expedientes")

        puntaje_total = round(puntaje_academico + puntaje_socioeconomico + puntaje_ensayo_atestados, 2)

        score = db.query(EvaluationScore).filter(
            EvaluationScore.solicitud_id == solicitud_id,
            EvaluationScore.evaluador_id == evaluador_id
        ).first()

        if score:
            score.puntaje_academico = puntaje_academico
            score.puntaje_socioeconomico = puntaje_socioeconomico
            score.puntaje_ensayo_atestados = puntaje_ensayo_atestados
            score.puntaje_total = puntaje_total
            score.dictamen_individual = dictamen_individual
            score.observaciones = observaciones
            score.fecha_evaluacion = datetime.now(timezone.utc)
        else:
            score = EvaluationScore(
                solicitud_id=solicitud_id,
                evaluador_id=evaluador_id,
                comite_id=assignment.comite_id,
                puntaje_academico=puntaje_academico,
                puntaje_socioeconomico=puntaje_socioeconomico,
                puntaje_ensayo_atestados=puntaje_ensayo_atestados,
                puntaje_total=puntaje_total,
                dictamen_individual=dictamen_individual,
                observaciones=observaciones
            )
            db.add(score)

        solicitud.estado = "EN_EVALUACION"
        db.commit()
        db.refresh(score)
        return score

    @staticmethod
    def consolidate_committee_scores(db: Session, solicitud_id: UUID) -> Dict[str, Any]:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        scores = db.query(EvaluationScore).filter(EvaluationScore.solicitud_id == solicitud_id).all()
        if not scores:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay calificaciones registradas para esta solicitud")

        promedio = sum(s.puntaje_total for s in scores) / len(scores)
        promedio = round(promedio, 2)

        dictamen_final = "RECOMENDADO" if promedio >= 70.0 else "NO_RECOMENDADO"
        solicitud.puntaje_ponderado_comite = promedio
        solicitud.dictamen_comite = dictamen_final
        solicitud.estado = "DICTAMINADA"

        # Trazabilidad
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="EVALUACION",
            titulo="Dictamen del Comité Colegiado",
            descripcion=f"Calificación colegiada consolidada: {promedio} pts ({dictamen_final}).",
            visible_estudiante=True
        )
        db.add(event)

        db.commit()
        return {
            "solicitud_id": solicitud.id,
            "numero_expediente": solicitud.numero_expediente,
            "total_evaluaciones": len(scores),
            "puntaje_promedio": promedio,
            "dictamen_recomendado": dictamen_final
        }
