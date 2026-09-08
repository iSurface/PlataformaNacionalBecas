# -*- coding: utf-8 -*-
"""
Servicio de Dominio: Convocatorias de Becas y Catálogo Ciudadano
Sprint 2 - HU-002, HU-003, HU-004, HU-005, HU-006
"""
import math
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.infrastructure.models.scholarship import ScholarshipCall, CallRequirement
from app.infrastructure.models.catalog import ScholarshipType, EducationLevel, Department
from app.schemas.scholarship import (
    ScholarshipCallCreate, ScholarshipCallUpdate, CallRequirementCreate,
    ScholarshipCallPublicSummary, PaginatedCallResponse, ScholarshipCallDetailResponse,
    CallRequirementResponse
)

class ScholarshipService:

    @staticmethod
    def create_call(db: Session, user_id: UUID, req: ScholarshipCallCreate) -> ScholarshipCall:
        """HU-002: Crea una nueva convocatoria en estado BORRADOR."""
        if req.fecha_cierre <= req.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de cierre debe ser posterior a la fecha de inicio de la convocatoria."
            )

        # Generar código correlativo si no se proveyó uno
        if not req.codigo:
            year = datetime.now().year
            count = db.query(ScholarshipCall).count() + 1
            codigo = f"BEC-{year}-{count:04d}"
        else:
            codigo = req.codigo.strip().upper()

        existente = db.query(ScholarshipCall).filter(ScholarshipCall.codigo == codigo).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una convocatoria con el código '{codigo}'."
            )

        call = ScholarshipCall(
            codigo=codigo,
            titulo=req.titulo.strip(),
            descripcion=req.descripcion.strip(),
            tipo_beca_id=req.tipo_beca_id,
            nivel_educativo_id=req.nivel_educativo_id,
            departamento_id=req.departamento_id,
            cupos_disponibles=req.cupos_disponibles,
            presupuesto_total=req.presupuesto_total,
            monto_individual=req.monto_individual,
            promedio_minimo_requerido=req.promedio_minimo_requerido,
            fecha_inicio=req.fecha_inicio,
            fecha_cierre=req.fecha_cierre,
            estado="BORRADOR",
            bases_url=req.bases_url,
            cronograma_detalle=req.cronograma_detalle,
            creado_por_id=user_id
        )
        db.add(call)
        db.flush()

        # Agregar requisitos iniciales si vienen adjuntos
        if req.requisitos_iniciales:
            for r in req.requisitos_iniciales:
                req_obj = CallRequirement(
                    convocatoria_id=call.id,
                    nombre=r.nombre.strip(),
                    descripcion=r.descripcion,
                    es_obligatorio=r.es_obligatorio,
                    tipo_documento=r.tipo_documento.upper(),
                    peso_maximo_mb=r.peso_maximo_mb,
                    orden=r.orden
                )
                db.add(req_obj)

        db.commit()
        db.refresh(call)
        return call

    @staticmethod
    def update_call(db: Session, call_id: UUID, req: ScholarshipCallUpdate) -> ScholarshipCall:
        """HU-002: Actualiza parámetros de la convocatoria (Solo si está en BORRADOR)."""
        call = db.query(ScholarshipCall).filter(ScholarshipCall.id == call_id).first()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada.")

        if call.estado != "BORRADOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar una convocatoria en estado '{call.estado}'. Solo se permite en BORRADOR."
            )

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(call, key, value)

        if call.fecha_cierre <= call.fecha_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de cierre debe ser posterior a la fecha de inicio."
            )

        db.commit()
        db.refresh(call)
        return call

    @staticmethod
    def add_requirement(db: Session, call_id: UUID, req: CallRequirementCreate) -> CallRequirement:
        """HU-002: Agrega un requisito documental a la convocatoria."""
        call = db.query(ScholarshipCall).filter(ScholarshipCall.id == call_id).first()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada.")

        if call.estado != "BORRADOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden agregar requisitos a convocatorias en estado BORRADOR."
            )

        requirement = CallRequirement(
            convocatoria_id=call.id,
            nombre=req.nombre.strip(),
            descripcion=req.descripcion,
            es_obligatorio=req.es_obligatorio,
            tipo_documento=req.tipo_documento.upper(),
            peso_maximo_mb=req.peso_maximo_mb,
            orden=req.orden
        )
        db.add(requirement)
        db.commit()
        db.refresh(requirement)
        return requirement

    @staticmethod
    def publish_call(db: Session, call_id: UUID) -> ScholarshipCall:
        """HU-003: Publicación oficial de la convocatoria tras validar reglas de completitud."""
        call = db.query(ScholarshipCall).filter(ScholarshipCall.id == call_id).first()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada.")

        if call.estado != "BORRADOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La convocatoria ya se encuentra en estado '{call.estado}'."
            )

        if not call.requisitos or len(call.requisitos) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede publicar una convocatoria sin al menos 1 requisito documental."
            )

        now = datetime.now(timezone.utc)
        if call.fecha_cierre <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de cierre de la convocatoria ya venció. Actualice las fechas antes de publicar."
            )

        call.estado = "PUBLICADA"
        db.commit()
        db.refresh(call)
        return call

    @staticmethod
    def close_call(db: Session, call_id: UUID) -> ScholarshipCall:
        """HU-003: Cierre formal de la recepción de postulaciones."""
        call = db.query(ScholarshipCall).filter(ScholarshipCall.id == call_id).first()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada.")

        if call.estado != "PUBLICADA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden cerrar convocatorias que estén PUBLICADAS (Estado actual: '{call.estado}')."
            )

        call.estado = "CERRADA"
        db.commit()
        db.refresh(call)
        return call

    @staticmethod
    def list_public_calls(
        db: Session,
        q: Optional[str] = None,
        tipo_id: Optional[UUID] = None,
        nivel_id: Optional[UUID] = None,
        depto_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedCallResponse:
        """HU-004 y HU-006: Búsqueda y catálogo ciudadano paginado y optimizado para móvil."""
        now = datetime.now(timezone.utc)
        query = db.query(ScholarshipCall).filter(
            ScholarshipCall.es_activo == True,
            ScholarshipCall.estado == "PUBLICADA"
        )

        if q:
            search = f"%{q.strip()}%"
            query = query.filter(or_(
                ScholarshipCall.titulo.ilike(search),
                ScholarshipCall.descripcion.ilike(search),
                ScholarshipCall.codigo.ilike(search)
            ))

        if tipo_id:
            query = query.filter(ScholarshipCall.tipo_beca_id == tipo_id)
        if nivel_id:
            query = query.filter(ScholarshipCall.nivel_educativo_id == nivel_id)
        if depto_id:
            query = query.filter(or_(
                ScholarshipCall.departamento_id == depto_id,
                ScholarshipCall.departamento_id.is_(None) # Incluye cobertura nacional
            ))

        total = query.count()
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        offset = (page - 1) * page_size
        calls = query.order_by(ScholarshipCall.fecha_cierre.asc()).offset(offset).limit(page_size).all()

        items = []
        for c in calls:
            dias = max(0, (c.fecha_cierre - now).days)
            depto_str = c.departamento.nombre if c.departamento else "Cobertura Nacional"
            items.append(ScholarshipCallPublicSummary(
                id=c.id,
                codigo=c.codigo,
                titulo=c.titulo,
                tipo_beca=c.tipo_beca.nombre if c.tipo_beca else "General",
                nivel_educativo=c.nivel_educativo.nombre if c.nivel_educativo else "Todos",
                departamento_cobertura=depto_str,
                cupos_disponibles=c.cupos_disponibles,
                monto_individual=float(c.monto_individual),
                promedio_minimo_requerido=c.promedio_minimo_requerido,
                fecha_cierre=c.fecha_cierre,
                estado=c.estado,
                dias_restantes=dias
            ))

        return PaginatedCallResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items
        )

    @staticmethod
    def get_public_call_detail(db: Session, call_id: UUID) -> ScholarshipCallDetailResponse:
        """HU-005: Ficha técnica detallada de bases y requisitos."""
        call = db.query(ScholarshipCall).filter(
            ScholarshipCall.id == call_id,
            ScholarshipCall.es_activo == True
        ).first()

        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada.")

        reqs = [CallRequirementResponse.model_validate(r) for r in call.requisitos]
        depto_nombre = call.departamento.nombre if call.departamento else "Cobertura Nacional"

        return ScholarshipCallDetailResponse(
            id=call.id,
            codigo=call.codigo,
            titulo=call.titulo,
            descripcion=call.descripcion,
            tipo_beca_id=call.tipo_beca_id,
            nivel_educativo_id=call.nivel_educativo_id,
            departamento_id=call.departamento_id,
            cupos_disponibles=call.cupos_disponibles,
            presupuesto_total=float(call.presupuesto_total),
            monto_individual=float(call.monto_individual),
            promedio_minimo_requerido=call.promedio_minimo_requerido,
            fecha_inicio=call.fecha_inicio,
            fecha_cierre=call.fecha_cierre,
            bases_url=call.bases_url,
            cronograma_detalle=call.cronograma_detalle,
            estado=call.estado,
            tipo_beca_nombre=call.tipo_beca.nombre if call.tipo_beca else "",
            nivel_educativo_nombre=call.nivel_educativo.nombre if call.nivel_educativo else "",
            departamento_nombre=depto_nombre,
            creado_en=call.creado_en,
            actualizado_en=call.actualizado_en,
            requisitos=reqs
        )
