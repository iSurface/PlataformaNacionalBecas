# -*- coding: utf-8 -*-
"""
Generador del Documento de Visión Oficial (2 Páginas Exactas)
Plataforma Nacional para la Gestión Integral de Becas (MINEDUC)
"""
import os, subprocess, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\recab\OneDrive\Documentos\ProyectoFinalAnalisis\user stories and interviews"
pdf_file = os.path.join(base_dir, "Documento_de_Vision_Proyecto_Becas.pdf")
html_file = os.path.join(base_dir, "temp_html", "Documento_de_Vision.html")
os.makedirs(os.path.join(base_dir, "temp_html"), exist_ok=True)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

HTML_VISION = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  @page {
    size: letter portrait;
    margin: 10mm 12mm 10mm 12mm;
  }
  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 8.5pt;
    line-height: 1.26;
    color: #111;
    margin: 0;
    padding: 0;
  }
  .page {
    page-break-after: always;
    position: relative;
    height: 100%;
  }
  .page:last-child {
    page-break-after: avoid;
  }
  .header-scrum {
    text-align: center;
    margin-bottom: 6px;
  }
  .header-scrum .title-line1 {
    color: #002060;
    font-weight: bold;
    font-size: 8pt;
    letter-spacing: 0.3px;
  }
  .header-scrum .title-line2 {
    color: #2E75B6;
    font-weight: bold;
    font-size: 7.5pt;
  }
  .green-banner-main {
    background-color: #70AD47;
    color: white;
    font-weight: bold;
    font-size: 12pt;
    text-align: center;
    padding: 4px;
    border-radius: 2px;
    margin-top: 4px;
    margin-bottom: 6px;
    letter-spacing: 0.4px;
  }
  .sub-title-center {
    color: #002060;
    font-weight: bold;
    text-align: center;
    font-size: 9.5pt;
    margin-bottom: 5px;
  }
  .green-banner-sec {
    background-color: #70AD47;
    color: white;
    font-weight: bold;
    font-size: 8.8pt;
    text-align: left;
    padding: 2.5px 6px;
    border-radius: 2px;
    margin-top: 6px;
    margin-bottom: 4px;
  }
  table.form-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 5px;
  }
  table.form-table td, table.form-table th {
    border: 1px solid #BFBFBF;
    padding: 3.5px 6px;
    font-size: 8.2pt;
    vertical-align: middle;
  }
  table.form-table th.table-header-dark {
    background-color: #002060;
    color: white;
    font-weight: bold;
    text-align: left;
    font-size: 8.2pt;
  }
  .label-bold {
    font-weight: bold;
    width: 140px;
    background-color: #F8FAFC;
  }
  .box-content {
    border: 1px solid #BFBFBF;
    padding: 5px 8px;
    font-size: 8.2pt;
    line-height: 1.28;
    background-color: #FFFFFF;
    margin-bottom: 5px;
  }
  .highlight-vision {
    background-color: #EFF6FF;
    border-left: 3px solid #002060;
    padding: 5px 8px;
    font-size: 8.2pt;
    line-height: 1.28;
    margin-bottom: 5px;
  }
  ul {
    margin: 2px 0 2px 18px;
    padding: 0;
  }
  li {
    margin-bottom: 2px;
  }
</style>
</head>
<body>

<!-- PÁGINA 1 -->
<div class="page">
  <div class="header-scrum">
    <div class="title-line1">MINISTERIO DE EDUCACIÓN DE GUATEMALA (MINEDUC) &nbsp;|&nbsp; PROYECTO NACIONAL DE TRANSFORMACIÓN DIGITAL</div>
    <div class="title-line2">✦ DOCUMENTO DE VISIÓN, ALCANCE Y OBJETIVOS ESTRATÉGICOS (UML / SCRUM) ✦</div>
  </div>

  <div class="green-banner-main">DOCUMENTO DE VISIÓN DEL PRODUCTO</div>

  <table class="form-table">
    <tr>
      <td class="label-bold">Proyecto:</td>
      <td><b>Plataforma Nacional para la Gestión Integral de Becas</b></td>
      <td class="label-bold">Versión:</td>
      <td>1.0 Oficial (Cierre Sprints 1 a 6)</td>
    </tr>
    <tr>
      <td class="label-bold">Institución / Cliente:</td>
      <td>Ministerio de Educación (MINEDUC) / Dirección de Becas</td>
      <td class="label-bold">Ámbito:</td>
      <td>Nacional (22 Departamentos / 340 Municipios)</td>
    </tr>
    <tr>
      <td class="label-bold">Responsable Funcional:</td>
      <td>Erick Chuquiej (Product Owner)</td>
      <td class="label-bold">Equipo de Ingeniería:</td>
      <td>W. Celada, R. Álvarez, D. Ericastilla, J. Alvizures</td>
    </tr>
  </table>

  <div class="green-banner-sec">1. PROBLEMA PRINCIPAL Y OPORTUNIDAD DEL NEGOCIO</div>
  <div class="box-content">
    <b>Situación Previa (El Problema):</b> Históricamente, la gestión de becas del MINEDUC operaba mediante procesos 100% manuales basados en papel, exigiendo traslados presenciales de estudiantes de áreas rurales hacia cabeceras departamentales o la capital. Este modelo generaba: <b>(a)</b> Extrema lentitud administrativa con ciclos de dictamen superiores a 120 días; <b>(b)</b> Pérdida, deterioro y vulnerabilidad física de expedientes confidenciales; <b>(c)</b> Falta absoluta de trazabilidad ciudadana (el postulante desconocía el estado de su trámite); <b>(d)</b> Riesgo permanente de discrecionalidad y falta de estandarización en las calificaciones de comités evaluadores; y <b>(e)</b> Ausencia de una pista de auditoría inmutable para entes fiscalizadores (Contraloría General de Cuentas).<br>
    <b>Oportunidad de Transformación:</b> Centralizar, transparentar y blindar digitalmente todo el flujo de adjudicación mediante un monolito modular moderno en AWS, erradicando intermediarios y garantizando igualdad de oportunidades a nivel nacional.
  </div>

  <div class="green-banner-sec">2. PROPÓSITO GENERAL Y DECLARACIÓN DE VISIÓN (PRODUCT VISION STATEMENT)</div>
  <div class="highlight-vision">
    <b>Declaración Formal de Visión:</b><br>
    * <b>Para:</b> Los estudiantes guatemaltecos con mérito académico y necesidad socioeconómica, y las autoridades rectoras del MINEDUC,<br>
    * <b>Quienes:</b> Requieren un mecanismo ágil, confiable y transparente para solicitar, evaluar y adjudicar programas de asistencia educativa,<br>
    * <b>La Plataforma Nacional de Becas:</b> Es un sistema web integral, seguro y de alta disponibilidad desplegado en la nube de AWS,<br>
    * <b>Que:</b> Automatiza el ciclo de vida completo de la postulación: desde la publicación de convocatorias y validación de CUI (Módulo 11), hasta la evaluación colegiada paramétrica, control financiero de doble aprobación, notificación al estudiante y auditoría forense inmutable,<br>
    * <b>A diferencia de:</b> Los procesos burocráticos tradicionales en papel con ventanillas físicas dispersas y criterios discrecionales,<br>
    * <b>Nuestro Producto:</b> Garantiza transparencia total, integridad criptográfica (SHA-256), acceso universal responsive móvil y rendición de cuentas pública en tiempo real.
  </div>

  <div class="green-banner-sec">3. OBJETIVOS ESTRATÉGICOS, OPERATIVOS Y TÉCNICOS</div>
  <table class="form-table">
    <tr>
      <th class="table-header-dark" style="width: 25%;">Dimensión</th>
      <th class="table-header-dark">Metas y Objetivos Cuantificables del Proyecto</th>
    </tr>
    <tr>
      <td><b>Estratégicos e Institucionales</b></td>
      <td>
        • <b>Inclusión y Equidad:</b> Cobertura en los 22 departamentos, facilitando el acceso a jóvenes de escasos recursos sin viajar.<br>
        • <b>Despapelización Total:</b> Reducción del 100% de expedientes en papel y erradicación de costos de archivo físico.<br>
        • <b>Cero Tolerancia a la Corrupción:</b> Cumplimiento estricto del estándar de auditoría gubernamental y publicación en padrón.
      </td>
    </tr>
    <tr>
      <td><b>Operativos y de Negocio</b></td>
      <td>
        • <b>Reducción de Tiempos de Ciclo:</b> Disminuir el tiempo de tramitación de expedientes de 4 meses a menos de 20 días hábiles.<br>
        • <b>Evaluación Colegiada Estandarizada:</b> Rúbricas digitales objetivas con ponderación socioeconómica (40%) y académica (60%).<br>
        • <b>Control Financiero Jerárquico:</b> Regla de doble aprobación obligatoria para montos mayores a Q10,000.00.
      </td>
    </tr>
    <tr>
      <td><b>Técnicos y de Arquitectura</b></td>
      <td>
        • <b>Seguridad de Grado Gubernamental:</b> Autenticación con Argon2id, tokens JWT (30 min) y protección anti-fuerza bruta (5 intentos).<br>
        • <b>Alta Disponibilidad y Resiliencia:</b> Arquitectura contenerizada en AWS ECS Fargate y base relacional Amazon RDS PostgreSQL 16.<br>
        • <b>Integridad y Trazabilidad:</b> Hasheo SHA-256 en atestados PDF, notificaciones vía Amazon SES y bitácora de eventos inmutable.
      </td>
    </tr>
  </table>
</div>

<!-- PÁGINA 2 -->
<div class="page">
  <div class="header-scrum">
    <div class="title-line1">MINISTERIO DE EDUCACIÓN DE GUATEMALA (MINEDUC) &nbsp;|&nbsp; PROYECTO NACIONAL DE TRANSFORMACIÓN DIGITAL</div>
    <div class="title-line2">✦ DOCUMENTO DE VISIÓN, ALCANCE Y OBJETIVOS ESTRATÉGICOS (UML / SCRUM) ✦</div>
  </div>

  <div class="green-banner-sec" style="margin-top: 2px;">4. ALCANCE Y DESARROLLO DEL PRODUCTO A LO LARGO DE LOS SPRINTS</div>

  <table class="form-table">
    <tr>
      <th class="table-header-dark" style="width: 70px;">Sprint</th>
      <th class="table-header-dark" style="width: 170px;">Enfoque y Épicas</th>
      <th class="table-header-dark">Capacidades y Valor Entregado al Negocio</th>
      <th class="table-header-dark" style="width: 45px;">SP</th>
    </tr>
    <tr>
      <td><b>Sprint 1</b></td>
      <td><b>Identidad, RBAC y Catálogos</b><br>(EP-01 a EP-03)</td>
      <td>Cimientos de seguridad: Registro digital con validación de CUI (módulo 11), activación vía email, login con protección anti-fuerza bruta, control de acceso basado en roles (RBAC) y catálogos normalizados (geografía, niveles y tipos de beca).</td>
      <td style="text-align: center;">16</td>
    </tr>
    <tr>
      <td><b>Sprint 2</b></td>
      <td><b>Perfiles y Convocatorias</b><br>(EP-01 a EP-04)</td>
      <td>Gestión del perfil socioeconómico y académico del estudiante, parametrización de convocatorias con cupos y fechas de vigencia, motor de búsqueda público con filtros y diseño adaptativo base.</td>
      <td style="text-align: center;">21</td>
    </tr>
    <tr>
      <td><b>Sprint 3</b></td>
      <td><b>Postulaciones y Documentos</b><br>(EP-01 a EP-03)</td>
      <td>Ciclo de solicitud digital (borrador y envío definitivo), validación automática de reglas de elegibilidad, subida y previsualización de documentos PDF con integridad SHA-256 y despacho de notificaciones por Amazon SES.</td>
      <td style="text-align: center;">25</td>
    </tr>
    <tr>
      <td><b>Sprint 4</b></td>
      <td><b>Comités y Evaluación Colegiada</b><br>(EP-01 a EP-03)</td>
      <td>Subsanación documental en plazo improrrogable, conformación de comités evaluadores, asignación equitativa de expedientes, declaración jurada de no conflicto de interés y evaluación mediante rúbricas digitales ponderadas.</td>
      <td style="text-align: center;">25</td>
    </tr>
    <tr>
      <td><b>Sprint 5</b></td>
      <td><b>Resolución, Auditoría y Transparencia</b><br>(EP-01 a EP-05)</td>
      <td>Emisión de dictámenes, acuerdos ministeriales de adjudicación, seguimiento en línea para estudiantes, registro cronológico de estados, tablero gerencial de control, bitácora de auditoría inmutable y portal de transparencia ciudadana.</td>
      <td style="text-align: center;">30</td>
    </tr>
    <tr>
      <td><b>Sprint 6</b></td>
      <td><b>Reglas Financieras, Notificaciones y UX</b><br>(EP-01 a EP-04)</td>
      <td>Segunda aprobación obligatoria para montos &gt; Q10,000, notificaciones en tiempo real al estudiante por cambio de estado, bitácora forense de operaciones críticas (quién/cuándo/operación/resultado), recuperación de clave GUI, Disclaimer y responsividad móvil total.</td>
      <td style="text-align: center;">24</td>
    </tr>
    <tr>
      <td colspan="3" style="text-align: right; font-weight: bold; background-color: #F8FAFC;">TOTAL VELOCIDAD Y ESFUERZO ACUMULADO DEL SISTEMA:</td>
      <td style="text-align: center; font-weight: bold; background-color: #70AD47; color: white;">141 SP</td>
    </tr>
  </table>

  <div class="green-banner-sec">5. LÍMITES DEL SISTEMA Y ASPECTOS FUERA DE ALCANCE (OUT OF SCOPE)</div>
  <div class="box-content" style="padding: 4px 6px;">
    • <b>Dispersión Bancaria en Línea:</b> El sistema genera la nómina oficial foliada de beneficiarios y resoluciones legalizadas para su ejecución administrativa en la Tesorería Nacional; no efectúa transferencias interbancarias directas en este MVP.<br>
    • <b>Enlace síncrono web service RENAP:</b> La validación de identidad se garantiza algorítmicamente mediante el cálculo del dígito verificador estándar nacional (Módulo 11) sobre el CUI de 13 dígitos y cotejo documental en PDF.<br>
    • <b>Conectividad sin Internet (Offline Mode):</b> La plataforma requiere conectividad web estándar (móvil 3G/4G o WiFi) desde navegador moderno.
  </div>

  <div class="green-banner-sec">6. FACTORES CRÍTICOS DE ÉXITO Y GOBERNANZA</div>
  <table class="form-table" style="margin-bottom: 6px;">
    <tr>
      <td class="label-bold" style="width: 25%;"><b>Gobernanza y Probidad:</b></td>
      <td>Segregación absoluta de funciones: un postulante no evalúa, un evaluador no adjudica y la Autoridad Superior audita montos altos.</td>
    </tr>
    <tr>
      <td class="label-bold"><b>Inclusión Territorial:</b></td>
      <td>Diseño móvil optimizado que permite a estudiantes de cualquier departamento postularse directamente desde un celular inteligente.</td>
    </tr>
    <tr>
      <td class="label-bold"><b>Blindaje Jurídico:</b></td>
      <td>Garantía de no repudio mediante bitácora inmutable de auditoría forense apta para inspecciones de la Contraloría General de Cuentas.</td>
    </tr>
  </table>

  <div class="green-banner-sec" style="margin-top: 4px;">7. APROBACIÓN FORMAL DEL DOCUMENTO DE VISIÓN</div>
  <table class="form-table">
    <tr>
      <th class="table-header-dark" style="width: 75px;">Fecha</th>
      <th class="table-header-dark" style="width: 135px;">Nombre</th>
      <th class="table-header-dark" style="width: 185px;">Cargo / Rol en el Proyecto</th>
      <th class="table-header-dark">Firma Digital</th>
    </tr>
    <tr>
      <td>29/10/2026</td>
      <td>Erick Chuquiej</td>
      <td>Product Owner / Coordinador Funcional</td>
      <td><i>Aprobado digitalmente</i></td>
    </tr>
    <tr>
      <td>29/10/2026</td>
      <td>Walter Celada</td>
      <td>Arquitecto de Software / Backend Lead</td>
      <td><i>Aprobado digitalmente</i></td>
    </tr>
    <tr>
      <td>29/10/2026</td>
      <td>Raúl Álvarez</td>
      <td>Administrador de Base de Datos / DBA</td>
      <td><i>Aprobado digitalmente</i></td>
    </tr>
    <tr>
      <td>29/10/2026</td>
      <td>Daniel Ericastilla</td>
      <td>Ingeniero Frontend / UI-UX Lead</td>
      <td><i>Aprobado digitalmente</i></td>
    </tr>
    <tr>
      <td>29/10/2026</td>
      <td>Javier Alvizures</td>
      <td>Ingeniero de QA y DevOps Lead</td>
      <td><i>Aprobado digitalmente</i></td>
    </tr>
  </table>
</div>

</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(HTML_VISION)

print(f"Compilando Documento de Visión en PDF: {pdf_file}")

cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    f"--print-to-pdf={pdf_file}",
    html_file
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(pdf_file):
    size_kb = os.path.getsize(pdf_file) / 1024
    print(f"[OK] Generado exitosamente: {pdf_file} ({size_kb:.1f} KB)")
else:
    print(f"[ERROR] Generando PDF: {res.stderr}")
