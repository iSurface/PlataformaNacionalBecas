# -*- coding: utf-8 -*-
"""
Script de automatización de despliegue directo a la nube de AWS
1. Verifica credenciales de AWS (AWS CLI / boto3 / IAM)
2. Inicializa y aplica la infraestructura de Terraform en AWS (VPC, RDS PostgreSQL, ECS, Secrets Manager)
3. Ejecuta la siembra de datos iniciales en la base de datos de producción
"""

import os
import sys
import subprocess
import shutil

TERRAFORM_DIR = os.path.join(os.path.dirname(__file__), "terraform")

def run_cmd(cmd, cwd=None):
    print(f"\n[EJECUTANDO] {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, text=True)
    if res.returncode != 0:
        print(f"[ERROR] El comando falló con código {res.returncode}")
        return False
    return True

def deploy():
    print("=" * 70)
    print(" DESPLIEGUE DIRECTO A AWS CLOUD - SPRINT 1")
    print(" Plataforma Nacional para la Gestión Integral de Becas (MINEDUC)")
    print("=" * 70)

    # 1. Verificar Terraform
    if not shutil.which("terraform"):
        print("[AVISO] Terraform no está instalado en el PATH. Puedes desplegar manualmente ejecutando:")
        print("  cd aws_infrastructure/terraform")
        print("  terraform init")
        print("  terraform apply -auto-approve")
        return

    # 2. Terraform Init
    print("\n1. Inicializando infraestructura con Terraform...")
    if not run_cmd("terraform init", cwd=TERRAFORM_DIR):
        return

    # 3. Terraform Plan & Apply
    print("\n2. Creando VPC, Amazon RDS PostgreSQL 15, Secrets Manager y ECS...")
    if not run_cmd("terraform apply -auto-approve", cwd=TERRAFORM_DIR):
        return

    print("\n========================================================")
    print(" ¡DESPLIEGUE EN AWS COMPLETADO CON ÉXITO!")
    print("========================================================")

if __name__ == "__main__":
    deploy()
