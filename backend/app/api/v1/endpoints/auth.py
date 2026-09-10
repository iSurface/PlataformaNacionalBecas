from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, 
    ForgotPasswordRequest, ResetPasswordRequest, GenericResponse,
    GoogleLoginResponse, GoogleCallbackResponse, GoogleCompleteRegistrationRequest
)
from app.schemas.user import UserDetailResponse
from app.services.auth_service import AuthService
from app.api.middlewares.auth_guard import get_current_user
from app.infrastructure.models.user import User

router = APIRouter(prefix="/auth", tags=["Autenticación e Identidad (Sprint 1 & Sprint 2)"])

@router.post("/register", response_model=GenericResponse, status_code=status.HTTP_201_CREATED, summary="HU-001: Registro de Postulante")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Permite el registro de nuevos postulantes con validación de CUI y envío de correo de activación (24h)."""
    res = AuthService.register_user(db, req)
    return GenericResponse(success=True, message=res["message"], data=res)

@router.get("/activate", response_model=GenericResponse, summary="HU-001: Activación de Cuenta")
def activate_account(token: str = Query(..., description="Token de activación recibido por correo"), db: Session = Depends(get_db)):
    """Activa la cuenta del usuario validando la firma y vigencia del token."""
    res = AuthService.activate_account(db, token)
    return GenericResponse(success=True, message=res["message"])

@router.post("/resend-activation", response_model=GenericResponse, summary="HU-001: Reenviar Token de Activación")
def resend_activation(email: str = Query(..., description="Correo electrónico de la cuenta registrada"), db: Session = Depends(get_db)):
    """Genera y retorna un nuevo token de activación para cuentas registradas pendientes de activación."""
    res = AuthService.resend_activation_token(db, email)
    return GenericResponse(success=True, message=res["message"], data=res)

@router.post("/login", response_model=TokenResponse, summary="HU-002: Inicio de Sesión y Emisión JWT")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Autentica credenciales, bloquea tras 5 intentos fallidos y emite token JWT con tiempo de expiración (30 min)."""
    return AuthService.authenticate_user(db, req)

@router.post("/forgot-password", response_model=GenericResponse, summary="HU-003: Solicitud de Recuperación de Clave")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Despacha un enlace de restablecimiento con vigencia estricta de 15 minutos (previene enumeración de usuarios)."""
    res = AuthService.forgot_password(db, req.email)
    return GenericResponse(success=True, message=res["message"], data=res)

@router.post("/reset-password", response_model=GenericResponse, summary="HU-003: Restablecimiento de Clave")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Actualiza la contraseña del usuario utilizando el token temporal recibido por correo."""
    res = AuthService.reset_password(db, req)
    return GenericResponse(success=True, message=res["message"])

@router.get("/me", response_model=UserDetailResponse, summary="Consulta del Usuario Autenticado")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retorna la información del perfil del usuario actualmente autenticado."""
    persona = current_user.persona
    return UserDetailResponse(
        id=current_user.id,
        cui=current_user.cui,
        email=current_user.email,
        estado=current_user.estado,
        primer_nombre=persona.primer_nombre if persona else "",
        segundo_nombre=persona.segundo_nombre if persona else None,
        primer_apellido=persona.primer_apellido if persona else "",
        segundo_apellido=persona.segundo_apellido if persona else None,
        nombre_completo=persona.nombre_completo if persona else current_user.email,
        telefono=persona.telefono if persona else None,
        fecha_creacion=current_user.fecha_creacion,
        ultimo_acceso=current_user.ultimo_acceso,
        roles=[r.codigo for r in current_user.roles if r.es_activo]
    )

# ==========================================================
# ENDPOINTS GOOGLE OAUTH 2.0 (HU-001)
# ==========================================================
@router.get("/google/login", summary="HU-001: Iniciar Autenticación con Google")
def google_login(
    redirect_uri: Optional[str] = Query(None, description="URI de callback personalizada (opcional)"),
    redirect_to_google: bool = Query(True, description="Si es True realiza un HTTP 307 Redirect a Google; si es False retorna la URL en JSON")
):
    """
    Inicia el flujo de autenticación con Google OAuth 2.0.
    Redirecciona al usuario a la pantalla oficial de Google o retorna la URL para clientes desacoplados.
    """
    auth_url = AuthService.get_google_auth_url(redirect_uri=redirect_uri)
    if redirect_to_google:
        return RedirectResponse(url=auth_url)
    return GoogleLoginResponse(authorization_url=auth_url)

@router.get("/google/callback", response_model=GoogleCallbackResponse, summary="HU-001: Callback de Google OAuth 2.0")
def google_callback(
    code: str = Query(..., description="Código de autorización retornado por Google"),
    error: Optional[str] = Query(None, description="Error reportado por Google si el usuario cancela"),
    redirect_uri: Optional[str] = Query(None, description="URI de redireccionamiento utilizada al iniciar el flujo"),
    db: Session = Depends(get_db)
):
    """
    Recibe el código retornado por Google.
    - Si el usuario ya existe en el sistema: Retorna la sesión activa con JWT (is_new_user=False).
    - Si es un nuevo postulante: Retorna los datos precargados y un registration_token temporal para completar el CUI obligatorio (is_new_user=True).
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Autenticación con Google cancelada o fallida: {error}"
        )
    return AuthService.handle_google_callback(db=db, code=code, redirect_uri=redirect_uri)

@router.post("/google/complete-registration", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="HU-001: Completar Registro Google con CUI Obligatorio")
def google_complete_registration(
    req: GoogleCompleteRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Completa el registro de un nuevo postulante autenticado con Google:
    Valida y asocia su CUI obligatorio de 13 dígitos (Módulo 11), crea su usuario en estado ACTIVO y emite su token JWT.
    """
    return AuthService.complete_google_registration(db=db, req=req)
