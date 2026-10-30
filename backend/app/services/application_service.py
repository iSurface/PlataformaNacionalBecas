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
from app.infrastructure.models.user import User
from app.services.audit_service import AuditService

class ApplicationService:
    @staticmethod
    def transition_state(
        db: Session,
        solicitud: Application,
        nuevo_estado: str,
        actor: User,
        comentario: str,
        tipo_evento: str,
        titulo_evento: str,
        descripcion_evento: str,
        notif_tipo: str = "INFO",
        operacion_audit: Optional[str] = None,
        resultado_audit: str = "EXITOSO",
        detalles_audit: Optional[str] = None,
        ip_address: Optional[str] = None,
        notificar_estudiante: bool = True
    ) -> Application:
        """
        Helper centralizado para transicionar el estado de un expediente garantizando:
        - Registro de historial de estado (ApplicationStatusHistory)
        - Evento visible en tiempo real para el estudiante (ApplicationEvent - HU-002)
        - Notificación interna al buzón del estudiante (InternalNotification - HU-002)
        - Registro forense inmutable de auditoría en 4 dimensiones (AuditLog - HU-003)
        """
        estado_anterior = solicitud.estado
        solicitud.estado = nuevo_estado
        solicitud.fecha_actualizacion = datetime.now(timezone.utc)

        # 1. Historial de estados
        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            cambiado_por_id=actor.id,
            comentario=comentario
        )
        db.add(history)

        # 2. Evento de trazabilidad del estudiante (HU-002)
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento=tipo_evento,
            titulo=titulo_evento,
            descripcion=descripcion_evento,
            actor_id=actor.id,
            visible_estudiante=True
        )
        db.add(event)

        # 3. Notificación interna obligatoria al estudiante (HU-002)
        if notificar_estudiante and solicitud.postulante_id:
            notif = InternalNotification(
                usuario_id=solicitud.postulante_id,
                titulo=titulo_evento,
                mensaje=f"Expediente {solicitud.numero_expediente or 'En trámite'}: {descripcion_evento}",
                tipo=notif_tipo
            )
            db.add(notif)

        # 4. Asiento en Bitácora Forense (HU-003)
        user_rol = actor.rol if hasattr(actor, 'rol') else (actor.roles[0].codigo if actor.roles else "USUARIO")
        audit = AuditLog(
            usuario_id=actor.id,
            usuario_nombre=actor.nombre_completo,
            usuario_rol=user_rol,
            modulo="POSTULACIONES",
            accion="CAMBIO_ESTADO",
            operacion=operacion_audit or f"CAMBIO_ESTADO_{nuevo_estado}",
            resultado=resultado_audit,
            detalles=detalles_audit or comentario,
            entidad="Application",
            entidad_id=str(solicitud.id),
            ip_address=ip_address,
            datos_anteriores={"estado": estado_anterior},
            datos_nuevos={"estado": nuevo_estado}
        )
        db.add(audit)

        db.commit()
        db.refresh(solicitud)
        return solicitud

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

        if convocatoria.promedio_minimo_requerido and promedio < convocatoria.promedio_minimo_requerido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El promedio académico ({promedio:.1f}) no alcanza el mínimo requerido para esta beca ({convocatoria.promedio_minimo_requerido:.1f})"
            )

        monto = convocatoria.monto_individual or 0.0
        requiere_2da = (monto > 10000.0)

        solicitud = Application(
            postulante_id=user_id,
            convocatoria_id=convocatoria_id,
            estado="BORRADOR",
            promedio_postulacion=promedio,
            monto_solicitado=monto,
            requiere_segunda_aprobacion=requiere_2da,
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
            descripcion=f"Se ha iniciado el expediente digital de postulación. Monto referencial: Q {monto:,.2f}.",
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
        norm_estado = "NO_ADMISIBLE" if estado_nuevo == "RECHAZADA" else estado_nuevo
        if norm_estado not in ["ADMISIBLE", "OBSERVADA", "NO_ADMISIBLE"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de admisibilidad no válido (Use ADMISIBLE, OBSERVADA o NO_ADMISIBLE / RECHAZADA)")

        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

        if norm_estado == "NO_ADMISIBLE" and (not observaciones or len(observaciones.strip()) < 3):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rechazo de plano requiere justificar obligatoriamente el motivo.")

        estado_anterior = solicitud.estado
        solicitud.estado = norm_estado
        solicitud.observaciones_verificacion = observaciones
        solicitud.verificado_por_id = reviewer_id

        history = ApplicationStatusHistory(
            solicitud_id=solicitud.id,
            estado_anterior=estado_anterior,
            estado_nuevo=norm_estado,
            cambiado_por_id=reviewer_id,
            comentario=observaciones or f"Dictamen de admisibilidad administrativa: {norm_estado}"
        )
        db.add(history)

        # Evento trazabilidad
        event = ApplicationEvent(
            solicitud_id=solicitud.id,
            tipo_evento="VERIFICACION",
            titulo=f"Filtro Administrativo: {norm_estado}",
            descripcion=observaciones or f"El expediente fue calificado como {norm_estado}.",
            actor_id=reviewer_id,
            visible_estudiante=True
        )
        db.add(event)

        # Notificación al estudiante
        notif_tipo = "SUCCESS" if norm_estado == "ADMISIBLE" else ("WARNING" if norm_estado == "OBSERVADA" else "INFO")
        notif = InternalNotification(
            usuario_id=solicitud.postulante_id,
            titulo=f"Expediente {norm_estado}",
            mensaje=f"Tu expediente {solicitud.numero_expediente} fue calificado como {norm_estado}. {observaciones or ''}",
            tipo=notif_tipo
        )
        db.add(notif)

        # Auditoría Forense (HU-016 y HU-008)
        db.add(AuditLog(
            usuario_id=reviewer_id,
            modulo="ADMISIBILIDAD",
            accion="DICTAMEN_ADMISIBILIDAD",
            operacion="RECHAZAR_PLANO" if norm_estado == "NO_ADMISIBLE" else ("APROBAR_ADMISIBILIDAD" if norm_estado == "ADMISIBLE" else "OBSERVAR_SUBSANACION"),
            resultado="EXITOSO",
            detalles=f"Expediente {solicitud.numero_expediente or solicitud.id} transicionado de {estado_anterior} a {norm_estado}. Justificación: {observaciones or 'N/A'}",
            entidad="Application",
            entidad_id=str(solicitud.id),
            datos_nuevos={"estado_anterior": estado_anterior, "estado_nuevo": norm_estado, "observaciones": observaciones}
        ))

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

    @staticmethod
    def approve_first_phase(
        db: Session,
        solicitud_id: UUID,
        approver: User,
        monto_aprobado: Optional[float] = None,
        observaciones: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Application:
        """
        HU-001: Primera fase de aprobación (Evaluador / Coordinador).
        Si el monto de la beca supera Q 10,000.00, pasa a PENDIENTE_SEGUNDA_APROBACION.
        Si es menor o igual a Q 10,000.00, se adjudica directamente.
        """
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expediente no encontrado")

        if solicitud.estado not in ["DICTAMINADA", "ADMISIBLE", "EN_EVALUACION", "ENVIADA"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede emitir primera aprobación sobre un expediente en estado '{solicitud.estado}'"
            )

        if monto_aprobado is not None and monto_aprobado > 0:
            solicitud.monto_solicitado = monto_aprobado
        elif not solicitud.monto_solicitado and solicitud.convocatoria:
            solicitud.monto_solicitado = solicitud.convocatoria.monto_individual or 0.0

        monto = solicitud.monto_solicitado or 0.0
        solicitud.primera_aprobacion_por_id = approver.id
        solicitud.fecha_primera_aprobacion = datetime.now(timezone.utc)
        solicitud.observaciones_primera_aprobacion = observaciones

        if monto > 10000.0:
            solicitud.requiere_segunda_aprobacion = True
            nuevo_estado = "PENDIENTE_SEGUNDA_APROBACION"
            titulo_evento = "Primera Aprobación Emitida (> Q 10,000)"
            desc_evento = f"Expediente evaluado favorablemente por {approver.nombre_completo}. Por superar el monto de Q 10,000.00 (Monto: Q {monto:,.2f}), requiere segunda aprobación de Dirección Ministerial (HU-001)."
            notif_tipo = "ACTION_REQUIRED"
            operacion = "APROBACION_PRIMERA_FASE_MAYOR_10K"
        else:
            solicitud.requiere_segunda_aprobacion = False
            nuevo_estado = "ADJUDICADA"
            titulo_evento = "Beca Aprobada y Adjudicada"
            desc_evento = f"Expediente aprobado y adjudicado satisfactoriamente por {approver.nombre_completo} (Monto: Q {monto:,.2f})."
            notif_tipo = "SUCCESS"
            operacion = "APROBACION_DIRECTA_MENOR_10K"

        return ApplicationService.transition_state(
            db=db,
            solicitud=solicitud,
            nuevo_estado=nuevo_estado,
            actor=approver,
            comentario=observaciones or desc_evento,
            tipo_evento="APROBACION_FASE_1",
            titulo_evento=titulo_evento,
            descripcion_evento=desc_evento,
            notif_tipo=notif_tipo,
            operacion_audit=operacion,
            resultado_audit="EXITOSO",
            detalles_audit=f"Primera aprobación completada. Monto: Q {monto:,.2f}. Requiere 2da firma: {solicitud.requiere_segunda_aprobacion}",
            ip_address=ip_address
        )

    @staticmethod
    def approve_second_phase(
        db: Session,
        solicitud_id: UUID,
        approver: User,
        observaciones: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Application:
        """
        HU-001: Segunda fase de aprobación obligatoria para montos > Q 10,000.00.
        Aplica estrictamente RB-014 (Segregación de Funciones): no puede aprobar la misma persona.
        """
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expediente no encontrado")

        if solicitud.estado != "PENDIENTE_SEGUNDA_APROBACION":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El expediente está en estado '{solicitud.estado}', no requiere ni permite segunda aprobación."
            )

        user_rol = approver.rol if hasattr(approver, 'rol') else (approver.roles[0].codigo if approver.roles else "USUARIO")

        # REGLA DE NEGOCIO ESTRICTA (RB-014): SEGREGACIÓN DE FUNCIONES
        if solicitud.primera_aprobacion_por_id and str(solicitud.primera_aprobacion_por_id) == str(approver.id):
            # Registrar intento de colusión en bitácora forense de auditoría con resultado DENEGADO (HU-003)
            AuditService.log(
                db=db,
                modulo="POSTULACIONES",
                accion="SEGUNDA_APROBACION",
                operacion="SEGUNDA_APROBACION_MONTO_MAYOR_10K",
                resultado="DENEGADO",
                detalles=f"Violación de Segregación de Funciones (RB-014): El usuario {approver.nombre_completo} ({approver.email}) intentó realizar ambas aprobaciones para la solicitud {solicitud.numero_expediente}.",
                entidad="Application",
                entidad_id=str(solicitud.id),
                usuario_id=approver.id,
                usuario_nombre=approver.nombre_completo,
                usuario_rol=user_rol,
                ip_address=ip_address,
                datos_anteriores={"estado": solicitud.estado, "primera_aprobacion_por_id": str(solicitud.primera_aprobacion_por_id)}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Violación de regla de negocio (RB-014): La segunda aprobación debe ser realizada por un funcionario distinto al que emitió la primera aprobación."
            )

        solicitud.segunda_aprobacion_por_id = approver.id
        solicitud.fecha_segunda_aprobacion = datetime.now(timezone.utc)
        solicitud.observaciones_segunda_aprobacion = observaciones

        monto = solicitud.monto_solicitado or 0.0
        primer_aprobador_nombre = solicitud.primera_aprobacion_por.nombre_completo if solicitud.primera_aprobacion_por else "Comité Evaluador"
        desc_evento = f"Segunda aprobación ministerial ratificada por {approver.nombre_completo} ({user_rol}). Primera firma por {primer_aprobador_nombre}. Beca por Q {monto:,.2f} formalmente adjudicada."

        return ApplicationService.transition_state(
            db=db,
            solicitud=solicitud,
            nuevo_estado="ADJUDICADA",
            actor=approver,
            comentario=observaciones or desc_evento,
            tipo_evento="SEGUNDA_APROBACION",
            titulo_evento="Segunda Aprobación Ministerial Ratificada",
            descripcion_evento=desc_evento,
            notif_tipo="SUCCESS",
            operacion_audit="SEGUNDA_APROBACION_MONTO_MAYOR_10K",
            resultado_audit="EXITOSO",
            detalles_audit=f"Segregación verificada. 1ra firma: {primer_aprobador_nombre}, 2da firma: {approver.nombre_completo}. Monto: Q {monto:,.2f}",
            ip_address=ip_address
        )

    @staticmethod
    def reject_application(
        db: Session,
        solicitud_id: UUID,
        reviewer: User,
        motivo: str,
        ip_address: Optional[str] = None
    ) -> Application:
        """
        HU-003: Rechazo formal de solicitud con registro forense y notificación inmediata.
        """
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expediente no encontrado")

        return ApplicationService.transition_state(
            db=db,
            solicitud=solicitud,
            nuevo_estado="RECHAZADA",
            actor=reviewer,
            comentario=f"Rechazo de solicitud: {motivo}",
            tipo_evento="RECHAZO",
            titulo_evento="Solicitud No Aprobada",
            descripcion_evento=f"La solicitud fue rechazada por la autoridad evaluadora. Motivo: {motivo}",
            notif_tipo="WARNING",
            operacion_audit="RECHAZO_SOLICITUD",
            resultado_audit="EXITOSO",
            detalles_audit=f"Rechazo formal emitido por {reviewer.nombre_completo}. Motivo: {motivo}",
            ip_address=ip_address
        )
