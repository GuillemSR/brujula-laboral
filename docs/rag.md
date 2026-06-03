# RAG Inicial

## Decision

Empezar con RAG propio, pequeno y controlado. Evaluar Bedrock Knowledge Bases mas adelante si reduce complejidad sin perder control sobre metadatos juridicos y coste.

## Flujo

```text
fuentes publicas -> chunks -> embeddings -> vector store -> retrieval -> prompt con citas -> Bedrock
```

## Metadatos minimos

- `source_id`
- `title`
- `type`
- `source_url`
- `published_at`
- `updated_at`
- `valid_from`
- `valid_to`
- `territory`
- `sector`
- `legal_rank`

## Documentos privados

Los documentos privados no forman parte del RAG global:

```text
documento privado -> extraccion temporal -> contexto de la consulta -> borrado
```

No se guardan, no se indexan y no se usan para entrenar.
