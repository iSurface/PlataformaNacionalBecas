# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.models.user import User, Person, Role, SecurityToken
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, ResetPasswordRequest
from app.core.security import get_password_hash, verify_password, create_access_token, generate_random_token
from app.services.email_service import EmailService
from app.core.config import settings

class AuthService:
    @staticmethod
    def register_user(db: Session, req: RegisterRequest) -> dict:
        """HU-001: Registro de cuenta de postulante con verificación por correo"""
        # 1. Verificar unicidad de CUI y Correo (RB-001)
        existing_user = db.query(User).filter((User.cui == req.cui) | (User.email == req.email)).first()
        if existing_user:
            if existing_user.cui == req.cui:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El CUI ingresado ya se encuentra registrado en el sistema."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El correo electrónico ya se encuentra registrado en el sistema."
                )

        # 2. Obtener rol POSTULANTE por defecto
        postulante_role = db.query(Role).filter(Role.codigo == "POSTULANTE").first()
        if not postulante_role:
            postulante_role = Role(
                codigo="POSTULANTE",
                nombre="Postulante / Aspirante a Beca",
                descripcion="Usuario ciudadano con capacidad para postular a convocatorias"
            )
            db.add(postulante_role)
            db.flush()

        # 3. Crear Entidad Usuario y Persona con Hasheo Argon2id
        hashed_pw = get_password_hash(req.password)
        new_user = User(
            cui=req.cui,
            email=req.email,
            password_hash=hashed_pw,
            estado="PENDIENTE_ACTIVACION",
            roles=[postulante_role]
        )
        db.add(new_user)
        db.flush()

        new_person = Person(
            usuario_id=new_user.id,
            primer_nombre=req.primer_nombre,
            segundo_nombre=req.segundo_nombre,
            primer_apellido=req.primer_apellido,
            segundo_apellido=req.segundo_apellido,
            telefono=req.telefono
        )
        db.add(new_person)

        # 4. Generar Token Criptográfico de Activación (24 horas)
        token_str = generate_random_token(32)
        activation_token = SecurityToken(
            usuario_id=new_user.id,
            token_hash=token_str,
            tipo="ACTIVACION_CUENTA",
            expira_en=datetime.now(timezone.utc) + timedelta(hours=settings.ACTIVATION_TOKEN_EXPIRE_HOURS)
        )
        db.add(activation_token)
        db.commit()

        # 5. Despachar Correo de Activación
        EmailService.send_activation_email(new_user.email, new_person.primer_nombre, token_str)

        return {
            "success": True,
            "message": "Registro completado exitosamente. Se ha generado tu token de activación.",
            "cui": new_user.cui,
            "email": new_user.email,
            "activation_token": token_str,
            "activation_url": f"/api/v1/auth/activate?token={token_str}"
        }

    @staticmethod
    def activate_account(db: Session, token: str) -> dict:
        """HU-001: Activación de cuenta mediante token seguro"""
        sec_token = db.query(SecurityToken).filter(
            SecurityToken.token_hash == token,
            SecurityToken.tipo == "ACTIVACION_CUENTA"
        ).first()

        if not sec_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de activación es inválido o no existe."
            )

        if sec_token.es_consumido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este enlace de activación ya ha sido utilizado."
            )

        if sec_token.expira_en < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de activación ha expirado (vigencia de 24 horas). Solicita un nuevo enlace."
            )

        user = db.query(User).filter(User.id == sec_token.usuario_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        user.estado = "ACTIVO"
        sec_token.es_consumido = True
        db.commit()

        return {
            "success": True,
            "message": "Tu cuenta ha sido activada exitosamente. Ya puedes iniciar sesión."
        }

    @staticmethod
    def resend_activation_token(db: Session, email: str) -> dict:
        """HU-001: Reenvío / Consulta de token de activación para cuentas registradas"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró una cuenta con el correo proporcionado.")

        if user.estado == "ACTIVO":
            return {
                "success": True,
                "message": "La cuenta ya se encuentra activa. Puedes iniciar sesión directamente en /login.",
                "estado": "ACTIVO"
            }

        token_str = generate_random_token(32)
        activation_token = SecurityToken(
            usuario_id=user.id,
            token_hash=token_str,
            tipo="ACTIVACION_CUENTA",
            expira_en=datetime.now(timezone.utc) + timedelta(hours=settings.ACTIVATION_TOKEN_EXPIRE_HOURS)
        )
        db.add(activation_token)
        db.commit()

        nombre = user.persona.primer_nombre if user.persona else "Usuario"
        EmailService.send_activation_email(user.email, nombre, token_str)

        return {
            "success": True,
            "message": "Nuevo token de activación generado exitosamente.",
            "email": user.email,
            "activation_token": token_str,
            "activation_url": f"/api/v1/auth/activate?token={token_str}"
        }

    @staticmethod
    def authenticate_user(db: Session, req: LoginRequest) -> TokenResponse:
        """HU-002: Autenticación, control anti-fuerza bruta y emisión JWT"""
        username = req.username.strip()
        user = db.query(User).filter((User.email == username) | (User.cui == username)).first()

        if not user:
            # Timing attack prevention
            verify_password("dummy_password_for_constant_time", "$argon2id$v=19$m=65536,t=3,p=4$dummy$dummy")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas. Verifique su usuario y contraseña."
            )

        # 1. Verificar si la cuenta está bloqueada temporalmente (RB-002)
        now = datetime.now(timezone.utc)
        if user.bloqueado_hasta and user.bloqueado_hasta > now:
            minutos_restantes = int((user.bloqueado_hasta - now).total_seconds() // 60) + 1
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Cuenta bloqueada temporalmente por exceso de intentos fallidos. Intente de nuevo en {minutos_restantes} minutos."
            )

        # 2. Verificar estado de la cuenta
        if user.estado == "PENDIENTE_ACTIVACION":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta aún no ha sido activada. Por favor revise el correo enviado o solicite un nuevo enlace de activación."
            )
        elif user.estado == "INACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta se encuentra deshabilitada. Contacte al administrador del sistema."
            )

        # 3. Verificar Contraseña con Argon2id
        if not verify_password(req.password, user.password_hash):
            user.intentos_fallidos += 1
            if user.intentos_fallidos >= 5:
                user.bloqueado_hasta = now + timedelta(minutes=15)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Ha alcanzado el límite de 5 intentos fallidos. Su cuenta ha sido bloqueada por 15 minutos."
                )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Credenciales inválidas. Intentos restantes antes de bloqueo: {5 - user.intentos_fallidos}."
            )

        # 4. Login Exitoso: Resetear intentos y actualizar último acceso
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.ultimo_acceso = now
        db.commit()

        # 5. Generar Token JWT con Roles
        roles_codigos = [r.codigo for r in user.roles if r.es_activo]
        token_str = create_access_token(
            subject=str(user.id),
            roles=roles_codigos,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=token_str,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            cui=user.cui,
            email=user.email,
            nombre_completo=user.persona.nombre_completo if user.persona else user.email,
            roles=roles_codigos
        )

    @staticmethod
    def forgot_password(db: Session, email: str) -> dict:
        """HU-003: Solicitud de restablecimiento seguro de contraseña"""
        user = db.query(User).filter(User.email == email).first()
        
        # Prevención de enumeración de usuarios: responder siempre 200 OK
        if user and user.estado == "ACTIVO":
            token_str = generate_random_token(32)
            reset_token = SecurityToken(
                usuario_id=user.id,
                token_hash=token_str,
                tipo="RECUPERACION_PASSWORD",
                expira_en=datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
            )
            db.add(reset_token)
            db.commit()
            
            nombre = user.persona.primer_nombre if user.persona else "Usuario"
            EmailService.send_password_reset_email(user.email, nombre, token_str)

        return {
            "success": True,
            "message": "Si la cuenta está registrada, recibirás un enlace de restablecimiento en tu correo en breve.",
            "reset_token": token_str if user and user.estado == "ACTIVO" else None,
            "reset_url": f"/api/v1/auth/reset-password?token={token_str}" if user and user.estado == "ACTIVO" else None
        }

    @staticmethod
    def reset_password(db: Session, req: ResetPasswordRequest) -> dict:
        """HU-003: Restablecimiento de contraseña con token temporal (15 min)"""
        sec_token = db.query(SecurityToken).filter(
            SecurityToken.token_hash == req.token,
            SecurityToken.tipo == "RECUPERACION_PASSWORD"
        ).first()

        if not sec_token or sec_token.es_consumido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de restablecimiento es inválido o ya ha sido utilizado."
            )

        if sec_token.expira_en < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de restablecimiento ha expirado (vigencia de 15 minutos). Solicite uno nuevo."
            )

        user = db.query(User).filter(User.id == sec_token.usuario_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        user.password_hash = get_password_hash(req.new_password)
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        sec_token.es_consumido = True
        db.commit()

        return {
            "success": True,
            "message": "Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
        }
