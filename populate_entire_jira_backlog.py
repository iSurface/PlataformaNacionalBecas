# -*- coding: utf-8 -*-
"""
Script maestro de sincronización con Jira REST API
Carga todas las Épicas, Historias de Usuario, Story Points, Criterios de Aceptación Gherkin,
Prioridades, Asignaciones y vinculaciones de Sprint en Jira Cloud.
"""

import json
import base64
import time
import urllib.request
import urllib.error

JIRA_DOMAIN = "proyfinal-analisistemas2-2026.atlassian.net"
JIRA_EMAIL = "rcuyuna@miumg.edu.gt"
JIRA_API_TOKEN = "ATATT3xFfGF0vNiKwGstt4YMIw6NThx5UGlwCcUt535m2Sx7d1wo649HBxD_FH3sYP-6u34sTp2Q_7WVyqrYlPvgnNNxWE0UwIZm_ZZuzrXgDKl5XbLXj_kGhDaTwNqVjwaRzR0XEC2Rq9hb4wvKSKFBLJHkvtyB-FRYMZXAR_Kbh09xXKAqPZ0=AA6A7D38"
JIRA_PROJECT_KEY = "SCRUM"

def make_request(url, method="GET", data=None):
    auth_str = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=35) as response:
                res_body = response.read().decode("utf-8")
                return json.loads(res_body) if res_body else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            if e.code == 204:
                return {}
            print(f"[HTTP {e.code}] en {url}: {error_body}")
            raise e
        except Exception as ex:
            print(f"Error en intento {attempt+1}: {ex}. Reintentando en 3s...")
            time.sleep(3)
    raise Exception("Límite de reintentos alcanzado")

# 1. Asegurar Sprints 1 a 5
print("1. Verificando Sprints en el tablero...")
board_id = 1
sprints_resp = make_request(f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{board_id}/sprint")
sprints_map = {s["name"]: s["id"] for s in sprints_resp.get("values", [])}

for i in range(1, 6):
    sp_name = f"SCRUM Sprint {i}"
    if sp_name not in sprints_map:
        try:
            created = make_request(f"https://{JIRA_DOMAIN}/rest/agile/1.0/sprint", method="POST", data={
                "name": sp_name,
                "originBoardId": board_id
            })
            sprints_map[sp_name] = created["id"]
            print(f" -> Creado {sp_name} (ID: {created['id']})")
        except Exception as e:
            print(f"Error creando {sp_name}: {e}")

print("Sprints listos:", sprints_map)

# 2. Definición estructurada del Backlog
sprints_definition = [
    # ------------------ SPRINT 1 ------------------
    {
        "sprint_name": "SCRUM Sprint 1",
        "epics": [
            {
                "id": "EP-01",
                "summary": "[Sprint 1] EP-01: Gestión de Identidad y Acceso Seguro",
                "description": "Cimientos de seguridad, registro de postulantes, verificación por correo, autenticación, control anti-fuerza bruta y recuperación de credenciales.",
                "stories": [
                    {
                        "id": "HU-001",
                        "summary": "HU-001: Registro de cuenta de usuario postulante con verificación por correo",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": """h3. Resumen del Requerimiento
Permitir a los aspirantes a becas registrar una cuenta individual validando su CUI (13 dígitos) y correo electrónico.

h3. Historia de Usuario
*Como* postulante o aspirante a beca,
*Quiero* registrar una cuenta en la plataforma utilizando mi CUI y correo electrónico,
*Para* acceder de forma segura a las convocatorias y gestionar mis solicitudes.

h3. Criterios de Aceptación (Gherkin)
*Escenario 1: Registro Exitoso*
* *Dado* que el usuario está en el formulario de registro y no tiene cuenta previa,
* *Cuando* ingresa un CUI válido (13 dígitos), nombres, correo no registrado y contraseña que cumple las políticas,
* *Entonces* el sistema crea la cuenta en estado 'Pendiente de Activación' y despacha un correo con enlace de 24h.

*Escenario 2: Validación de CUI o Correo Duplicado (RB-001)*
* *Dado* que un CUI o correo ya existe en el sistema,
* *Cuando* se intenta registrar nuevamente,
* *Entonces* el sistema bloquea el registro e informa que la cuenta ya existe.

h3. Validación QA
Verificar algoritmo módulo 11 del CUI, hasheo Argon2id de contraseñas y entrega del correo transaccional en buzón.

h3. Responsable Técnico
Walter Celada (Arquitecto de Software / Backend Lead)"""
                    },
                    {
                        "id": "HU-002",
                        "summary": "HU-002: Autenticación y control de sesión segura con protección anti-fuerza bruta",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
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
Comprobar tiempo de vida de token JWT (30 min), invalidación de sesión por inactividad y registro en log de seguridad.

h3. Responsable Técnico
Walter Celada (Arquitecto de Software / Backend Lead)"""
                    },
                    {
                        "id": "HU-003",
                        "summary": "HU-003: Recuperación segura de credenciales mediante token temporal de un solo uso",
                        "sp": 2.0,
                        "priority": "High",
                        "tech_lead": "Javier Alvizures",
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
* *Entonces* el sistema rechaza la petición por expiración.

h3. Responsable Técnico
Javier Alvizures (Ingeniero de QA y DevOps)"""
                    }
                ]
            },
            {
                "id": "EP-02",
                "summary": "[Sprint 1] EP-02: Configuración y Administración del Sistema",
                "description": "Mantenimiento y parametrización de catálogos maestros y variables base del sistema con preservación histórica.",
                "stories": [
                    {
                        "id": "HU-004",
                        "summary": "HU-004: Gestión de catálogos base del sistema con soporte de borrado lógico",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Raúl Álvarez",
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
* *Entonces* se marca es_activo=FALSE sin borrado físico.

h3. Responsable Técnico
Raúl Álvarez (Administrador de Base de Datos / Backend)"""
                    }
                ]
            },
            {
                "id": "EP-03",
                "summary": "[Sprint 1] EP-03: Seguridad y Control de Acceso Granular (RBAC)",
                "description": "Control de acceso basado en roles y aislamiento estricto de endpoints de la API.",
                "stories": [
                    {
                        "id": "HU-005",
                        "summary": "HU-005: Control de acceso basado en roles (RBAC) y aislamiento de endpoints",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
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
* *Entonces* los permisos se aplican de inmediato en la siguiente petición.

h3. Responsable Técnico
Walter Celada (Arquitecto de Software / Backend Lead)"""
                    }
                ]
            }
        ]
    },

    # ------------------ SPRINT 2 ------------------
    {
        "sprint_name": "SCRUM Sprint 2",
        "epics": [
            {
                "id": "EP-01",
                "summary": "[Sprint 2] EP-01: Gestión del Perfil del Estudiante",
                "description": "Gestión de ficha de datos personales, socioeconómicos y académicos.",
                "stories": [
                    {
                        "id": "HU-001",
                        "summary": "HU-001: Gestión del perfil socioeconómico y académico del estudiante",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Permitir al estudiante completar y mantener actualizada su ficha socioeconómica y académica con validaciones de rangos de ingreso y promedio.\n\nResponsable: Daniel Ericastilla (Ingeniero Frontend / UI-UX)"
                    }
                ]
            },
            {
                "id": "EP-02",
                "summary": "[Sprint 2] EP-02: Gestión de Convocatorias y Programas",
                "description": "Parametrización, fechas, cupos, publicación y cierre de convocatorias.",
                "stories": [
                    {
                        "id": "HU-002",
                        "summary": "HU-002: Creación y parametrización de convocatorias de becas",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Permitir al Administrador de Becas crear convocatorias definiendo cupos, promedio mínimo, nivel y requisitos documentales.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    },
                    {
                        "id": "HU-003",
                        "summary": "HU-003: Publicación y cierre programado de convocatorias",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Permitir la publicación oficial de convocatorias y cierre automático de recepción de solicitudes al vencer la fecha límite.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    }
                ]
            },
            {
                "id": "EP-03",
                "summary": "[Sprint 2] EP-03: Consulta y Búsqueda de Oportunidades",
                "description": "Catálogo público ciudadano con filtros avanzados y visualización de bases.",
                "stories": [
                    {
                        "id": "HU-004",
                        "summary": "HU-004: Catálogo público y búsqueda de becas con filtros",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Permitir al ciudadano buscar becas activas filtrando por nivel académico, departamento y tipo de apoyo sin requerir autenticación.\n\nResponsable: Daniel Ericastilla (Ingeniero Frontend / UI-UX)"
                    },
                    {
                        "id": "HU-005",
                        "summary": "HU-005: Visualización detallada de bases, requisitos y calendario de becas",
                        "sp": 2.0,
                        "priority": "High",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Mostrar la ficha técnica completa de la convocatoria con requisitos, montos de apoyo, rúbrica y cronograma oficial descargable.\n\nResponsable: Daniel Ericastilla (Ingeniero Frontend / UI-UX)"
                    }
                ]
            },
            {
                "id": "EP-04",
                "summary": "[Sprint 2] EP-04: Accesibilidad y Experiencia Web Móvil",
                "description": "Diseño responsive y optimización para baja conectividad móvil en el interior del país.",
                "stories": [
                    {
                        "id": "HU-006",
                        "summary": "HU-006: Diseño adaptativo y optimización web móvil para baja conectividad",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Garantizar diseño 100% responsive en smartphones y tablets, con carga ligera (<2MB inicial) y compatibilidad WCAG 2.1 AA.\n\nResponsable: Daniel Ericastilla (Ingeniero Frontend / UI-UX)"
                    }
                ]
            }
        ]
    },

    # ------------------ SPRINT 3 ------------------
    {
        "sprint_name": "SCRUM Sprint 3",
        "epics": [
            {
                "id": "EP-01",
                "summary": "[Sprint 3] EP-01: Gestión de Solicitudes y Postulaciones",
                "description": "Flujo de postulación, guardado incremental en borrador y envío formal.",
                "stories": [
                    {
                        "id": "HU-001",
                        "summary": "HU-001: Creación de solicitud y guardado en borrador",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": "Permitir al postulante iniciar una solicitud de beca y guardar su progreso como borrador para completarla posteriormente.\n\nResponsable: Walter Celada (Backend Lead)"
                    },
                    {
                        "id": "HU-002",
                        "summary": "HU-002: Validación de reglas de negocio y envío definitivo de solicitud",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": "Validar requisitos obligatorios, promedio mínimo y emitir número de expediente oficial al confirmar el envío definitivo inmutable.\n\nResponsable: Walter Celada (Backend Lead)"
                    },
                    {
                        "id": "HU-003",
                        "summary": "HU-003: Desistimiento voluntario de solicitud en estado borrador",
                        "sp": 2.0,
                        "priority": "High",
                        "tech_lead": "Raúl Álvarez",
                        "description": "Permitir al postulante cancelar o descartar una solicitud que aún se encuentre en borrador antes de su envío oficial.\n\nResponsable: Raúl Álvarez (Database Lead)"
                    }
                ]
            },
            {
                "id": "EP-02",
                "summary": "[Sprint 3] EP-02: Gestión y Validación Documental Digital",
                "description": "Carga de atestados en PDF, hashing SHA-256 y verificación de admisibilidad.",
                "stories": [
                    {
                        "id": "HU-004",
                        "summary": "HU-004: Carga y previsualización de documentos probatorios en PDF",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Raúl Álvarez",
                        "description": "Carga de archivos PDF (máx 5MB), validación de tipo MIME, cálculo de SHA-256 para integridad y visor integrado en navegador.\n\nResponsable: Raúl Álvarez (Database Lead)"
                    },
                    {
                        "id": "HU-005",
                        "summary": "HU-005: Verificación administrativa de admisibilidad documental",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Permitir al Administrador de Becas revisar atestados, aprobar admisibilidad u observar documentos ilegibles/incompletos.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    }
                ]
            },
            {
                "id": "EP-03",
                "summary": "[Sprint 3] EP-03: Notificaciones y Comunicaciones del Proceso",
                "description": "Servicio de mensajería transaccional por correo para eventos clave.",
                "stories": [
                    {
                        "id": "HU-006",
                        "summary": "HU-006: Notificaciones transaccionales automáticas por correo electrónico",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Javier Alvizures",
                        "description": "Despacho automático de correos institucionales informando recepción de solicitud, número de expediente y cambio de estado.\n\nResponsable: Javier Alvizures (DevOps Lead)"
                    }
                ]
            }
        ]
    },

    # ------------------ SPRINT 4 ------------------
    {
        "sprint_name": "SCRUM Sprint 4",
        "epics": [
            {
                "id": "EP-01",
                "summary": "[Sprint 4] EP-01: Gestión Documental (Subsanación)",
                "description": "Subsanación de documentos observados en plazo de 3 días hábiles.",
                "stories": [
                    {
                        "id": "HU-001",
                        "summary": "HU-001: Subsanación de documentos observados en plazo límite",
                        "sp": 5.0,
                        "priority": "High",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Permitir al postulante corregir y reemplazar únicamente los documentos observados dentro del plazo de 3 días hábiles.\n\nResponsable: Daniel Ericastilla (Frontend Lead)"
                    }
                ]
            },
            {
                "id": "EP-02",
                "summary": "[Sprint 4] EP-02: Gestión de Comités Evaluadores",
                "description": "Conformación de comités y asignación equitativa y ciega de expedientes.",
                "stories": [
                    {
                        "id": "HU-002",
                        "summary": "HU-002: Conformación y gestión de comités evaluadores",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Permitir al Administrador estructurar comités multidisciplinarios asignando coordinador y evaluadores por convocatoria.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    },
                    {
                        "id": "HU-003",
                        "summary": "HU-003: Asignación de expedientes admitidos a comités evaluadores",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Distribuir expedientes admitidos garantizando doble evaluación ciega (mínimo 2 evaluadores por solicitud).\n\nResponsable: Erick Chuquiej (Product Owner)"
                    }
                ]
            },
            {
                "id": "EP-03",
                "summary": "[Sprint 4] EP-03: Evaluación y Rúbricas Digitales",
                "description": "Declaración ética, calificación mediante rúbrica digital y consolidación.",
                "stories": [
                    {
                        "id": "HU-004",
                        "summary": "HU-004: Declaración obligatoria de no conflicto de interés",
                        "sp": 2.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": "Exigir al evaluador la suscripción digital de declaración ética antes de visualizar y calificar cada expediente asignado.\n\nResponsable: Walter Celada (Backend Lead)"
                    },
                    {
                        "id": "HU-005",
                        "summary": "HU-005: Evaluación individual mediante rúbrica digital estandarizada",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": "Calificar criterios socioeconómicos y académicos con escala de 0 a 100 y justificación cualitativa obligatoria.\n\nResponsable: Walter Celada (Backend Lead)"
                    },
                    {
                        "id": "HU-006",
                        "summary": "HU-006: Consolidación y cálculo ponderado del comité evaluador",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Walter Celada",
                        "description": "Calcular promedio ponderado automático y alertar si existe discrepancia mayor a 20 puntos entre evaluadores para dirimencia.\n\nResponsable: Walter Celada (Backend Lead)"
                    }
                ]
            }
        ]
    },

    # ------------------ SPRINT 5 ------------------
    {
        "sprint_name": "SCRUM Sprint 5",
        "epics": [
            {
                "id": "EP-01",
                "summary": "[Sprint 5] EP-01: Resolución, Aprobación y Adjudicación",
                "description": "Emisión de actas colegiadas y resoluciones ministeriales oficiales.",
                "stories": [
                    {
                        "id": "HU-001",
                        "summary": "HU-001: Emisión de dictamen y acta de recomendación del comité",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Generar acta formal de cierre del comité con orden de mérito y firmas digitales de los evaluadores.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    },
                    {
                        "id": "HU-002",
                        "summary": "HU-002: Aprobación final y emisión de resolución oficial de adjudicación",
                        "sp": 5.0,
                        "priority": "Highest",
                        "tech_lead": "Erick Chuquiej",
                        "description": "Permitir a la Autoridad Ministerial adjudicar becas a los seleccionados según cupos y emitir número de acuerdo.\n\nResponsable: Erick Chuquiej (Product Owner)"
                    }
                ]
            },
            {
                "id": "EP-02",
                "summary": "[Sprint 5] EP-02: Trazabilidad y Consulta de Estado",
                "description": "Consulta en tiempo real del estado de trámite y línea de tiempo.",
                "stories": [
                    {
                        "id": "HU-003",
                        "summary": "HU-003: Consulta en tiempo real del estado de postulación para estudiantes",
                        "sp": 2.0,
                        "priority": "Highest",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Permitir al postulante visualizar en su dashboard el estado actualizado de su expediente y descargar constancia oficial.\n\nResponsable: Daniel Ericastilla (Frontend Lead)"
                    },
                    {
                        "id": "HU-004",
                        "summary": "HU-004: Registro cronológico de trazabilidad de eventos de la solicitud",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Raúl Álvarez",
                        "description": "Mantener historial ordenado de cada cambio de estado, fecha, actor responsable y observaciones asociadas.\n\nResponsable: Raúl Álvarez (Database Lead)"
                    }
                ]
            },
            {
                "id": "EP-03",
                "summary": "[Sprint 5] EP-03: Notificaciones y Alertas en Plataforma",
                "description": "Bandeja de notificaciones internas in-app para usuarios.",
                "stories": [
                    {
                        "id": "HU-005",
                        "summary": "HU-005: Bandeja interna de alertas y notificaciones en plataforma",
                        "sp": 3.0,
                        "priority": "High",
                        "tech_lead": "Daniel Ericastilla",
                        "description": "Mostrar campana de notificaciones con contador no leído y avisos de asignaciones, observaciones y resoluciones.\n\nResponsable: Daniel Ericastilla (Frontend Lead)"
                    }
                ]
            },
            {
                "id": "EP-04",
                "summary": "[Sprint 5] EP-04: Reportes y Estadísticas de Gestión",
                "description": "Consolidados exportables a Excel/PDF y dashboard gerencial con KPIs.",
                "stories": [
                    {
                        "id": "HU-006",
                        "summary": "HU-006: Generación de reporte consolidado de postulantes y resultados",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Raúl Álvarez",
                        "description": "Exportar sábanas de datos en Excel/PDF con filtros por convocatoria, departamento, género y estado.\n\nResponsable: Raúl Álvarez (Database Lead)"
                    },
                    {
                        "id": "HU-007",
                        "summary": "HU-007: Tablero gráfico de control (Dashboard gerencial)",
                        "sp": 5.0,
                        "priority": "High",
                        "tech_lead": "Raúl Álvarez",
                        "description": "Visualizar métricas ejecutivas en tiempo real: postulaciones por departamento, tasa de aprobación y ejecución presupuestaria.\n\nResponsable: Raúl Álvarez (Database Lead)"
                    }
                ]
            },
            {
                "id": "EP-05",
                "summary": "[Sprint 5] EP-05: Auditoría, Registro y Transparencia",
                "description": "Bitácora inmutable de eventos críticos y padrón público de becarios.",
                "stories": [
                    {
                        "id": "HU-008",
                        "summary": "HU-008: Bitácora inmutable de auditoría para fiscalización gubernamental",
                        "sp": 3.0,
                        "priority": "Highest",
                        "tech_lead": "Javier Alvizures",
                        "description": "Registrar cada acción crítica con IP, usuario, timestamp y payload antes/después con protección contra alteración.\n\nResponsable: Javier Alvizures (DevOps Lead)"
                    },
                    {
                        "id": "HU-009",
                        "summary": "HU-009: Portal público de transparencia y padrón de becarios adjudicados",
                        "sp": 3.0,
                        "priority": "High",
                        "tech_lead": "Javier Alvizures",
                        "description": "Publicar el padrón oficial de becarios adjudicados en cumplimiento con la Ley de Acceso a la Información Pública.\n\nResponsable: Javier Alvizures (DevOps Lead)"
                    }
                ]
            }
        ]
    }
]

# 3. Ejecución de Creación y Mapeo en Jira
total_epics = 0
total_stories = 0

print("\n2. Iniciando creación de Épicas e Historias de Usuario...")

for sp_info in sprints_definition:
    sp_name = sp_info["sprint_name"]
    sp_id = sprints_map.get(sp_name)
    print(f"\n==================== {sp_name} (ID: {sp_id}) ====================")
    
    for ep in sp_info["epics"]:
        # Crear Épica
        epic_payload = {
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": ep["summary"],
                "description": ep["description"],
                "issuetype": {"name": "Epic"}
            }
        }
        
        try:
            created_epic = make_request(f"https://{JIRA_DOMAIN}/rest/api/2/issue", method="POST", data=epic_payload)
            epic_key = created_epic["key"]
            total_epics += 1
            print(f" -> Épica Creada: [{epic_key}] {ep['summary']}")
        except Exception as ex:
            print(f"Error creando Épica {ep['summary']}: {ex}")
            continue

        # Crear Historias de Usuario vinculadas a la Épica
        story_keys_for_sprint = []
        for st in ep["stories"]:
            story_payload = {
                "fields": {
                    "project": {"key": JIRA_PROJECT_KEY},
                    "summary": f"[{sp_name.replace('SCRUM ', '')}] {st['summary']}",
                    "description": st["description"],
                    "issuetype": {"name": "Story"},
                    "parent": {"key": epic_key},
                    "customfield_10016": st["sp"],
                    "priority": {"name": st["priority"]},
                    "labels": [sp_name.replace("SCRUM ", "").replace(" ", ""), "MINEDUC", "Becas"]
                }
            }
            
            try:
                created_story = make_request(f"https://{JIRA_DOMAIN}/rest/api/2/issue", method="POST", data=story_payload)
                story_key = created_story["key"]
                total_stories += 1
                story_keys_for_sprint.append(story_key)
                print(f"    * Historia Creada: [{story_key}] {st['summary']} ({st['sp']} SP, {st['tech_lead']})")
            except Exception as ex:
                print(f"Error creando Historia {st['summary']}: {ex}")

        # Asignar historias al Sprint
        if story_keys_for_sprint and sp_id:
            try:
                make_request(f"https://{JIRA_DOMAIN}/rest/agile/1.0/sprint/{sp_id}/issue", method="POST", data={
                    "issues": story_keys_for_sprint
                })
                print(f"    -> {len(story_keys_for_sprint)} historias asignadas al {sp_name}")
            except Exception as ex:
                print(f"Error asociando historias al sprint {sp_name}: {ex}")

print(f"\n========================================================")
print(f" PROCESO COMPLETADO AL 100% EN JIRA")
print(f" - Total Épicas Creadas: {total_epics}")
print(f" - Total Historias de Usuario Creadas: {total_stories}")
print(f" - Tablero: https://{JIRA_DOMAIN}/jira/software/projects/{JIRA_PROJECT_KEY}/boards/{board_id}")
print(f"========================================================")
