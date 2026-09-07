# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.infrastructure.models.user import Base, User, Person, Role, Permission
from app.infrastructure.models.catalog import Department, Municipality, EducationLevel, ScholarshipType
from app.core.security import get_password_hash

def seed_initial_data():
    """Siembra los datos iniciales indispensables de seguridad, roles y catálogos en PostgreSQL"""
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
            ("ADMIN_BECAS", "Administrador de Becas", "Gestión de convocatorias y expedientes", [perms_map["SCHOLARSHIP_MANAGE"], perms_map["SCHOLARSHIP_VIEW"]]),
            ("EVALUADOR", "Evaluador Académico", "Calificación técnica y ética de solicitudes", [perms_map["EVALUATION_MANAGE"]]),
            ("COORD_COMITE", "Coordinador de Comité", "Liderazgo de comités y dirimencia", [perms_map["EVALUATION_MANAGE"]]),
            ("AUTORIDAD", "Autoridad de Aprobación", "Firma y emisión de resoluciones ministeriales", [perms_map["SCHOLARSHIP_VIEW"]]),
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
                roles=[roles_map["SYSADMIN"]]
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
        for code, name, desc in tipos_beca_data:
            stype = db.query(ScholarshipType).filter(ScholarshipType.codigo == code).first()
            if not stype:
                stype = ScholarshipType(codigo=code, nombre=name, descripcion=desc)
                db.add(stype)

        db.commit()
        print("¡Siembra de datos iniciales en PostgreSQL completada al 100%!")
    except Exception as ex:
        db.rollback()
        print(f"Error sembrando datos: {ex}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_data()
