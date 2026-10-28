# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.infrastructure.models.user import Base, User, Person, Role, Permission
from app.infrastructure.models.catalog import Department, Municipality, EducationLevel, ScholarshipType
from app.infrastructure.models.scholarship import ScholarshipCall, CallRequirement
from app.infrastructure.models.student_profile import StudentProfile
from app.infrastructure.models.application import Application, ApplicationDocument, ApplicationStatusHistory
from app.infrastructure.models.evaluation import EvaluationCommittee, CommitteeMember, ApplicationAssignment, EvaluationScore
from app.infrastructure.models.resolution import CommitteeAct, AwardResolution, ApplicationEvent, InternalNotification, AuditLog
from app.core.security import get_password_hash
from datetime import datetime, timezone, timedelta
import hashlib

def seed_initial_data():
    """Siembra los datos iniciales indispensables de seguridad, roles, catálogos y Sprints 1 a 5"""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        print("Iniciando siembra de datos maestros en PostgreSQL...")

        # 1. Permisos Base
        permissions_data = [
            ("IAM_ADMIN", "Seguridad", "Administración total de usuarios y roles"),
            ("CATALOG_MANAGE", "Configuración", "Mantenimiento de catálogos maestros"),
            ("SCHOLARSHIP_VIEW", "Convocatorias", "Consulta pública y privada de becas"),
            ("SCHOLARSHIP_MANAGE", "Convocatorias", "Creación y administración de convocatorias"),
            ("EVALUATION_MANAGE", "Evaluaciones", "Calificación y comités evaluadores"),
            ("AUDIT_VIEW", "Auditoría", "Acceso a registros y bitácora de auditoría"),
        ]
        perms_map = {}
        for code, mod, desc in permissions_data:
            p = db.query(Permission).filter(Permission.codigo == code).first()
            if not p:
                p = Permission(codigo=code, modulo=mod, accion=desc)
                db.add(p)
                db.flush()
            perms_map[code] = p

        # 2. Roles Institucionales
        roles_data = [
            ("SYSADMIN", "Administrador Técnico", "Acceso global al sistema y seguridad", list(perms_map.values())),
            ("POSTULANTE", "Postulante / Estudiante", "Aspirante ciudadano a programas de becas", [perms_map["SCHOLARSHIP_VIEW"]]),
            ("ADMIN_MINEDUC", "Administrador MINEDUC", "Gestión de convocatorias y expedientes", [perms_map["SCHOLARSHIP_MANAGE"], perms_map["SCHOLARSHIP_VIEW"], perms_map["EVALUATION_MANAGE"]]),
            ("ADMIN_BECAS", "Administrador de Becas", "Gestión de convocatorias y expedientes", [perms_map["SCHOLARSHIP_MANAGE"], perms_map["SCHOLARSHIP_VIEW"]]),
            ("EVALUADOR", "Evaluador Académico", "Calificación técnica y ética de solicitudes", [perms_map["EVALUATION_MANAGE"]]),
            ("DIRECTOR", "Director Ministerial", "Aprobación y resolución de becas", [perms_map["SCHOLARSHIP_MANAGE"], perms_map["AUDIT_VIEW"]]),
            ("AUDITOR", "Auditor de Control", "Fiscalización y consulta de bitácoras", [perms_map["AUDIT_VIEW"]])
        ]
        roles_map = {}
        for code, name, desc, perms in roles_data:
            r = db.query(Role).filter(Role.codigo == code).first()
            if not r:
                r = Role(codigo=code, nombre=name, descripcion=desc, permisos=perms)
                db.add(r)
                db.flush()
            roles_map[code] = r

        # 3. Usuario Administrador Inicial
        admin_email = "admin@becas.mineduc.gob.gt"
        admin_cui = "1000000010101"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                cui=admin_cui,
                email=admin_email,
                password_hash=get_password_hash("AdminBecas2026!#Segura"),
                estado="ACTIVO",
                roles=[roles_map["SYSADMIN"], roles_map["ADMIN_MINEDUC"]]
            )
            db.add(admin_user)
            db.flush()

            admin_person = Person(
                usuario_id=admin_user.id,
                primer_nombre="Administrador",
                primer_apellido="MINEDUC",
                telefono="24119595"
            )
            db.add(admin_person)
            print(f" -> Creado Usuario SysAdmin inicial: {admin_email}")

        # 3.1 Usuario Evaluador
        eval_email = "evaluador1@becas.mineduc.gob.gt"
        eval_user = db.query(User).filter(User.email == eval_email).first()
        if not eval_user:
            eval_user = User(
                cui="2000000010101",
                email=eval_email,
                password_hash=get_password_hash("Evaluador2026!#Seguro"),
                estado="ACTIVO",
                roles=[roles_map["EVALUADOR"]]
            )
            db.add(eval_user)
            db.flush()
            eval_person = Person(
                usuario_id=eval_user.id,
                primer_nombre="Carlos",
                primer_apellido="Méndez",
                telefono="24119596"
            )
            db.add(eval_person)
            print(f" -> Creado Usuario Evaluador: {eval_email}")

        # 3.2 Usuario Director Ministerial (Sprint 6 - HU-001 Doble Aprobación)
        director_email = "director@becas.mineduc.gob.gt"
        director_user = db.query(User).filter(User.email == director_email).first()
        if not director_user:
            director_user = User(
                cui="4000000010101",
                email=director_email,
                password_hash=get_password_hash("Director2026!#Seguro"),
                estado="ACTIVO",
                roles=[roles_map["DIRECTOR"]]
            )
            db.add(director_user)
            db.flush()
            director_person = Person(
                usuario_id=director_user.id,
                primer_nombre="Elena",
                primer_apellido="Sandoval",
                telefono="24119597"
            )
            db.add(director_person)
            print(f" -> Creado Usuario Director Ministerial: {director_email}")

        # 3.2 Usuario Estudiante Demo
        student_email = "estudiante.demo@becas.mineduc.gob.gt"
        student_user = db.query(User).filter(User.email == student_email).first()
        if not student_user:
            student_user = User(
                cui="3000000010101",
                email=student_email,
                password_hash=get_password_hash("Estudiante2026!#Seguro"),
                estado="ACTIVO",
                roles=[roles_map["POSTULANTE"]]
            )
            db.add(student_user)
            db.flush()
            student_person = Person(
                usuario_id=student_user.id,
                primer_nombre="Lucía",
                primer_apellido="Morales",
                telefono="55551234"
            )
            db.add(student_person)
            print(f" -> Creado Usuario Estudiante Demo: {student_email}")

        # 4. Departamentos de Guatemala
        deptos_data = [
            ("01", "Guatemala"), ("02", "El Progreso"), ("03", "Sacatepéquez"), ("04", "Chimaltenango"),
            ("05", "Escuintla"), ("06", "Santa Rosa"), ("07", "Sololá"), ("08", "Totonicapán"),
            ("09", "Quetzaltenango"), ("10", "Suchitepéquez"), ("11", "Retalhuleu"), ("12", "San Marcos"),
            ("13", "Huehuetenango"), ("14", "Quiché"), ("15", "Baja Verapaz"), ("16", "Alta Verapaz"),
            ("17", "Petén"), ("18", "Izabal"), ("19", "Zacapa"), ("20", "Chiquimula"),
            ("21", "Jalapa"), ("22", "Jutiapa")
        ]
        dept_map = {}
        for code, name in deptos_data:
            d = db.query(Department).filter(Department.codigo == code).first()
            if not d:
                d = Department(codigo=code, nombre=name)
                db.add(d)
                db.flush()
            dept_map[code] = d

        # Municipios principales de Guatemala (Cabeceras)
        muni_data = [
            ("01", "0101", "Guatemala"), ("01", "0102", "Santa Catarina Pinula"), ("01", "0108", "Mixco"), ("01", "0115", "Villa Nueva"),
            ("03", "0301", "Antigua Guatemala"), ("07", "0701", "Sololá"), ("09", "0901", "Quetzaltenango"),
            ("13", "1301", "Huehuetenango"), ("14", "1401", "Santa Cruz del Quiché"), ("16", "1601", "Cobán"),
            ("17", "1701", "Flores"), ("18", "1801", "Puerto Barrios"), ("20", "2001", "Chiquimula")
        ]
        for dept_code, muni_code, muni_name in muni_data:
            m = db.query(Municipality).filter(Municipality.codigo == muni_code).first()
            if not m and dept_code in dept_map:
                m = Municipality(departamento_id=dept_map[dept_code].id, codigo=muni_code, nombre=muni_name)
                db.add(m)

        # 5. Niveles Educativos
        niveles_data = [
            ("BASICO", "Nivel Medio - Ciclo Básico", "Educación secundaria básica (1ero a 3ero básico)"),
            ("DIVERSIFICADO", "Nivel Medio - Ciclo Diversificado", "Bachillerato, Perito o Magisterio"),
            ("LICENCIATURA", "Nivel Superior - Grado / Licenciatura", "Estudios universitarios de primer ciclo"),
            ("MAESTRIA", "Nivel Superior - Posgrado / Maestría", "Especialización y posgrados avanzados"),
            ("DOCTORADO", "Nivel Superior - Posgrado / Doctorado", "Investigación doctoral académica")
        ]
        for code, name, desc in niveles_data:
            lvl = db.query(EducationLevel).filter(EducationLevel.codigo == code).first()
            if not lvl:
                lvl = EducationLevel(codigo=code, nombre=name, descripcion=desc)
                db.add(lvl)

        # 6. Tipos de Beca
        tipos_beca_data = [
            ("EXCELENCIA_ACADEMICA", "Beca por Excelencia Académica", "Dirigida a estudiantes con promedios sobresalientes (>= 85 pts)"),
            ("ESCASOS_RECURSOS", "Beca de Apoyo Socioeconómico", "Focalizada en población estudiantil en situación de vulnerabilidad"),
            ("TALENTO_DEPORTIVO_ARTISTICO", "Beca por Talento Deportivo y Artístico", "Reconocimiento a atletas y artistas destacados"),
            ("INCLUSION_DISCAPACIDAD", "Beca de Inclusión para Personas con Discapacidad", "Apoyo adaptado para estudiantes con necesidades especiales")
        ]
        tipos_map = {}
        for code, name, desc in tipos_beca_data:
            stype = db.query(ScholarshipType).filter(ScholarshipType.codigo == code).first()
            if not stype:
                stype = ScholarshipType(codigo=code, nombre=name, descripcion=desc)
                db.add(stype)
                db.flush()
            tipos_map[code] = stype

        # 7. Convocatorias Iniciales del MINEDUC
        lvl_div = db.query(EducationLevel).filter(EducationLevel.codigo == "DIVERSIFICADO").first()
        now = datetime.now(timezone.utc)
        call_medio = db.query(ScholarshipCall).filter(ScholarshipCall.codigo == "BEC-2026-MEDIO-01").first()
        if not call_medio:
            call_medio = ScholarshipCall(
                codigo="BEC-2026-MEDIO-01",
                titulo="Beca Nacional al Mérito Académico - Nivel Diversificado 2026",
                descripcion="Programa ministerial de estímulo económico mensual para estudiantes sobresalientes de ciclo diversificado en todo el territorio nacional.",
                tipo_beca_id=tipos_map["EXCELENCIA_ACADEMICA"].id,
                nivel_educativo_id=lvl_div.id if lvl_div else list(tipos_map.values())[0].id,
                departamento_id=None,
                cupos_disponibles=500,
                presupuesto_total=4500000.00,
                monto_individual=1000.00,
                promedio_minimo_requerido=85.0,
                fecha_inicio=now - timedelta(days=10),
                fecha_cierre=now + timedelta(days=35),
                estado="PUBLICADA",
                bases_url="https://becas.mineduc.gob.gt/bases/bases_convocatoria_medio_2026.pdf",
                cronograma_detalle={
                    "apertura_solicitudes": (now - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "cierre_solicitudes": (now + timedelta(days=35)).strftime("%Y-%m-%d"),
                    "periodo_evaluacion": (now + timedelta(days=40)).strftime("%Y-%m-%d"),
                    "publicacion_resultados": (now + timedelta(days=55)).strftime("%Y-%m-%d")
                },
                creado_por_id=admin_user.id
            )
            db.add(call_medio)
            db.flush()

            reqs = [
                ("Certificado Oficial de Calificaciones del Ciclo Anterior", "Emitido por la dirección del centro educativo con sello oficial", True, "PDF", 5, 1),
                ("Certificado de Nacimiento (RENAP) o Fotocopia de DPI", "Documento de identificación vigente y legible", True, "PDF", 5, 2),
                ("Carta de Buena Conducta y Recomendación Docente", "Firmada por docente o director del establecimiento", False, "PDF", 3, 3)
            ]
            for nom, desc, oblig, tipo, peso, orden in reqs:
                db.add(CallRequirement(
                    convocatoria_id=call_medio.id,
                    nombre=nom,
                    descripcion=desc,
                    es_obligatorio=oblig,
                    tipo_documento=tipo,
                    peso_maximo_mb=peso,
                    orden=orden
                ))
            print(" -> Convocatoria Nivel Diversificado sembrada exitosamente")

        # 8. Perfil Estudiante Demo
        if student_user:
            profile = db.query(StudentProfile).filter(StudentProfile.usuario_id == student_user.id).first()
            if not profile:
                profile = StudentProfile(
                    usuario_id=student_user.id,
                    departamento_residencia_id=dept_map["01"].id,
                    institucion_origen="Instituto Nacional Central para Varones",
                    carrera_o_grado="Bachillerato en Ciencias y Letras",
                    promedio_general=92.5,
                    ingreso_mensual_familiar=3200.0,
                    dependientes_hogar=4,
                    tipo_vivienda="ALQUILADA",
                    perfil_completo=True
                )
                db.add(profile)
                db.flush()

        # 9. Comité Evaluador Colegiado (Sprint 4)
        committee = db.query(EvaluationCommittee).filter(EvaluationCommittee.codigo == "COM-2026-MEDIO-01").first()
        if not committee and call_medio:
            committee = EvaluationCommittee(
                codigo="COM-2026-MEDIO-01",
                nombre="Comité Colegiado de Evaluación de Becas de Diversificado",
                convocatoria_id=call_medio.id,
                estado="ACTIVO"
            )
            db.add(committee)
            db.flush()

            if eval_user:
                member = CommitteeMember(
                    comite_id=committee.id,
                    usuario_id=eval_user.id,
                    rol_comite="EVALUADOR",
                    declaracion_conflicto=True,
                    fecha_declaracion=now - timedelta(days=2)
                )
                db.add(member)
            print(" -> Comité Evaluador Colegiado sembrado")

        # 10. Expediente Demo Adjudicado (Sprint 3, 4 y 5)
        if student_user and call_medio:
            app_demo = db.query(Application).filter(Application.postulante_id == student_user.id).first()
            if not app_demo:
                app_demo = Application(
                    numero_expediente="EXP-2026-MEDIO-00001",
                    postulante_id=student_user.id,
                    convocatoria_id=call_medio.id,
                    estado="ADJUDICADA",
                    promedio_postulacion=92.5,
                    puntaje_ponderado_comite=94.5,
                    dictamen_comite="RECOMENDADO",
                    fecha_envio=now - timedelta(days=8),
                    verificado_por_id=admin_user.id,
                    observaciones_verificacion="Expediente cumple cabalmente con todos los requisitos de bases y atestados probatorios."
                )
                db.add(app_demo)
                db.flush()

                # Trazabilidad completa (Sprint 5 - HU-003)
                events_data = [
                    ("CREACION", "Borrador de Expediente Creado", "Se inició el expediente digital.", now - timedelta(days=9)),
                    ("ENVIO", "Expediente Formalizado", "Postulación formalizada con correlativo oficial EXP-2026-MEDIO-00001.", now - timedelta(days=8)),
                    ("VERIFICACION", "Filtro Administrativo: ADMISIBLE", "Verificación legal y documental concluida satisfactoriamente.", now - timedelta(days=6)),
                    ("ASIGNACION", "Asignación a Comité Colegiado", "Expediente asignado al Comité de Becas de Diversificado.", now - timedelta(days=5)),
                    ("EVALUACION", "Dictamen Colegiado Favorable", "Calificación ponderada: 94.50 / 100 puntos (RECOMENDADO).", now - timedelta(days=3)),
                    ("ADJUDICACION", "Beca Oficialmente Adjudicada", "Adjudicación ministerial emitida mediante Resolución RES-MINEDUC-2026-0042.", now - timedelta(days=1)),
                ]
                for te, tit, desc, dt in events_data:
                    db.add(ApplicationEvent(
                        solicitud_id=app_demo.id,
                        tipo_evento=te,
                        titulo=tit,
                        descripcion=desc,
                        actor_id=admin_user.id,
                        visible_estudiante=True,
                        creado_en=dt
                    ))

                # Notificación al estudiante (HU-005)
                db.add(InternalNotification(
                    usuario_id=student_user.id,
                    titulo="¡Felicidades! Beca Adjudicada",
                    mensaje="Tu expediente EXP-2026-MEDIO-00001 ha sido aprobado y adjudicado oficialmente mediante Resolución Ministerial RES-MINEDUC-2026-0042.",
                    tipo="SUCCESS",
                    leida=False,
                    creado_en=now - timedelta(days=1)
                ))

                # Resolución Ministerial Oficial (HU-002)
                res_demo = db.query(AwardResolution).filter(AwardResolution.numero_resolucion == "RES-MINEDUC-2026-0042").first()
                if not res_demo:
                    res_demo = AwardResolution(
                        convocatoria_id=call_medio.id,
                        numero_resolucion="RES-MINEDUC-2026-0042",
                        titulo="Resolución de Adjudicación Oficial de Becas al Mérito Diversificado 2026",
                        considerando="Que la educación es un derecho humano y deber del Estado garantizar becas a jóvenes de rendimiento destacado.",
                        por_tanto="Se adjudica el beneficio económico mensual a los estudiantes recomendados por el Comité Colegiado.",
                        total_becarios_adjudicados=120,
                        monto_total_comprometido=1200000.00,
                        emitida_por_id=admin_user.id,
                        estado="PUBLICADA",
                        fecha_resolucion=now - timedelta(days=1)
                    )
                    db.add(res_demo)

                # Bitácora Inmutable de Auditoría (HU-008 & HU-003)
                db.add(AuditLog(
                    usuario_id=admin_user.id,
                    usuario_nombre=admin_user.nombre_completo,
                    usuario_rol="ADMIN_MINEDUC",
                    modulo="ADJUDICACION",
                    accion="EMITIR_RESOLUCION_MINISTERIAL",
                    operacion="EMITIR_RESOLUCION_MINISTERIAL",
                    resultado="EXITOSO",
                    detalles="Resolución ministerial RES-MINEDUC-2026-0042 publicada oficialmente para 120 becarios.",
                    entidad="AwardResolution",
                    entidad_id="RES-MINEDUC-2026-0042",
                    datos_nuevos={"total_becarios": 120, "monto_total": 1200000.00},
                    timestamp=now - timedelta(days=1)
                ))
                print(" -> Expediente Demo Adjudicado y Resolución Ministerial sembrados exitosamente")

        # 11. Convocatoria y Expediente de Mayor Cuantía (> Q 10,000) (Sprint 6 - HU-001)
        lvl_mae = db.query(EducationLevel).filter(EducationLevel.codigo == "MAESTRIA").first()
        call_posgrado = db.query(ScholarshipCall).filter(ScholarshipCall.codigo == "BEC-2026-POSGRADO-01").first()
        if not call_posgrado:
            call_posgrado = ScholarshipCall(
                codigo="BEC-2026-POSGRADO-01",
                titulo="Beca Nacional de Posgrado e Investigación Científica 2026",
                descripcion="Programa ministerial de alto nivel para estudios avanzados de maestría y doctorado con financiamiento de Q 15,000.00.",
                tipo_beca_id=tipos_map["EXCELENCIA_ACADEMICA"].id,
                nivel_educativo_id=lvl_mae.id if lvl_mae else list(tipos_map.values())[0].id,
                departamento_id=None,
                cupos_disponibles=200,
                presupuesto_total=3000000.00,
                monto_individual=15000.00, # > Q 10,000.00 (Requiere Doble Aprobación)
                promedio_minimo_requerido=85.0,
                fecha_inicio=now - timedelta(days=15),
                fecha_cierre=now + timedelta(days=45),
                estado="PUBLICADA",
                bases_url="https://becas.mineduc.gob.gt/bases/bases_convocatoria_posgrado_2026.pdf",
                cronograma_detalle={
                    "apertura_solicitudes": (now - timedelta(days=15)).strftime("%Y-%m-%d"),
                    "cierre_solicitudes": (now + timedelta(days=45)).strftime("%Y-%m-%d")
                },
                creado_por_id=admin_user.id
            )
            db.add(call_posgrado)
            db.flush()
            print(" -> Convocatoria Posgrado (> Q10k) sembrada exitosamente")

        # Estudiante Posgrado Demo
        posgrado_email = "estudiante.posgrado@becas.mineduc.gob.gt"
        posgrado_user = db.query(User).filter(User.email == posgrado_email).first()
        if not posgrado_user:
            posgrado_user = User(
                cui="5000000010101",
                email=posgrado_email,
                password_hash=get_password_hash("Posgrado2026!#Seguro"),
                estado="ACTIVO",
                roles=[roles_map["POSTULANTE"]]
            )
            db.add(posgrado_user)
            db.flush()
            posgrado_person = Person(
                usuario_id=posgrado_user.id,
                primer_nombre="Fernando",
                primer_apellido="Reyes",
                telefono="55554321"
            )
            db.add(posgrado_person)

            # Perfil
            db.add(StudentProfile(
                usuario_id=posgrado_user.id,
                departamento_residencia_id=dept_map["01"].id,
                institucion_origen="Universidad de San Carlos de Guatemala",
                carrera_o_grado="Maestría en Ciencias de la Computación",
                promedio_general=95.0,
                ingreso_mensual_familiar=5000.0,
                dependientes_hogar=2,
                tipo_vivienda="PROPIA",
                perfil_completo=True
            ))

        if posgrado_user and call_posgrado:
            app_posgrado = db.query(Application).filter(Application.postulante_id == posgrado_user.id).first()
            if not app_posgrado:
                app_posgrado = Application(
                    numero_expediente="EXP-2026-POSGRADO-00001",
                    postulante_id=posgrado_user.id,
                    convocatoria_id=call_posgrado.id,
                    estado="PENDIENTE_SEGUNDA_APROBACION",
                    promedio_postulacion=95.0,
                    monto_solicitado=15000.00,
                    requiere_segunda_aprobacion=True,
                    puntaje_ponderado_comite=96.0,
                    dictamen_comite="RECOMENDADO",
                    primera_aprobacion_por_id=admin_user.id,
                    fecha_primera_aprobacion=now - timedelta(days=2),
                    observaciones_primera_aprobacion="Aprobación técnica de primera fase emitida. Supera el umbral de Q 10,000.00; requiere segunda aprobación de Dirección Ministerial (HU-001).",
                    fecha_envio=now - timedelta(days=10),
                    verificado_por_id=admin_user.id
                )
                db.add(app_posgrado)
                db.flush()

                # Trazabilidad
                db.add(ApplicationEvent(
                    solicitud_id=app_posgrado.id,
                    tipo_evento="CREACION",
                    titulo="Borrador Creado",
                    descripcion="Expediente digital de posgrado iniciado.",
                    actor_id=posgrado_user.id,
                    visible_estudiante=True,
                    creado_en=now - timedelta(days=12)
                ))
                db.add(ApplicationEvent(
                    solicitud_id=app_posgrado.id,
                    tipo_evento="ENVIO",
                    titulo="Expediente Formalizado",
                    descripcion="Postulación formalizada con correlativo EXP-2026-POSGRADO-00001.",
                    actor_id=posgrado_user.id,
                    visible_estudiante=True,
                    creado_en=now - timedelta(days=10)
                ))
                db.add(ApplicationEvent(
                    solicitud_id=app_posgrado.id,
                    tipo_evento="APROBACION_FASE_1",
                    titulo="Primera Aprobación Emitida (> Q 10,000)",
                    descripcion="Expediente por Q 15,000.00 aprobado en primera fase por Coordinación. En espera de segunda firma de Dirección Ministerial.",
                    actor_id=admin_user.id,
                    visible_estudiante=True,
                    creado_en=now - timedelta(days=2)
                ))

                # Notificación
                db.add(InternalNotification(
                    usuario_id=posgrado_user.id,
                    titulo="Primera Aprobación Emitida (> Q 10,000)",
                    mensaje="Tu expediente EXP-2026-POSGRADO-00001 (Q 15,000.00) superó satisfactoriamente la primera fase de aprobación. Actualmente se encuentra en Dirección Ministerial para la segunda aprobación obligatoria.",
                    tipo="ACTION_REQUIRED",
                    leida=False,
                    creado_en=now - timedelta(days=2)
                ))

                # Bitácora Forense (HU-003)
                db.add(AuditLog(
                    usuario_id=admin_user.id,
                    usuario_nombre=admin_user.nombre_completo,
                    usuario_rol="ADMIN_MINEDUC",
                    modulo="POSTULACIONES",
                    accion="APROBACION_PRIMERA_FASE",
                    operacion="APROBACION_PRIMERA_FASE_MAYOR_10K",
                    resultado="EXITOSO",
                    detalles="Primera aprobación completada para expediente EXP-2026-POSGRADO-00001 por Q 15,000.00. Se activa bandera de requerimiento de segunda firma.",
                    entidad="Application",
                    entidad_id=str(app_posgrado.id),
                    datos_nuevos={"estado": "PENDIENTE_SEGUNDA_APROBACION", "monto": 15000.00},
                    timestamp=now - timedelta(days=2)
                ))
                print(" -> Expediente Demo Posgrado PENDIENTE_SEGUNDA_APROBACION sembrado exitosamente")

        db.commit()
        print("¡Siembra de datos completa (Sprints 1 a 5) en PostgreSQL completada al 100%!")
    except Exception as ex:
        db.rollback()
        print(f"Error sembrando datos: {ex}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_data()
