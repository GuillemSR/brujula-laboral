# Instrucciones Para Agentes

Este repositorio desarrolla un asistente laboral y sindical para Espana.

## Principios

- Mantener el proyecto pequeno, legible y facil de operar por una persona.
- Preferir un monolito modular antes que microservicios.
- Documentar las decisiones tecnicas en `docs/`.
- No introducir servicios externos nuevos sin justificar coste, seguridad y mantenimiento.
- Cuando se trabaje con AWS, usar AWS MCP si esta disponible para validar documentacion, disponibilidad regional, configuracion y estado de servicios.
- Usar las herramientas, plugins y skills adecuados para validar tareas automaticamente cuando sea razonable: tests, linters, navegador integrado, AWS MCP u otras capacidades disponibles segun el tipo de cambio.

## Seguimiento de tareas

- `TASKS.md` es la fuente principal de seguimiento local del proyecto.
- Cuando se detecte una nueva tarea durante el trabajo, preguntar al usuario si quiere anadirla a `TASKS.md`.
- Si el usuario confirma que quiere registrarla, crear la tarea en la fase mas adecuada de `TASKS.md`.
- Si el usuario pide "siguientes pasos", "siguientes tareas" o una priorizacion de trabajo, revisar primero `TASKS.md` y basar la respuesta en su estado actual.
- Si una tarea se completa durante el trabajo, actualizar `TASKS.md` cuando sea claramente la misma tarea registrada.

## Privacidad

- No guardar prompts de usuarios, respuestas del modelo ni documentos privados por defecto.
- No registrar contenido sensible en logs.
- No indexar documentos privados en el RAG global.
- Tratar documentos subidos como contexto temporal de una unica consulta.
- No commitear credenciales, `.env` reales, datos personales ni documentos de usuarios.
- No enviar al AWS MCP prompts reales, respuestas, documentos privados, textos extraidos ni secretos.

## Codigo

- Backend en Python/FastAPI.
- Separar adaptadores de AWS de la logica de dominio.
- Mantener el RAG propio inicialmente, con posibilidad de evaluar Bedrock Knowledge Bases despues.
- Preferir nombres claros y modulos pequenos.
- Escribir documentacion y textos de producto en espanol.
