# Documentos Privados Temporales

## Decision

El flujo de documentos privados debe permitir varias preguntas sobre el mismo
documento durante una ventana corta, sin convertir el documento en historial
persistente de conversacion.

El diseno objetivo es:

```text
subida -> S3 temporal cifrado -> document_id efimero -> preguntas posteriores
       -> extraccion temporal -> respuesta -> borrado explicito o expiracion
```

El `document_id` debe ser un identificador aleatorio, no derivado del nombre del
archivo ni de su contenido. Las preguntas posteriores podran referenciar ese
`document_id` hasta que expire o se borre.

## Alcance local de desarrollo

La primera implementacion funcional debe apuntar al diseno objetivo con S3
temporal cifrado y `document_id` efimero. No hace falta construir primero un
flujo local/in-memory completo y migrarlo despues.

El almacenamiento local temporal o memoria puede existir solo como doble de test
o ayuda de desarrollo, por ejemplo para validar el contrato HTTP sin tocar AWS en
cada test. Ese modo no debe presentarse como comportamiento principal, porque
puede perder el documento entre procesos, reinicios o despliegues.

## Diseno objetivo con S3

- Guardar el binario original en el bucket temporal cifrado ya documentado en
  `docs/aws-setup.md`.
- Usar claves S3 internas basadas en `document_id` y, si hace falta, un prefijo
  tecnico como `temporary-documents/`.
- No incluir datos personales, nombres reales de archivo ni contenido extraido
  en claves S3, tags, logs o metricas.
- Aplicar TTL corto a nivel de aplicacion y lifecycle corto a nivel de bucket.
- Permitir borrado explicito desde backend cuando termine el flujo o cuando el
  usuario lo solicite.
- No indexar documentos privados en el RAG global.
- No persistir texto extraido; extraerlo solo como contexto temporal de consulta.
- Si el documento expira, la API debe responder que el usuario debe volver a
  subirlo.

## Estado implementado

La API ya expone:

- `POST /documents`: recibe un archivo, valida tipo y tamano, genera un
  `document_id` aleatorio y lo guarda en S3 temporal cifrado.
- `DELETE /documents/{document_id}`: borra explicitamente el objeto temporal.
- `POST /ask` y `POST /query`: aceptan un `document_id` opcional, recuperan el
  objeto temporal, extraen texto en memoria y usan ese texto solo como contexto
  efimero para orientar la busqueda en el corpus publico. El texto extraido no
  se guarda, no se indexa en el RAG global y no se devuelve como fragmento de la
  respuesta extractiva.

El adaptador `S3TemporaryStorage` usa claves internas con el formato
`temporary-documents/{document_id}`. No incluye el nombre real del archivo ni
contenido extraido en la clave S3 ni en los metadatos del objeto.

Si `KMS_KEY_ID` esta configurado, la subida usa SSE-KMS. Si no lo esta, fuerza
SSE-S3 con `AES256`, coherente con el bucket temporal inicial documentado.

La extraccion inicial admite texto plano y Markdown cuando el objeto temporal se
recupera con `text/plain`, `text/markdown` o `application/octet-stream`. PDF y
DOCX siguen admitidos en la subida, pero la consulta devuelve un error
controlado hasta incorporar extractores especificos.

## Contrato esperado

La subida debe devolver una respuesta sin contenido sensible, por ejemplo:

```json
{
  "document_id": "identificador-aleatorio",
  "filename": "nombre-normalizado.txt",
  "content_type": "text/plain",
  "size_bytes": 1234,
  "expires_in_minutes": 30
}
```

Las consultas con documento deben enviar el `document_id` junto a la pregunta. El
backend cargara el documento temporal, extraera el texto necesario sin persistirlo
y construira la respuesta con las fuentes publicas que correspondan.

## Tipos de archivo admitidos

La subida temporal admite inicialmente estos formatos:

| Extension | MIME admitidos |
| --- | --- |
| `.txt` | `text/plain`, `application/octet-stream` |
| `.md` | `text/markdown`, `text/plain`, `application/octet-stream` |
| `.pdf` | `application/pdf`, `application/octet-stream` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/octet-stream` |

`application/octet-stream` se acepta para estos formatos porque algunos
navegadores o clientes HTTP no informan un MIME especifico fiable. La extension
debe seguir siendo una de las admitidas.

El limite inicial de tamano es `TEMP_DOCUMENT_MAX_BYTES`, por defecto 5 MiB.
Ampliar tipos o tamano debe hacerse junto con tests y revision de privacidad,
extraccion y coste.

## Plan de actuacion siguiente

1. Ampliar extraccion real para PDF y DOCX sin persistir contenido.
2. Borrar explicitamente el temporal cuando el flujo lo requiera y mantener el
   lifecycle del bucket como red de seguridad.
3. Verificar que logs, errores, respuestas, claves S3 y metadatos no contienen
   texto del documento ni datos personales derivados.
4. Validar configuracion AWS del bucket temporal cuando haya credenciales
   disponibles, sin enviar documentos, texto extraido, prompts ni respuestas a
   herramientas externas.

## Que borrar si se crea soporte local

Si durante la implementacion se crea soporte local/in-memory auxiliar, revisar y
eliminar lo que no siga siendo necesario cuando el flujo S3 este operativo:

- almacenamiento local temporal usado solo para desarrollo de la subida;
- mapas o caches en memoria de `document_id` a contenido de documento;
- rutas API que acepten contenido de documento en cada pregunta si ya existe
  subida previa con `document_id`;
- tests que validen comportamiento solo-in-memory como flujo principal;
- configuracion local que sugiera retencion mas larga que el TTL objetivo.

Se pueden conservar dobles de prueba o adaptadores locales si siguen siendo
utiles para tests, pero deben estar nombrados claramente como infraestructura de
test/desarrollo y no como comportamiento de produccion.

## Validacion minima

- Tests de subida valida y rechazo de archivo vacio, demasiado grande o tipo no
  admitido.
- Tests de consulta posterior con `document_id` vigente y expirado.
- Tests de borrado explicito.
- Revision de que respuestas, logs, claves, tags y errores no contienen texto del
  documento ni datos personales derivados.
- Validacion AWS del bucket temporal: cifrado, bloqueo publico, lifecycle y
  permisos minimos, sin enviar documentos ni texto extraido a herramientas MCP.

Validacion local actual:

- `.\scripts\check.ps1`: formato, lint y suite completa correctos.
- Tests especificos de subida, validaciones, borrado y adaptador S3 con dobles
  locales.
- Validacion AWS MCP repetida el 2026-06-10 sobre el bucket temporal real:
  region `eu-south-2`, bloqueo publico completo, SSE-S3 `AES256`, lifecycle a 1
  dia, versionado suspendido, ownership enforced y bucket vacio.
