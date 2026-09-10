# -*- coding: utf-8 -*-
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Tabla asociativa Usuarios - Roles (Muchos a Muchos)
user_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

# Tabla asociativa Roles - Permisos (Muchos a Muchos)
role_permissions = Table(
    "rol_permisos",
    Base.metadata,
    Column("rol_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", UUID(as_uuid=True), ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cui = Column(String(13), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    google_id = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    estado = Column(String(30), nullable=False, default="PENDIENTE_ACTIVACION", index=True)  # PENDIENTE_ACTIVACION, ACTIVO, BLOQUEADO_TEMPORAL, INACTIVO
    intentos_fallidos = Column(Integer, default=0, nullable=False)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    persona = relationship("Person", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_roles, back_populates="usuarios", lazy="joined")
    tokens = relationship("SecurityToken", back_populates="usuario", cascade="all, delete-orphan")

class Person(Base):
    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    primer_nombre = Column(String(60), nullable=False)
    segundo_nombre = Column(String(60), nullable=True)
    primer_apellido = Column(String(60), nullable=False)
    segundo_apellido = Column(String(60), nullable=True)
    telefono = Column(String(20), nullable=True)

    usuario = relationship("User", back_populates="persona")

    @property
    def nombre_completo(self) -> str:
        nombres = f"{self.primer_nombre} {self.segundo_nombre or ''}".strip()
        apellidos = f"{self.primer_apellido} {self.segundo_apellido or ''}".strip()
        return f"{nombres} {apellidos}".strip()

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(40), unique=True, nullable=False, index=True)  # SYSADMIN, POSTULANTE, ADMIN_BECAS, EVALUADOR, COORD_COMITE, AUTORIDAD, AUDITOR
    nombre = Column(String(80), nullable=False)
    descripcion = Column(String(255), nullable=True)
    es_activo = Column(Boolean, default=True, nullable=False)

    usuarios = relationship("User", secondary=user_roles, back_populates="roles")
    permisos = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="joined")

class Permission(Base):
    __tablename__ = "permisos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(60), unique=True, nullable=False, index=True)  # IAM_ADMIN, CATALOG_MANAGE, SCHOLARSHIP_VIEW, etc.
    modulo = Column(String(60), nullable=False)
    accion = Column(String(60), nullable=False)

    roles = relationship("Role", secondary=role_permissions, back_populates="permisos")

class SecurityToken(Base):
    __tablename__ = "tokens_seguridad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    tipo = Column(String(30), nullable=False)  # ACTIVACION_CUENTA, RECUPERACION_PASSWORD
    expira_en = Column(DateTime(timezone=True), nullable=False)
    es_consumido = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    usuario = relationship("User", back_populates="tokens")
