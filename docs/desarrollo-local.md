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
.\scripts\dev.ps1
```

Comprobar el endpoint de salud:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Pruebas

Ejecutar la suite de tests:

```powershell
.\scripts\test.ps1
```

Ejecutar solo los tests del backend:

```powershell
.\scripts\test.ps1 backend/tests
```

## Lint y formato

Revisar el codigo con Ruff:

```powershell
.\scripts\lint.ps1
```

Aplicar formato con Ruff:

```powershell
.\scripts\format.ps1
```

Comprobar formato sin modificar archivos:

```powershell
.\scripts\format.ps1 --check
```

## Comprobacion rapida antes de subir cambios

Para cambios de codigo, ejecutar como minimo:

```powershell
.\scripts\check.ps1
```

Para cambios solo de documentacion, basta con revisar el diff y comprobar que no se han incluido credenciales, documentos privados ni contenido sensible.
