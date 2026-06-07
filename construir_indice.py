"""
Construye el índice vectorial (Chroma) con TRES colecciones:
  oficial      <- PDFs de planes de gobierno (carpeta Planes/)
  declaracion  <- data/declaraciones.jsonl (transcripciones de videos)
  opinion      <- data/opiniones.jsonl (comentarios)

Embeddings 100% locales con BGE-M3. Uso: python construir_indice.py
"""
import json
import sys

import chromadb
import pdfplumber
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import config
from utils_limpieza import limpiar_texto, chunk_texto


def candidato_desde_archivo(nombre_archivo):
    """Mapea el PDF -> candidato (por el campo 'pdf' del config, luego por alias)."""
    for cand in config.CANDIDATOS:
        if cand.get("pdf") and cand["pdf"].lower() == nombre_archivo.lower():
            return cand["nombre"]
    base = nombre_archivo.lower()
    for cand in config.CANDIDATOS:
        if any(a.lower() in base for a in cand["alias"]):
            return cand["nombre"]
    return nombre_archivo


def cargar_pdfs():
    """Extrae, limpia y trocea los PDFs -> registros 'oficial'."""
    registros = []
    pdfs = sorted(config.PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"[PDF] No hay PDFs en {config.PDF_DIR}.")
    for pdf_path in pdfs:
        candidato = candidato_desde_archivo(pdf_path.name)
        with pdfplumber.open(pdf_path) as pdf:
            for n_pag, page in enumerate(pdf.pages, start=1):
                texto = limpiar_texto(page.extract_text() or "", quitar_emojis=False)
                for chunk in chunk_texto(texto, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
                    registros.append({
                        "text": chunk, "source_type": "oficial", "candidate": candidato,
                        "url": f"{pdf_path.name} (pág. {n_pag})",
                        "platform": "plan_gobierno", "title": pdf_path.name,
                    })
        print(f"[PDF] {pdf_path.name} -> {candidato}")
    return registros


def cargar_jsonl(ruta, etiqueta):
    """Lee un .jsonl (declaraciones u opiniones) -> registros (ya troceados)."""
    registros = []
    if not ruta.exists():
        print(f"[{etiqueta}] No existe {ruta} (omito).")
        return registros
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            try:
                r = json.loads(linea)
            except Exception:
                continue
            if r.get("text"):
                registros.append(r)
    print(f"[{etiqueta}] {len(registros)} fragmentos cargados")
    return registros


def indexar(registros, nombre_col, modelo, client):
    """Crea/reemplaza una colección y la llena con embeddings locales."""
    if not registros:
        print(f"[Índice] Sin datos para '{nombre_col}', se omite.")
        return
    try:
        client.delete_collection(nombre_col)   # recrea limpio al re-ejecutar
    except Exception:
        pass
    col = client.create_collection(nombre_col, metadata={"hnsw:space": "cosine"})
    textos = [r["text"] for r in registros]
    print(f"[Índice] Embeddings de {len(textos)} fragmentos para '{nombre_col}'...")
    emb = modelo.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=32).tolist()
    ids = [f"{nombre_col}-{i}" for i in range(len(registros))]
    metas = [{
        "source_type": r.get("source_type", ""), "candidate": r.get("candidate", ""),
        "url": r.get("url", ""), "platform": r.get("platform", ""), "title": r.get("title", ""),
    } for r in registros]
    for i in tqdm(range(0, len(ids), 256), desc=f"add {nombre_col}"):
        sl = slice(i, i + 256)
        col.add(ids=ids[sl], documents=textos[sl], embeddings=emb[sl], metadatas=metas[sl])
    print(f"[Índice] '{nombre_col}' listo con {col.count()} fragmentos.")


def main():
    oficial = cargar_pdfs()
    declaracion = cargar_jsonl(config.DECLARACIONES_FILE, "Declaraciones")
    opinion = cargar_jsonl(config.OPINIONS_FILE, "Opiniones")
    if not (oficial or declaracion or opinion):
        print("No hay nada que indexar.")
        sys.exit(1)

    print(f"\nCargando modelo de embeddings: {config.EMBEDDING_MODEL} (la 1ª vez tarda)...")
    modelo = SentenceTransformer(config.EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))

    indexar(oficial, "oficial", modelo, client)
    indexar(declaracion, "declaracion", modelo, client)
    indexar(opinion, "opinion", modelo, client)
    print(f"\nÍndice guardado en {config.CHROMA_DIR}. Ya puedes correr chatbot.py")


if __name__ == "__main__":
    main()
