# TASKS

## Fase 0 - Base del proyecto

- [x] Crear estructura inicial del repositorio.
- [x] Validar entorno local: dependencias, `pytest`, `ruff` y arranque FastAPI.
- [x] Revisar y versionar el documento de analisis en una ubicacion estable.
- [x] Definir comandos locales de desarrollo y pruebas.
- [x] Crear scripts locales para dev/test/lint en `scripts/`.
- [x] Crear dataset inicial de evaluacion con 20-50 preguntas.

## Fase 1 - Backend y RAG local

- [x] Implementar endpoint de salud.
- [x] Implementar endpoint de consulta sin documento.
- [x] Definir esquema de metadatos del corpus RAG.
- [x] Crear loader inicial de corpus desde JSON/Markdown.
- [x] Crear pipeline inicial de chunking por fuente juridica.
- [x] Crear adaptador inicial de embeddings.
- [x] Crear busqueda RAG local para prototipo.
- [x] Generar respuestas con citas.

## Fase 2 - AWS manual

- [ ] Comparar `eu-west-1`, `eu-south-2` y `eu-central-1` para Bedrock y servicios necesarios.
- [ ] Validar comparativa regional con AWS MCP si esta disponible.
- [ ] Crear budget y alarmas de coste.
- [ ] Habilitar modelos Bedrock candidatos.
- [ ] Validar modelos Bedrock, permisos IAM y region con AWS MCP si esta disponible.
- [ ] Crear bucket temporal cifrado para documentos.
- [ ] Validar bloqueo publico, cifrado y lifecycle del bucket temporal con AWS MCP si esta disponible.
- [ ] Validar que CloudWatch no contiene prompts, respuestas ni documentos.
- [ ] Documentar configuracion real en `docs/aws-setup.md`.

## Fase 3 - Documentos privados

- [ ] Implementar subida temporal de documentos.
- [ ] Extraer texto sin persistir contenido.
- [ ] Borrar temporales explicitamente.
- [ ] Verificar que no hay contenido sensible en logs.
- [ ] Preparar aviso de privacidad previo a subida.

## Fase 4 - Web simple

- [ ] Servir `web/index.html` y assets estaticos desde FastAPI en `/` para desarrollo local.
- [ ] Conectar chat con backend.
- [ ] Mostrar fuentes y limites de la respuesta.
- [ ] Anadir flujo de subida de documento.
- [ ] Revisar experiencia movil basica.

## Fase 5 - Evaluacion y apertura

- [ ] Benchmark de modelos Bedrock candidatos.
- [ ] Pruebas de abstencion y datos faltantes.
- [ ] Crear checklist de pruebas manuales antes de abrir una beta.
- [ ] Validar la app con navegador integrado; investigar si persiste bloqueo de `localhost`/`127.0.0.1`.
- [ ] Revision legal/RGPD antes de exponer documentos privados publicamente.
- [ ] Rate limiting y proteccion basica frente a abuso.
