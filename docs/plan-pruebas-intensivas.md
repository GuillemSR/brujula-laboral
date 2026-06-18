# Plan de Pruebas Intensivas

Este plan define las pruebas necesarias antes de usar la aplicacion en un
despliegue privado de AWS. El objetivo es detectar regresiones funcionales,
problemas de privacidad, fallos de RAG, errores en documentos temporales y
defectos visibles de la web antes de avanzar a pruebas con datos reales.

## Alcance

Incluye:

- codigo Python, configuracion y scripts locales;
- API FastAPI: salud, consultas, streaming y documentos;
- RAG local con corpus publico;
- privacidad, logs y errores;
- documentos temporales en memoria local y S3 temporal;
- placeholder web en escritorio y movil;
- casos limite y estados de error;
- despliegue AWS privado cuando se ejecute la parte posterior de la Fase 4.5.

No incluye una revision legal/RGPD completa ni una auditoria de seguridad
externa. Esas revisiones siguen pendientes antes de abrir el producto a terceros.

## Reglas de Privacidad Durante Pruebas

- No usar documentos reales con datos personales salvo que sea imprescindible y
  el entorno este revisado.
- No commitear `.env`, credenciales, capturas con datos personales, documentos
  privados ni logs con prompts o respuestas.
- No enviar prompts reales, respuestas, documentos privados, texto extraido ni
  secretos a herramientas externas de validacion.
- Usar sentinelas artificiales para comprobar fugas, por ejemplo
  `SENTINELA_PRIVADA_123`, y verificar que no aparecen en logs ni errores.
- Los documentos subidos se tratan como contexto temporal de una unica sesion:
  no se indexan en el RAG global y no se guardan como corpus.

## Gates Locales

Estos comandos son el minimo antes de subir cambios de codigo:

```powershell
.\scripts\lint.ps1
.\scripts\test.ps1
.\scripts\format.ps1 --check
```

Para una comprobacion completa local:

```powershell
.\scripts\check.ps1
```

Si el cambio solo toca documentacion, basta con revisar el diff y comprobar que
no se han incluido credenciales, documentos privados ni contenido sensible.

## Configuraciones de Prueba

### Mock Local

Uso: validar API, RAG y web sin depender de AWS ni Ollama.

```env
AI_PROVIDER=mock
BEDROCK_MODEL_ID=mock.amazon.nova-micro-v1:0
RAG_VECTOR_BACKEND=local
TEMP_DOCUMENT_STORAGE=memory
```

### Ollama Local Temporal

Uso: validar experiencia generativa y streaming mientras Bedrock no este
disponible.

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL_ID=qwen2.5:1.5b
OLLAMA_TIMEOUT_SECONDS=120
TEMP_DOCUMENT_STORAGE=memory
RAG_VECTOR_BACKEND=local
```

Comprobacion previa:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

### AWS Privado

Uso: validar el comportamiento real con Bedrock y S3 temporal antes de abrir
ninguna beta.

```env
AI_PROVIDER=bedrock
AWS_REGION=eu-south-2
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
S3_TEMP_BUCKET=<bucket-temporal>
RAG_VECTOR_BACKEND=local
```

Comprobaciones previas:

```powershell
aws sts get-caller-identity --region eu-south-2
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Matriz de Pruebas

| Area | Pruebas automaticas | Pruebas manuales o navegador | Criterio de salida |
| --- | --- | --- | --- |
| Codigo | Ruff check, Ruff format check, pytest completo | Revision de diff | Sin errores ni cambios sensibles |
| API salud | Tests de `/health` | `Invoke-RestMethod /health` | Respuesta 200 estable |
| Consulta sin documento | Tests de `/ask`, `/query` y validaciones | Preguntas laborales basicas desde la web | Respuesta orientativa y sin errores internos |
| Streaming | Tests del cliente Ollama y contrato de streaming si aplica | Ver texto aparecer progresivamente en la web | NDJSON con `meta`, `chunk` y `done` |
| RAG | Tests de loader, metadata, chunking, embeddings, retrieval y citas | Preguntas con fuentes esperadas | Solo se muestran fuentes recuperadas reales |
| Documentos | Tests de subida, validacion, borrado, expiracion y storage | Subir, consultar y quitar `.txt`/`.md`; probar PDF/DOCX no extraibles | Sin persistencia indebida ni errores internos |
| Privacidad | Tests de logs y errores con sentinelas | Revisar terminal y respuestas visibles | No aparecen prompts, documentos ni sentinelas |
| Web escritorio | Tests estaticos y navegador integrado | Chat, fuentes, errores, subida, borrado, estados de carga | Flujo completo usable |
| Web movil | Navegador responsive | 390x844 y anchuras pequenas | Sin solapes ni controles inaccesibles |
| AWS privado | Tests locales mas validacion AWS MCP cuando proceda | Health, web, ask, documentos, CloudWatch y coste | Sin datos sensibles en logs y recursos minimos |

## Casos API Minimos

### Salud

- `GET /health` devuelve 200.
- La respuesta no depende de Bedrock, Ollama, S3 ni RAG.

### Consulta

- Pregunta laboral valida sin documento.
- Pregunta corta o vacia devuelve validacion controlada.
- Pregunta excesivamente larga devuelve validacion controlada sin repetir el
  texto original.
- Error temporal de proveedor devuelve una respuesta o error controlado, sin
  propagar trazas internas al usuario.
- Si no hay fuentes RAG relevantes, la respuesta sigue siendo orientativa y no
  inventa citas.

### Streaming

- `POST /ask/stream` devuelve eventos NDJSON parseables.
- El primer evento util incluye metadatos y fuentes.
- Los fragmentos de texto llegan en orden.
- El evento final marca la respuesta como terminada.
- Si falla el proveedor, el error es controlado y no contiene secretos ni prompt
  completo.

### Documentos

- Subida valida de `.txt` y `.md`.
- Rechazo de archivo vacio.
- Rechazo de archivo demasiado grande.
- Rechazo de extension o MIME no admitido.
- `document_id` aleatorio y no derivado del nombre ni contenido.
- Consulta con `document_id` vigente.
- Consulta con `document_id` inexistente o expirado.
- Borrado explicito con `DELETE /documents/{document_id}`.
- PDF y DOCX se suben si cumplen contrato, pero la consulta debe devolver error
  controlado mientras no haya extractor real.

## Casos RAG Minimos

- Cargar `corpus/sources.example.json` sin errores de metadata.
- Verificar que cada `content_path` existe.
- Chunking con identificadores estables.
- Recuperacion para preguntas sobre Estatuto de los Trabajadores, registro de
  jornada y trabajo a distancia.
- Respuestas con marcadores de cita solo cuando hay fuentes recuperadas.
- No mezclar documentos privados con el corpus publico.
- No degradar si una fuente queda en estado `pending_review`; debe tratarse
  segun la politica definida en el loader.

## Casos Web Minimos

Ejecutar con:

```powershell
.\scripts\dev.ps1
```

Abrir:

```text
http://127.0.0.1:8000/
```

Comprobar:

- carga inicial sin errores visibles;
- envio de pregunta sin documento;
- render de streaming sin duplicar texto;
- fuentes visibles cuando la API las devuelve;
- errores de validacion comprensibles;
- boton de documento abre selector de archivo;
- subida valida muestra nombre normalizado, tamano y TTL;
- quitar documento llama a `DELETE /documents/{document_id}`;
- estados de carga no bloquean permanentemente la interfaz;
- la vista movil no solapa controles ni corta texto de botones.

Viewports minimos:

- escritorio: `1440x900`;
- portatil: `1280x720`;
- movil: `390x844`.

## Casos de Privacidad y Logs

Usar valores artificiales:

```text
SENTINELA_PROMPT_PRIVADO_123
SENTINELA_DOCUMENTO_PRIVADO_456
SENTINELA_ERROR_INTERNO_789
```

Comprobar:

- no aparecen en logs de aplicacion;
- no aparecen en access logs;
- no aparecen en errores 4xx/5xx;
- no aparecen en claves S3, tags, metadata tecnica ni nombres persistidos;
- no se escriben en ficheros del repositorio;
- no se indexan en el corpus RAG.

En local, `scripts/dev.ps1` debe arrancar Uvicorn sin access logs. En AWS, el
despliegue debe aplicar una politica equivalente o saneada para rutas con
`document_id`.

## Casos AWS Privados

Antes de desplegar:

- confirmar region `eu-south-2`;
- confirmar modelos Bedrock habilitados;
- confirmar bucket temporal con bloqueo publico, cifrado y lifecycle;
- confirmar budget y alarmas de coste;
- confirmar que no se usan documentos reales en validaciones automaticas.

Despues de desplegar:

- `/health` responde 200;
- la web carga desde el endpoint desplegado;
- `/ask` funciona con Bedrock o devuelve error controlado si hay cuota agotada;
- subida, consulta y borrado de documentos temporales funcionan con S3;
- CloudWatch no contiene prompts, respuestas, texto extraido ni documentos;
- el bucket temporal queda vacio o con objetos dentro del TTL esperado;
- los costes quedan dentro del presupuesto definido.

## Evidencia Esperada

Cada sesion de pruebas intensivas debe dejar, como minimo:

- comandos ejecutados y resultado;
- version o commit probado;
- configuracion usada: mock, Ollama local o AWS privado;
- incidencias encontradas;
- decisiones de correccion o registro en `TASKS.md`;
- lista de pruebas manuales que Codex no haya podido ejecutar.

La evidencia no debe incluir prompts reales, respuestas completas con contenido
privado, documentos privados, secretos ni capturas con datos personales.

## Criterio de Finalizacion de la Fase de Pruebas

La Fase 4.5 puede avanzar hacia despliegue privado cuando:

- los gates locales pasan;
- las pruebas de navegador cubren chat, fuentes, errores, documentos y
  responsive;
- los casos de privacidad no muestran fugas;
- los fallos encontrados estan corregidos o registrados;
- las pruebas manuales pendientes estan documentadas;
- el runtime AWS inicial queda elegido y documentado;
- el despliegue privado valida salud, web, consultas, documentos, Bedrock, S3,
  costes y logs.
