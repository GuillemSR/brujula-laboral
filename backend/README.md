# Backend

Backend Python/FastAPI para Brujula Laboral.

## Modulos principales

- `api`: endpoints HTTP.
- `ai`: adaptadores de modelos, inicialmente AWS Bedrock.
- `rag`: chunking, embeddings, retrieval y citas.
- `documents`: extraccion temporal de documentos privados.
- `storage`: adaptadores local/S3.
- `privacy`: reglas de no retencion, sanitizacion y borrado.
- `cli`: tareas locales de ingesta y evaluacion.

El objetivo inicial es un monolito modular: una unica aplicacion desplegable con fronteras internas claras.

## Endpoints iniciales

- `GET /health`: comprobacion basica de salud.
- `POST /ask`: consulta laboral/sindical sin documento privado adjunto.
- `POST /ask/stream`: consulta en streaming NDJSON para el placeholder local.
- `POST /query`: alias semantico de `/ask` para consultas sin documento.
- `POST /documents`: subida temporal de documento privado a S3 cifrado.
- `DELETE /documents/{document_id}`: borrado explicito de documento temporal.

## Documentos temporales

La subida inicial admite `.txt`, `.md`, `.pdf` y `.docx`, con un limite por
defecto de 5 MiB (`TEMP_DOCUMENT_MAX_BYTES`). El endpoint devuelve un
`document_id` efimero y no devuelve contenido del archivo.
