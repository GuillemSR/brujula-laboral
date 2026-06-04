# Corpus

Espacio para fuentes publicas y manifiestos de ingesta.

Reglas iniciales:

- No incluir documentos privados de usuarios.
- Preferir fuentes oficiales o verificables.
- Mantener metadatos de fuente, URL, fecha, vigencia, ambito y jerarquia.
- Separar legislacion, guias oficiales, convenios y FAQs propias.

## Manifiesto local

`sources.example.json` define fuentes publicas y apunta a contenido Markdown local mediante
`content_path`, relativo al propio manifiesto. El loader inicial valida el JSON, comprueba que
los `source_id` sean unicos y carga solo archivos `.md` no vacios.

Ejemplo de validacion/carga:

```powershell
python -m app.cli.ingest_corpus corpus/sources.example.json
```
