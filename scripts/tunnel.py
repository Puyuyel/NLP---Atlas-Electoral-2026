"""
Túnel SSH para acceder al servidor phantom desde fuera de la red PUCP.

    py scripts/tunnel.py

Abre localhost:<local_port> → bridge → phantom:5000
Deja corriendo mientras uses la app. Ctrl+C para cerrar.
"""
import sys, select, threading, socketserver
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import paramiko
from creds_lib import load_creds

# ─── Configuración ────────────────────────────────────────────────────────────
creds = load_creds()

BRIDGE_HOST  = creds['bridge']['host']
BRIDGE_USER  = creds['bridge']['user']
BRIDGE_PASS  = creds['bridge']['pass']
REMOTE_HOST  = creds['phantom']['host']
REMOTE_PORT  = creds['remote_port']
LOCAL_PORT   = creds.get('local_port', 5000)

# ─── Lógica de reenvío de datos ───────────────────────────────────────────────
_transport = None   # se asigna después de conectar

def _forward(chan, sock):
    while True:
        r, _, _ = select.select([sock, chan], [], [], 5)
        if sock in r:
            data = sock.recv(4096)
            if not data:
                break
            chan.sendall(data)
        if chan in r:
            data = chan.recv(4096)
            if not data:
                break
            sock.sendall(data)
    chan.close()
    sock.close()


class _Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            chan = _transport.open_channel(
                'direct-tcpip',
                (REMOTE_HOST, REMOTE_PORT),
                self.request.getpeername(),
            )
        except Exception as e:
            print(f'[tunnel] No se pudo abrir canal: {e}')
            return
        t = threading.Thread(target=_forward, args=(chan, self.request), daemon=True)
        t.start()
        t.join()


class _Server(socketserver.ThreadingTCPServer):
    daemon_threads      = True
    allow_reuse_address = True


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    global _transport

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f'Conectando al bridge {BRIDGE_HOST}...')
    client.connect(BRIDGE_HOST, username=BRIDGE_USER, password=BRIDGE_PASS, timeout=15)
    _transport = client.get_transport()

    print(f'\nTunel activo:  http://localhost:{LOCAL_PORT}')
    print(f'               → {REMOTE_HOST}:{REMOTE_PORT} (via bridge)')
    print('\nAbre http://localhost:5000 en tu navegador.')
    print('Ctrl+C para cerrar el tunel.\n')

    server = _Server(('127.0.0.1', LOCAL_PORT), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        client.close()
        print('Tunel cerrado.')


if __name__ == '__main__':
    main()
