# -*- coding: utf-8 -*-
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.infrastructure.models.scholarship import ScholarshipCall
from app.infrastructure.models.application import Application
from app.infrastructure.models.resolution import AwardResolution
from app.infrastructure.models.student_profile import StudentProfile
from app.infrastructure.models.catalog import Department

class DashboardService:
    @staticmethod
    def get_management_kpis(db: Session) -> Dict[str, Any]:
        total_convocatorias = db.query(func.count(ScholarshipCall.id)).filter(
            ScholarshipCall.estado == "PUBLICADA"
        ).scalar() or 0

        total_solicitudes = db.query(func.count(Application.id)).scalar() or 0

        total_adjudicados = db.query(func.count(Application.id)).filter(
            Application.estado == "ADJUDICADA"
        ).scalar() or 0

        presupuesto_total = db.query(func.sum(AwardResolution.monto_total_comprometido)).scalar() or 0.0

        # Solicitudes agrupadas por estado
        estados_count = db.query(Application.estado, func.count(Application.id)).group_by(Application.estado).all()
        solicitudes_por_estado = {estado: count for estado, count in estados_count}

        # Distribución departamental
        dept_dist = {}
        rows = db.query(Department.nombre, func.count(Application.id)).join(
            StudentProfile, StudentProfile.departamento_residencia_id == Department.id
        ).join(
            Application, Application.postulante_id == StudentProfile.usuario_id
        ).group_by(Department.nombre).all()

        for dept, count in rows:
            dept_dist[dept] = count

        return {
            "total_convocatorias_activas": total_convocatorias,
            "total_solicitudes_recibidas": total_solicitudes,
            "total_becarios_adjudicados": total_adjudicados,
            "presupuesto_total_comprometido": round(float(presupuesto_total), 2),
            "solicitudes_por_estado": solicitudes_por_estado,
            "distribucion_departamental": dept_dist
        }

    @staticmethod
    def get_transparency_registry(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Registro público de beneficiarios con anonimización legal (Decreto 57-2008)"""
        adjudicadas = db.query(Application).filter(Application.estado == "ADJUDICADA").limit(limit).all()
        results = []
        for a in adjudicadas:
            user = a.postulante
            if user:
                if hasattr(user, "persona") and user.persona:
                    nombre_completo = user.persona.nombre_completo
                elif hasattr(user, "nombre_completo"):
                    nombre_completo = user.nombre_completo
                else:
                    nombre_completo = user.email
            else:
                nombre_completo = "Beneficiario"

            parts = nombre_completo.split()
            if len(parts) >= 2:
                anon = f"{parts[0][0]}. {parts[1]}"
            else:
                anon = nombre_completo

            dept_nombre = "Guatemala"
            if user and hasattr(user, "perfil_estudiante") and user.perfil_estudiante:
                perfil = user.perfil_estudiante[0] if isinstance(user.perfil_estudiante, list) else user.perfil_estudiante
                if perfil and hasattr(perfil, "departamento") and perfil.departamento:
                    dept_nombre = perfil.departamento.nombre

            monto = 1000.0
            if a.convocatoria and hasattr(a.convocatoria, "monto_individual") and a.convocatoria.monto_individual is not None:
                monto = float(a.convocatoria.monto_individual)

            results.append({
                "numero_expediente": a.numero_expediente or "N/A",
                "postulante_anonimizado": anon,
                "convocatoria_titulo": a.convocatoria.titulo if a.convocatoria else "Beca Nacional",
                "departamento": dept_nombre,
                "monto_mensual": monto,
                "fecha_adjudicacion": a.fecha_actualizacion.strftime("%Y-%m-%d") if a.fecha_actualizacion else "2026-10-27",
                "resolucion_oficial": "RES-MINEDUC-2026-0042"
            })
        return results
