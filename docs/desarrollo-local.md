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

## Prueba local con mock de Bedrock

Para trabajar sin cuota activa de Bedrock, activar el proveedor mock. El mock no
llama a AWS y devuelve una respuesta con la misma forma basica de la API
`Converse` de Bedrock:

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
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
S3_TEMP_BUCKET=<bucket-temporal>
```

La terminal debe tener credenciales AWS validas:

```powershell
aws sts get-caller-identity --region eu-south-2
```

Despues arrancar la app con `.\scripts\dev.ps1` y abrir
`http://127.0.0.1:8000/`. La prueba esperada es subir un `.txt` o `.md`,
preguntar con el documento activo y quitarlo para disparar
`DELETE /documents/{document_id}`. No usar documentos reales con datos
personales en pruebas de desarrollo salvo que se haya revisado antes la
politica de logs y borrado.

Si `BEDROCK_MODEL_ID` no esta configurado, o si Bedrock devuelve un error
temporal como limite diario de tokens, la API mantiene la experiencia con una
respuesta orientativa local. Para probar la experiencia generativa sin depender
de cuota, usar `AI_PROVIDER=mock`. La generacion real en AWS debe validarse
cuando haya cuota disponible.

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
