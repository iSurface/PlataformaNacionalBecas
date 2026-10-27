# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from pydantic import BaseModel

# --- DASHBOARD GERENCIAL Y TRANSPARENCIA ---

class DashboardKpis(BaseModel):
    total_convocatorias_activas: int
    total_solicitudes_recibidas: int
    total_becarios_adjudicados: int
    presupuesto_total_comprometido: float
    solicitudes_por_estado: Dict[str, int]
    distribucion_departamental: Dict[str, int]

class TransparencyBeneficiaryItem(BaseModel):
    numero_expediente: str
    postulante_anonimizado: str # Ej. "J. Pérez G."
    convocatoria_titulo: str
    departamento: str
    monto_mensual: float
    fecha_adjudicacion: str
    resolucion_oficial: str
