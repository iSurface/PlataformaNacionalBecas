# -*- coding: utf-8 -*-
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.models.catalog import Department, Municipality, EducationLevel, ScholarshipType, EducationalInstitution
from app.schemas.catalog import (
    DepartmentResponse, MunicipalityResponse, EducationLevelResponse, 
    ScholarshipTypeResponse, CreateCatalogItemRequest
)

class CatalogService:
    @staticmethod
    def get_departments(db: Session, only_active: bool = True) -> List[Department]:
        query = db.query(Department)
        if only_active:
            query = query.filter(Department.es_activo == True)
        return query.order_by(Department.codigo).all()

    @staticmethod
    def get_municipalities(db: Session, department_id: Optional[UUID] = None, only_active: bool = True) -> List[Municipality]:
        query = db.query(Municipality)
        if department_id:
            query = query.filter(Municipality.departamento_id == department_id)
        if only_active:
            query = query.filter(Municipality.es_activo == True)
        return query.order_by(Municipality.codigo).all()

    @staticmethod
    def get_education_levels(db: Session, only_active: bool = True) -> List[EducationLevel]:
        query = db.query(EducationLevel)
        if only_active:
            query = query.filter(EducationLevel.es_activo == True)
        return query.order_by(EducationLevel.codigo).all()

    @staticmethod
    def get_scholarship_types(db: Session, only_active: bool = True) -> List[ScholarshipType]:
        query = db.query(ScholarshipType)
        if only_active:
            query = query.filter(ScholarshipType.es_activo == True)
        return query.order_by(ScholarshipType.codigo).all()

    @staticmethod
    def create_scholarship_type(db: Session, req: CreateCatalogItemRequest) -> ScholarshipType:
        """Crea un nuevo tipo de beca con validación de código único"""
        existing = db.query(ScholarshipType).filter(
            (ScholarshipType.codigo == req.codigo) | (ScholarshipType.nombre == req.nombre)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código o nombre del tipo de beca ya existe."
            )
        new_item = ScholarshipType(
            codigo=req.codigo.upper(),
            nombre=req.nombre,
            descripcion=req.descripcion
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @staticmethod
    def toggle_scholarship_type_status(db: Session, item_id: UUID, is_active: bool) -> ScholarshipType:
        """RB-025: Borrado lógico de elementos de catálogo para preservar integridad histórica"""
        item = db.query(ScholarshipType).filter(ScholarshipType.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de beca no encontrado.")
        item.es_activo = is_active
        db.commit()
        db.refresh(item)
        return item
