# Desarrollo local

Comandos base para trabajar con el proyecto en una maquina Windows con PowerShell.

## Requisitos

- Python 3.11 o superior.
- PowerShell.
- Git.

## Entorno

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias de aplicacion y desarrollo:

```powershell
pip install -e ".[dev]"
```

La configuracion local debe partir de `.env.example`. Si se necesita un `.env`, crearlo fuera de Git y no commitearlo:

```powershell
Copy-Item .env.example .env
```

## Desarrollo

Arrancar FastAPI en local:

```powershell
uvicorn app.main:app --reload --app-dir backend
```

Comprobar el endpoint de salud:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Pruebas

Ejecutar la suite de tests:

```powershell
pytest
```

Ejecutar solo los tests del backend:

```powershell
pytest backend/tests
```

## Lint y formato

Revisar el codigo con Ruff:

```powershell
ruff check .
```

Aplicar formato con Ruff:

```powershell
ruff format .
```

Comprobar formato sin modificar archivos:

```powershell
ruff format --check .
```

## Comprobacion rapida antes de subir cambios

Para cambios de codigo, ejecutar como minimo:

```powershell
ruff check .
ruff format --check .
pytest
```

Para cambios solo de documentacion, basta con revisar el diff y comprobar que no se han incluido credenciales, documentos privados ni contenido sensible.
