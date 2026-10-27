# -*- coding: utf-8 -*-
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.models.application import Application
from app.infrastructure.models.evaluation import EvaluationCommittee
from app.infrastructure.models.resolution import CommitteeAct, AwardResolution, ApplicationEvent, InternalNotification, AuditLog
from app.infrastructure.models.scholarship import ScholarshipCall

class ResolutionService:
    @staticmethod
    def create_committee_act(
        db: Session,
        comite_id: UUID,
        numero_acta: str,
        resumen_deliberacion: str,
        total_evaluados: int,
        total_recomendados: int,
        firmado_por_id: UUID
    ) -> CommitteeAct:
        existing = db.query(CommitteeAct).filter(CommitteeAct.numero_acta == numero_acta).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de acta ya existe")

        act = CommitteeAct(
            comite_id=comite_id,
            numero_acta=numero_acta,
            resumen_deliberacion=resumen_deliberacion,
            total_evaluados=total_evaluados,
            total_recomendados=total_recomendados,
            firmado_por_id=firmado_por_id
        )
        db.add(act)

        audit = AuditLog(
            usuario_id=firmado_por_id,
            modulo="EVALUACIONES",
            accion="EMITIR_ACTA_DICTAMEN",
            entidad="CommitteeAct",
            entidad_id=str(act.id),
            datos_nuevos={"numero_acta": numero_acta}
        )
        db.add(audit)

        db.commit()
        db.refresh(act)
        return act

    @staticmethod
    def issue_award_resolution(
        db: Session,
        convocatoria_id: UUID,
        numero_resolucion: str,
        titulo: str,
        considerando: str,
        por_tanto: str,
        total_becarios: int,
        monto_total: float,
        emitida_por_id: UUID
    ) -> AwardResolution:
        existing = db.query(AwardResolution).filter(AwardResolution.numero_resolucion == numero_resolucion).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de resolución ministerial ya existe")

        resolution = AwardResolution(
            convocatoria_id=convocatoria_id,
            numero_resolucion=numero_resolucion,
            titulo=titulo,
            considerando=considerando,
            por_tanto=por_tanto,
            total_becarios_adjudicados=total_becarios,
            monto_total_comprometido=monto_total,
            emitida_por_id=emitida_por_id,
            estado="PUBLICADA"
        )
        db.add(resolution)

        # Actualizar expedientes dictaminados de la convocatoria
        solicitudes = db.query(Application).filter(
            Application.convocatoria_id == convocatoria_id,
            Application.estado == "DICTAMINADA"
        ).all()

        for s in solicitudes:
            if s.dictamen_comite == "RECOMENDADO":
                s.estado = "ADJUDICADA"
                event = ApplicationEvent(
                    solicitud_id=s.id,
                    tipo_evento="ADJUDICACION",
                    titulo="Beca Oficialmente Adjudicada",
                    descripcion=f"Adjudicada bajo Resolución Ministerial {numero_resolucion}.",
                    actor_id=emitida_por_id,
                    visible_estudiante=True
                )
                db.add(event)

                notif = InternalNotification(
                    usuario_id=s.postulante_id,
                    titulo="¡Felicidades! Beca Adjudicada",
                    mensaje=f"Tu expediente {s.numero_expediente} ha sido adjudicado favorablemente mediante la resolución {numero_resolucion}.",
                    tipo="SUCCESS"
                )
                db.add(notif)
            else:
                s.estado = "RECHAZADA"
                event = ApplicationEvent(
                    solicitud_id=s.id,
                    tipo_evento="RECHAZO",
                    titulo="Proceso Concluido",
                    descripcion=f"No adjudicado en la resolución {numero_resolucion}.",
                    actor_id=emitida_por_id,
                    visible_estudiante=True
                )
                db.add(event)

        db.commit()
        db.refresh(resolution)
        return resolution

    @staticmethod
    def get_events_for_application(db: Session, solicitud_id: UUID, user_id: UUID, is_admin: bool = False) -> List[ApplicationEvent]:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if not is_admin and str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

        query = db.query(ApplicationEvent).filter(ApplicationEvent.solicitud_id == solicitud_id)
        if not is_admin:
            query = query.filter(ApplicationEvent.visible_estudiante == True)
        
        return query.order_by(ApplicationEvent.creado_en.asc()).all()

    @staticmethod
    def get_user_notifications(db: Session, user_id: UUID) -> List[InternalNotification]:
        return db.query(InternalNotification).filter(
            InternalNotification.usuario_id == user_id
        ).order_by(InternalNotification.creado_en.desc()).all()

    @staticmethod
    def mark_notification_read(db: Session, notif_id: UUID, user_id: UUID) -> InternalNotification:
        notif = db.query(InternalNotification).filter(
            InternalNotification.id == notif_id,
            InternalNotification.usuario_id == user_id
        ).first()
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        notif.leida = True
        db.commit()
        return notif
