"""
Herramienta de administrador: crea o actualiza scripts/creds.enc.

Solo necesitan ejecutarlo quienes tienen acceso directo al servidor
(cuando cambian credenciales o configuración del servidor).
Los demás usuarios del repo solo necesitan la CLAVE DEL PROYECTO
para usar tunnel.py y deploy.py.

    py scripts/init_creds.py
"""
import sys, getpass
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from creds_lib import save_creds

# ─── Credenciales actuales del servidor ───────────────────────────────────────
# Actualizar aquí si cambian las credenciales o la topología.
CREDS = {
    "bridge": {
        "host": "200.16.4.64",
        "user": "bridge",
        "pass": "h4l0h0m0r4pucp",
    },
    "phantom": {
        "host": "172.19.4.64",
        "user": "rholguin",
        "pass": "holguin",
    },
    "remote_dir":  "/home/rholguin/NLP---Atlas-Electoral-2026",
    "remote_port": 5000,
    "local_port":  5000,
}

print("=== Inicializar/actualizar credenciales cifradas ===")
print("Escribe la clave del proyecto que compartirás con tu equipo.")
print("(No la guardes en el repo — compártela por otro canal.)\n")

pw1 = getpass.getpass("Nueva clave del proyecto: ")
pw2 = getpass.getpass("Confirmar clave:          ")

if pw1 != pw2:
    print("Error: las claves no coinciden.")
    sys.exit(1)

if len(pw1) < 6:
    print("Error: la clave debe tener al menos 6 caracteres.")
    sys.exit(1)

save_creds(CREDS, pw1)
print("\nHecho. Comparte la clave con tu equipo por un canal seguro")
print("(mensaje directo, gestor de contraseñas, etc.) — nunca por el repo.")
