# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.models.user import Base

class Department(Base):
    __tablename__ = "cat_departamentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(80), unique=True, nullable=False)
    es_activo = Column(Boolean, default=True, nullable=False)

    municipios = relationship("Municipality", back_populates="departamento", cascade="all, delete-orphan")

class Municipality(Base):
    __tablename__ = "cat_municipios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    departamento_id = Column(UUID(as_uuid=True), ForeignKey("cat_departamentos.id", ondelete="RESTRICT"), nullable=False)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(80), nullable=False)
    es_activo = Column(Boolean, default=True, nullable=False)

    departamento = relationship("Department", back_populates="municipios")

class EducationLevel(Base):
    __tablename__ = "cat_niveles_educativos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(20), unique=True, nullable=False, index=True)  # BASICO, DIVERSIFICADO, LICENCIATURA, MAESTRIA, DOCTORADO
    nombre = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    es_activo = Column(Boolean, default=True, nullable=False)

class ScholarshipType(Base):
    __tablename__ = "cat_tipos_beca"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(30), unique=True, nullable=False, index=True)  # EXCELENCIA_ACADEMICA, ESCASOS_RECURSOS, TALENTO_DEPORTIVO, DISCAPACIDAD
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    es_activo = Column(Boolean, default=True, nullable=False)

class EducationalInstitution(Base):
    __tablename__ = "cat_instituciones_educativas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(30), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    tipo_sector = Column(String(30), nullable=False, default="PUBLICO")  # PUBLICO, PRIVADO, POR_COOPERATIVA
    es_activo = Column(Boolean, default=True, nullable=False)
