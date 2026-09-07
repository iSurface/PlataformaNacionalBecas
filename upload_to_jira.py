# -*- coding: utf-8 -*-
"""
Script de automatización para crear Épicas e Historias de Usuario directamente
en tu proyecto de Jira a través del REST API v3 / v2 de Jira Cloud.

Instrucciones:
1. Instala requests si no lo tienes: pip install requests
2. Configura las variables:
   - JIRA_DOMAIN (ejemplo: 'tudominio.atlassian.net')
   - JIRA_EMAIL (tu correo de Atlassian)
   - JIRA_API_TOKEN (generado en https://id.atlassian.com/manage-profile/security/api-tokens)
   - JIRA_PROJECT_KEY (la clave de tu proyecto, ejemplo: 'BECAS', 'PROY', etc.)
3. Ejecuta: python upload_to_jira.py
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

# ==================== CONFIGURACIÓN ====================
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "tu-dominio.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "tu_correo@ejemplo.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "TU_JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "BECAS")

# ========================================================

def make_jira_request(endpoint, method="GET", data=None):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/{endpoint}"
    auth_str = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[ERROR HTTP {e.code}] {error_body}")
        raise e

def test_connection():
    print(f"Probando conexión con Jira ({JIRA_DOMAIN})...")
    try:
        user_info = make_jira_request("myself")
        print(f"-> Conexión exitosa. Autenticado como: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
        return True
    except Exception as e:
        print(f"-> Error de conexión con Jira. Verifica tu dominio, correo y API Token.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print(" CARGADOR AUTOMÁTICO DE BACKLOG EN JIRA")
    print("=" * 60)
    if JIRA_API_TOKEN == "TU_JIRA_API_TOKEN":
        print("Por favor configura tus credenciales de Jira en este script o por variables de entorno:")
        print(" - JIRA_DOMAIN (ej. 'mineduc-becas.atlassian.net')")
        print(" - JIRA_EMAIL (ej. 'erick.chuquiej@mineduc.gob.gt')")
        print(" - JIRA_API_TOKEN (generado en Atlassian Security)")
        print(" - JIRA_PROJECT_KEY (ej. 'BECAS')")
        print("\nTambién puedes usar el archivo CSV generado directamente en Jira:")
        print("  -> c:\\Users\\recab\\OneDrive\\Documentos\\ProyectoFinalAnalisis\\jira_backlog_import.csv")
    else:
        test_connection()
