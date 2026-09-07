# -*- coding: utf-8 -*-
from uuid import UUID
from typing import Optional, List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.infrastructure.models.user import User

security_scheme = HTTPBearer(auto_error=True)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extrae y valida el token JWT del header Authorization, retornando la entidad User activa"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autorización inválido (sujeto faltante)."
            )
        user_id = UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado (inactividad superior a 30 minutos). Por favor inicie sesión nuevamente."
        )
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token de autenticación."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario de la sesión no encontrado."
        )

    if user.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cuenta no autorizada. Estado actual: {user.estado}."
        )

    return user

def require_roles(allowed_roles: List[str]):
    """
    HU-005 / RB-026: Decorador de autorización basada en roles (RBAC).
    Verifica que el usuario autenticado posea al menos uno de los roles permitidos.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [r.codigo for r in current_user.roles if r.es_activo]
        
        # SYSADMIN tiene acceso global
        if "SYSADMIN" in user_roles:
            return current_user

        has_permission = any(role in user_roles for role in allowed_roles)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}."
            )
        return current_user

    return role_checker
