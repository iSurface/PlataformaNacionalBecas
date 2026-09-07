# -*- coding: utf-8 -*-
"""
Script para generar el archivo CSV oficial de importación para Jira
con todas las Épicas, Historias de Usuario (32), Story Points, Sprints,
Criterios de Aceptación (Gherkin), Prioridades MoSCoW, Responsables y Componentes.
"""

import csv
import os

output_csv = r"c:\Users\recab\OneDrive\Documentos\ProyectoFinalAnalisis\jira_backlog_import.csv"

# Definición de datos de las 32 historias y sus épicas
backlog_data = [
    # ==================== SPRINT 1 ====================
    {
        "issue_type": "Epic",
        "epic_name": "S1-EP01: Gestión de Identidad y Acceso",
        "summary": "[Sprint 1] EP-01: Gestión de Identidad y Acceso Seguro",
        "description": "Épica de cimientos para el registro, activación, autenticación y recuperación de credenciales en el sistema.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 1",
        "assignee": "Walter Celada",
        "component": "Seguridad e Identidad",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-001: Registro de cuenta de usuario postulante con verificación por correo",
        "description": """h3. Resumen del Requerimiento
Permitir a los estudiantes aspirantes a becas registrar una cuenta individual validando su CUI (13 dígitos) y correo electrónico.

h3. Historia de Usuario
*Como* postulante o aspirante a beca,
*Quiero* registrar una cuenta en la plataforma utilizando mi CUI y correo electrónico,
*Para* acceder de forma segura a las convocatorias y gestionar mis solicitudes.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Registro Exitoso*
* *Dado* que el usuario está en el formulario de registro y no tiene una cuenta previa,
* *Cuando* ingresa un CUI válido de 13 dígitos, nombres, correo no registrado y contraseña que cumple las políticas,
* *Entonces* el sistema crea la cuenta en estado 'Pendiente de Activación' y despacha un correo con enlace de 24h.

*Escenario 2: Validación de CUI o Correo Duplicado (RB-001)*
* *Dado* que un CUI o correo ya existe en el sistema,
* *Cuando* se intenta registrar nuevamente,
* *Entonces* el sistema bloquea el registro e informa que la cuenta ya existe.

h3. Validación QA
Verificar algoritmo módulo 11 del CUI, hasheo Argon2id de contraseñas y entrega del correo transaccional en buzón.

h3. Reglas de Negocio
* RB-001: Unicidad de cuenta por CUI.
* RB-002: Políticas de contraseñas y activación obligatoria.""",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 1",
        "assignee": "Walter Celada",
        "component": "Seguridad e Identidad",
        "epic_link": "S1-EP01: Gestión de Identidad y Acceso"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-002: Autenticación y control de sesión segura con protección anti-fuerza bruta",
        "description": """h3. Resumen del Requerimiento
Autenticar usuarios mediante CUI/correo y contraseña, bloqueando temporalmente accesos tras 5 intentos fallidos consecutivos.

h3. Historia de Usuario
*Como* usuario registrado,
*Quiero* iniciar sesión de manera segura con mis credenciales,
*Para* acceder a las funcionalidades correspondientes a mi rol.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Inicio de Sesión Exitoso*
* *Dado* un usuario activo con credenciales correctas,
* *Cuando* ingresa usuario y contraseña válidos,
* *Entonces* el sistema emite token JWT (30 min) y redirige al panel según rol.

*Escenario 2: Bloqueo Anti-Fuerza Bruta (RB-002)*
* *Dado* una cuenta activa,
* *Cuando* se registran 5 intentos fallidos consecutivos,
* *Entonces* la cuenta se bloquea temporalmente por 15 minutos.

h3. Validación QA
Comprobar tiempo de vida de token JWT (30 min), invalidación de sesión por inactividad y registro en log de seguridad.""",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 1",
        "assignee": "Walter Celada",
        "component": "Seguridad e Identidad",
        "epic_link": "S1-EP01: Gestión de Identidad y Acceso"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-003: Recuperación segura de credenciales mediante token temporal de un solo uso",
        "description": """h3. Resumen del Requerimiento
Permitir a los usuarios restablecer su contraseña olvidada mediante un enlace seguro temporal por correo (15 min).

h3. Historia de Usuario
*Como* usuario que ha olvidado su contraseña,
*Quiero* solicitar un enlace de restablecimiento seguro a mi correo,
*Para* recuperar el acceso a mi cuenta sin intervención administrativa.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Solicitud y Uso de Token Válido*
* *Dado* un usuario con correo registrado,
* *Cuando* solicita restablecer clave y abre el enlace antes de 15 minutos,
* *Entonces* puede definir una nueva clave que cumpla las políticas.

*Escenario 2: Token Expirado o Reutilizado*
* *Dado* un enlace con más de 15 minutos o ya usado,
* *Cuando* el usuario intenta utilizarlo,
* *Entonces* el sistema rechaza la petición por expiración.""",
        "priority": "High",
        "story_points": "2",
        "sprint": "Sprint 1",
        "assignee": "Javier Alvizures",
        "component": "Seguridad e Identidad",
        "epic_link": "S1-EP01: Gestión de Identidad y Acceso"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S1-EP02: Configuración y Administración del Sistema",
        "summary": "[Sprint 1] EP-02: Configuración y Administración del Sistema",
        "description": "Mantenimiento y parametrización de catálogos maestros y variables base del sistema.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 1",
        "assignee": "Raúl Álvarez",
        "component": "Configuración del Sistema",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-004: Gestión de catálogos base del sistema con soporte de borrado lógico",
        "description": """h3. Resumen del Requerimiento
Parametrizar catálogos maestros (departamentos, municipios, niveles educativos, tipos de beca) con preservación histórica.

h3. Historia de Usuario
*Como* Administrador Técnico (SysAdmin),
*Quiero* administrar los catálogos maestros de datos,
*Para* mantener actualizada la información base sin modificar código fuente.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Creación de Catálogo*
* *Dado* el SysAdmin autenticado,
* *Cuando* crea un nuevo elemento con código único,
* *Entonces* queda disponible inmediatamente en las listas desplegables.

*Escenario 2: Borrado Lógico (RB-025)*
* *Dado* un elemento referenciado históricamente,
* *Cuando* se deshabilita,
* *Entonces* se marca es_activo=FALSE sin borrado físico.""",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 1",
        "assignee": "Raúl Álvarez",
        "component": "Configuración del Sistema",
        "epic_link": "S1-EP02: Configuración y Administración del Sistema"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S1-EP03: Seguridad y Control de Acceso Granular",
        "summary": "[Sprint 1] EP-03: Seguridad y Control de Acceso Granular (RBAC)",
        "description": "Control de acceso basado en roles y aislamiento estricto de endpoints de la API.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 1",
        "assignee": "Walter Celada",
        "component": "Seguridad e Identidad",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-005: Control de acceso basado en roles (RBAC) y aislamiento de endpoints",
        "description": """h3. Resumen del Requerimiento
Asignar roles y proteger endpoints de la API mediante middleware de autorización con principio de menor privilegio.

h3. Historia de Usuario
*Como* Administrador del Sistema,
*Quiero* asignar roles y validar permisos en cada petición HTTP,
*Para* garantizar que los usuarios solo accedan a los recursos permitidos.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Acceso No Autorizado (RB-026)*
* *Dado* un usuario sin el rol requerido,
* *Cuando* intenta invocar un endpoint protegido,
* *Entonces* el sistema responde HTTP 403 Forbidden y registra en auditoría.

*Escenario 2: Asignación de Roles por SysAdmin*
* *Dado* el SysAdmin autenticado,
* *Cuando* asigna un rol a un usuario,
* *Entonces* los permisos se aplican de inmediato en la siguiente petición.""",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 1",
        "assignee": "Walter Celada",
        "component": "Seguridad e Identidad",
        "epic_link": "S1-EP03: Seguridad y Control de Acceso Granular"
    },

    # ==================== SPRINT 2 ====================
    {
        "issue_type": "Epic",
        "epic_name": "S2-EP01: Gestión del Perfil del Estudiante",
        "summary": "[Sprint 2] EP-01: Gestión del Perfil del Estudiante",
        "description": "Gestión de ficha de datos personales, socioeconómicos y académicos.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "Perfil Estudiante",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-001: Gestión del perfil socioeconómico y académico del estudiante",
        "description": "Permitir al estudiante completar y mantener actualizada su ficha socioeconómica y académica con validaciones de rangos de ingreso y promedio.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "Perfil Estudiante",
        "epic_link": "S2-EP01: Gestión del Perfil del Estudiante"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S2-EP02: Gestión de Convocatorias y Programas",
        "summary": "[Sprint 2] EP-02: Gestión de Convocatorias y Programas",
        "description": "Parametrización, fechas, cupos, publicación y cierre de convocatorias.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 2",
        "assignee": "Erick Chuquiej",
        "component": "Convocatorias",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-002: Creación y parametrización de convocatorias de becas",
        "description": "Permitir al Administrador de Becas crear convocatorias definiendo cupos, promedio mínimo, nivel y requisitos documentales.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 2",
        "assignee": "Erick Chuquiej",
        "component": "Convocatorias",
        "epic_link": "S2-EP02: Gestión de Convocatorias y Programas"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-003: Publicación y cierre programado de convocatorias",
        "description": "Permitir la publicación oficial de convocatorias y cierre automático de recepción de solicitudes al vencer la fecha límite.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 2",
        "assignee": "Erick Chuquiej",
        "component": "Convocatorias",
        "epic_link": "S2-EP02: Gestión de Convocatorias y Programas"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S2-EP03: Consulta y Búsqueda de Oportunidades",
        "summary": "[Sprint 2] EP-03: Consulta y Búsqueda de Oportunidades",
        "description": "Catálogo público ciudadano con filtros avanzados y visualización de bases.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "Catálogo Público",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-004: Catálogo público y búsqueda de becas con filtros",
        "description": "Permitir al ciudadano buscar becas activas filtrando por nivel académico, departamento y tipo de apoyo sin requerir autenticación.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "Catálogo Público",
        "epic_link": "S2-EP03: Consulta y Búsqueda de Oportunidades"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-005: Visualización detallada de bases, requisitos y calendario de becas",
        "description": "Mostrar la ficha técnica completa de la convocatoria con requisitos, montos de apoyo, rúbrica y cronograma oficial descargable.",
        "priority": "High",
        "story_points": "2",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "Catálogo Público",
        "epic_link": "S2-EP03: Consulta y Búsqueda de Oportunidades"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S2-EP04: Accesibilidad y Experiencia Web Móvil",
        "summary": "[Sprint 2] EP-04: Accesibilidad y Experiencia Web Móvil",
        "description": "Diseño responsive y optimización para baja conectividad móvil en el interior del país.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "UI / Frontend",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-006: Diseño adaptativo y optimización web móvil para baja conectividad",
        "description": "Garantizar diseño 100% responsive en smartphones y tablets, con carga ligera (<2MB inicial) y compatibilidad WCAG 2.1 AA.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 2",
        "assignee": "Daniel Ericastilla",
        "component": "UI / Frontend",
        "epic_link": "S2-EP04: Accesibilidad y Experiencia Web Móvil"
    },

    # ==================== SPRINT 3 ====================
    {
        "issue_type": "Epic",
        "epic_name": "S3-EP01: Gestión de Solicitudes y Postulaciones",
        "summary": "[Sprint 3] EP-01: Gestión de Solicitudes y Postulaciones",
        "description": "Flujo de postulación, guardado incremental en borrador y envío formal.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 3",
        "assignee": "Walter Celada",
        "component": "Postulaciones",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-001: Creación de solicitud y guardado en borrador",
        "description": "Permitir al postulante iniciar una solicitud de beca y guardar su progreso como borrador para completarla posteriormente.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 3",
        "assignee": "Walter Celada",
        "component": "Postulaciones",
        "epic_link": "S3-EP01: Gestión de Solicitudes y Postulaciones"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-002: Validación de reglas de negocio y envío definitivo de solicitud",
        "description": "Validar requisitos obligatorios, promedio mínimo y emitir número de expediente oficial al confirmar el envío definitivo inmutable.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 3",
        "assignee": "Walter Celada",
        "component": "Postulaciones",
        "epic_link": "S3-EP01: Gestión de Solicitudes y Postulaciones"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-003: Desistimiento voluntario de solicitud en estado borrador",
        "description": "Permitir al postulante cancelar o descartar una solicitud que aún se encuentre en borrador antes de su envío oficial.",
        "priority": "High",
        "story_points": "2",
        "sprint": "Sprint 3",
        "assignee": "Raúl Álvarez",
        "component": "Postulaciones",
        "epic_link": "S3-EP01: Gestión de Solicitudes y Postulaciones"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S3-EP02: Gestión y Validación Documental Digital",
        "summary": "[Sprint 3] EP-02: Gestión y Validación Documental Digital",
        "description": "Carga de atestados en PDF, hashing SHA-256 y verificación de admisibilidad.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 3",
        "assignee": "Raúl Álvarez",
        "component": "Documentación",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-004: Carga y previsualización de documentos probatorios en PDF",
        "description": "Carga de archivos PDF (máx 5MB), validación de tipo MIME, cálculo de SHA-256 para integridad y visor integrado en navegador.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 3",
        "assignee": "Raúl Álvarez",
        "component": "Documentación",
        "epic_link": "S3-EP02: Gestión y Validación Documental Digital"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-005: Verificación administrativa de admisibilidad documental",
        "description": "Permitir al Administrador de Becas revisar atestados, aprobar admisibilidad u observar documentos ilegibles/incompletos.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 3",
        "assignee": "Erick Chuquiej",
        "component": "Documentación",
        "epic_link": "S3-EP02: Gestión y Validación Documental Digital"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S3-EP03: Notificaciones y Comunicaciones del Proceso",
        "summary": "[Sprint 3] EP-03: Notificaciones y Comunicaciones del Proceso",
        "description": "Servicio de mensajería transaccional por correo para eventos clave.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 3",
        "assignee": "Javier Alvizures",
        "component": "Notificaciones",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-006: Notificaciones transaccionales automáticas por correo electrónico",
        "description": "Despacho automático de correos institucionales informando recepción de solicitud, número de expediente y cambio de estado.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 3",
        "assignee": "Javier Alvizures",
        "component": "Notificaciones",
        "epic_link": "S3-EP03: Notificaciones y Comunicaciones del Proceso"
    },

    # ==================== SPRINT 4 ====================
    {
        "issue_type": "Epic",
        "epic_name": "S4-EP01: Gestión Documental (Subsanación)",
        "summary": "[Sprint 4] EP-01: Gestión Documental (Subsanación)",
        "description": "Subsanación de documentos observados en plazo de 3 días hábiles.",
        "priority": "High",
        "story_points": "",
        "sprint": "Sprint 4",
        "assignee": "Daniel Ericastilla",
        "component": "Documentación",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-001: Subsanación de documentos observados en plazo límite",
        "description": "Permitir al postulante corregir y reemplazar únicamente los documentos observados dentro del plazo de 3 días hábiles.",
        "priority": "High",
        "story_points": "5",
        "sprint": "Sprint 4",
        "assignee": "Daniel Ericastilla",
        "component": "Documentación",
        "epic_link": "S4-EP01: Gestión Documental (Subsanación)"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S4-EP02: Gestión de Comités Evaluadores",
        "summary": "[Sprint 4] EP-02: Gestión de Comités Evaluadores",
        "description": "Conformación de comités y asignación equitativa y ciega de expedientes.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 4",
        "assignee": "Erick Chuquiej",
        "component": "Comités y Evaluaciones",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-002: Conformación y gestión de comités evaluadores",
        "description": "Permitir al Administrador estructurar comités multidisciplinarios asignando coordinador y evaluadores por convocatoria.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 4",
        "assignee": "Erick Chuquiej",
        "component": "Comités y Evaluaciones",
        "epic_link": "S4-EP02: Gestión de Comités Evaluadores"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-003: Asignación de expedientes admitidos a comités evaluadores",
        "description": "Distribuir expedientes admitidos garantizando doble evaluación ciega (mínimo 2 evaluadores por solicitud).",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 4",
        "assignee": "Erick Chuquiej",
        "component": "Comités y Evaluaciones",
        "epic_link": "S4-EP02: Gestión de Comités Evaluadores"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S4-EP03: Evaluación y Rúbricas Digitales",
        "summary": "[Sprint 4] EP-03: Evaluación y Rúbricas Digitales",
        "description": "Declaración ética, calificación mediante rúbrica digital y consolidación.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 4",
        "assignee": "Walter Celada",
        "component": "Comités y Evaluaciones",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-004: Declaración obligatoria de no conflicto de interés",
        "description": "Exigir al evaluador la suscripción digital de declaración ética antes de visualizar y calificar cada expediente asignado.",
        "priority": "Highest",
        "story_points": "2",
        "sprint": "Sprint 4",
        "assignee": "Walter Celada",
        "component": "Comités y Evaluaciones",
        "epic_link": "S4-EP03: Evaluación y Rúbricas Digitales"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-005: Evaluación individual mediante rúbrica digital estandarizada",
        "description": "Calificar criterios socioeconómicos y académicos con escala de 0 a 100 y justificación cualitativa obligatoria.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 4",
        "assignee": "Walter Celada",
        "component": "Comités y Evaluaciones",
        "epic_link": "S4-EP03: Evaluación y Rúbricas Digitales"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-006: Consolidación y cálculo ponderado del comité evaluador",
        "description": "Calcular promedio ponderado automático y alertar si existe discrepancia mayor a 20 puntos entre evaluadores para dirimencia.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 4",
        "assignee": "Walter Celada",
        "component": "Comités y Evaluaciones",
        "epic_link": "S4-EP03: Evaluación y Rúbricas Digitales"
    },

    # ==================== SPRINT 5 ====================
    {
        "issue_type": "Epic",
        "epic_name": "S5-EP01: Resolución, Aprobación y Adjudicación",
        "summary": "[Sprint 5] EP-01: Resolución, Aprobación y Adjudicación",
        "description": "Emisión de actas colegiadas y resoluciones ministeriales oficiales.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 5",
        "assignee": "Erick Chuquiej",
        "component": "Resolución y Adjudicación",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-001: Emisión de dictamen y acta de recomendación del comité",
        "description": "Generar acta formal de cierre del comité con orden de mérito y firmas digitales de los evaluadores.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Erick Chuquiej",
        "component": "Resolución y Adjudicación",
        "epic_link": "S5-EP01: Resolución, Aprobación y Adjudicación"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-002: Aprobación final y emisión de resolución oficial de adjudicación",
        "description": "Permitir a la Autoridad Ministerial adjudicar becas a los seleccionados según cupos y emitir número de acuerdo.",
        "priority": "Highest",
        "story_points": "5",
        "sprint": "Sprint 5",
        "assignee": "Erick Chuquiej",
        "component": "Resolución y Adjudicación",
        "epic_link": "S5-EP01: Resolución, Aprobación y Adjudicación"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S5-EP02: Trazabilidad y Consulta de Estado",
        "summary": "[Sprint 5] EP-02: Trazabilidad y Consulta de Estado",
        "description": "Consulta en tiempo real del estado de trámite y línea de tiempo.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 5",
        "assignee": "Daniel Ericastilla",
        "component": "Trazabilidad",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-003: Consulta en tiempo real del estado de postulación para estudiantes",
        "description": "Permitir al postulante visualizar en su dashboard el estado actualizado de su expediente y descargar constancia oficial.",
        "priority": "Highest",
        "story_points": "2",
        "sprint": "Sprint 5",
        "assignee": "Daniel Ericastilla",
        "component": "Trazabilidad",
        "epic_link": "S5-EP02: Trazabilidad y Consulta de Estado"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-004: Registro cronológico de trazabilidad de eventos de la solicitud",
        "description": "Mantener historial ordenado de cada cambio de estado, fecha, actor responsable y observaciones asociadas.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Raúl Álvarez",
        "component": "Trazabilidad",
        "epic_link": "S5-EP02: Trazabilidad y Consulta de Estado"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S5-EP03: Notificaciones y Alertas en Plataforma",
        "summary": "[Sprint 5] EP-03: Notificaciones y Alertas en Plataforma",
        "description": "Bandeja de notificaciones internas in-app para usuarios.",
        "priority": "High",
        "story_points": "",
        "sprint": "Sprint 5",
        "assignee": "Daniel Ericastilla",
        "component": "Notificaciones",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-005: Bandeja interna de alertas y notificaciones en plataforma",
        "description": "Mostrar campana de notificaciones con contador no leído y avisos de asignaciones, observaciones y resoluciones.",
        "priority": "High",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Daniel Ericastilla",
        "component": "Notificaciones",
        "epic_link": "S5-EP03: Notificaciones y Alertas en Plataforma"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S5-EP04: Reportes y Estadísticas de Gestión",
        "summary": "[Sprint 5] EP-04: Reportes y Estadísticas de Gestión",
        "description": "Consolidados exportables a Excel/PDF y dashboard gerencial con KPIs.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 5",
        "assignee": "Raúl Álvarez",
        "component": "Reportes y Estadísticas",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-006: Generación de reporte consolidado de postulantes y resultados",
        "description": "Exportar sábanas de datos en Excel/PDF con filtros por convocatoria, departamento, género y estado.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Raúl Álvarez",
        "component": "Reportes y Estadísticas",
        "epic_link": "S5-EP04: Reportes y Estadísticas de Gestión"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-007: Tablero gráfico de control (Dashboard gerencial)",
        "description": "Visualizar métricas ejecutivas en tiempo real: postulaciones por departamento, tasa de aprobación y ejecución presupuestaria.",
        "priority": "High",
        "story_points": "5",
        "sprint": "Sprint 5",
        "assignee": "Raúl Álvarez",
        "component": "Reportes y Estadísticas",
        "epic_link": "S5-EP04: Reportes y Estadísticas de Gestión"
    },
    {
        "issue_type": "Epic",
        "epic_name": "S5-EP05: Auditoría, Registro y Transparencia",
        "summary": "[Sprint 5] EP-05: Auditoría, Registro y Transparencia",
        "description": "Bitácora inmutable de eventos críticos y padrón público de becarios.",
        "priority": "Highest",
        "story_points": "",
        "sprint": "Sprint 5",
        "assignee": "Javier Alvizures",
        "component": "Auditoría y Transparencia",
        "epic_link": ""
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-008: Bitácora inmutable de auditoría para fiscalización gubernamental",
        "description": "Registrar cada acción crítica con IP, usuario, timestamp y payload antes/después con protección contra alteración.",
        "priority": "Highest",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Javier Alvizures",
        "component": "Auditoría y Transparencia",
        "epic_link": "S5-EP05: Auditoría, Registro y Transparencia"
    },
    {
        "issue_type": "Story",
        "epic_name": "",
        "summary": "HU-009: Portal público de transparencia y padrón de becarios adjudicados",
        "description": "Publicar el padrón oficial de becarios adjudicados en cumplimiento con la Ley de Acceso a la Información Pública.",
        "priority": "High",
        "story_points": "3",
        "sprint": "Sprint 5",
        "assignee": "Javier Alvizures",
        "component": "Auditoría y Transparencia",
        "epic_link": "S5-EP05: Auditoría, Registro y Transparencia"
    }
]

headers = [
    "Issue Type",
    "Epic Name",
    "Summary",
    "Description",
    "Priority",
    "Story Points",
    "Sprint",
    "Assignee",
    "Component",
    "Epic Link"
]

with open(output_csv, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)
    for row in backlog_data:
        writer.writerow([
            row["issue_type"],
            row["epic_name"],
            row["summary"],
            row["description"],
            row["priority"],
            row["story_points"],
            row["sprint"],
            row["assignee"],
            row["component"],
            row["epic_link"]
        ])

print(f"Archivo CSV de Jira generado exitosamente: {output_csv} ({len(backlog_data)} registros)")
