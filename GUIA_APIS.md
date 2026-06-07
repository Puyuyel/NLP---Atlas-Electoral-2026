# Cómo obtener las claves de API (gratis)

Necesitas dos, ambas **gratuitas**. No hay que pagar nada ni poner tarjeta.

> **¿Con prisa?** Puedes probar el chatbot **sin ninguna API**, solo con los planes:
> corre `python construir_indice.py` y luego `python chatbot.py`. Las opiniones de
> redes las agregas después. Reddit es la más fácil; YouTube toma un poco más.

---

## 1) Reddit (lo más fácil — empieza por aquí)

Sirve para bajar publicaciones y comentarios. **No** necesita tarjeta ni proyecto.

1. Inicia sesión en Reddit en tu navegador.
2. Entra a: **https://www.reddit.com/prefs/apps**
3. Baja hasta el final y haz clic en **"are you a developer? create an app…"**
   (o **"create another app…"**).
4. Llena el formulario:
   - **name:** `chatbot-electoral` (cualquier nombre)
   - tipo: marca **script**  ← importante
   - **redirect uri:** `http://localhost:8080` (es obligatorio, pon eso)
   - description: opcional
5. Clic en **"create app"**.
6. Ahora ves tu app. Copia dos datos:
   - **client_id:** la cadena corta que aparece **debajo del nombre de la app**
     (justo bajo el texto "personal use script").
   - **secret:** el valor del campo **"secret"**.

Eso es todo. Ese par (`client_id` + `secret`) es lo que va en `config.py`.

---

## 2) YouTube Data API v3 (para comentarios de videos)

Sirve para bajar comentarios de debates/entrevistas. Es gratis pero pasa por
Google Cloud (unos pasos más).

1. Entra a **https://console.cloud.google.com/** con tu cuenta de Google.
2. Arriba, en el selector de proyectos → **"Proyecto nuevo"** → ponle nombre
   (ej. `chatbot-electoral`) → **Crear**. Espera unos segundos y selecciónalo.
3. Menú ☰ → **"APIs y servicios"** → **"Biblioteca"**.
4. Busca **"YouTube Data API v3"**, ábrela y haz clic en **"Habilitar"**.
5. Menú ☰ → **"APIs y servicios"** → **"Credenciales"**.
6. Arriba: **"+ Crear credenciales"** → **"Clave de API"**.
7. Copia la clave que aparece. (Opcional: "Restringir clave" → limítala a
   *YouTube Data API v3*.)

Esa clave es tu `YOUTUBE_API_KEY`.

> Límite gratis: 10,000 unidades/día. Bajar 100 comentarios cuesta 1 unidad,
> así que alcanza de sobra para el proyecto.

### (Aparte) IDs de los videos
Para YouTube además hay que decirle de **qué videos** bajar comentarios. El ID es
lo que va después de `v=` en la URL:
`https://www.youtube.com/watch?v=`**`dQw4w9WgXcQ`** → el ID es `dQw4w9WgXcQ`.
Esos IDs van en la lista `youtube_videos` de cada candidato en `config.py`.

---

## 3) Dónde pegar las claves

Abre **`config.py`** y pega cada clave entre las comillas (ya están marcadas):

```python
YOUTUBE_API_KEY      = "AIza...tu_clave..." or os.getenv("YOUTUBE_API_KEY", "")
REDDIT_CLIENT_ID     = "abc123..."          or os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = "xyz789..."          or os.getenv("REDDIT_CLIENT_SECRET", "")
```

⚠ **No** subas el `config.py` con las claves dentro a GitHub ni lo compartas.

### Alternativa (variables de entorno, Windows PowerShell)
Si no quieres pegarlas en el archivo, deja las comillas vacías y, en PowerShell,
antes de correr los scripts:

```powershell
$env:YOUTUBE_API_KEY="AIza...";  $env:REDDIT_CLIENT_ID="abc123";  $env:REDDIT_CLIENT_SECRET="xyz789"
```

(Eso dura solo esa ventana de terminal. Para que sea permanente usa `setx`.)
