# -*- coding: utf-8 -*-
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.infrastructure.models.resolution import AuditLog

class AuditService:
    @staticmethod
    def log(
        db: Session,
        modulo: str,
        accion: str,
        entidad: str,
        entidad_id: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
        usuario_nombre: Optional[str] = None,
        usuario_rol: Optional[str] = None,
        operacion: Optional[str] = None,
        resultado: str = "EXITOSO",
        detalles: Optional[str] = None,
        ip_address: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            modulo=modulo,
            accion=accion,
            operacion=operacion or accion,
            resultado=resultado,
            detalles=detalles,
            entidad=entidad,
            entidad_id=entidad_id,
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            usuario_rol=usuario_rol,
            ip_address=ip_address,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
        db.add(audit_entry)
        db.commit()
        return audit_entry

    @staticmethod
    def list_logs(
        db: Session,
        limit: int = 100,
        solicitud_id: Optional[str] = None,
        operacion: Optional[str] = None,
        resultado: Optional[str] = None
    ) -> List[AuditLog]:
        query = db.query(AuditLog)
        if solicitud_id:
            query = query.filter(AuditLog.entidad_id == str(solicitud_id))
        if operacion:
            query = query.filter(AuditLog.operacion.ilike(f"%{operacion}%"))
        if resultado:
            query = query.filter(AuditLog.resultado == resultado)
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
