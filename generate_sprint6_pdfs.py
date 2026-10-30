# -*- coding: utf-8 -*-
"""
Generador oficial de Historias de Usuario para el SPRINT 6
Plataforma Nacional para la Gestión Integral de Becas (MINEDUC)

Formato 100% idéntico a los Sprints 1 a 5 (Plantilla oficial de 3 páginas)
"""
import os, subprocess, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\recab\OneDrive\Documentos\ProyectoFinalAnalisis\user stories and interviews"
sprint6_dir = os.path.join(base_dir, "Sprint 6")
temp_html_dir = os.path.join(base_dir, "temp_html")

os.makedirs(sprint6_dir, exist_ok=True)
os.makedirs(temp_html_dir, exist_ok=True)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with open(r"C:\Users\recab\.gemini\antigravity\brain\9b9f18d6-1ba6-4e96-af5c-bdeac83c93e8\scratch\clean_template.html", "r", encoding="utf-8") as f:
    template = f.read()

stories_sprint_6 = [
    {
        "id": "HU-001",
        "file": "HU-001_Segunda_Aprobacion_Montos_Mayores_10000.pdf",
        "area": "Dirección Financiera y Despacho Superior",
        "epic": "EP-01: Control Financiero y Aprobaciones Jerárquicas",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Walter Celada (Arquitecto de Software / Backend Lead)",
        "resumen": "Implementar la regla de negocio y flujo de trabajo que exige una segunda aprobación obligatoria por parte de la Dirección Superior / Autoridad Financiera para toda solicitud de beca cuyo monto asignado supere los Q10,000.00 antes de que pase al estado final de 'Adjudicada' o 'Autorizada'.",
        "como": "Autoridad Nominadora y Director Superior del MINEDUC,",
        "yo_quiero": "Que las solicitudes de beca cuyo monto supere los Q10,000.00 requieran una segunda aprobación jerárquica obligatoria tras el dictamen favorable inicial,",
        "de_manera_que": "Se garantice el estricto control presupuestario, la probidad y la debida autorización de desembolsos mayores en cumplimiento con la normativa de auditoría gubernamental.",
        "beneficio": "Mitigación de riesgos de fraude y sobregiro presupuestario en montos mayores, trazabilidad legal y cumplimiento de las directrices de la Contraloría General de Cuentas.",
        "comentarios": "Las solicitudes con montos menores o iguales a Q10,000.00 continúan con el flujo de aprobación simple de una sola firma autorizada.",
        "dado": "Que un expediente de beca cuenta con primera aprobación favorable y el monto de financiamiento asignado es estrictamente mayor a Q10,000.00,",
        "cuando": "La Autoridad Evaluadora emite la aprobación de primera instancia,",
        "entonces": "El sistema coloca la solicitud en estado 'Pendiente de Segunda Aprobación', bloquea la emisión del acuerdo final de adjudicación y despacha una alerta a la bandeja del Director Superior; únicamente tras la firma y confirmación digital del segundo aprobador la solicitud pasa a estado 'Adjudicada'.",
        "qa": "1. Verificar que una solicitud de Q10,000.00 exacta o menor complete el flujo con una sola aprobación.<br>2. Probar que una solicitud de Q10,000.01 o mayor pase a 'Pendiente de Segunda Aprobación'.<br>3. Verificar que un usuario sin rol de 'Director Superior' no pueda emitir la segunda aprobación.<br>4. Comprobar que si la segunda aprobación es rechazada, se registre la justificación y cambie a 'Rechazada en Segunda Instancia'.",
        "resultado": "Flujo jerárquico automatizado y condicional por monto, con estados 'Pendiente de Segunda Aprobación' y 'Adjudicada' plenamente validados.",
        "riesgos": "Cuello de botella en la bandeja de la Autoridad Superior si no se cuenta con alertas o delegación temporal.",
        "supuestos": "Los montos de las becas están parametrizados en el catálogo de convocatorias y calculados con precisión decimal.",
        "limitaciones": "Aplica únicamente a montos adjudicados que excedan el umbral estricto de Q10,000.00.",
        "dependencias": "Módulo de Adjudicaciones y Resoluciones (Sprint 5).",
        "obj": "Fortalecimiento de la transparencia, control fiscal y gobernanza de los fondos públicos educativos.",
        "kpi": "100% de expedientes de alto monto auditados con doble firma digital antes de ejecución de pago.",
        "area_imp": "Dirección Financiera, Despacho Superior y Auditoría Interna.",
        "complejidad": "5 Story Points",
        "valor": "Muy Alto (Control y Cumplimiento Normativo)"
    },
    {
        "id": "HU-002",
        "file": "HU-002_Notificaciones_Eventos_Cambio_Estado_Estudiante.pdf",
        "area": "Experiencia del Postulante y Comunicaciones Transaccionales",
        "epic": "EP-02: Comunicación y Trazabilidad en Tiempo Real",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Javier Alvizures (Ingeniero de QA y DevOps Lead)",
        "resumen": "Garantizar que ante cualquier cambio de estado en una solicitud de beca (ej. Borrador, Enviada, En Subsanación, Admitida, En Evaluación, Pendiente de Segunda Aprobación, Adjudicada o Rechazada), el sistema registre el evento cronológico y dispare de forma asíncrona una notificación por correo electrónico y en la plataforma para el estudiante.",
        "como": "Estudiante postulante o aspirante a beca registrado,",
        "yo_quiero": "Recibir una notificación inmediata por correo electrónico y en mi panel cada vez que mi solicitud de beca cambie de estado,",
        "de_manera_que": "Conozca en tiempo real el progreso de mi trámite, esté informado sobre posibles requerimientos de subsanación y no dependa de consultas presenciales ni llamadas telefónicas.",
        "beneficio": "Transparencia total de cara al ciudadano, reducción drástica de consultas a mesa de ayuda y respuesta oportuna ante observaciones documentales.",
        "comentarios": "Las notificaciones deben incluir el nombre del estudiante, número de expediente, estado anterior, estado nuevo, fecha/hora y enlace directo a la plataforma.",
        "dado": "Que una solicitud de beca experimenta una transición de estado en el sistema realizada por un funcionario o por un proceso automático,",
        "cuando": "Se confirma el cambio de estado en la base de datos,",
        "entonces": "El sistema genera el registro del evento en la tabla de trazabilidad, construye la plantilla con los datos del expediente y despacha un correo electrónico vía Amazon SES, reflejando simultáneamente la alerta en la bandeja del estudiante.",
        "qa": "1. Simular transiciones de estado: Enviada -> En Subsanación, y verificar entrega de correo con instrucciones.<br>2. Comprobar que el correo no exponga datos sensibles ni credenciales.<br>3. Verificar registro simultáneo en la bandeja de notificaciones interna del postulante.<br>4. Probar resiliencia ante fallo de envío de correo (reintento asíncrono sin bloquear la transacción principal).",
        "resultado": "Despacho automático de notificaciones por email e internas en menos de 5 segundos tras cualquier actualización de estado.",
        "riesgos": "Bloqueo o demora en buzones de destino configurados con filtros estrictos de spam (mitigado con DKIM/SPF en Amazon SES).",
        "supuestos": "El estudiante ingresó una dirección de correo válida y verificada en el registro de su cuenta.",
        "limitaciones": "No incluye envío de SMS en esta versión (exclusivo para email y portal web).",
        "dependencias": "Amazon SES y Motor de Trazabilidad de Solicitudes.",
        "obj": "Acercamiento y democratización del servicio público educativo a través de canales digitales abiertos.",
        "kpi": "Tiempo promedio de enteramiento del postulante reducido a < 1 minuto; 0 quejas por falta de aviso sobre estados.",
        "area_imp": "Mesa de Ayuda, Dirección de Becas y Postulantes.",
        "complejidad": "3 Story Points",
        "valor": "Alto (Transparencia y Reducción de Incertidumbre)"
    },
    {
        "id": "HU-003",
        "file": "HU-003_Bitacora_Auditoria_Detallada_Operaciones_Criticas.pdf",
        "area": "Seguridad de la Información y Auditoría Gubernamental",
        "epic": "EP-02: Comunicación y Trazabilidad en Tiempo Real",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Raúl Álvarez (Administrador de Base de Datos / Backend)",
        "resumen": "Implementar un mecanismo de registro inmutable de auditoría forense que almacene con precisión quién ejecutó la acción (ID, CUI, nombre y rol), cuándo ocurrió (marca de tiempo ISO-8601 UTC), qué operación se realizó (aprobación, rechazo, modificación de datos, cambio de estado, dictamen) y cuál fue el resultado obtenido con su respectiva justificación.",
        "como": "Auditor Interno del MINEDUC y Oficial de Seguridad de la Información,",
        "yo_quiero": "Que cada aprobación, rechazo, rectificación o modificación relevante de una solicitud quede registrada en una bitácora inmutable con el detalle de quién, cuándo, qué operación y cuál fue el resultado,",
        "de_manera_que": "Exista una evidencia documental y digital fidedigna para auditorías de la Contraloría General de Cuentas y revisiones de control interno.",
        "beneficio": "Garantía de no repudio, prevención de manipulaciones no autorizadas, trazabilidad forense completa y blindaje jurídico ante impugnaciones.",
        "comentarios": "Los registros de esta tabla son de solo inserción (INSERT-only); ningún usuario, ni siquiera el SysAdmin, podrá modificarlos o eliminarlos mediante la aplicación.",
        "dado": "Que un funcionario (revisor, evaluador, comité o director) ejecuta una acción de aprobación, rechazo o modificación en una solicitud,",
        "cuando": "Se confirma la transacción en la base de datos relacional,",
        "entonces": "Se inserta de manera atómica un registro en la tabla de bitácora con: usuario_id, cui_operador, rol, ip_origen, timestamp, solicitud_id, tipo_operacion, datos_anteriores, datos_nuevos, resultado y motivo_justificacion.",
        "qa": "1. Ejecutar una aprobación y verificar que se genere la tupla exacta con IP y timestamp.<br>2. Intentar ejecutar UPDATE o DELETE directo en la tabla de auditoría y comprobar que esté protegido.<br>3. Verificar que la bitácora capture tanto operaciones exitosas como intentos denegados.<br>4. Validar vista de consulta de auditoría con filtros por fecha, solicitud y usuario.",
        "resultado": "100% de eventos críticos almacenados en bitácora protegida contra manipulación y con reporte de auditoría consultable.",
        "riesgos": "Crecimiento acelerado del volumen de la tabla si no se implementa particionamiento por rangos de fecha en PostgreSQL.",
        "supuestos": "La infraestructura de RDS PostgreSQL cuenta con sincronización horaria precisa mediante servicio NTP.",
        "limitaciones": "Exclusivo para operaciones sobre solicitudes y perfiles; logs de red se delegan a CloudWatch.",
        "dependencias": "Modelo de datos de solicitudes y esquema de auditoría (Sprint 5).",
        "obj": "Cero tolerancia a la discrecionalidad y transparencia absoluta en la gestión de recursos del Estado.",
        "kpi": "100% de operaciones sensibles trazadas; tiempo de respuesta a requerimientos de auditoría reducido de 15 días a 1 hora.",
        "area_imp": "Auditoría Interna, Asesoría Jurídica y Dirección de Informática.",
        "complejidad": "5 Story Points",
        "valor": "Muy Alto (Seguridad, Probidad y Cumplimiento Legal)"
    },
    {
        "id": "HU-004",
        "file": "HU-004_Reinicio_Recuperacion_Contrasena_GUI.pdf",
        "area": "Gestión de Identidad y Mesa de Ayuda",
        "epic": "EP-03: Seguridad de Acceso y Gestión de Identidad",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Walter Celada / Raúl Álvarez",
        "resumen": "Habilitar el flujo integral y amigable desde la interfaz gráfica web para que los usuarios (postulantes y funcionarios) que olviden su contraseña puedan solicitar su reinicio mediante correo electrónico, recibiendo un enlace seguro con token temporal de 15 minutos de un solo uso para ingresar una nueva contraseña robusta.",
        "como": "Usuario del sistema que ha olvidado o extraviado su contraseña de acceso,",
        "yo_quiero": "Solicitar el reinicio de mi contraseña desde la pantalla de inicio de sesión mediante mi correo electrónico registrado,",
        "de_manera_que": "Pueda recuperar el acceso a mi cuenta de forma rápida, autónoma y segura sin necesidad de contactar al administrador ni reiniciar mi expediente.",
        "beneficio": "Autonomía total del usuario, descongestión de canales de soporte técnico y protección de cuentas contra secuestro de credenciales.",
        "comentarios": "Para evitar ataques de enumeración de usuarios, el sistema siempre responderá el mismo mensaje genérico: 'Si el correo ingresado coincide con una cuenta activa, recibirás un enlace de restablecimiento'.",
        "dado": "Que un usuario registrado se encuentra en la pantalla de Login y hace clic en '¿Olvidaste tu contraseña?',",
        "cuando": "Ingresa su correo electrónico registrado y presiona 'Enviar Enlace',",
        "entonces": "El sistema valida la solicitud, genera un token criptográfico firmado con validez de 15 minutos, envía el enlace por correo y, al abrirlo, presenta un formulario seguro donde valida la nueva contraseña con políticas de complejidad y hasheo Argon2id, invalidando de inmediato las sesiones previas.",
        "qa": "1. Validar que enlaces con más de 15 minutos muestren mensaje de token expirado.<br>2. Comprobar que un token ya utilizado quede consumido y no permita un segundo uso.<br>3. Probar que la nueva contraseña requiera 8+ caracteres, mayúsculas, minúsculas, números y símbolos.<br>4. Verificar que se pueda iniciar sesión inmediatamente con la nueva credencial.",
        "resultado": "Proceso de recuperación completado en menos de 2 minutos por el usuario, con protección contra reuso y expiración estricta.",
        "riesgos": "Ataques de saturación de peticiones de recuperación (mitigado con limitador de tasa o rate-limiting por IP).",
        "supuestos": "El servidor de correo Amazon SES se encuentra operativo y el remitente institucional verificado.",
        "limitaciones": "El enlace de recuperación es válido únicamente por 15 minutos y se invalida al ser utilizado.",
        "dependencias": "Servicio de correo transaccional y Hasher Argon2id (Sprint 1).",
        "obj": "Autoservicio ciudadano y modernización de la gestión de identidad digital pública.",
        "kpi": "Reducción del 95% de tickets de soporte técnico por bloqueo u olvido de contraseña.",
        "area_imp": "Mesa de Ayuda, Soporte Técnico y Postulantes.",
        "complejidad": "3 Story Points",
        "valor": "Alto (Autogestión de Acceso y Reducción de Soporte)"
    },
    {
        "id": "HU-005",
        "file": "HU-005_Disclaimer_Institucional_Terminos_Educativos.pdf",
        "area": "Asesoría Jurídica y Cumplimiento Normativo",
        "epic": "EP-03: Seguridad de Acceso y Gestión de Identidad",
        "sprint": "Sprint 6",
        "prioridad": "Should",
        "tech_lead": "Erick Chuquiej (Product Owner / Coordinador Funcional)",
        "resumen": "Implementar en la plataforma un modal interactivo y visible de Disclaimer Institucional y Descargo de Responsabilidad (indicando el carácter formativo del proyecto universitario UMG en convenio simulado con el MINEDUC, la veracidad jurada de los datos ingresados y la política de protección y confidencialidad de la información personal de los postulantes).",
        "como": "Representante Legal e Institucional del Proyecto MINEDUC / UMG,",
        "yo_quiero": "Mostrar una advertencia formal y descargo de responsabilidad (Disclaimer) antes del ingreso y durante la postulación,",
        "de_manera_que": "Los postulantes y funcionarios conozcan el marco legal, los términos de uso ético, la naturaleza de declaración jurada de los datos y el propósito educativo de la plataforma.",
        "beneficio": "Transparencia legal, protección contra declaraciones falsas bajo apercibimiento legal y claridad sobre el tratamiento confidencial de los datos personales.",
        "comentarios": "Debe contar con un botón explícito de 'He leído y acepto los términos institucionales' que guarde la conformidad en la sesión del usuario.",
        "dado": "Que un usuario nuevo o existente ingresa a la plataforma web o va a enviar un formulario con carácter de declaración jurada,",
        "cuando": "Se despliega el portal o la vista de envío de solicitud,",
        "entonces": "El sistema presenta el modal institucional con el texto oficial del Disclaimer, bloqueando la interacción de fondo hasta que el usuario lea y marque la casilla de aceptación, registrando la conformidad en el perfil y permitiendo la continuidad de la sesión.",
        "qa": "1. Verificar que el modal no permita continuar si no se presiona 'Aceptar y Continuar'.<br>2. Probar que el texto del Disclaimer sea legible en pantallas de escritorio y móviles.<br>3. Confirmar que la aceptación quede registrada con timestamp en el perfil del usuario.<br>4. Verificar que se pueda volver a consultar el Disclaimer desde el pie de página institucional.",
        "resultado": "Modal de descargo desplegado correctamente, accesible desde cualquier vista y con registro de aceptación del usuario.",
        "riesgos": "Fatiga de usuario si el modal se presenta repetitivamente en cada navegación (debe almacenarse en sesión o cookie de consentimiento).",
        "supuestos": "El texto del descargo cuenta con la aprobación funcional del Product Owner y asesoría académica.",
        "limitaciones": "No sustituye las actas notariales en casos de convocatorias internacionales que lo requieran específicamente.",
        "dependencias": "Capa de presentación web y gestión de sesiones.",
        "obj": "Fomento de la cultura de legalidad, ética y apego a la normativa en el uso de herramientas tecnológicas estatales.",
        "kpi": "100% de usuarios informados y con aceptación verificable de términos antes de remitir expedientes.",
        "area_imp": "Asesoría Jurídica, Dirección de Becas y Postulantes.",
        "complejidad": "2 Story Points",
        "valor": "Medio / Alto (Validez Jurídica y Cumplimiento Ético)"
    },
    {
        "id": "HU-006",
        "file": "HU-006_Correccion_Interfaz_Control_Permisos_RBAC.pdf",
        "area": "Desarrollo Frontend y Seguridad de la Información",
        "epic": "EP-04: Experiencia de Usuario y Control de Interfaz",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Daniel Ericastilla (Ingeniero Frontend / UI-UX Lead)",
        "resumen": "Corregir la interfaz de usuario para que todos los menús, botones de acción, paneles de administración y formularios se rendericen y protejan de manera estricta y dinámica según los roles y permisos concedidos por el token JWT (evitando que usuarios sin privilegios visualicen opciones de comités, dictámenes o catálogos administrativos).",
        "como": "Usuario autenticado (postulante, revisor, evaluador, comité o administrador),",
        "yo_quiero": "Que la interfaz gráfica de la plataforma muestre exclusivamente las opciones, formularios y botones correspondientes a mi rol y permisos asignados,",
        "de_manera_que": "Tenga una experiencia limpia, intuitiva y no intente ejecutar acciones prohibidas que deriven en errores de acceso no autorizado (HTTP 403).",
        "beneficio": "Experiencia de usuario libre de confusiones, blindaje visual del sistema contra accesos indebidos y coherencia entre la UI y la API backend.",
        "comentarios": "La protección en UI es un facilitador de experiencia de usuario (UX Guard); el backend mantiene la validación obligatoria e inviolable con el middleware RBAC.",
        "dado": "Que un usuario inicia sesión con un rol específico (ejemplo: 'Postulante'),",
        "cuando": "Carga el panel principal de la aplicación,",
        "entonces": "La interfaz evalúa los claims de permisos del token JWT y oculta completamente los menús de 'Revisión Administrativa', 'Comité Evaluador' y 'Configuración de Catálogos', presentando únicamente sus postulaciones, convocatorias públicas y perfil.",
        "qa": "1. Iniciar sesión como Postulante y verificar que no existan botones de 'Aprobar' o 'Evaluar'.<br>2. Iniciar sesión como Evaluador y verificar que solo aparezcan expedientes asignados a su comité.<br>3. Forzar cambio de URL en el navegador y comprobar que el router redirija a 'Acceso Denegado'.<br>4. Verificar que el cierre de sesión limpie instantáneamente el estado visual de permisos.",
        "resultado": "Interfaz 100% personalizada por rol, sin fugas de componentes restringidos ni botones inhabilitados confusos.",
        "riesgos": "Inconsistencias en el renderizado si el token expira mientras el usuario navega (solucionado con interceptor HTTP que refresca o redirige a login).",
        "supuestos": "La matriz de roles y permisos RBAC del backend entrega los claims adecuados en la carga útil del JWT.",
        "limitaciones": "No suple la seguridad del backend, la cual es mandatoria e independiente.",
        "dependencias": "Middleware de Autenticación RBAC (Sprint 1) y Frontend SPA.",
        "obj": "Usabilidad, eficiencia operativa y gobierno de accesos en sistemas gubernamentales críticos.",
        "kpi": "Cero incidentes de confusión de roles o intentos de acceso no autorizado en interfaz.",
        "area_imp": "Equipo de Desarrollo Frontend, Mesa de Ayuda y Usuarios Finales.",
        "complejidad": "3 Story Points",
        "valor": "Alto (Seguridad Visual, UX Coherente y Aislamiento)"
    },
    {
        "id": "HU-007",
        "file": "HU-007_Responsividad_Optimizacion_Dispositivos_Moviles.pdf",
        "area": "Experiencia de Usuario (UI/UX) y Accesibilidad Ciudadana",
        "epic": "EP-04: Experiencia de Usuario y Control de Interfaz",
        "sprint": "Sprint 6",
        "prioridad": "Must",
        "tech_lead": "Daniel Ericastilla (Ingeniero Frontend / UI-UX Lead)",
        "resumen": "Corregir y optimizar de forma integral el diseño adaptativo (responsive design) de la plataforma web en pantallas móviles (smartphones de 360px a 480px) y tablets (768px a 1024px), garantizando que las tablas de convocatorias, formularios de postulación, carga de documentos y modales se visualicen fluidamente sin desbordamientos horizontales.",
        "como": "Estudiante de escasos recursos o de áreas departamentales que accede a la plataforma desde un teléfono celular inteligente,",
        "yo_quiero": "Que todos los formularios, tablas, botones y pasos de mi postulación se adapten fluidamente a la pantalla vertical de mi dispositivo móvil,",
        "de_manera_que": "Pueda postularme a las becas, cargar mis requisitos en PDF y consultar el estado de mi trámite sin distorsiones visuales ni cortes de información.",
        "beneficio": "Verdadera equidad e inclusión territorial, permitiendo el acceso a jóvenes de departamentos que carecen de computadora portátil o de escritorio.",
        "comentarios": "Las tablas densas de datos deben transformarse dinámicamente en tarjetas apiladas verticales en pantallas con ancho menor a 768 píxeles.",
        "dado": "Que un postulante accede a la plataforma desde un navegador móvil (Android / iOS) con resolución reducida,",
        "cuando": "Navega por el catálogo de becas, llena formularios y consulta su expediente,",
        "entonces": "Los menús se condensan en un menú hamburguesa desplegable accesible, los campos de texto se organizan a una columna, los botones táctiles tienen área de toque óptima (mínimo 44x44 px) y no existe desplazamiento horizontal involuntario.",
        "qa": "1. Validar en emulador y dispositivos físicos en anchos de 360px, 375px, 412px y 768px.<br>2. Comprobar que ningún modal o diálogo sobrepase el ancho del viewport móvil.<br>3. Verificar facilidad de carga de archivos PDF desde la galería o gestor de archivos del móvil.<br>4. Realizar auditoría de accesibilidad Lighthouse mobile superando puntuación de 90.",
        "resultado": "Plataforma 100% usable, fluida y ergonómica en móviles sin pérdidas de funcionalidad ni desbordamientos de pantalla.",
        "riesgos": "Rendimiento en teléfonos con recursos limitados o navegadores antiguos si no se optimiza el CSS y los scripts.",
        "supuestos": "Más del 70% de los postulantes de áreas rurales interactúan principalmente a través de dispositivos móviles.",
        "limitaciones": "Se requiere conexión a Internet estándar (3G/4G/WiFi) y navegador web moderno (Chrome, Safari, Firefox).",
        "dependencias": "Hojas de estilo CSS y maquetación de componentes del Frontend.",
        "obj": "Inclusión digital, equidad en el acceso a la educación superior y descentralización administrativa.",
        "kpi": "Tasa de finalización de solicitudes en dispositivos móviles incrementada en un 45%.",
        "area_imp": "Postulantes a Nivel Nacional, Departamentos del Interior y Mesa de Ayuda.",
        "complejidad": "3 Story Points",
        "valor": "Alto (Inclusión Digital y Accesibilidad en Territorio)"
    }
]

print("=== Compilando las 7 Historias de Usuario oficiales en PDF para Sprint 6 ===")

for st in stories_sprint_6:
    html_content = template
    replacements = {
        "proyecto": "Plataforma Nacional para la Gestión Integral de Becas",
        "area": st["area"],
        "epic": st["epic"],
        "sprint": st["sprint"],
        "id_historia": st["id"],
        "responsable_tecnico": st["tech_lead"],
        "estado": "Aprobada para Desarrollo",
        "prioridad": st["prioridad"],
        "resumen_requerimiento": st["resumen"],
        "como": st["como"],
        "yo_quiero": st["yo_quiero"],
        "de_manera_que": st["de_manera_que"],
        "beneficio_esperado": st["beneficio"],
        "comentarios": st["comentarios"],
        "dado": st["dado"],
        "cuando": st["cuando"],
        "entonces": st["entonces"],
        "validacion_qa": st["qa"],
        "resultado_esperado": st["resultado"],
        "riesgos": st["riesgos"],
        "supuestos": st["supuestos"],
        "limitaciones": st["limitaciones"],
        "dependencias": st["dependencias"],
        "obj_estrategico": st["obj"],
        "kpi_impactado": st["kpi"],
        "area_impactada": st["area_imp"],
        "complejidad": st["complejidad"],
        "valor_negocio": st["valor"]
    }

    for k, v in replacements.items():
        html_content = html_content.replace(f"{{{k}}}", str(v))

    html_file = os.path.join(temp_html_dir, f"Sprint 6_{st['file'].replace('.pdf', '.html')}")
    pdf_file = os.path.join(sprint6_dir, st["file"])

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

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
        print(f"[OK] Generado: {st['id']} -> {st['file']} ({size_kb:.1f} KB)")
    else:
        print(f"[ERROR] en {st['id']}: {res.stderr}")

print("\n=== Todas las historias fueron generadas con el formato oficial idéntico ===")
