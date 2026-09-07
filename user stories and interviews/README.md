# REPOSITORIO DE REQUERIMIENTOS, MINUTAS E HISTORIAS DE USUARIO SCRUM (100% PDF)
**Proyecto:** Plataforma Nacional para la Gestión Integral de Becas  
**Cliente:** Ministerio de Educación de Guatemala (MINEDUC)  
**Marco Metodológico:** Scrum | Fase de Levantamiento y Descubrimiento  

### 👥 Equipo Consultor de Proyecto:
1. **Erick Chuquiej** — *Product Owner / Responsable Funcional*
2. **Walter Celada** — *Arquitecto de Software / Backend Lead*
3. **Raúl Álvarez** — *Administrador de Base de Datos / Backend*
4. **Daniel Ericastilla** — *Ingeniero Frontend / UI-UX Lead*
5. **Javier Alvizures** — *Ingeniero de QA y DevOps Lead*

---

## 📁 ESTRUCTURA DE DIRECTORIOS POR SPRINT

```
user stories and interviews/
├── README.md                                  # Catálogo maestro de artefactos
├── Entrevistas/                               # 4 Minutas de Entrevista Oficiales en PDF (IT SOLUTIONS v1.0)
│   ├── Minuta_Entrevista_001_Direccion_Becas.pdf
│   ├── Minuta_Entrevista_002_Comite_Evaluador.pdf
│   ├── Minuta_Entrevista_003_Postulante_Estudiantil.pdf
│   └── Minuta_Entrevista_004_Auditoria_Gubernamental.pdf
├── Sprint 1/                                  # 5 Historias de Usuario en PDF (Épicas EP-01 a EP-03)
│   ├── HU-001_Registro_Cuenta_Postulante.pdf
│   ├── HU-002_Autenticacion_Sesion_Segura.pdf
│   ├── HU-003_Recuperacion_Segura_Credenciales.pdf
│   ├── HU-004_Gestion_Catalogos_Base_Sistema.pdf
│   └── HU-005_Control_Acceso_RBAC_Aislamiento.pdf
├── Sprint 2/                                  # 6 Historias de Usuario en PDF (Épicas EP-01 a EP-04)
│   ├── HU-001_Gestion_Perfil_Socioeconomico_Academico.pdf
│   ├── HU-002_Creacion_Parametrizacion_Convocatorias.pdf
│   ├── HU-003_Publicacion_Cierre_Convocatorias.pdf
│   ├── HU-004_Catalogo_Publico_Busqueda_Becas.pdf
│   ├── HU-005_Visualizacion_Detalle_Bases_Requisitos.pdf
│   └── HU-006_Diseno_Adaptativo_Optimizacion_Web.pdf
├── Sprint 3/                                  # 6 Historias de Usuario en PDF (Épicas EP-01 a EP-03)
│   ├── HU-001_Creacion_Solicitud_Guardado_Borrador.pdf
│   ├── HU-002_Validacion_Reglas_Envio_Definitivo.pdf
│   ├── HU-003_Desistimiento_Voluntario_Borrador.pdf
│   ├── HU-004_Carga_Previsualizacion_Documentos_PDF.pdf
│   ├── HU-005_Verificacion_Administrativa_Admisibilidad.pdf
│   └── HU-006_Notificaciones_Transaccionales_Email.pdf
├── Sprint 4/                                  # 6 Historias de Usuario en PDF (Épicas EP-01 a EP-03)
│   ├── HU-001_Subsanacion_Documentos_Observados.pdf
│   ├── HU-002_Conformacion_Comites_Evaluadores.pdf
│   ├── HU-003_Asignacion_Expedientes_Comites.pdf
│   ├── HU-004_Declaracion_No_Conflicto_Interes.pdf
│   ├── HU-005_Evaluacion_Individual_Rubrica_Digital.pdf
│   └── HU-006_Consolidacion_Calculo_Ponderado_Comite.pdf
└── Sprint 5/                                  # 9 Historias de Usuario en PDF (Épicas EP-01 a EP-05)
    ├── HU-001_Emision_Dictamen_Acta_Recomendacion.pdf
    ├── HU-002_Aprobacion_Final_Resolucion_Adjudicacion.pdf
    ├── HU-003_Consulta_Estado_Tiempo_Real_Estudiante.pdf
    ├── HU-004_Registro_Cronologico_Trazabilidad_Eventos.pdf
    ├── HU-005_Bandeja_Interna_Alertas_Notificaciones.pdf
    ├── HU-006_Generacion_Reporte_Consolidado_Postulantes.pdf
    ├── HU-007_Tablero_Grafico_Dashboard_Gerencial.pdf
    ├── HU-008_Bitacora_Inmutable_Auditoria.pdf
    └── HU-009_Portal_Transparencia_Padron_Becarios.pdf
```

---

## 📑 MINUTAS DE ENTREVISTAS (PDF)
* [Minuta 001 - Dirección Nacional de Becas (MINEDUC)](Entrevistas/Minuta_Entrevista_001_Direccion_Becas.pdf)
* [Minuta 002 - Presidente de Comité Evaluador Académico](Entrevistas/Minuta_Entrevista_002_Comite_Evaluador.pdf)
* [Minuta 003 - Representante Estudiantil Departamental](Entrevistas/Minuta_Entrevista_003_Postulante_Estudiantil.pdf)
* [Minuta 004 - Auditor Interno de Control Gubernamental](Entrevistas/Minuta_Entrevista_004_Auditoria_Gubernamental.pdf)

---

## 📋 CATÁLOGO MAESTRO POR SPRINT (CON REINICIO DE ÉPICAS)

### 🔹 SPRINT 1: Cimientos de Seguridad, RBAC y Catálogos Maestros (16 SP)
| ID Historia | Épica del Sprint | Título Resumido | Prioridad | SP | Documento PDF Oficial |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `HU-001` | `EP-01: Gestión de Identidad y Acceso` | Registro de cuenta de usuario postulante | **Must** | 3 | [Sprint 1 / HU-001.pdf](Sprint%201/HU-001_Registro_Cuenta_Postulante.pdf) |
| `HU-002` | `EP-01: Gestión de Identidad y Acceso` | Autenticación y control de sesión segura | **Must** | 3 | [Sprint 1 / HU-002.pdf](Sprint%201/HU-002_Autenticacion_Sesion_Segura.pdf) |
| `HU-003` | `EP-01: Gestión de Identidad y Acceso` | Recuperación segura de credenciales | **Should** | 2 | [Sprint 1 / HU-003.pdf](Sprint%201/HU-003_Recuperacion_Segura_Credenciales.pdf) |
| `HU-004` | `EP-02: Configuración y Administración del Sistema` | Gestión de catálogos base del sistema | **Must** | 3 | [Sprint 1 / HU-004.pdf](Sprint%201/HU-004_Gestion_Catalogos_Base_Sistema.pdf) |
| `HU-005` | `EP-03: Seguridad y Control de Acceso Granular` | Control de acceso basado en roles (RBAC) | **Must** | 5 | [Sprint 1 / HU-005.pdf](Sprint%201/HU-005_Control_Acceso_RBAC_Aislamiento.pdf) |

### 🔹 SPRINT 2: Perfiles, Convocatorias y Catálogo Ciudadano (21 SP)
| ID Historia | Épica del Sprint | Título Resumido | Prioridad | SP | Documento PDF Oficial |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `HU-001` | `EP-01: Gestión del Perfil del Estudiante` | Gestión del perfil socioeconómico y académico | **Must** | 5 | [Sprint 2 / HU-001.pdf](Sprint%202/HU-001_Gestion_Perfil_Socioeconomico_Academico.pdf) |
| `HU-002` | `EP-02: Gestión de Convocatorias y Programas` | Creación y parametrización de convocatorias | **Must** | 5 | [Sprint 2 / HU-002.pdf](Sprint%202/HU-002_Creacion_Parametrizacion_Convocatorias.pdf) |
| `HU-003` | `EP-02: Gestión de Convocatorias y Programas` | Publicación y cierre programado de convocatorias | **Must** | 3 | [Sprint 2 / HU-003.pdf](Sprint%202/HU-003_Publicacion_Cierre_Convocatorias.pdf) |
| `HU-004` | `EP-03: Consulta y Búsqueda de Oportunidades` | Catálogo público y búsqueda con filtros | **Must** | 3 | [Sprint 2 / HU-004.pdf](Sprint%202/HU-004_Catalogo_Publico_Busqueda_Becas.pdf) |
| `HU-005` | `EP-03: Consulta y Búsqueda de Oportunidades` | Visualización de bases y requisitos | **Must** | 2 | [Sprint 2 / HU-005.pdf](Sprint%202/HU-005_Visualizacion_Detalle_Bases_Requisitos.pdf) |
| `HU-006` | `EP-04: Accesibilidad y Experiencia Web Móvil` | Diseño adaptativo y optimización web móvil | **Must** | 3 | [Sprint 2 / HU-006.pdf](Sprint%202/HU-006_Diseno_Adaptativo_Optimizacion_Web.pdf) |

### 🔹 SPRINT 3: Postulaciones, Documentos y Verificación (25 SP)
| ID Historia | Épica del Sprint | Título Resumido | Prioridad | SP | Documento PDF Oficial |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `HU-001` | `EP-01: Gestión de Solicitudes y Postulaciones` | Creación de solicitud y borrador | **Must** | 5 | [Sprint 3 / HU-001.pdf](Sprint%203/HU-001_Creacion_Solicitud_Guardado_Borrador.pdf) |
| `HU-002` | `EP-01: Gestión de Solicitudes y Postulaciones` | Validación de reglas y envío definitivo | **Must** | 5 | [Sprint 3 / HU-002.pdf](Sprint%203/HU-002_Validacion_Reglas_Envio_Definitivo.pdf) |
| `HU-003` | `EP-01: Gestión de Solicitudes y Postulaciones` | Desistimiento voluntario de borrador | **Should** | 2 | [Sprint 3 / HU-003.pdf](Sprint%203/HU-003_Desistimiento_Voluntario_Borrador.pdf) |
| `HU-004` | `EP-02: Gestión y Validación Documental Digital` | Carga y previsualización de documentos PDF | **Must** | 5 | [Sprint 3 / HU-004.pdf](Sprint%203/HU-004_Carga_Previsualizacion_Documentos_PDF.pdf) |
| `HU-005` | `EP-02: Gestión y Validación Documental Digital` | Verificación administrativa de admisibilidad | **Must** | 5 | [Sprint 3 / HU-005.pdf](Sprint%203/HU-005_Verificacion_Administrativa_Admisibilidad.pdf) |
| `HU-006` | `EP-03: Notificaciones y Comunicaciones` | Notificaciones transaccionales automáticas email | **Must** | 3 | [Sprint 3 / HU-006.pdf](Sprint%203/HU-006_Notificaciones_Transaccionales_Email.pdf) |

### 🔹 SPRINT 4: Subsanación, Comités y Evaluación Colegiada (25 SP)
| ID Historia | Épica del Sprint | Título Resumido | Prioridad | SP | Documento PDF Oficial |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `HU-001` | `EP-01: Gestión Documental (Subsanación)` | Subsanación de documentos observados en plazo | **Should** | 5 | [Sprint 4 / HU-001.pdf](Sprint%204/HU-001_Subsanacion_Documentos_Observados.pdf) |
| `HU-002` | `EP-02: Gestión de Comités Evaluadores` | Conformación de comités evaluadores | **Must** | 3 | [Sprint 4 / HU-002.pdf](Sprint%204/HU-002_Conformacion_Comites_Evaluadores.pdf) |
| `HU-003` | `EP-02: Gestión de Comités Evaluadores` | Asignación de expedientes a comités | **Must** | 5 | [Sprint 4 / HU-003.pdf](Sprint%204/HU-003_Asignacion_Expedientes_Comites.pdf) |
| `HU-004` | `EP-03: Evaluación y Rúbricas Digitales` | Declaración obligatoria de no conflicto de interés | **Must** | 2 | [Sprint 4 / HU-004.pdf](Sprint%204/HU-004_Declaracion_No_Conflicto_Interes.pdf) |
| `HU-005` | `EP-03: Evaluación y Rúbricas Digitales` | Evaluación individual con rúbrica digital | **Must** | 5 | [Sprint 4 / HU-005.pdf](Sprint%204/HU-005_Evaluacion_Individual_Rubrica_Digital.pdf) |
| `HU-006` | `EP-03: Evaluación y Rúbricas Digitales` | Consolidación y cálculo ponderado del comité | **Must** | 5 | [Sprint 4 / HU-006.pdf](Sprint%204/HU-006_Consolidacion_Calculo_Ponderado_Comite.pdf) |

### 🔹 SPRINT 5: Dictamen, Adjudicación, Trazabilidad, Auditoría y Transparencia (30 SP)
| ID Historia | Épica del Sprint | Título Resumido | Prioridad | SP | Documento PDF Oficial |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `HU-001` | `EP-01: Resolución, Aprobación y Adjudicación` | Emisión de dictamen y acta de recomendación | **Must** | 3 | [Sprint 5 / HU-001.pdf](Sprint%205/HU-001_Emision_Dictamen_Acta_Recomendacion.pdf) |
| `HU-002` | `EP-01: Resolución, Aprobación y Adjudicación` | Aprobación final y resolución de adjudicación | **Must** | 5 | [Sprint 5 / HU-002.pdf](Sprint%205/HU-002_Aprobacion_Final_Resolucion_Adjudicacion.pdf) |
| `HU-003` | `EP-02: Trazabilidad y Consulta de Estado` | Consulta de estado en línea para estudiantes | **Must** | 2 | [Sprint 5 / HU-003.pdf](Sprint%205/HU-003_Consulta_Estado_Tiempo_Real_Estudiante.pdf) |
| `HU-004` | `EP-02: Trazabilidad y Consulta de Estado` | Registro cronológico de trazabilidad de eventos | **Must** | 3 | [Sprint 5 / HU-004.pdf](Sprint%205/HU-004_Registro_Cronologico_Trazabilidad_Eventos.pdf) |
| `HU-005` | `EP-03: Notificaciones y Alertas en Plataforma` | Bandeja interna de alertas y notificaciones | **Should** | 3 | [Sprint 5 / HU-005.pdf](Sprint%205/HU-005_Bandeja_Interna_Alertas_Notificaciones.pdf) |
| `HU-006` | `EP-04: Reportes y Estadísticas de Gestión` | Generación de reporte consolidado | **Must** | 3 | [Sprint 5 / HU-006.pdf](Sprint%205/HU-006_Generacion_Reporte_Consolidado_Postulantes.pdf) |
| `HU-007` | `EP-04: Reportes y Estadísticas de Gestión` | Tablero gráfico de control (Dashboard) | **Should** | 5 | [Sprint 5 / HU-007.pdf](Sprint%205/HU-007_Tablero_Grafico_Dashboard_Gerencial.pdf) |
| `HU-008` | `EP-05: Auditoría, Registro y Transparencia` | Bitácora inmutable de auditoría | **Must** | 3 | [Sprint 5 / HU-008.pdf](Sprint%205/HU-008_Bitacora_Inmutable_Auditoria.pdf) |
| `HU-009` | `EP-05: Auditoría, Registro y Transparencia` | Portal de transparencia y padrón de becarios | **Should** | 3 | [Sprint 5 / HU-009.pdf](Sprint%205/HU-009_Portal_Transparencia_Padron_Becarios.pdf) |

---
*Todos los archivos PDF han sido compilados y validados formalmente con la participación y firmas digitales de los 5 integrantes del equipo.*
