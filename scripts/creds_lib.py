"""
Cifrado/descifrado de credenciales del servidor (Fernet + PBKDF2).
El archivo creds.enc está en este mismo directorio y es seguro de commitear
porque sin la clave del proyecto no revela nada.
"""
import base64, json, os, getpass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

CREDS_FILE = Path(__file__).parent / 'creds.enc'


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def load_creds(password: str | None = None) -> dict:
    """Descifra y devuelve las credenciales del servidor.

    Si no se pasa password, lo pide por consola.
    Lanza FileNotFoundError si creds.enc no existe.
    Lanza ValueError si la clave es incorrecta.
    """
    if not CREDS_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {CREDS_FILE}.\n"
            "Pídele al administrador del proyecto el archivo creds.enc\n"
            "o ejecúta scripts/init_creds.py si eres el administrador."
        )
    if password is None:
        password = getpass.getpass("Clave del proyecto Atlas Electoral: ")

    data  = CREDS_FILE.read_bytes()
    salt  = data[:16]
    token = data[16:]
    key   = _derive_key(password, salt)

    try:
        plaintext = Fernet(key).decrypt(token)
    except InvalidToken:
        raise ValueError("Clave incorrecta. Verifica la clave con el administrador del proyecto.")

    return json.loads(plaintext)


def save_creds(creds: dict, password: str) -> None:
    """Cifra las credenciales y las guarda en creds.enc."""
    salt  = os.urandom(16)
    key   = _derive_key(password, salt)
    token = Fernet(key).encrypt(json.dumps(creds, ensure_ascii=False).encode())
    CREDS_FILE.write_bytes(salt + token)
    print(f"Credenciales guardadas en {CREDS_FILE}")
