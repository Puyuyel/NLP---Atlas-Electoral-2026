# Nuevo enfoque del chatbot electoral — Perú 2026

> Documento de diseño para rediseñar el chatbot: corpus más rico (plan oficial + opinión pública) y un motor de respuestas que sí sea coherente, **corriendo 100 % local/offline**.

---

## 1. Diagnóstico: por qué las respuestas salen incoherentes

Hay dos causas de raíz, y no son la misma cosa:

1. **El corpus es muy chico** (solo 5 PDFs). El recuperador tiene poco material y muchas veces trae fragmentos pobres o irrelevantes.
2. **El modelo de generación es demasiado pequeño** (tipo T5 / GPT-2 o un fine-tune casero). Aunque le des buen contexto, ese tipo de modelo no tiene capacidad de *síntesis instruida*: no redacta respuestas coherentes ni sigue instrucciones.

La idea clave de un RAG: **calidad final ≈ calidad de recuperación × capacidad de generación.** Hoy los dos eslabones están débiles. La buena noticia es que **ninguno requiere entrenar un modelo desde cero** — el camino correcto para un proyecto de curso es *recuperar bien* y *delegar la redacción a una LLM instruida que corra en local*.

---

## 2. Qué cambia (resumen ejecutivo)

| Componente | Antes | Ahora | Por qué |
|---|---|---|---|
| **Generación** | Modelo chico / casero (T5, GPT-2…) | LLM instruida local: **Qwen3 8B** vía Ollama | Coherencia real y seguimiento de instrucciones |
| **Recuperación** | Embeddings básicos, sin reranking | **BGE-M3** + **Chroma** + reranker **BGE-v2-m3** | Que entre el fragmento correcto |
| **Corpus** | 5 PDFs | PDFs (oficial) **+** opiniones (YouTube/Reddit), separados y etiquetados | Contraste "plan vs. gente" que pidió el profe |
| **Prompt** | Libre / improvisado | Prompt estructurado que **prohíbe inventar** y fuerza formato | Menos alucinación, respuestas verificables |

Todo lo nuevo corre **offline** después de la primera descarga de pesos. ✔ Cumple el requisito de "100 % local".

---

## 3. Arquitectura propuesta (corpus dual)

```
                ┌──────────────────────────┐
   PDFs JNE ───>│  Ingesta + limpieza      │
 (planes gob.)  │  · extraer texto         │
                │  · chunking ~600 tokens  │
 YouTube/Reddit │  · metadatos:            │
 (opiniones) ──>│    tipo, candidato, url  │
                └───────────┬──────────────┘
                            │ embeddings BGE-M3
                            ▼
                ┌──────────────────────────┐
                │  Índice vectorial Chroma │
                │  colección OFICIAL       │
                │  colección OPINIÓN       │
                └───────────┬──────────────┘
   pregunta ───────────────>│  recupera top-k de CADA colección
                            ▼
                ┌──────────────────────────┐
                │  Reranker BGE-v2-m3      │  ordena por relevancia real
                └───────────┬──────────────┘
                            ▼
                ┌──────────────────────────┐
                │  LLM local (Ollama,      │  prompt estructurado:
                │  Qwen3 8B)               │  "plan dice X / gente opina Y"
                └───────────┬──────────────┘
                            ▼
                   respuesta + fuentes citadas
```

**Decisión de diseño central:** mantener **dos sub-corpus separados y etiquetados** (`source_type = oficial | opinion`). En cada consulta recuperamos de *ambos*, así el bot siempre puede contrastar lo que **promete el plan** con lo que **opina la gente**.

---

## 4. Componentes concretos (modelos vigentes a junio 2026)

- **LLM de generación (local, Ollama): `qwen3:8b`** — multilingüe fuerte, muy bueno en español.
  - Si el hardware es justo (≤ 8 GB RAM): `qwen3:4b`, `gemma3`, o `mistral-nemo` (sólido en español/europeo).
  - Si hay GPU de 16 GB+: `gpt-oss:20b` o `qwen3:30b` para más calidad.
- **Embeddings (local): `BAAI/bge-m3`** — multilingüe (100+ idiomas), el default recomendado para self-hosting.
- **Reranker (local): `BAAI/bge-reranker-v2-m3`** — mejora muchísimo la precisión del top-k (alternativa: `Qwen3-Reranker-0.6B`).
- **Vector store: Chroma** — local, persistente y fácil de usar.

---

## 5. El corpus de opiniones (gratis y robusto)

**Realidad de Twitter/X en 2026:** ya **no hay tier gratis** para nuevos desarrolladores; ahora es pago por uso (~US$0.005 por tweet leído) y el track académico se eliminó en 2023. Para un proyecto de curso conviene usar fuentes gratuitas que cumplen el mismo objetivo de "opinión pública":

- **YouTube Data API (gratis, cuota generosa):** comentarios en videos de debates, entrevistas y noticias de cada candidato. Es la mejor fuente: alto volumen, en español y fácil de filtrar por candidato.
- **Reddit API vía PRAW (gratis):** subreddits como r/PERU; discusión política argumentada.
- **(Opcional) Twitter/X** solo si consiguen presupuesto.

**Limpieza imprescindible** (las opiniones son ruidosas): quitar URLs/emojis, normalizar texto, **filtrar idioma** (solo español con `langdetect`), **deduplicar**, **filtrar por palabras clave del candidato** y descartar comentarios muy cortos o spam.

**Rigor y ética (incluirlo en el informe):** las opiniones de redes tienen sesgo (no son una muestra representativa), hay bots y trolls. El bot debe presentarlas **como percepciones** ("algunos usuarios opinan…"), nunca como hechos. Guardar siempre `fecha` y `url` de cada opinión para trazabilidad.

---

## 6. Pipeline paso a paso (mapeado a los scripts entregados)

1. **`colectar_opiniones.py`** → baja comentarios de YouTube + posts/comentarios de Reddit → `data/opiniones.jsonl`
2. **`construir_indice.py`** → lee los PDFs (`data/planes_pdf/`) + `opiniones.jsonl` → chunking → embeddings BGE-M3 → Chroma (colecciones `oficial` y `opinion`)
3. **`chatbot.py`** → pregunta del usuario → recupera de oficial+opinión → reranker → prompt estructurado → Qwen3 (Ollama) → respuesta con fuentes

---

## 7. Por qué esto sí arregla la coherencia

- Una **LLM instruida** sabe redactar y seguir el formato pedido; el modelo chico no podía, por más buen contexto que tuviera.
- El **reranker** garantiza que entre el fragmento correcto (si entra basura, sale basura).
- El **prompt** prohíbe inventar y obliga a citar → menos alucinación y respuestas que se pueden verificar.
- El **corpus dual** entrega exactamente el "esto dice el plan / esto opina la gente" que pidió el profe.

---

## 8. Próximos pasos

1. Instalar **Ollama** y ejecutar `ollama pull qwen3:8b` (o el modelo que aguante el hardware).
2. Crear claves de **YouTube Data API** y **Reddit (script app)** — son gratuitas.
3. Colocar los 5 PDFs en `data/planes_pdf/` y correr los 3 scripts en orden.
4. **Evaluación (para el informe):** armar 15–20 preguntas de prueba y medir si responde correcto y cita bien. Es la mejor evidencia de que el nuevo enfoque funciona.
