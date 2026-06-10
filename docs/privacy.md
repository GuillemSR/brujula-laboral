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

## Logs y errores

Las respuestas de validacion deben evitar devolver los valores originales de la
entrada, porque una pregunta o campo invalido puede contener datos personales.
Los errores operativos de almacenamiento temporal deben usar mensajes genericos
orientados al usuario y no propagar mensajes internos de excepciones.

La verificacion local de privacidad debe incluir sentinelas sensibles en
preguntas, documentos y mensajes de error simulados, y comprobar que no aparecen
en logs ni en respuestas de error.

Los access logs HTTP deben estar desactivados o saneados en entornos donde haya
documentos privados. Aunque las rutas no incluyen texto del documento ni la
pregunta, `DELETE /documents/{document_id}` contiene una referencia temporal al
documento y no debe conservarse en logs. El script local `scripts/dev.ps1`
arranca Uvicorn con `--no-access-log`; cualquier despliegue posterior debe
mantener una politica equivalente.
