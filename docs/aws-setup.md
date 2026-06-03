# AWS Setup Manual

Configuracion inicial prevista para un proyecto personal.

## Principios

- Crear lo minimo.
- Documentar cada recurso creado.
- Activar budgets antes de pruebas intensivas.
- No guardar contenido sensible en logs.
- No subir credenciales al repositorio.

## Region

Comparar antes de fijar:

- `eu-west-1`: Irlanda.
- `eu-south-2`: Espana.
- `eu-central-1`: Frankfurt.

Criterios:

- disponibilidad de Bedrock y modelos candidatos;
- coste;
- servicios necesarios;
- residencia de datos en UE;
- simplicidad operativa.

## Checklist inicial

- [ ] Cuenta o entorno AWS separado para el proyecto.
- [ ] Budget mensual y alarma de coste.
- [ ] IAM minimo para desarrollo.
- [ ] Modelos Bedrock candidatos habilitados.
- [ ] Bucket S3 temporal con bloqueo publico.
- [ ] Cifrado S3 con KMS o SSE-S3 segun fase.
- [ ] Lifecycle corto para documentos temporales.
- [ ] CloudWatch sin prompts, respuestas ni documentos.

## Uso del AWS MCP

Usarlo primero para consulta y verificacion. Siempre que este disponible, validar con AWS MCP el correcto funcionamiento o configuracion de los servicios AWS antes de dar una tarea por cerrada.

- disponibilidad regional;
- lectura de documentacion;
- inspeccion de recursos;
- validacion de comandos.

Evitar que cree arquitectura compleja automaticamente hasta estabilizar el diseno.

## Validacion recomendada con AWS MCP

Regla general: el MCP debe usarse para verificar configuracion y funcionamiento, no para exponer contenido sensible. No enviar prompts reales, respuestas de usuarios, documentos privados, textos extraidos ni credenciales al MCP.

Validaciones iniciales:

- Region: comprobar disponibilidad de Bedrock, S3, CloudWatch, KMS y servicios necesarios en `eu-west-1`, `eu-south-2` y `eu-central-1`.
- Bedrock: verificar modelos habilitados, region usada y permisos de invocacion antes de conectar el backend.
- IAM: revisar que los roles tengan permisos minimos, especialmente `bedrock:InvokeModel`, S3 temporal y CloudWatch.
- S3 temporal: comprobar bloqueo de acceso publico, cifrado, lifecycle corto y ausencia de versionado/backups innecesarios para documentos privados.
- KMS: validar clave usada por S3 si se usa customer-managed key y permisos de cifrado/descifrado.
- CloudWatch: confirmar que los logs tecnicos existen y que no contienen prompts, respuestas ni documentos.
- Costes: revisar Budget, alarmas y recursos activos antes de pruebas intensivas.
- Red: si se habilita VPC/PrivateLink, comprobar endpoints necesarios y que no se introduzca NAT Gateway salvo necesidad clara.

Evidencia minima a documentar en este archivo:

- fecha de validacion;
- region;
- servicios revisados;
- resultado;
- cambios pendientes;
- comandos o consultas usadas, sin secretos ni datos personales.
