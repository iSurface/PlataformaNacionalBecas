# -*- coding: utf-8 -*-
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserDetailResponse, RoleResponse, AssignRolesRequest
from app.schemas.auth import GenericResponse
from app.infrastructure.models.user import User, Role
from app.api.middlewares.auth_guard import require_roles

router = APIRouter(prefix="/admin", tags=["Administración de Usuarios y Roles (Sprint 1)"])

@router.get("/users", response_model=List[UserDetailResponse], summary="HU-005: Listar Usuarios del Sistema (Admin)")
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["SYSADMIN"]))
):
    """Retorna la lista de usuarios registrados con sus roles asociados."""
    users = db.query(User).offset(skip).limit(limit).all()
    results = []
    for u in users:
        p = u.persona
        results.append(UserDetailResponse(
            id=u.id,
            cui=u.cui,
            email=u.email,
            estado=u.estado,
            primer_nombre=p.primer_nombre if p else "",
            segundo_nombre=p.segundo_nombre if p else None,
            primer_apellido=p.primer_apellido if p else "",
            segundo_apellido=p.segundo_apellido if p else None,
            nombre_completo=p.nombre_completo if p else u.email,
            telefono=p.telefono if p else None,
            fecha_creacion=u.fecha_creacion,
            ultimo_acceso=u.ultimo_acceso,
            roles=[r.codigo for r in u.roles if r.es_activo]
        ))
    return results

@router.get("/roles", response_model=List[RoleResponse], summary="Listar Roles Disponibles")
def list_roles(
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["SYSADMIN"]))
):
    """Retorna los roles institucionales disponibles en la matriz RBAC."""
    return db.query(Role).filter(Role.es_activo == True).all()

@router.put("/users/{user_id}/roles", response_model=GenericResponse, summary="HU-005: Asignar Roles a Usuario")
def assign_roles(
    user_id: UUID,
    req: AssignRolesRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(["SYSADMIN"]))
):
    """Asigna uno o más roles a un usuario institucional."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    roles_to_assign = db.query(Role).filter(Role.codigo.in_(req.roles_codigos)).all()
    if len(roles_to_assign) != len(req.roles_codigos):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más códigos de rol no son válidos.")

    user.roles = roles_to_assign
    db.commit()

    return GenericResponse(
        success=True,
        message=f"Roles actualizados exitosamente para el usuario {user.email}.",
        data={"user_id": str(user.id), "roles": [r.codigo for r in roles_to_assign]}
    )
