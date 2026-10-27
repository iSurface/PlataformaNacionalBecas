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
        ip_address: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            modulo=modulo,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            usuario_id=usuario_id,
            ip_address=ip_address,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
        db.add(audit_entry)
        db.commit()
        return audit_entry

    @staticmethod
    def list_logs(db: Session, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
