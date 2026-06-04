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
- `POST /query`: alias semantico de `/ask` para consultas sin documento.
