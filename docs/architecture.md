# Arquitectura Inicial

## Decision

Monolito modular en Python/FastAPI.

```text
web estatica -> FastAPI -> RAG propio -> AWS Bedrock
                         -> S3 temporal para documentos privados
```

## Por que no microservicios ahora

El proyecto es personal y pequeno. Separar servicios desde el principio aumentaria costes, IAM, despliegues, logs y mantenimiento sin una necesidad real. La separacion se hara primero en modulos internos.

## Fronteras internas

- `api`: entrada HTTP.
- `ai`: llamadas a modelos y Bedrock.
- `rag`: recuperacion de fuentes publicas.
- `documents`: procesamiento temporal de archivos privados.
- `storage`: S3/local.
- `privacy`: no retencion, sanitizacion y borrado.

## Separaciones futuras

Separar workers de ingesta o documentos solo si aparecen tiempos largos, escalado distinto o requisitos de aislamiento.
