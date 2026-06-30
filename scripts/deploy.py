"""
Deploy de la UI al servidor phantom.

    py scripts/deploy.py

Sube templates/index.html, static/css/style.css, static/js/app.js,
app.py y traduccion.py al servidor y reinicia el screen 'atlas' (Flask).
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import paramiko
from creds_lib import load_creds

# ─── Archivos a subir (relativos a la raíz del repo) ─────────────────────────
REPO_ROOT = Path(__file__).parent.parent
FILES = [
    'templates/index.html',
    'static/css/style.css',
    'static/js/app.js',
    'app.py',          # backend: maneja el parámetro lang (es/qu)
    'traduccion.py',   # módulo de traducción ES<->quechua (requerido por app.py)
]

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    creds    = load_creds()
    rdir     = creds['remote_dir']
    b        = creds['bridge']
    ph       = creds['phantom']

    # 1. Verificar archivos locales
    print('\nVerificando archivos locales:')
    for rel in FILES:
        p = REPO_ROOT / rel
        if not p.exists():
            print(f'  FALTA  {rel}')
            sys.exit(1)
        print(f'  OK     {rel}  ({p.stat().st_size:,} bytes)')

    # 2. Conectar
    print(f'\nConectando a bridge {b["host"]}...')
    bridge = paramiko.SSHClient()
    bridge.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    bridge.connect(b['host'], username=b['user'], password=b['pass'], timeout=15)

    ch = bridge.get_transport().open_channel('direct-tcpip', (ph['host'], 22), ('127.0.0.1', 0))
    phantom = paramiko.SSHClient()
    phantom.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    phantom.connect(ph['host'], username=ph['user'], password=ph['pass'], sock=ch, timeout=15)
    print('Conectado.')

    # 3. Subir archivos
    print('\nSubiendo archivos:')
    sftp = phantom.open_sftp()
    for rel in FILES:
        local  = REPO_ROOT / rel
        remote = f'{rdir}/{rel}'
        print(f'  -> {rel}', end='', flush=True)
        sftp.put(str(local), remote)
        print(f'  ({local.stat().st_size:,} bytes)  OK')
    sftp.close()

    # 4. Reiniciar Flask
    # bash -l lee .profile → OLLAMA_HOST=http://127.0.0.1:11435 disponible
    print('\nReiniciando screen atlas...')
    restart = (
        'screen -S atlas -X quit 2>/dev/null; sleep 1; '
        f"screen -dmS atlas bash -l -c 'cd {rdir} && python3 app.py > /tmp/atlas.log 2>&1'; "
        'sleep 2; screen -ls'
    )
    _, stdout, _ = phantom.exec_command(restart, timeout=20)
    print(stdout.read().decode('utf-8', errors='replace').strip())

    # 5. Esperar warmup y mostrar log
    print('\nEsperando warmup de modelos (~25s)...')
    time.sleep(25)
    _, stdout, _ = phantom.exec_command('tail -8 /tmp/atlas.log', timeout=10)
    log = stdout.read().decode('utf-8', errors='replace')
    for line in log.splitlines():
        print(f'  {line}')

    phantom.close()
    bridge.close()

    print('\nDeploy completado.')
    print('Para acceder: py scripts/tunnel.py  →  http://localhost:5000')


if __name__ == '__main__':
    main()
