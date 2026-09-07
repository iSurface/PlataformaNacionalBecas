# -*- coding: utf-8 -*-
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.security import validate_password_complexity, validate_cui

class RegisterRequest(BaseModel):
    cui: str = Field(..., description="Código Único de Identificación (13 dígitos numéricos)")
    primer_nombre: str = Field(..., min_length=2, max_length=60)
    segundo_nombre: Optional[str] = Field(None, max_length=60)
    primer_apellido: str = Field(..., min_length=2, max_length=60)
    segundo_apellido: Optional[str] = Field(None, max_length=60)
    telefono: Optional[str] = Field(None, max_length=20)
    email: EmailStr = Field(..., description="Correo electrónico institucional o personal")
    password: str = Field(..., min_length=8, description="Contraseña con mayúscula, minúscula, número y símbolo")

    @field_validator("cui")
    def validate_cui_field(cls, v: str) -> str:
        v_clean = v.strip()
        if not validate_cui(v_clean):
            raise ValueError("El CUI ingresado no es válido (debe tener 13 dígitos y verificar algoritmo módulo 11).")
        return v_clean

    @field_validator("password")
    def validate_password_field(cls, v: str) -> str:
        if not validate_password_complexity(v):
            raise ValueError("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo especial.")
        return v

class LoginRequest(BaseModel):
    username: str = Field(..., description="Correo electrónico o CUI del usuario")
    password: str = Field(..., description="Contraseña del usuario")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: UUID
    cui: str
    email: str
    nombre_completo: str
    roles: List[str]

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico asociado a la cuenta")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Token seguro recibido por correo")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

    @field_validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        if not validate_password_complexity(v):
            raise ValueError("La nueva contraseña no cumple con las políticas de complejidad requeridas.")
        return v

class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
