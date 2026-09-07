# 🇬🇹 Plataforma Nacional para la Gestión Integral de Becas

> **Ministerio de Educación de Guatemala (MINEDUC)**  
> Sistema integral para la administración, postulación, evaluación colegiada, adjudicación oficial y fiscalización pública del ciclo de vida de becas nacionales.

---

## 👥 Equipo del Proyecto (Sprint 1)
* **Raúl Álvarez** 
* **Erick Chuquiej** 
* **Walter Celada**
* **Daniel Ericastilla** 
* **Javier Alvizures** 

---

## 🏛️ Arquitectura del Sistema (Clean Architecture)

El backend está desarrollado en **Python 3.11** utilizando **FastAPI** y **SQLAlchemy**, siguiendo los principios de arquitectura limpia:

```
backend/
├── app/
│   ├── api/
│   │   ├── middlewares/        # Guardianes de seguridad (RBAC y autenticación)
│   │   └── v1/endpoints/       # Controladores HTTP (Auth, Catálogos, Admin)
│   ├── core/                   # Configuración, BD y funciones criptográficas
│   ├── infrastructure/
│   │   ├── models/             # Modelos de dominio PostgreSQL (ORM)
│   │   └── seeders.py          # Siembra automática de catálogos y usuarios
│   ├── schemas/                # Data Transfer Objects (DTOs con Pydantic v2)
│   └── services/               # Lógica de negocio pura e independiente
└── main.py                     # Punto de entrada de la aplicación FastAPI
```

---

## 🔒 Mecanismos de Seguridad Implementados
1. **Validación CUI Nacional (`RB-001`):** Verificación algorítmica obligatoria de los 13 dígitos del DPI mediante el algoritmo **Módulo 11** oficial de RENAP.
2. **Criptografía de Contraseñas:** Hashing mediante **Argon2id** (estándar resistente a ataques por GPU y tablas arcoíris).
3. **Control Anti-Fuerza Bruta:** 5 intentos fallidos consecutivos bloquean temporalmente la cuenta por 15 minutos (`HTTP 423 Locked`).
4. **Sesiones Seguras:** Emisión de **JSON Web Tokens (JWT)** con tiempo de vida estricto (TTL de 30 minutos).
5. **Control de Acceso Basado en Roles (RBAC):** Matriz institucional de 7 roles (`SYSADMIN`, `ADMIN_BECAS`, `EVALUADOR`, `COORD_COMITE`, `AUTORIDAD`, `AUDITOR`, `POSTULANTE`).

---

## ☁️ Infraestructura en la Nube (AWS Cloud)

Toda la infraestructura está automatizada como código (**IaC**) mediante **Terraform**:
* **Red:** Amazon VPC de 3 niveles con subredes públicas, privadas de aplicación y privadas de base de datos aislada.
* **Base de Datos:** Amazon RDS for PostgreSQL 16 cifrada con claves AWS KMS (AES-256).
* **Cómputo:** Amazon ECS Fargate con tareas de contenedor sin servidor.
* **Balanceo de Carga:** Application Load Balancer (ALB) con terminación HTTP/HTTPS.
* **Secretos:** AWS Secrets Manager para credenciales de base de datos y llaves JWT.

---

## 🚀 Documentación Interactiva (Swagger / OpenAPI)
* **Swagger UI:** `/docs`
* **ReDoc:** `/redoc`
* **Esquema OpenAPI:** `/api/v1/openapi.json`
* **Healthcheck:** `/health`
