# Placeholder Web Temporal

## Decision

Se elimina la propuesta visual anterior y se deja una web estatica minima en
`web/` solo para probar funcionalidad local.

El placeholder conserva:

- envio de consultas a `POST /ask`;
- streaming de respuestas desde `POST /ask/stream` cuando esta disponible;
- visualizacion de respuesta y fuentes consultadas;
- subida y borrado de documento temporal mediante `POST /documents` y
  `DELETE /documents/{document_id}`;
- boton de clip con aviso breve antes de subir documentos.

No conserva assets visuales, hero, direccion de arte ni componentes pensados
para la web final. La web definitiva se redisenara mas adelante.

## Retirada futura

Cuando se cree la web real, sustituir `web/index.html`, `web/styles.css` y
`web/app.js`. Esta documentacion puede eliminarse junto con el placeholder.
