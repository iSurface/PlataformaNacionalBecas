# -*- coding: utf-8 -*-
"""
Endpoints de la API: Tablero Gerencial, Fiscalización Pública y Bitácora Inmutable
Sprint 5 - HU-006, HU-007, HU-008, HU-009
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import get_current_user, require_roles
from app.infrastructure.models.user import User
from app.schemas.dashboard import DashboardKpis, TransparencyBeneficiaryItem
from app.schemas.resolution import AuditLogResponse
from app.services.dashboard_service import DashboardService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/kpis", response_model=DashboardKpis, summary="HU-006: Métricas y Tablero Gerencial de Impacto")
def get_kpis(
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "AUDITOR", "ADMIN_BECAS", "SYSADMIN"])),
    db: Session = Depends(get_db)
):
    return DashboardService.get_management_kpis(db)

@router.get("/transparency", response_model=List[TransparencyBeneficiaryItem], summary="HU-007: Padrón Público de Beneficiarios (Decreto 57-2008)")
def get_transparency_registry(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Acceso público ciudadano y entes de control al padrón oficial anonimizado."""
    return DashboardService.get_transparency_registry(db, limit)

@router.get("/audit-logs", response_model=List[AuditLogResponse], summary="HU-008 & HU-003: Bitácora Inmutable de Auditoría en 4 Dimensiones")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    solicitud_id: Optional[str] = Query(None, description="Filtrar por ID de solicitud"),
    operacion: Optional[str] = Query(None, description="Filtrar por tipo de operación"),
    resultado: Optional[str] = Query(None, description="Filtrar por resultado: EXITOSO, DENEGADO, ERROR"),
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "AUDITOR", "SYSADMIN", "ADMIN_BECAS"])),
    db: Session = Depends(get_db)
):
    logs = AuditService.list_logs(db, limit=limit, solicitud_id=solicitud_id, operacion=operacion, resultado=resultado)
    return [
        AuditLogResponse(
            id=log.id,
            usuario_id=log.usuario_id,
            usuario_nombre=log.usuario_nombre or (log.usuario.nombre_completo if log.usuario else "Sistema"),
            usuario_rol=log.usuario_rol or (log.usuario.rol if log.usuario else "SISTEMA"),
            ip_address=log.ip_address,
            timestamp=log.timestamp,
            modulo=log.modulo,
            accion=log.accion,
            operacion=log.operacion or log.accion,
            entidad=log.entidad,
            entidad_id=log.entidad_id,
            resultado=log.resultado or "EXITOSO",
            detalles=log.detalles
        ) for log in logs
    ]
