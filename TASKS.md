# TASKS

## Fase 0 - Base del proyecto

- [x] Crear estructura inicial del repositorio.
- [ ] Revisar y versionar el documento de analisis en una ubicacion estable.
- [ ] Definir comandos locales de desarrollo y pruebas.
- [ ] Crear dataset inicial de evaluacion con 20-50 preguntas.

## Fase 1 - Backend y RAG local

- [ ] Implementar endpoint de salud.
- [ ] Implementar endpoint de consulta sin documento.
- [ ] Crear pipeline inicial de chunking por fuente juridica.
- [ ] Crear adaptador inicial de embeddings.
- [ ] Crear busqueda RAG local para prototipo.
- [ ] Generar respuestas con citas.

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

- [ ] Conectar chat con backend.
- [ ] Mostrar fuentes y limites de la respuesta.
- [ ] Anadir flujo de subida de documento.
- [ ] Revisar experiencia movil basica.

## Fase 5 - Evaluacion y apertura

- [ ] Benchmark de modelos Bedrock candidatos.
- [ ] Pruebas de abstencion y datos faltantes.
- [ ] Revision legal/RGPD antes de exponer documentos privados publicamente.
- [ ] Rate limiting y proteccion basica frente a abuso.
