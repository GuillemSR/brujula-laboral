# Cierre Parcial de Pruebas Intensivas

Fecha: 2026-06-18 17:29:13 +02:00

Commit base revisado: `238b702`

Rama: `main`

## Objetivo

Cerrar las dos tareas de seguimiento posteriores a las pruebas locales y de web:

- documentar las pruebas que Codex no pudo ejecutar automaticamente y pedir al
  usuario que las haga manualmente;
- corregir o registrar los fallos encontrados durante las pruebas intensivas.

Este cierre no sustituye las tareas posteriores de eleccion de runtime AWS,
despliegue privado ni validacion del despliegue.

## Evidencia Revisada

Documentos revisados:

- `docs/plan-pruebas-intensivas.md`;
- `docs/evidencia-pruebas-locales.md`;
- `docs/evidencia-pruebas-web.md`;
- `docs/aws-setup.md`;
- `docs/desarrollo-local.md`;
- `TASKS.md`.

Resultado consolidado:

- pruebas locales automatizadas correctas;
- pruebas de web correctas con Chrome/Playwright como respaldo;
- sin fallos funcionales de aplicacion encontrados en la fase local;
- varias limitaciones quedan registradas para no confundirlas con validaciones
  ya realizadas.

## Pruebas Que Codex No Puede Dar Por Cerradas

Estas pruebas requieren intervencion manual del usuario, entorno externo o una
fase posterior del proyecto.

### Navegador Integrado Real de Codex

Codex intento usar el plugin Browser y este listo una instancia de `Codex In-app
Browser`, pero la conexion de automatizacion estaba cerrada. La prueba funcional
se ejecuto con Chrome/Playwright como respaldo y paso.

Accion manual solicitada al usuario:

- abrir `http://127.0.0.1:8000/` o el puerto local que este usando la app;
- verificar visualmente que la pagina carga;
- enviar una pregunta simple;
- comprobar que la respuesta aparece y que los controles son utilizables.

Esta comprobacion manual no necesita documentos reales.

### Calidad Juridica de Respuestas

Los tests comprueban estructura, citas disponibles, privacidad y comportamiento
tecnico. No sustituyen una revision juridica experta de la calidad de cada
respuesta.

Accion manual solicitada al usuario:

- revisar varias respuestas con criterio juridico o laboral;
- confirmar que la respuesta distingue entre ley, convenio y orientacion
  practica;
- anotar cualquier caso donde falte prudencia, matiz o cita relevante.

### Revision Legal y RGPD

La politica tecnica de privacidad esta documentada, pero no equivale a una
revision legal formal.

Accion manual solicitada al usuario:

- revisar aviso legal, politica de privacidad, base juridica, retencion,
  derechos de usuario y tratamiento de documentos privados antes de exponer el
  producto a terceros.

### Pruebas Con Bedrock Real

Estado actualizado el 2026-06-24: Bedrock Runtime se valido con invocaciones
sinteticas minimas. Nova Micro, Nova Lite y Nova Pro funcionan desde
`eu-west-3`; Nova Micro sigue bloqueado cuando la llamada se inicia en
`eu-south-2`. La configuracion de desarrollo usa Nova Micro por coste minimo.

Sigue pendiente para el despliegue privado:

- comprobar latencia y calidad con el flujo completo de la aplicacion;
- revisar CloudWatch despues de invocar el modelo desplegado;
- medir coste y cuotas bajo una carga de prueba controlada.

### Pruebas Con S3 Temporal Real Desde La Web

Estado actualizado el 2026-06-24: se ejecuto el flujo integrado local contra
AWS con un documento sintetico:

- `GET /health`: 200;
- `POST /documents`: 200 y almacenamiento temporal en S3;
- `POST /ask`: 200 usando Bedrock Runtime real;
- `DELETE /documents/{document_id}`: 200;
- prefijo `temporary-documents/` vacio al terminar.

No se registraron el texto sintetico ni la respuesta. Sigue pendiente repetirlo
en el despliegue privado y verificar CloudWatch:

- subir un `.txt` o `.md` sintetico en el entorno AWS privado;
- preguntar con el documento activo;
- quitar el documento;
- verificar que CloudWatch y S3 no retienen contenido sensible fuera del TTL
  esperado.

### Documentos Reales o Sensibles

Codex no debe usar documentos personales reales para pruebas. Las pruebas se han
hecho con archivos sinteticos.

Accion manual solicitada al usuario:

- no usar documentos reales hasta validar despliegue, logs, borrado y aviso de
  privacidad;
- si se hace una prueba privada con documento real, usar un documento preparado
  y revisar antes que no contiene datos innecesarios.

## Incidencias y Limitaciones Registradas

### Sin Fallos Funcionales Bloqueantes

No se encontraron fallos funcionales de aplicacion en las pruebas locales y de
web ya ejecutadas. Por tanto, no hubo cambios de codigo que corregir en esta
tarea.

### Browser Plugin No Automatizable En Esta Sesion

Tipo: limitacion de herramienta.

Estado: registrada.

Detalle: el plugin Browser estaba disponible, pero la instancia expuesta para
automatizacion aparecia desconectada. Se uso Chrome/Playwright como respaldo y
la prueba funcional paso.

Impacto: no bloquea la aplicacion. Si vuelve a ocurrir, repetir prueba con
Browser visible o con Playwright y documentar la herramienta usada.

### Evaluacion RAG Automatizada No Implementada

Tipo: hueco de producto/herramienta.

Estado: registrada.

Detalle: existe `evals/questions.seed.jsonl`, pero
`backend.app.cli.evaluate_models` devuelve `Model evaluation is not implemented
yet`.

Impacto: no bloquea las pruebas locales actuales, pero limita la comparacion
objetiva de recuperacion, abstencion y calidad de respuestas. Ya existe una
tarea posterior en Fase 5 para crear evaluacion automatica de recuperacion y
abstencion.

### Warning De Cache De Pytest

Tipo: warning local no bloqueante.

Estado: registrado.

Detalle: pytest emite un `PytestCacheWarning` al intentar escribir
`.pytest_cache`.

Impacto: los tests pasan. No afecta a la suite ni a la aplicacion. Se puede
limpiar `.pytest_cache` manualmente si molesta, pero no requiere correccion de
codigo.

### PDF y DOCX Sin Extraccion Real

Tipo: limitacion funcional conocida.

Estado: registrada.

Detalle: la subida de PDF/DOCX esta permitida por contrato, pero la consulta
devuelve error controlado mientras no haya extractores reales.

Impacto: comportamiento esperado en esta fase. `docs/documentos-privados.md`
mantiene como siguiente actuacion ampliar extraccion real para PDF y DOCX.

## Solicitud Al Usuario

Antes de avanzar a despliegue AWS privado, conviene que el usuario ejecute estas
comprobaciones manuales:

- abrir la web local en el navegador integrado visible de Codex o en navegador
  normal y confirmar que el flujo basico se ve correcto;
- revisar cualitativamente varias respuestas laborales importantes;
- no usar documentos reales hasta validar logs y borrado en AWS;
- preparar una revision legal/RGPD antes de cualquier exposicion a terceros;
- durante el despliegue AWS privado, repetir las pruebas integradas con Bedrock
  y S3 reales.

## Conclusion

Las dos tareas quedan cerradas para el alcance actual:

- las pruebas no automatizadas quedan documentadas y trasladadas al usuario;
- las incidencias encontradas quedan registradas;
- no hay fallos funcionales de aplicacion pendientes de correccion en esta fase
  local.
