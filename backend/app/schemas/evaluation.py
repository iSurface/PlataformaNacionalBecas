# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# --- SPRINT 4: COMITÉS Y EVALUACIONES ---

class CommitteeCreate(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    convocatoria_id: UUID

class CommitteeMemberAdd(BaseModel):
    usuario_id: UUID
    rol_comite: str = Field("EVALUADOR", description="PRESIDENTE, SECRETARIO, VOCAL, EVALUADOR")

class ConflictDeclarationRequest(BaseModel):
    acepta_terminos: bool = Field(True, description="Declaración formal de no poseer parentesco ni conflicto de interés")

class AssignApplicationsRequest(BaseModel):
    solicitud_ids: List[UUID]

class EvaluationRubricScoreRequest(BaseModel):
    solicitud_id: UUID
    puntaje_academico: float = Field(..., ge=0, le=40, description="Mérito Académico (0 a 40 pts)")
    puntaje_socioeconomico: float = Field(..., ge=0, le=40, description="Condición Socioeconómica (0 a 40 pts)")
    puntaje_ensayo_atestados: float = Field(..., ge=0, le=20, description="Ensayo de Motivación y Atestados (0 a 20 pts)")
    dictamen_individual: str = Field("FAVORABLE", description="FAVORABLE, NO_FAVORABLE, RESERVA")
    observaciones: Optional[str] = None

class EvaluationScoreResponse(BaseModel):
    id: UUID
    solicitud_id: UUID
    evaluador_id: UUID
    puntaje_academico: float
    puntaje_socioeconomico: float
    puntaje_ensayo_atestados: float
    puntaje_total: float
    dictamen_individual: str
    observaciones: Optional[str] = None
    fecha_evaluacion: datetime

    class Config:
        from_attributes = True

class CommitteeConsolidationResponse(BaseModel):
    solicitud_id: UUID
    numero_expediente: Optional[str] = None
    total_evaluaciones: int
    puntaje_promedio: float
    dictamen_recomendado: str
