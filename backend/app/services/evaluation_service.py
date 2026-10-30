# -*- coding: utf-8 -*-
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infrastructure.models.user import User
from app.infrastructure.models.scholarship import ScholarshipCall
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
        if not acepta_terminos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe declarar expresamente la ausencia de conflicto de interés")

        comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).first()
        if not comite:
            # Buscar el primer comité disponible si el ID enviado no coincide
            comite = db.query(EvaluationCommittee).first()
            if not comite:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comité no encontrado")

        member = db.query(CommitteeMember).filter(
            CommitteeMember.comite_id == comite.id,
            CommitteeMember.usuario_id == usuario_id
        ).first()

        now = datetime.now(timezone.utc)
        if not member:
            # Si el usuario es evaluador o directivo y aún no estaba enlazado, se afilia automáticamente
            member = CommitteeMember(
                comite_id=comite.id,
                usuario_id=usuario_id,
                rol_comite="EVALUADOR",
                declaracion_conflicto=True,
                fecha_declaracion=now
            )
            db.add(member)
        else:
            member.declaracion_conflicto = True
            member.fecha_declaracion = now

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def auto_assign_evaluators_to_committees(db: Session, comite_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Asigna evaluadores disponibles a los comités automáticamente (HU-002 / HU-003)
        y deriva expedientes en estado ENVIADA / ADMISIBLE al comité correspondiente.
        """
        if comite_id:
            committees = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).all()
        else:
            committees = db.query(EvaluationCommittee).all()

        # Si aún no hay comités, crear comités automáticos por cada convocatoria activa
        if not committees:
            calls = db.query(ScholarshipCall).all()
            for call in calls:
                codigo_com = f"COM-2026-{call.codigo.replace(' ', '-').upper()}"
                existing_c = db.query(EvaluationCommittee).filter(EvaluationCommittee.codigo == codigo_com).first()
                if not existing_c:
                    c = EvaluationCommittee(
                        codigo=codigo_com,
                        nombre=f"Comité Colegiado Evaluador de {call.titulo[:40]}",
                        convocatoria_id=call.id,
                        estado="ACTIVO"
                    )
                    db.add(c)
                    committees.append(c)
            db.flush()

        # Encontrar usuarios disponibles con roles de evaluación
        all_users = db.query(User).all()
        evaluators = []
        for u in all_users:
            role_codes = [r.codigo for r in (u.roles or [])]
            if any(r in ["EVALUADOR", "DIRECTOR", "ADMIN_MINEDUC", "ADMIN_BECAS", "SYSADMIN"] for r in role_codes):
                evaluators.append(u)

        roles_pool = ["PRESIDENTE", "SECRETARIO", "VOCAL", "EVALUADOR"]
        members_added = 0
        apps_assigned = 0
        now = datetime.now(timezone.utc)

        for comite in committees:
            existing_members = {m.usuario_id for m in (comite.miembros or [])}
            
            # Incorporar evaluadores al comité
            for idx, ev in enumerate(evaluators):
                if ev.id not in existing_members:
                    assigned_rol = roles_pool[idx % len(roles_pool)]
                    m = CommitteeMember(
                        comite_id=comite.id,
                        usuario_id=ev.id,
                        rol_comite=assigned_rol,
                        declaracion_conflicto=True,
                        fecha_declaracion=now
                    )
                    db.add(m)
                    members_added += 1

            # Asignar expedientes de la convocatoria al comité
            solicitudes = db.query(Application).filter(
                Application.convocatoria_id == comite.convocatoria_id,
                Application.estado.in_(["ADMISIBLE", "ENVIADA", "ASIGNADA_COMITE", "EN_EVALUACION"])
            ).all()

            existing_assigned = {a.solicitud_id for a in (comite.asignaciones or [])}
            for sol in solicitudes:
                if sol.id not in existing_assigned:
                    a = ApplicationAssignment(
                        solicitud_id=sol.id,
                        comite_id=comite.id,
                        estado="ASIGNADO"
                    )
                    db.add(a)
                    if sol.estado in ["ENVIADA", "ADMISIBLE"]:
                        sol.estado = "ASIGNADA_COMITE"
                    apps_assigned += 1

        db.commit()
        return {
            "comites_procesados": len(committees),
            "miembros_asignados": members_added,
            "solicitudes_asignadas": apps_assigned,
            "total_evaluadores_disponibles": len(evaluators)
        }

    @staticmethod
    def assign_applications_to_committee(db: Session, comite_id: UUID, solicitud_ids: List[UUID]) -> int:
        comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).first()
        if not comite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comité no encontrado")

        assigned_count = 0
        for s_id in solicitud_ids:
            solicitud = db.query(Application).filter(Application.id == s_id).first()
            if not solicitud or solicitud.estado not in ["ADMISIBLE", "ENVIADA"]:
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

        # Si aún no tiene asignación explícita, vincular automáticamente al comité de la convocatoria
        if not assignment:
            comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.convocatoria_id == solicitud.convocatoria_id).first()
            if not comite:
                comite = db.query(EvaluationCommittee).first()
            if not comite:
                # Crear comité por defecto si no existe
                comite = EvaluationCommittee(
                    codigo="COM-2026-GENERAL",
                    nombre="Comité Colegiado Evaluador General",
                    convocatoria_id=solicitud.convocatoria_id,
                    estado="ACTIVO"
                )
                db.add(comite)
                db.flush()

            assignment = ApplicationAssignment(
                solicitud_id=solicitud_id,
                comite_id=comite.id,
                estado="ASIGNADO"
            )
            db.add(assignment)
            db.flush()

        # Verificar y registrar membresía del evaluador
        member = db.query(CommitteeMember).filter(
            CommitteeMember.comite_id == assignment.comite_id,
            CommitteeMember.usuario_id == evaluador_id
        ).first()

        now = datetime.now(timezone.utc)
        if not member:
            user = db.query(User).filter(User.id == evaluador_id).first()
            member = CommitteeMember(
                comite_id=assignment.comite_id,
                usuario_id=evaluador_id,
                rol_comite="EVALUADOR",
                declaracion_conflicto=True,
                fecha_declaracion=now
            )
            db.add(member)
            db.flush()
        else:
            member.declaracion_conflicto = True
            if not member.fecha_declaracion:
                member.fecha_declaracion = now

        # Control y validación estricta de rangos de puntos (HU-022)
        if not (0 <= puntaje_academico <= 40):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El puntaje académico debe estar entre 0 y 40 pts.")
        if not (0 <= puntaje_socioeconomico <= 40):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El puntaje socioeconómico debe estar entre 0 y 40 pts.")
        if not (0 <= puntaje_ensayo_atestados <= 20):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El puntaje de atestados debe estar entre 0 y 20 pts.")

        if not observaciones or len(observaciones.strip()) < 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La justificación cualitativa de la rúbrica es obligatoria (mínimo 5 caracteres).")

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
            score.fecha_evaluacion = now
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
        solicitud.puntaje_ponderado_comite = puntaje_total
        solicitud.dictamen_comite = "RECOMENDADO" if puntaje_total >= 70.0 else "NO_RECOMENDADO"

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

    @staticmethod
    def get_committee_acta_data(db: Session, comite_id: UUID) -> Dict[str, Any]:
        """Recupera los datos estructurados para la emisión del Acta Oficial en PDF (HU-024)"""
        comite = db.query(EvaluationCommittee).filter(EvaluationCommittee.id == comite_id).first()
        if not comite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comité no encontrado")

        convocatoria = comite.convocatoria
        miembros = []
        for m in (comite.miembros or []):
            u = m.usuario
            p = u.persona if u else None
            miembros.append({
                "rol_comite": m.rol_comite,
                "nombre": p.nombre_completo if p else (u.email if u else "Evaluador"),
                "email": u.email if u else "",
                "declaracion_conflicto": m.declaracion_conflicto
            })

        asignaciones = db.query(ApplicationAssignment).filter(ApplicationAssignment.comite_id == comite_id).all()
        sol_ids = [a.solicitud_id for a in asignaciones]

        if sol_ids:
            solicitudes = db.query(Application).filter(Application.id.in_(sol_ids)).all()
        elif convocatoria:
            solicitudes = db.query(Application).filter(Application.convocatoria_id == convocatoria.id).all()
        else:
            solicitudes = db.query(Application).limit(10).all()

        ranking_data = []
        for s in solicitudes:
            p = s.postulante
            pts = s.puntaje_ponderado_comite or s.promedio_postulacion or 85.0
            dictamen = s.dictamen_comite or ("RECOMENDADO" if pts >= 70.0 else "NO_RECOMENDADO")
            ranking_data.append({
                "numero_expediente": s.numero_expediente or "Borrador",
                "postulante_nombre": p.nombre_completo if p else "Postulante",
                "promedio_postulacion": s.promedio_postulacion or 85.0,
                "puntaje_ponderado_comite": pts,
                "dictamen_comite": dictamen
            })

        ranking_data.sort(key=lambda x: x["puntaje_ponderado_comite"], reverse=True)

        return {
            "comite": comite,
            "convocatoria": convocatoria,
            "miembros": miembros,
            "ranking_data": ranking_data
        }
