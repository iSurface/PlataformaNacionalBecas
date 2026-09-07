# -*- coding: utf-8 -*-
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Contexto criptográfico para hasheo seguro
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Genera el hash seguro de la contraseña utilizando Argon2id"""
    return pwd_context.hash(password)

def validate_password_complexity(password: str) -> bool:
    """
    Valida las políticas de complejidad de contraseñas:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial (@$!%*?&#)
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[@$!%*?&#._\-+]", password):
        return False
    return True

def validate_cui(cui: str) -> bool:
    """
    Valida sintácticamente el CUI guatemalteco de 13 dígitos:
    - Longitud exacta de 13 caracteres numéricos.
    - Primeros 8 dígitos: correlativo.
    - 9no dígito: verificador (algoritmo módulo 11).
    - Últimos 4 dígitos: código de departamento (2) y municipio (2).
    """
    if not cui or len(cui) != 13 or not cui.isdigit():
        return False
    
    # Validación básica de código de departamento (01 a 22)
    depto = int(cui[9:11])
    if depto < 1 or depto > 22:
        return False

    # Algoritmo de Módulo 11 para los primeros 9 dígitos
    correlativo = [int(d) for d in cui[:8]]
    verificador = int(cui[8])
    
    total = sum(d * (i + 2) for i, d in enumerate(correlativo))
    residuo = total % 11
    
    digito_calculado = 11 - residuo
    if digito_calculado == 11:
        digito_calculado = 0
    elif digito_calculado == 10:
        digito_calculado = 0  # Regla estándar en documento de identidad
        
    return verificador == digito_calculado

def create_access_token(subject: Union[str, Any], roles: list[str], expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado con expiración para control de sesión"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {
        "sub": str(subject),
        "roles": roles,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def generate_random_token(bytes_length: int = 32) -> str:
    """Genera un token criptográficamente seguro de un solo uso para enlaces de activación o reseteo"""
    return secrets.token_urlsafe(bytes_length)
