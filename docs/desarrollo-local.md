# Desarrollo local

Comandos base para trabajar con el proyecto en una maquina Windows con PowerShell.

## Requisitos

- Python 3.11 o superior.
- PowerShell.
- Git.

## Entorno

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias de aplicacion y desarrollo:

```powershell
pip install -e ".[dev]"
```

La configuracion local debe partir de `.env.example`. Si se necesita un `.env`, crearlo fuera de Git y no commitearlo:

```powershell
Copy-Item .env.example .env
```

`ALLOWED_ORIGINS` debe mantenerse como lista JSON, por ejemplo:

```env
ALLOWED_ORIGINS=["http://localhost:8000","http://localhost:5173"]
```

## Desarrollo

Arrancar FastAPI en local:

```powershell
.\scripts\dev.ps1
```

Comprobar el endpoint de salud:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Abrir la interfaz web estatica servida por FastAPI:

```text
http://127.0.0.1:8000/
```

Los assets de desarrollo se sirven desde `/static/*`. La interfaz usa rutas
relativas para llamar a `POST /ask`, `POST /documents` y
`DELETE /documents/{document_id}` desde el mismo origen local.
El placeholder usa `POST /ask/stream` para pintar la respuesta por fragmentos;
`POST /ask` se mantiene como endpoint no streaming.

## Prueba local opcional con Ollama

Para trabajar sin AWS, se puede usar la aplicacion local de Ollama. Esta
integracion es opcional y esta pensada solo para desarrollo:
no llama a AWS, no anade servicios gestionados y se retira cambiando
`AI_PROVIDER` o eliminando `app.ai.ollama_client`.
Cuando se usa desde la web local, la respuesta se consume en streaming mediante
NDJSON para poder ver el texto aparecer progresivamente.

Configuracion recomendada para el `.env` local:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL_ID=qwen2.5:1.5b
OLLAMA_TIMEOUT_SECONDS=120
TEMP_DOCUMENT_STORAGE=memory
RAG_VECTOR_BACKEND=local
```

Comprobar que Ollama esta arrancado:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

## Prueba local con mock de Bedrock

Para tests deterministas o trabajo sin AWS, activar el proveedor mock. El mock no
llama a AWS y devuelve una respuesta con la misma forma basica de la API
`Converse` de Bedrock. La respuesta local incluye varios parrafos, una lista de
acciones y, cuando el RAG local recupera fuentes, marcadores como `[1]` para
revisar como se ve una cita en la interfaz:

```env
AI_PROVIDER=mock
BEDROCK_MODEL_ID=mock.amazon.nova-micro-v1:0
RAG_VECTOR_BACKEND=local
```

Los embeddings del RAG local ya usan `LocalHashEmbeddingProvider`, que es
determinista y no llama a Titan Embeddings ni a ningun servicio externo.

## Prueba local con documentos temporales en S3

Para probar la subida real de documentos sin desplegar la aplicacion, usar el
backend local contra el bucket temporal de S3 ya creado:

```env
AI_PROVIDER=bedrock
AWS_REGION=eu-south-2
BEDROCK_REGION=eu-west-3
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
S3_TEMP_BUCKET=<bucket-temporal>
```

La terminal debe tener credenciales AWS validas:

```powershell
aws sts get-caller-identity
```

Despues arrancar la app con `.\scripts\dev.ps1` y abrir
`http://127.0.0.1:8000/`. La prueba esperada es subir un `.txt` o `.md`,
preguntar con el documento activo y quitarlo para disparar
`DELETE /documents/{document_id}`. No usar documentos reales con datos
personales en pruebas de desarrollo salvo que se haya revisado antes la
politica de logs y borrado.

`AWS_REGION` conserva la region del bucket S3. `BEDROCK_REGION` controla solo el
cliente de Bedrock Runtime. El perfil `eu.*` mantiene el procesamiento dentro de
la geografia europea, aunque puede enrutar entre varias regiones de la UE.

Si `BEDROCK_MODEL_ID` no esta configurado o Bedrock devuelve un error temporal,
la API mantiene la experiencia con una respuesta orientativa local. Para pruebas
deterministas y sin coste, usar `AI_PROVIDER=mock`.

Los modelos y precios verificados se documentan en
`docs/modelos-bedrock.md`.

## Pruebas

Ejecutar la suite de tests:

```powershell
.\scripts\test.ps1
```

Ejecutar solo los tests del backend:

```powershell
.\scripts\test.ps1 backend/tests
```

## Lint y formato

Revisar el codigo con Ruff:

```powershell
.\scripts\lint.ps1
```

Aplicar formato con Ruff:

```powershell
.\scripts\format.ps1
```

Comprobar formato sin modificar archivos:

```powershell
.\scripts\format.ps1 --check
```

## Comprobacion rapida antes de subir cambios

Para cambios de codigo, ejecutar como minimo:

```powershell
.\scripts\check.ps1
```

Para cambios solo de documentacion, basta con revisar el diff y comprobar que no se han incluido credenciales, documentos privados ni contenido sensible.
