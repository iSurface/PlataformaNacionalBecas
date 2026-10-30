# -*- coding: utf-8 -*-
"""
Endpoints de la API: Reportes Operacionales Consolidados (PDF y Excel/CSV)
Sprint 5 - HU-029
"""
import io
import csv
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.middlewares.auth_guard import require_roles
from app.infrastructure.models.user import User
from app.infrastructure.models.application import Application
from app.infrastructure.models.scholarship import ScholarshipCall
from app.services.pdf_report_service import PdfReportService

router = APIRouter()

@router.get("/applications/consolidated-pdf", summary="HU-029: Exportar Reporte Consolidado de Postulantes en PDF")
def export_consolidated_pdf(
    convocatoria_id: Optional[UUID] = Query(None),
    estado: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "AUDITOR", "ADMIN_BECAS", "SYSADMIN", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    """
    HU-029: Permite a los administradores y auditores filtrar y exportar
    reportes operacionales de postulantes y sus estados en formato PDF.
    """
    query = db.query(Application)
    filtros = []
    if convocatoria_id:
        query = query.filter(Application.convocatoria_id == convocatoria_id)
        conv = db.query(ScholarshipCall).filter(ScholarshipCall.id == convocatoria_id).first()
        if conv:
            filtros.append(f"Convocatoria: {conv.titulo[:30]}")
    if estado:
        query = query.filter(Application.estado == estado)
        filtros.append(f"Estado: {estado}")

    apps = query.order_by(Application.fecha_creacion.desc()).all()
    filter_desc = " | ".join(filtros) if filtros else "Todos los expedientes registrados"

    pdf_bytes = PdfReportService.generate_consolidated_applicants_pdf(apps, filter_desc)
    filename = f"Reporte_Consolidado_Postulantes_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Type": "ConsolidadoPostulantes-HU029"
        }
    )

@router.get("/applications/consolidated-csv", summary="HU-029: Exportar Reporte Consolidado de Postulantes en Excel / CSV")
def export_consolidated_csv(
    convocatoria_id: Optional[UUID] = Query(None),
    estado: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["ADMIN_MINEDUC", "DIRECTOR", "AUDITOR", "ADMIN_BECAS", "SYSADMIN", "EVALUADOR"])),
    db: Session = Depends(get_db)
):
    """
    HU-029: Permite a los administradores y auditores exportar reportes operacionales
    tabulares compatibles con Microsoft Excel en formato CSV con codificación UTF-8 BOM.
    """
    query = db.query(Application)
    if convocatoria_id:
        query = query.filter(Application.convocatoria_id == convocatoria_id)
    if estado:
        query = query.filter(Application.estado == estado)

    apps = query.order_by(Application.fecha_creacion.desc()).all()

    output = io.StringIO()
    # UTF-8 BOM para apertura nativa e inmediata en Excel
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=",", quoting=csv.QUOTE_MINIMAL)

    # Encabezados de columnas
    writer.writerow([
        "No.",
        "Numero Expediente",
        "Nombre Completo Postulante",
        "CUI / Identificacion",
        "Correo Electronico",
        "Telefono",
        "Convocatoria de Beca",
        "Promedio Postulacion",
        "Monto Solicitado (Q)",
        "Estado Expediente",
        "Fecha de Formalizacion",
        "Dictamen de Comite",
        "Puntaje Comite"
    ])

    for i, app in enumerate(apps, 1):
        u = app.postulante
        p = u.persona if u else None
        p_nombre = p.nombre_completo if p else (u.email if u else "Postulante")
        cui = u.cui if u and u.cui else "-"
        email = u.email if u else "-"
        tel = p.telefono if p and p.telefono else "-"
        conv_tit = app.convocatoria.titulo if app.convocatoria else "General"
        f_envio = app.fecha_envio.strftime("%Y-%m-%d %H:%M") if app.fecha_envio else "-"

        writer.writerow([
            i,
            app.numero_expediente or "BORRADOR",
            p_nombre,
            cui,
            email,
            tel,
            conv_tit,
            f"{app.promedio_postulacion or 0.0:.2f}",
            f"{float(app.monto_solicitado or 0.0):.2f}",
            app.estado,
            f_envio,
            app.dictamen_comite or "PENDIENTE",
            f"{app.puntaje_ponderado_comite or 0.0:.2f}"
        ])

    csv_data = output.getvalue().encode("utf-8")
    filename = f"Consolidado_Postulantes_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Type": "ConsolidadoPostulantes-CSV-HU029"
        }
    )
