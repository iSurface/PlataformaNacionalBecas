# -*- coding: utf-8 -*-
import os
import hashlib
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app.infrastructure.models.application import Application, ApplicationDocument
from app.infrastructure.models.scholarship import CallRequirement

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentService:
    @staticmethod
    def upload_document(db: Session, solicitud_id: UUID, requisito_id: UUID, file: UploadFile, user_id: UUID) -> ApplicationDocument:
        solicitud = db.query(Application).filter(Application.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        
        if str(solicitud.postulante_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para modificar esta solicitud")

        if solicitud.estado not in ["BORRADOR", "OBSERVADA"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pueden subir documentos en estado {solicitud.estado}")

        requisito = db.query(CallRequirement).filter(CallRequirement.id == requisito_id).first()
        if not requisito:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisito no encontrado")

        content = file.file.read()
        file_size = len(content)

        # Validaciones de seguridad
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo excede el tamaño máximo permitido (10MB)")

        # Validar tipo MIME PDF
        if not (file.filename.lower().endswith(".pdf") or file.content_type == "application/pdf"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se permiten atestados probatorios en formato PDF")

        # Integridad digital criptográfica SHA-256 (HU-004)
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Guardar archivo en disco
        solicitud_dir = os.path.join(UPLOAD_DIR, str(solicitud_id))
        os.makedirs(solicitud_dir, exist_ok=True)
        safe_filename = f"{requisito_id}_{file.filename}"
        file_path = os.path.join(solicitud_dir, safe_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        # Registrar o actualizar en la base de datos
        doc = db.query(ApplicationDocument).filter(
            ApplicationDocument.solicitud_id == solicitud_id,
            ApplicationDocument.requisito_id == requisito_id
        ).first()

        if doc:
            doc.nombre_archivo = file.filename
            doc.archivo_ruta = file_path
            doc.archivo_hash_sha256 = sha256_hash
            doc.tamano_bytes = file_size
            doc.mime_type = "application/pdf"
            doc.estado_verificacion = "SUBSANADO" if solicitud.estado == "OBSERVADA" else "PENDIENTE"
            if solicitud.estado == "OBSERVADA":
                doc.fecha_subsanacion = datetime.now(timezone.utc)
        else:
            doc = ApplicationDocument(
                solicitud_id=solicitud_id,
                requisito_id=requisito_id,
                nombre_archivo=file.filename,
                archivo_ruta=file_path,
                archivo_hash_sha256=sha256_hash,
                mime_type="application/pdf",
                tamano_bytes=file_size,
                estado_verificacion="PENDIENTE"
            )
            db.add(doc)

        db.commit()
        db.refresh(doc)
        return doc
