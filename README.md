# Brujula Laboral

Asistente laboral y sindical basado en IA, orientado a facilitar el acceso a informacion clara, fiable y citada sobre derechos laborales en Espana.

## Enfoque inicial

- Proyecto personal y pequeno, con arquitectura simple.
- Backend Python/FastAPI como monolito modular.
- RAG propio inicial para fuentes publicas laborales y sindicales.
- AWS Bedrock como proveedor de modelos gestionados.
- Documentos privados tratados de forma efimera y fuera del indice RAG.
- Configuracion AWS manual al inicio, documentada en el repositorio.

## Estructura

```text
backend/   API, RAG, Bedrock, documentos, almacenamiento y privacidad
web/       Interfaz estatica inicial de chat
corpus/    Fuentes publicas y manifiestos de ingesta
evals/     Preguntas y criterios de evaluacion
docs/      Arquitectura, AWS, privacidad y notas tecnicas
TASKS.md   Seguimiento local de tareas
```

El análisis inicial del producto y la arquitectura está versionado en `docs/analisis-inicial.md`. El documento fuente original se conserva en `docs/analisis-inicial.docx`.

## Arranque local previsto

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload --app-dir backend
```

La configuracion real debe partir de `.env.example`. No se deben commitear credenciales, prompts privados, respuestas de usuarios ni documentos subidos.
