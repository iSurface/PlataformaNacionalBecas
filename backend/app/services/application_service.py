# -*- coding: utf-8 -*-
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infrastructure.models.application import Application, ApplicationDocument, ApplicationStatusHistory
from app.infrastructure.models.scholarship import ScholarshipCall, CallRequirement
from app.infrastructure.models.student_profile import StudentProfile
from app.infrastructure.models.resolution import ApplicationEvent, InternalNotification, AuditLog

class ApplicationService:
    @staticmethod
    def create_or_get_draft(db: Session, user_id: UUID, convocatoria_id: UUID) -> Application:
        convocatoria = db.query(ScholarshipCall).filter(ScholarshipCall.id == convocatoria_id).first()
        if not convocatoria:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada")

        if convocatoria.estado != "PUBLICADA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La convocatoria no se encuentra abierta para postulaciones")

        # Regla de postulación única activa por convocatoria
        existing_active = db.query(Application).filter(
            Application.postulante_id == user_id,
            Application.convocatoria_id == convocatoria_id,
            Application.estado.notin_(["DESISTIDA", "RECHAZADA"])
        ).first()

        if existing_active:
            return existing_active

        # Validar perfil estudiantil y promedio mínimo
        profile = db.query(StudentProfile).filter(StudentProfile.usuario_id == user_id).first()
        promedio = profile.promedio_general if profile and profile.promedio_general else 85.0

        if convocatoria.promedio_minimo and promedio < convocatoria.promedio_minimo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El promedio académico ({promedio:.1f}) no alcanza el mínimo requerido para esta beca ({convocatoria.promedio_minimo:.1f})"
            )

        solicitud = Application(
            postulante_id=user_id,
            convocatoria_id=convocatoria_id,
            estado="BORRADOR",
            promedio_postulacion=promedio,
            datos_formulario={}
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)

        # Evento trazabilidad
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="CREACION",
            titulo="Borrador Creado",
            descripcion="Se ha iniciado el expediente digital de postulación.",
            actor_id=user_id,
            visible_estudiante=True
        )
        db.add(event)
        db.commit()

        return solicitud

    @staticmethod
    def update_draft(db: Session, solicitud_id: UUID, user_id: UUID, datos: Optional[Dict[str, Any]]) -> Application:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

        if solicitud.estado not in ["BORRADOR", "OBSERVADA"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se pueden actualizar solicitudes en borrador u observadas")

        if datos is not None:
            solicitud.datos_formulario = datos
        solicitud.fecha_actualizacion = datetime.now(timezone.utc)

        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def submit_application(db: Session, solicitud_id: UUID, user_id: UUID) -> Application:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

        if solicitud.estado != "BORRADOR":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La solicitud ya ha sido enviada previamente")

        # Validar que todos los requisitos obligatorios tengan documento subido
        requisitos_obligatorios = db.query(CallRequirement).filter(
            CallRequirement.convocatoria_id == solicitud.convocatoria_id,
            CallRequirement.es_obligatorio == True
        ).all()

        docs_cargados = {doc.requisito_id for doc in solicitud.documentos}
        faltantes = [req.nombre for req in requisitos_obligatorios if req.id not in docs_cargados]

        if faltantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Faltan atestados obligatorios por cargar: {', '.join(faltantes)}"
            )

        # Generar número correlativo inmutable oficial
        convocatoria = solicitud.convocatoria
        codigo_conv = convocatoria.codigo.replace(" ", "-").upper()
        total_enviadas = db.query(func.count(Application.id)).filter(
            Application.convocatoria_id == solicitud.convocatoria_id,
            Application.numero_expediente.isnot(None)
        ).scalar() or 0

        correlativo = total_enviadas + 1
        numero_exp = f"EXP-2026-{codigo_conv}-{correlativo:05d}"

        estado_anterior = solicitud.estado
        solicitud.numero_expediente = numero_exp
        solicitud.estado = "ENVIADA"
        solicitud.fecha_envio = datetime.now(timezone.utc)

        # Historial de cambios
        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo="ENVIADA",
            cambiado_por_id=user_id,
            comentario="Postulación formalizada exitosamente por el ciudadano"
        )
        db.add(history)

        # Trazabilidad
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="ENVIO",
            titulo="Expediente Formalizado",
            descripcion=f"Expediente asignado con correlativo oficial inmutable: {numero_exp}",
            actor_id=user_id,
            visible_estudiante=True
        )
        db.add(event)

        # Notificación interna
        notif = InternalNotification(
            usuario_id=user_id,
            titulo="Postulación Recibida",
            mensaje=f"Tu postulación a la beca '{convocatoria.titulo}' fue registrada formalmente bajo el expediente {numero_exp}.",
            tipo="SUCCESS"
        )
        db.add(notif)

        # Auditoría inmutable
        audit = AuditLog(
            usuario_id=user_id,
            modulo="POSTULACIONES",
            accion="FORMALIZAR_SOLICITUD",
            entidad="Application",
            entidad_id=str(solicitud.id),
            datos_nuevos={"numero_expediente": numero_exp, "estado": "ENVIADA"}
        )
        db.add(audit)

        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def withdraw_application(db: Session, solicitud_id: UUID, user_id: UUID, motivo: str) -> Application:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

        if solicitud.estado in ["DICTAMINADA", "ADJUDICADA", "DESISTIDA"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No es posible desistir un expediente en estado {solicitud.estado}")

        estado_anterior = solicitud.estado
        solicitud.estado = "DESISTIDA"
        solicitud.motivo_desistimiento = motivo

        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo="DESISTIDA",
            cambiado_por_id=user_id,
            comentario=f"Desistimiento voluntario: {motivo}"
        )
        db.add(history)

        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="DESISTIMIENTO",
            titulo="Desistimiento Registrado",
            descripcion=f"El postulante ha desistido formalmente del proceso. Motivo: {motivo}",
            actor_id=user_id,
            visible_estudiante=True
        )
        db.add(event)

        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def verify_admissibility(db: Session, solicitud_id: UUID, reviewer_id: UUID, estado_nuevo: str, observaciones: Optional[str]) -> Application:
        if estado_nuevo not in ["ADMISIBLE", "OBSERVADA", "NO_ADMISIBLE"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de admisibilidad no válido")

        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if solicitud.estado not in ["ENVIADA", "SUBSANADA", "EN_VERIFICACION"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se puede verificar una solicitud en estado {solicitud.estado}")

        estado_anterior = solicitud.estado
        solicitud.estado = estado_nuevo
        solicitud.observaciones_verificacion = observaciones
        solicitud.verificado_por_id = reviewer_id

        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            cambiado_por_id=reviewer_id,
            comentario=observaciones or f"Dictamen de admisibilidad administrativa: {estado_nuevo}"
        )
        db.add(history)

        # Evento trazabilidad
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="VERIFICACION",
            titulo=f"Filtro Administrativo: {estado_nuevo}",
            descripcion=observaciones or f"El expediente fue calificado como {estado_nuevo}.",
            actor_id=reviewer_id,
            visible_estudiante=True
        )
        db.add(event)

        # Notificación al estudiante
        notif_tipo = "SUCCESS" if estado_nuevo == "ADMISIBLE" else ("WARNING" if estado_nuevo == "OBSERVADA" else "INFO")
        notif = InternalNotification(
            usuario_id=solicitud.postulante_id,
            titulo=f"Expediente {estado_nuevo}",
            mensaje=f"Tu expediente {solicitud.numero_expediente} fue calificado como {estado_nuevo}. {observaciones or ''}",
            tipo=notif_tipo
        )
        db.add(notif)

        db.commit()
        db.refresh(solicitud)
        return solicitud

    @staticmethod
    def cure_observations(db: Session, solicitud_id: UUID, user_id: UUID) -> Application:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

        if solicitud.estado != "OBSERVADA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se pueden subsanar solicitudes observadas")

        estado_anterior = solicitud.estado
        solicitud.estado = "SUBSANADA"

        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo="SUBSANADA",
            cambiado_por_id=user_id,
            comentario="Atestados corregidos y subsanados en plazo por el postulante"
        )
        db.add(history)

        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="SUBSANACION",
            titulo="Subsanación Presentada",
            descripcion="El postulante actualizó la documentación observada para nueva revisión.",
            actor_id=user_id,
            visible_estudiante=True
        )
        db.add(event)

        db.commit()
        db.refresh(solicitud)
        return solicitud
