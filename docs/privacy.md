# Privacidad

## Politica tecnica inicial

- No guardar prompts de usuarios.
- No guardar respuestas del modelo.
- No guardar documentos privados.
- No indexar documentos privados.
- No escribir contenido sensible en logs.
- Guardar solo metricas tecnicas agregadas cuando sea necesario.

## Subida de documentos

Antes de subir documentos, la interfaz debe avisar:

- que la respuesta es orientativa;
- que el documento se procesa de forma temporal;
- que no se conserva por defecto;
- que no se usa para entrenar modelos;
- que conviene ocultar datos irrelevantes.

El diseno de detalle para permitir preguntas posteriores sobre un mismo
documento mediante `document_id` efimero esta en `docs/documentos-privados.md`.

## Revision pendiente

Antes de abrir publicamente el flujo con documentos privados, revisar RGPD, aviso legal, politica de privacidad, borrado efectivo y logs.
