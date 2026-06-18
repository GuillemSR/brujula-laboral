# Evidencia de Pruebas Web

Fecha: 2026-06-18 17:18:02 +02:00

Commit probado: `58df067`

Rama: `main`

URL local probada: `http://127.0.0.1:8010/`

Configuracion usada:

```env
AI_PROVIDER=mock
TEMP_DOCUMENT_STORAGE=memory
RAG_VECTOR_BACKEND=local
BEDROCK_MODEL_ID=mock.amazon.nova-micro-v1:0
```

## Herramienta de Navegador

Se intento usar el navegador integrado solicitado mediante el plugin Browser. El
plugin listo una instancia de `Codex In-app Browser`, pero la conexion expuesta
para automatizacion estaba cerrada y no permitia abrir una pagina nueva.

Para no bloquear la validacion, se ejecuto la misma prueba con Chrome controlado
por Playwright como respaldo. La limitacion queda registrada aqui porque afecta
a la herramienta de prueba, no al comportamiento de la aplicacion.

## Resultado General

Todos los checks funcionales ejecutados pasaron.

## Checks Ejecutados

### Carga Inicial

- La web cargo correctamente.
- `h1`: `Brujula Laboral`.
- Estado inicial de documento: `Sin documento adjunto.`
- Assets estaticos:
  - `/static/styles.css?v=placeholder-1`: 200.
  - `/static/app.js?v=placeholder-1`: 200.

Estado: correcto.

### Chat Sin Documento

Pregunta sintetica usada:

```text
Tengo derecho a registrar mi jornada laboral?
```

Resultado:

- `POST /ask/stream`: 200.
- `Content-Type`: `application/x-ndjson`.
- Se observo estado de carga.
- La respuesta se renderizo en la caja de resultado.
- El boton volvio a `Enviar` al terminar.
- Se mostraron fuentes consultadas.

Fuentes visibles: 4.

Estado: correcto.

### Error de Validacion

Se envio una pregunta en blanco desde el DOM para saltar la validacion nativa
`required` del navegador y probar el flujo de error del backend.

Resultado:

- `POST /ask/stream`: 422.
- La UI mostro estado `Error`.
- Mensaje visible: `La solicitud no es valida.`
- El boton volvio a quedar habilitado.

Estado: correcto.

### Subida de Documento `.txt`

Archivo sintetico temporal:

```text
C:\Users\Guillem\AppData\Local\Temp\brujula-test-document.txt
```

Resultado:

- `POST /documents`: 200.
- La UI mostro nombre del archivo, tamano y TTL.
- Estado visible: `brujula-test-document.txt`, `caduca en 30 min`.

Estado: correcto.

### Consulta Con Documento `.txt`

Resultado:

- `POST /ask/stream`: 200.
- `Content-Type`: `application/x-ndjson`.
- La respuesta se renderizo correctamente.
- La sentinela artificial del documento no aparecio en la UI.

Estado: correcto.

### Borrado de Documento `.txt`

Resultado:

- `DELETE /documents/{document_id}`: 200.
- La UI volvio a `Sin documento adjunto.`

Estado: correcto.

### Subida de Documento `.pdf`

Archivo sintetico temporal:

```text
C:\Users\Guillem\AppData\Local\Temp\brujula-test-document.pdf
```

Resultado:

- `POST /documents`: 200.
- La UI mostro nombre del archivo, tamano y TTL.

Estado: correcto.

### Consulta Con Documento `.pdf`

Resultado esperado mientras no haya extractor PDF real:

- `POST /ask/stream`: 422.
- La UI mostro estado `Error`.
- Mensaje visible:

```text
El formato del documento todavia no permite extraer texto.
```

Estado: correcto.

### Borrado de Documento `.pdf`

Resultado:

- `DELETE /documents/{document_id}`: 200.
- La UI volvio a `Sin documento adjunto.`

Estado: correcto.

## Responsive

Viewports probados:

| Viewport | Resultado |
| --- | --- |
| `1440x900` | Sin overflow horizontal |
| `1280x720` | Sin overflow horizontal |
| `390x844` | Sin overflow horizontal |

Los controles principales permanecieron dentro del ancho visible:

- formulario;
- textarea;
- boton de envio;
- boton de documento;
- estado de documento;
- caja de resultado.

Estado: correcto.

## Consola y Red

La consola registro dos errores de recurso correspondientes a los 422 esperados:

- validacion de pregunta en blanco;
- consulta de PDF sin extractor soportado.

No se observaron errores JavaScript ni errores inesperados de assets.

## Logs y Privacidad

Se revisaron los logs locales del servidor de prueba buscando:

- sentinelas artificiales;
- nombres de archivos de prueba;
- rutas `/ask`;
- rutas `/documents`.

No hubo coincidencias. El servidor se arranco sin access logs.

No se usaron documentos privados reales, prompts reales, respuestas privadas ni
secretos en esta validacion.

## Conclusion

La tarea de pruebas web queda completada con la herramienta disponible:

- chat correcto;
- fuentes visibles;
- errores controlados;
- subida y borrado de documentos correctos;
- PDF tratado como formato todavia no extraible;
- estados de carga observados;
- responsive correcto en los tres viewports definidos;
- sin fugas observadas en logs locales.
