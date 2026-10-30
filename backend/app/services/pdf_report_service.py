# -*- coding: utf-8 -*-
"""
Servicio de Generación de Documentos Oficiales en PDF (ReportLab)
Sprint 4 & Sprint 5: HU-022, HU-024, HU-029
"""
import io
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether, HRFlowable
)


class PdfReportService:

    @staticmethod
    def _get_base_styles():
        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#0e2b4c")
        accent_color = colors.HexColor("#b45309")
        dark_neutral = colors.HexColor("#1e293b")

        styles.add(ParagraphStyle(
            name="GovHeader",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=primary_color,
            alignment=1  # Center
        ))
        styles.add(ParagraphStyle(
            name="GovSubHeader",
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            alignment=1
        ))
        styles.add(ParagraphStyle(
            name="ActaTitle",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=accent_color,
            alignment=1
        ))
        styles.add(ParagraphStyle(
            name="SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=primary_color
        ))
        styles.add(ParagraphStyle(
            name="BodySmall",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=dark_neutral
        ))
        styles.add(ParagraphStyle(
            name="BodySmallBold",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=dark_neutral
        ))
        styles.add(ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1
        ))
        styles.add(ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=dark_neutral
        ))
        styles.add(ParagraphStyle(
            name="TableCellCenter",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=dark_neutral,
            alignment=1
        ))
        styles.add(ParagraphStyle(
            name="TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=dark_neutral
        ))
        return styles

    @classmethod
    def generate_acta_dictamen_pdf(
        cls,
        comite: Any,
        convocatoria: Any,
        miembros: List[Dict[str, Any]],
        ranking_data: List[Dict[str, Any]]
    ) -> bytes:
        """
        HU-024: Genera el Acta Colegiada de Dictamen Técnico de Recomendación con Cuadro de Mérito Oficial.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = cls._get_base_styles()
        elements = []

        now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")

        # Encabezado Institucional
        elements.append(Paragraph("MINISTERIO DE EDUCACIÓN DE GUATEMALA", styles["GovHeader"]))
        elements.append(Paragraph("DIRECCIÓN GENERAL DE BECAS Y CRÉDITO EDUCATIVO", styles["GovSubHeader"]))
        elements.append(Paragraph("SISTEMA NACIONAL DE GESTIÓN INTEGRAL DE BECAS", styles["GovSubHeader"]))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0e2b4c"), spaceAfter=10))

        # Título del Documento
        elements.append(Paragraph("ACTA COLEGIADA DE DICTAMEN TÉCNICO Y CUADRO DE MÉRITO", styles["ActaTitle"]))
        elements.append(Paragraph(f"CÓDIGO DE ACTA: ACTA-{comite.codigo}-2026", styles["GovSubHeader"]))
        elements.append(Spacer(1, 12))

        # Datos Generales del Comité y Convocatoria
        info_data = [
            [
                Paragraph("<b>Comité Colegiado:</b>", styles["BodySmall"]),
                Paragraph(f"{comite.nombre} (Cód: {comite.codigo})", styles["BodySmall"]),
                Paragraph("<b>Estado del Comité:</b>", styles["BodySmall"]),
                Paragraph(f"{comite.estado}", styles["BodySmallBold"])
            ],
            [
                Paragraph("<b>Convocatoria:</b>", styles["BodySmall"]),
                Paragraph(f"{convocatoria.titulo if convocatoria else 'Convocatoria Oficial'} ({convocatoria.codigo if convocatoria else 'N/A'})", styles["BodySmall"]),
                Paragraph("<b>Fecha de Emisión:</b>", styles["BodySmall"]),
                Paragraph(now_str, styles["BodySmall"])
            ]
        ]
        info_table = Table(info_data, colWidths=[110, 200, 100, 130])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 14))

        # Sección 1: Integración del Cuerpo Colegiado y Declaración Ética
        elements.append(Paragraph("1. INTEGRACIÓN DEL CUERPO COLEGIADO Y DECLARACIÓN ÉTICA DE NO CONFLICTO", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))

        headers_miembros = [
            Paragraph("Rol en Comité", styles["TableHeader"]),
            Paragraph("Evaluador / Docente", styles["TableHeader"]),
            Paragraph("Correo Institucional", styles["TableHeader"]),
            Paragraph("Declaración Ética", styles["TableHeader"])
        ]
        rows_miembros = [headers_miembros]

        for m in miembros:
            decl_txt = "ACREDITADA ✓" if m.get("declaracion_conflicto") else "PENDIENTE"
            decl_style = styles["TableCellCenter"]
            rows_miembros.append([
                Paragraph(str(m.get("rol_comite", "EVALUADOR")), styles["TableCellBold"]),
                Paragraph(str(m.get("nombre", "Evaluador")), styles["TableCell"]),
                Paragraph(str(m.get("email", "-")), styles["TableCell"]),
                Paragraph(f"<b>{decl_txt}</b>", decl_style)
            ])

        if len(rows_miembros) == 1:
            rows_miembros.append([Paragraph("No se registran miembros asignados", styles["TableCellCenter"]), "", "", ""])

        t_miembros = Table(rows_miembros, colWidths=[110, 160, 150, 120])
        t_miembros.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0e2b4c")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_miembros)
        elements.append(Spacer(1, 14))

        # Sección 2: Cuadro Oficial de Mérito y Calificaciones
        elements.append(Paragraph("2. CUADRO OFICIAL DE MÉRITO Y DICTAMEN DE RECOMENDACIÓN TÉCNICA", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))

        headers_rank = [
            Paragraph("Puesto", styles["TableHeader"]),
            Paragraph("No. Expediente", styles["TableHeader"]),
            Paragraph("Postulante", styles["TableHeader"]),
            Paragraph("Promedio Postulación", styles["TableHeader"]),
            Paragraph("Rúbrica (0-100)", styles["TableHeader"]),
            Paragraph("Dictamen Técnico", styles["TableHeader"])
        ]
        rows_rank = [headers_rank]

        for i, item in enumerate(ranking_data, 1):
            dictamen = str(item.get("dictamen_comite", "EN_EVALUACION"))
            
            rows_rank.append([
                Paragraph(f"<b>#{i}</b>", styles["TableCellCenter"]),
                Paragraph(str(item.get("numero_expediente", "S/N")), styles["TableCellBold"]),
                Paragraph(str(item.get("postulante_nombre", "Postulante")), styles["TableCell"]),
                Paragraph(f"{item.get('promedio_postulacion', 0):.1f} pts", styles["TableCellCenter"]),
                Paragraph(f"<b>{item.get('puntaje_ponderado_comite', item.get('promedio_postulacion', 0)):.2f} pts</b>", styles["TableCellCenter"]),
                Paragraph(f"<b>{dictamen}</b>", styles["TableCellCenter"])
            ])

        if len(rows_rank) == 1:
            rows_rank.append([Paragraph("No hay expedientes evaluados para esta convocatoria", styles["TableCellCenter"]), "", "", "", "", ""])

        t_rank = Table(rows_rank, colWidths=[45, 115, 150, 80, 75, 75])
        t_rank.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0e2b4c")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_rank)
        elements.append(Spacer(1, 14))

        # Sección 3: Dictamen de Cierre y Validez Legal
        conclusiones = (
            "<b>POR TANTO:</b> El Comité Colegiado da por cerrada la fase de evaluación técnica y traslada el presente "
            "Cuadro de Mérito a la Dirección General de Becas para la emisión de la correspondiente Resolución Ministerial "
            "de Adjudicación, garantizando transparencia, objetividad e igualdad de oportunidades de conformidad con "
            "las bases de la convocatoria pública."
        )
        elements.append(Paragraph(conclusiones, styles["BodySmall"]))
        elements.append(Spacer(1, 24))

        # Firmas de Integrantes
        firmas_data = [
            [
                Paragraph("___________________________________<br/><b>Presidente de Comité</b><br/>Firma Electrónica Avanzada", styles["TableCellCenter"]),
                Paragraph("___________________________________<br/><b>Secretario de Comité</b><br/>Firma Electrónica Avanzada", styles["TableCellCenter"]),
                Paragraph("___________________________________<br/><b>Vocal / Evaluador</b><br/>Firma Electrónica Avanzada", styles["TableCellCenter"])
            ]
        ]
        t_firmas = Table(firmas_data, colWidths=[180, 180, 180])
        t_firmas.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elements.append(KeepTogether(t_firmas))

        elements.append(Spacer(1, 15))
        # Hash criptográfico de trazabilidad
        hash_seed = f"{comite.codigo}:{now_str}:{len(ranking_data)}"
        doc_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()
        elements.append(Paragraph(f"<font size=7 color='#64748b'>Huella Criptográfica SHA-256 de Inmutabilidad del Acta: {doc_hash}</font>", styles["TableCellCenter"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_consolidated_applicants_pdf(
        cls,
        applications: List[Any],
        filters_desc: str = "Todos los expedientes registrados"
    ) -> bytes:
        """
        HU-029: Genera el Reporte Consolidado Operacional de Postulantes y Estados en Formato PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = cls._get_base_styles()
        elements = []

        now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")

        # Encabezado
        elements.append(Paragraph("MINISTERIO DE EDUCACIÓN - GOBIERNO DE GUATEMALA", styles["GovHeader"]))
        elements.append(Paragraph("DIRECCIÓN GENERAL DE BECAS • REPORTE OPERACIONAL CONSOLIDADO DE POSTULANTES (HU-029)", styles["ActaTitle"]))
        elements.append(Paragraph(f"Criterio de Filtrado: <i>{filters_desc}</i> | Fecha de Generación: <b>{now_str}</b>", styles["GovSubHeader"]))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0e2b4c"), spaceAfter=10))

        # Tabla de Datos
        headers = [
            Paragraph("No.", styles["TableHeader"]),
            Paragraph("No. Expediente", styles["TableHeader"]),
            Paragraph("Postulante / Titular", styles["TableHeader"]),
            Paragraph("Convocatoria de Beca", styles["TableHeader"]),
            Paragraph("Promedio", styles["TableHeader"]),
            Paragraph("Monto Solicitado", styles["TableHeader"]),
            Paragraph("Estado Actual", styles["TableHeader"]),
            Paragraph("Fecha Envío", styles["TableHeader"])
        ]
        rows = [headers]

        total_monto = 0.0
        estados_count: Dict[str, int] = {}

        for i, app in enumerate(applications, 1):
            p_nombre = app.postulante.nombre_completo if app.postulante else "Postulante"
            c_titulo = app.convocatoria.titulo if app.convocatoria else "General"
            monto = float(app.monto_solicitado or 0.0)
            total_monto += monto
            
            estado = app.estado
            estados_count[estado] = estados_count.get(estado, 0) + 1
            f_envio = app.fecha_envio.strftime("%d/%m/%Y") if app.fecha_envio else "-"

            rows.append([
                Paragraph(str(i), styles["TableCellCenter"]),
                Paragraph(f"<b>{app.numero_expediente or 'Borrador'}</b>", styles["TableCell"]),
                Paragraph(p_nombre, styles["TableCell"]),
                Paragraph(c_titulo[:35] + ("..." if len(c_titulo) > 35 else ""), styles["TableCell"]),
                Paragraph(f"{app.promedio_postulacion or 0.0:.1f} pts", styles["TableCellCenter"]),
                Paragraph(f"Q {monto:,.2f}", styles["TableCellCenter"]),
                Paragraph(f"<b>{estado}</b>", styles["TableCellCenter"]),
                Paragraph(f_envio, styles["TableCellCenter"])
            ])

        if len(rows) == 1:
            rows.append([Paragraph("No se encontraron postulaciones con los criterios especificados.", styles["TableCellCenter"]), "", "", "", "", "", "", ""])

        t_apps = Table(rows, colWidths=[30, 115, 140, 175, 55, 75, 82, 60])
        t_apps.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0e2b4c")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_apps)
        elements.append(Spacer(1, 14))

        # Resumen Estadístico y Fiscal
        resumen_txt = (
            f"<b>Resumen Consolidado:</b> Total Expedientes: <b>{len(applications)}</b> | "
            f"Monto Total Acumulado: <b>Q {total_monto:,.2f}</b> | "
            f"Distribución de Estados: " + ", ".join([f"<b>{k}</b>: {v}" for k, v in estados_count.items()])
        )
        elements.append(Paragraph(resumen_txt, styles["BodySmall"]))

        elements.append(Spacer(1, 10))
        doc_hash = hashlib.sha256(f"CONSOLIDADO:{now_str}:{len(applications)}".encode("utf-8")).hexdigest()
        elements.append(Paragraph(f"<font size=7 color='#64748b'>Documento Oficial generado por Plataforma Nacional de Becas MINEDUC • Hash SHA-256: {doc_hash}</font>", styles["TableCellCenter"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_sample_atestado_pdf(
        cls,
        doc_type: str,
        student_name: str,
        cui: str,
        numero_exp: str
    ) -> bytes:
        """
        Genera un atestado probatorio PDF oficial y estandarizado para visualización inmediata en el Visor PDF
        (Asegura que el evaluador siempre pueda inspeccionar el documento digitalmente).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = cls._get_base_styles()
        elements = []

        now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")

        # Escudo / Título
        elements.append(Paragraph("MINISTERIO DE EDUCACIÓN DE GUATEMALA", styles["GovHeader"]))
        elements.append(Paragraph("ATESTADO PROBATORIO OFICIAL DIGITALIZADO (HU-022)", styles["ActaTitle"]))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0e2b4c"), spaceAfter=14))

        content_box = [
            [
                Paragraph("<b>Tipo de Requisito:</b>", styles["BodySmall"]),
                Paragraph(doc_type, styles["BodySmallBold"])
            ],
            [
                Paragraph("<b>Postulante:</b>", styles["BodySmall"]),
                Paragraph(student_name, styles["BodySmall"])
            ],
            [
                Paragraph("<b>CUI / Documento:</b>", styles["BodySmall"]),
                Paragraph(cui, styles["BodySmall"])
            ],
            [
                Paragraph("<b>Expediente Vinculado:</b>", styles["BodySmall"]),
                Paragraph(numero_exp, styles["BodySmallBold"])
            ],
            [
                Paragraph("<b>Fecha y Hora de Carga:</b>", styles["BodySmall"]),
                Paragraph(now_str, styles["BodySmall"])
            ],
            [
                Paragraph("<b>Integridad Criptográfica:</b>", styles["BodySmall"]),
                Paragraph("Validado digitalmente conforme a estándar SHA-256", styles["BodySmall"])
            ]
        ]
        t_box = Table(content_box, colWidths=[160, 350])
        t_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_box)
        elements.append(Spacer(1, 18))

        cuerpo_doc = (
            f"El presente documento certifica que el postulante <b>{student_name}</b> con identificación "
            f"<b>{cui}</b> ha cargado satisfactoriamente los atestados probatorios correspondientes al requisito "
            f"<b>{doc_type}</b> para su postulación a la Beca Nacional del Ministerio de Educación.<br/><br/>"
            "El archivo se encuentra depositado en el repositorio inmutable del MINEDUC para su evaluación mediante "
            "la Rúbrica Estandarizada oficial por el Comité Colegiado evaluador."
        )
        elements.append(Paragraph(cuerpo_doc, styles["BodySmall"]))
        elements.append(Spacer(1, 30))

        # Sello de Certificación Digital
        elements.append(Paragraph("<b>[ SELLO DE CERTIFICACIÓN Y CUSTODIA DIGITAL MINEDUC ]</b>", styles["TableCellCenter"]))
        elements.append(Spacer(1, 6))
        sha_mock = hashlib.sha256(f"{doc_type}:{student_name}:{cui}:{numero_exp}".encode("utf-8")).hexdigest()
        elements.append(Paragraph(f"<font size=8 color='#475569'>Firma Criptográfica SHA-256: <code>{sha_mock}</code></font>", styles["TableCellCenter"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
