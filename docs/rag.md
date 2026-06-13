# RAG Inicial

## Decision

Empezar con RAG propio, pequeno y controlado. Evaluar Bedrock Knowledge Bases mas adelante si reduce complejidad sin perder control sobre metadatos juridicos y coste.

## Flujo

```text
fuentes publicas -> chunks -> embeddings -> vector store -> retrieval -> prompt con citas -> Bedrock
```

## Generacion de respuestas

El RAG es la fuente preferente cuando hay coincidencias relevantes, pero no debe
bloquear la experiencia de usuario. La aplicacion debe generar una respuesta
orientativa unica aunque no haya fuentes del corpus para la consulta.

Comportamiento esperado:

- Si hay fuentes RAG relevantes, se pasan al modelo como contexto principal y se
  muestran como fuentes consultadas.
- Si no hay fuentes RAG relevantes, el modelo responde igualmente con
  orientacion general prudente, sin presentar la ausencia de corpus como una
  negativa a responder.
- Si Bedrock no esta configurado o falla en desarrollo local, se usa un fallback
  orientativo local para mantener el flujo de la interfaz.
- Si `AI_PROVIDER=mock`, se usa un mock local de generacion con la forma basica
  de `Converse`, sin llamadas a AWS. El texto mockeado es deliberadamente mas
  largo y estructurado para revisar la interfaz con varios parrafos, lista de
  acciones y marcadores de cita. Solo usa marcadores como `[1]` cuando proceden
  de fuentes RAG recuperadas; no inventa citas si el prompt no trae evidencia.
- La respuesta no debe inventar fuentes, articulos o sentencias. Solo se citan
  fuentes que existan en el corpus recuperado.

Los embeddings del prototipo local se calculan con `LocalHashEmbeddingProvider`.
Ese proveedor es determinista y no llama a Titan Embeddings. Una futura
integracion real con Titan debe mantenerse detras de la interfaz
`EmbeddingProvider`.

## Metadatos del corpus

El corpus global solo contiene fuentes publicas. El manifiesto editable vive en
`corpus/sources.example.json` y debe validarse con los modelos de `app.rag.metadata`
antes de ingerir documentos.

### Fuente

- `source_id`: identificador estable en minusculas, numeros y guiones.
- `title`: titulo legible.
- `source_type`: `legislation`, `collective_agreement`, `official_guide`, `case_law` o `faq`.
- `source_url`: URL publica verificable.
- `publisher`: organismo o entidad responsable de la publicacion.
- `jurisdiction`: jurisdiccion principal, por defecto `Espana`.
- `territory`: `estatal`, `autonomico`, `provincial`, `municipal`, `europeo` u `other`.
- `sector`: sector laboral, o `general` si no aplica.
- `legal_rank`: `law`, `royal_decree`, `collective_agreement`, `official_guidance`, `case_law` u `other`.
- `published_at`, `updated_at`, `valid_from`, `valid_to`: fechas ISO `YYYY-MM-DD` cuando se conozcan.
- `status`: `active`, `superseded`, `pending_review` o `draft`.
- `language`: idioma, por defecto `es`.
- `content_path`: ruta relativa al manifiesto hacia el Markdown local de la fuente.
- `notes`: observaciones no sensibles.

### Chunk

Cada fragmento recuperable debe conservar:

- `chunk_id`: identificador estable derivado de `source_id` y el localizador del fragmento.
- `source_id`: referencia a la fuente.
- `section`: articulo, clausula, apartado, pagina o epigrafe.
- `citation_label`: etiqueta corta para mostrar como cita.
- `metadata`: herencia de los metadatos de fuente necesarios para filtrar, recuperar y citar.

## Documentos privados

Los documentos privados no forman parte del RAG global:

```text
documento privado -> extraccion temporal -> contexto de la consulta -> borrado
```

No se guardan, no se indexan y no se usan para entrenar.
