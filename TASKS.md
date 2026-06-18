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

- [x] Comparar `eu-west-1`, `eu-south-2` y `eu-central-1` para Bedrock y servicios necesarios.
- [x] Validar comparativa regional con AWS MCP si esta disponible.
- [x] Habilitar `eu-south-2` en la cuenta AWS y repetir validacion STS/Bedrock/modelos.
- [x] Crear budget y alarmas de coste.
- [x] Habilitar modelos Bedrock candidatos.
- [x] Validar modelos Bedrock, permisos IAM y region con AWS MCP si esta disponible.
- [x] Crear bucket temporal cifrado para documentos.
- [x] Validar bloqueo publico, cifrado y lifecycle del bucket temporal con AWS MCP si esta disponible.
- [x] Validar que CloudWatch no contiene prompts, respuestas ni documentos.
- [x] Documentar configuracion real en `docs/aws-setup.md`.

## Fase 3 - Documentos privados

- [x] Implementar subida temporal de documentos en S3 cifrado con `document_id` efimero.
- [x] Extraer texto sin persistir contenido.
- [x] Borrar temporales explicitamente.
- [x] Verificar que no hay contenido sensible en logs.

## Fase 4 - Web simple

- [x] Servir `web/index.html` y assets estaticos desde FastAPI en `/` para desarrollo local.
- [x] Conectar chat con backend.
- [x] Mostrar fuentes y limites de la respuesta.
- [x] Preparar aviso de privacidad previo a subida.
- [x] Anadir flujo de subida de documento.
- [x] Revisar experiencia movil basica.

## Fase 4.5 - Pruebas intensivas y despliegue AWS de prueba

- [x] Definir y documentar un plan de pruebas intensivas del producto: codigo, API, RAG, privacidad, documentos, web desktop/movil y casos limite.
- [x] Ejecutar pruebas automatizadas locales: formato, lint, tests de backend y cualquier evaluacion RAG disponible.
- [x] Probar la web con navegador integrado: chat, fuentes, errores, subida/borrado de documentos, estados de carga y experiencia responsive.
- [x] Documentar las pruebas que no pueda ejecutar Codex con herramientas automaticas y pedir al usuario que las haga manualmente.
- [x] Corregir o registrar los fallos encontrados durante las pruebas intensivas.
- [ ] Elegir y documentar el runtime inicial para desplegar el monolito en AWS sin abrir beta publica: Lambda/API Gateway, App Runner o ECS/Fargate.
- [ ] Desplegar backend y web en AWS para pruebas privadas con IAM minimo, variables configuradas, Bedrock, S3 temporal y politica de logs sin contenido sensible.
- [ ] Validar el despliegue AWS: `/health`, web, `/ask`, documentos temporales, borrado, Bedrock, costes y CloudWatch Logs sin prompts, respuestas ni documentos.

## Fase 5 - RAG de produccion

- [ ] Elegir backend vectorial inicial: PostgreSQL + pgvector, OpenSearch o FAISS gestionado por la app.
- [ ] Implementar pipeline de ingesta persistente con versionado de corpus y embeddings.
- [ ] Sustituir embeddings hash locales por embeddings reales.
- [ ] Implementar retrieval con filtros por metadatos juridicos.
- [ ] Conectar generacion Bedrock con contexto RAG y citas verificables.
- [ ] Crear evaluacion automatica de recuperacion y abstencion.

## Fase 6 - Evaluacion y apertura

- [ ] Benchmark de modelos Bedrock candidatos.
- [ ] Pruebas de abstencion y datos faltantes.
- [ ] Crear checklist de pruebas manuales antes de abrir una beta.
- [ ] Revisar si el bucket temporal de documentos debe migrar de SSE-S3 a SSE-KMS antes de preproduccion o inicio de produccion.
- [ ] Repetir validacion de CloudWatch Logs tras desplegar backend en AWS o habilitar documentos privados.
- [ ] Validar la app con navegador integrado; investigar si persiste bloqueo de `localhost`/`127.0.0.1`.
- [ ] Revision legal/RGPD antes de exponer documentos privados publicamente.
- [ ] Rate limiting y proteccion basica frente a abuso.
