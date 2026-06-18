# Evidencia de Pruebas Locales

Fecha: 2026-06-18 17:04:59 +02:00

Commit probado: `2a54f5e`

Rama: `main`

## Objetivo

Ejecutar las pruebas automatizadas locales definidas para la Fase 4.5:
formato, lint, tests de backend y cualquier evaluacion RAG disponible.

## Comandos Ejecutados

### Lint

```powershell
.\scripts\lint.ps1
```

Resultado:

```text
All checks passed!
```

Estado: correcto.

### Formato

```powershell
.\scripts\format.ps1 --check
```

Resultado:

```text
48 files already formatted
```

Estado: correcto.

### Tests

```powershell
.\scripts\test.ps1
```

Resultado:

```text
72 passed, 1 warning in 2.36s
```

Estado: correcto.

Warning no bloqueante:

```text
PytestCacheWarning: could not create cache path
D:\Projectos\brujula-laboral\.pytest_cache\v\cache\nodeids:
[WinError 183] No se puede crear un archivo que ya existe
```

El warning afecta a la cache local de pytest, no a la ejecucion ni al resultado
de la suite.

## Cobertura Ejecutada

La suite actual cubre:

- API de consultas y validaciones;
- cliente Bedrock y mock local;
- subida, borrado, expiracion y almacenamiento temporal de documentos;
- almacenamiento local temporal para desarrollo;
- cliente Ollama temporal;
- privacidad en logs y errores;
- RAG: respuestas, chunking, embeddings, loader, metadata y retrieval;
- almacenamiento temporal S3 con dobles de test;
- web estatica servida por FastAPI.

## Evaluacion RAG Automatizada

Existe un dataset semilla en `evals/questions.seed.jsonl`, pero no hay runner de
evaluacion RAG/modelos implementado todavia.

Comando revisado:

```powershell
.\.venv\Scripts\python.exe -m backend.app.cli.evaluate_models
```

Resultado:

```text
Model evaluation is not implemented yet
```

Conclusion: no habia una evaluacion RAG automatizada disponible que ejecutar en
esta tarea. El hueco queda documentado para abordarlo cuando se implemente la
evaluacion automatica de recuperacion y abstencion.

## Resultado

La tarea de pruebas automatizadas locales queda completada con los gates
disponibles actualmente:

- lint correcto;
- formato correcto;
- tests correctos;
- ausencia de runner RAG automatizado documentada.

No se han usado documentos privados, prompts reales, respuestas reales ni
secretos en esta validacion.
