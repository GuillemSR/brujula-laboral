# Evaluaciones

Dataset y criterios para comparar modelos, prompts y recuperacion RAG.

## Dataset inicial

`questions.seed.jsonl` contiene preguntas semilla para evaluar respuestas del asistente.
Cada linea es un objeto JSON independiente con esta estructura:

- `id`: identificador estable de la pregunta.
- `difficulty`: `sencilla`, `media` o `compleja`.
- `scope`: `personal` para casos de una persona trabajadora o `general` para informacion general laboral/sindical.
- `question`: pregunta en lenguaje natural.
- `tags`: temas principales.
- `expected`: comportamiento esperado de alto nivel, no una respuesta literal.

Criterios iniciales:

- Exactitud laboral/sindical.
- Citas correctas.
- Deteccion de datos faltantes.
- Distincion entre ley, convenio y orientacion practica.
- Prudencia ante casos sensibles.
- Claridad para ciudadania.
- Coste y latencia.
