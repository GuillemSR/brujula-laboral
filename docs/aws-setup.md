# AWS Setup Manual

Configuracion inicial prevista para un proyecto personal.

## Principios

- Crear lo minimo.
- Documentar cada recurso creado.
- Activar budgets antes de pruebas intensivas.
- No guardar contenido sensible en logs.
- No subir credenciales al repositorio.

## Estado operativo actual, 2026-06-24

- Recursos generales y bucket temporal: `eu-south-2` (Espana).
- Entrada de Bedrock Runtime: `eu-west-3` (Paris).
- Perfil de desarrollo: `eu.amazon.nova-micro-v1:0`.
- Motivo de la separacion: la cuenta tiene acceso operativo a Bedrock desde
  Paris, mientras las invocaciones iniciadas en Espana siguen devolviendo
  `Too many tokens per day`.
- El perfil `eu.*` puede enrutar dentro de la geografia europea. No garantiza
  procesamiento exclusivo en Paris ni en Espana.
- Configuracion y modelos probados: `docs/modelos-bedrock.md`.

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

### Comparativa inicial, 2026-06-04

AWS MCP se valido mediante el proxy configurado en Codex. La comparativa se ha
contrastado tambien con documentacion publica oficial de AWS y debe revalidarse
en consola antes de crear recursos reales o habilitar modelos.

| Region | Encaje para el proyecto | Bedrock y modelos | Servicios base | Riesgos / notas |
| --- | --- | --- | --- | --- |
| `eu-south-2` Espana | Mejor residencia geografica para una herramienta laboral espanola. | Bedrock tiene soporte regional para familias utiles como Amazon Nova, Titan Text Embeddings V2 y Claude 3.5 Sonnet. No aparecen algunos candidatos economicos de Mistral, `gpt-oss-20b` o `gpt-oss-120b` en las filas revisadas. | S3, KMS, CloudWatch, CloudWatch Logs, Lambda, PrivateLink, IAM, STS y otros servicios base estan incluidos o tienen endpoints regionales. | Candidato preferente si los modelos habilitados en la cuenta cubren calidad/coste. Hay que comprobar quotas y acceso real a modelos en la consola. |
| `eu-west-1` Irlanda | Region europea madura y operativamente simple. | Mejor cobertura practica para candidatos de bajo coste: Mistral Large, Ministral 14B/8B/3B, Mixtral, `gpt-oss-20b`, `gpt-oss-120b`, Amazon Nova y Titan Text Embeddings V2. | S3, KMS, CloudWatch y servicios base disponibles. | Buen fallback si `eu-south-2` no ofrece el modelo objetivo o tiene limitaciones de quota. Residencia sigue en UE, pero no en Espana. |
| `eu-central-1` Frankfurt | Region europea madura con buena postura de residencia UE. | Soporta Amazon Nova, Titan Text Embeddings V2, Claude 3.5 Sonnet, `gpt-oss-20b` y `gpt-oss-120b`. La cobertura Mistral revisada es mas limitada que Irlanda para los candidatos economicos iniciales. | S3, KMS, CloudWatch y servicios base disponibles. | Alternativa razonable si se prioriza Frankfurt o si el modelo elegido esta disponible alli. |

Decision actual: mantener `eu-south-2` como region principal de recursos y
almacenamiento, y usar temporalmente `eu-west-3` como region de entrada de
Bedrock. `BEDROCK_REGION` permite separar ambos destinos sin mover el bucket.
Evitar perfiles Global Cross-Region para consultas con datos privados; si se usa
Cross-Region, preferir perfiles EU/Geo y documentar que prompts y respuestas
pueden procesarse dentro de la geografia europea, no necesariamente en una sola
region.

### Comparativa de costes, 2026-06-04

Costes revisados con AWS Price List API via AWS MCP. Cifras en USD, sin impuestos
y sujetas a cambios. Para el MVP, los costes que mas afectan a la decision son
Bedrock/modelos y posibles endpoints privados; S3, KMS, Lambda y logs son
secundarios a bajo volumen.

Esta tabla se conserva como fotografia historica de la comparativa regional. La
configuracion vigente y los precios actuales de los modelos usados se mantienen
en `docs/modelos-bedrock.md`.

| Servicio / concepto | `eu-west-1` Irlanda | `eu-south-2` Espana | `eu-central-1` Frankfurt | Lectura |
| --- | ---: | ---: | ---: | --- |
| S3 Standard, primeros 50 TB | 0.023 USD/GB-mes | 0.023 USD/GB-mes | 0.0245 USD/GB-mes | Espana e Irlanda empatan; Frankfurt algo mas caro. |
| CloudWatch Logs, ingesta custom | 0.57 USD/GB | 0.57 USD/GB | 0.63 USD/GB | Espana e Irlanda empatan; Frankfurt algo mas caro. |
| VPC Interface Endpoint, hora | 0.011 USD/h | 0.011 USD/h | 0.012 USD/h | Espana e Irlanda empatan; Frankfurt algo mas caro. |
| Lambda requests | 0.20 USD / millon | 0.20 USD / millon | 0.20 USD / millon | Sin diferencia relevante. |
| Lambda compute x86, tier inicial | 0.0000166667 USD/GB-s | 0.0000166667 USD/GB-s | 0.0000166667 USD/GB-s | Sin diferencia relevante. |
| KMS customer managed key | 1 USD/clave-mes | 1 USD/clave-mes | 1 USD/clave-mes | Sin diferencia relevante. |
| KMS requests simetricas | 0.03 USD / 10k requests | 0.03 USD / 10k requests | 0.03 USD / 10k requests | Sin diferencia relevante. |

Bedrock, precios observados de modelos candidatos:

| Modelo / uso | `eu-west-1` Irlanda | `eu-south-2` Espana | `eu-central-1` Frankfurt | Lectura |
| --- | ---: | ---: | ---: | --- |
| Amazon Nova Micro | 0.000040 input / 0.000160 output por 1k tokens | 0.000039 input / 0.000156 output por 1k tokens | Disponible, validar cifra exacta antes de usar | Espana es ligeramente mas barata que Irlanda. |
| Amazon Nova Lite | 0.000069 input / 0.000276 output por 1k tokens | 0.000066 input / 0.000264 output por 1k tokens | Disponible, validar cifra exacta antes de usar | Buen candidato barato si se opera en Espana. |
| Amazon Nova Pro | 0.000920 input / 0.003680 output por 1k tokens | 0.000880 input / 0.003520 output por 1k tokens | Disponible, validar cifra exacta antes de usar | Espana es ligeramente mas barata. |
| Amazon Nova 2 Lite | 0.000374 input / 0.003157 output por 1k tokens | 0.000363 input / 0.003205 output por 1k tokens | Disponible, validar cifra exacta antes de usar | Muy parecido; no decide region. |
| Mistral Ministral 3B | 0.000120 input / 0.000120 output por 1k tokens | No encontrado en precios/modelos revisados | 0.000120 input / 0.000120 output por 1k tokens | Irlanda/Frankfurt dan mas variedad barata. |
| OpenAI gpt-oss-20b | 0.000080 input / 0.000350 output por 1k tokens | No encontrado en precios/modelos revisados | 0.000090 input / 0.000400 output por 1k tokens | Irlanda es mas barata y con mas cobertura. |

Conclusion historica: `eu-south-2` era la region objetivo por residencia. La
cuota efectiva de la cuenta obliga actualmente a iniciar Bedrock desde
`eu-west-3`; los demas recursos permanecen en Espana.

Fuentes oficiales revisadas:

- Amazon Bedrock Regional availability: https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html
- Amazon S3 endpoints and quotas: https://docs.aws.amazon.com/general/latest/gr/s3.html
- AWS KMS endpoints and quotas: https://docs.aws.amazon.com/general/latest/gr/kms.html
- Amazon CloudWatch endpoints and quotas: https://docs.aws.amazon.com/general/latest/gr/cw_region.html
- AWS Services by Region: https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/

Validacion AWS MCP, 2026-06-04:

- `get_regional_availability` confirma `Amazon Bedrock`, `Amazon Simple Storage
  Service (S3)`, `AWS Key Management Service (KMS)` y `Amazon CloudWatch` como
  `isAvailableIn` en `eu-west-1`, `eu-south-2` y `eu-central-1`.
- `aws account enable-region --region-name eu-south-2` se ejecuto correctamente.
- `aws account list-regions` muestra `eu-south-2` como `ENABLED`, y
  `eu-west-1`/`eu-central-1` como `ENABLED_BY_DEFAULT`.
- `aws sts get-caller-identity --region eu-south-2` responde correctamente.
- `aws bedrock list-foundation-models --region eu-south-2` devuelve 16 modelos,
  incluyendo Amazon Nova Micro/Lite/Pro, Nova 2 Lite, Titan Text Embeddings V2,
  Claude Haiku 4.5, Claude Sonnet 4/4.5/4.6 y Claude Opus 4.5/4.6/4.7/4.8.

## Checklist inicial

- [ ] Cuenta o entorno AWS separado para el proyecto.
- [x] Budget mensual y alarma de coste.
- [ ] IAM minimo para desarrollo.
- [x] Modelos Bedrock candidatos habilitados.
- [x] Bucket S3 temporal con bloqueo publico.
- [x] Cifrado S3 con KMS o SSE-S3 segun fase.
- [x] Lifecycle corto para documentos temporales.
- [x] CloudWatch sin prompts, respuestas ni documentos.

## Budget y alarmas de coste

Configuracion creada el 2026-06-09 con AWS MCP:

- Nombre: `brujula-laboral-mensual`.
- Tipo: `COST`.
- Periodicidad: mensual.
- Limite: 10 USD/mes.
- Moneda: AWS Budgets rechazo `EUR` para esta cuenta con el error `EUR is not
  in the supported unit set: [USD]`, por lo que se uso `USD`.
- Alcance: cuenta completa, sin filtros por servicio o region.
- Notificaciones por email:
  - `FORECASTED` mayor que 50%.
  - `ACTUAL` mayor que 80%.
  - `ACTUAL` mayor que 100%.
- Estado validado: budget `HEALTHY`; las tres notificaciones estan en estado
  `OK` y tienen suscriptor email configurado.

Evidencia AWS MCP:

- `budgets.CreateBudget` creo el budget en el endpoint de Billing
  `us-east-1`.
- `budgets.DescribeBudget` devolvio `BudgetLimit.Amount = 10.0`,
  `BudgetLimit.Unit = USD`, `TimeUnit = MONTHLY` y `HealthStatus.Status =
  HEALTHY`.
- `budgets.DescribeNotificationsForBudget` devolvio las tres notificaciones
  configuradas.
- `budgets.DescribeSubscribersForNotification` confirmo un suscriptor email por
  cada notificacion. La direccion no se documenta en el repositorio para evitar
  guardar datos personales.

## Modelos Bedrock candidatos

Seleccion inicial para pruebas de bajo coste:

- Generacion por defecto: Amazon Nova Micro, perfil de inferencia
  `eu.amazon.nova-micro-v1:0`.
- Generacion fallback barato: Amazon Nova Lite, perfil de inferencia
  `eu.amazon.nova-lite-v1:0`.
- Embeddings: Amazon Titan Text Embeddings V2, modelo
  `amazon.titan-embed-text-v2:0`.

Validacion real repetida el 2026-06-24:

- `eu-west-3` permite invocar los perfiles EU de Nova Micro, Nova Lite y Nova
  Pro.
- Claude Haiku 4.5 y Claude Sonnet 4.5 tambien responden desde `eu-west-3`.
- Claude Sonnet 4 original ya esta marcado como Legacy y no debe adoptarse.
- `eu-south-2` sigue rechazando Nova Micro por cuota diaria de la cuenta, aunque
  el perfil aparezca en el catalogo.
- Nova Micro cuesta 0.052 USD por millon de tokens de entrada y 0.208 USD por
  millon de tokens de salida en Paris segun AWS Price List API, con precio
  efectivo desde el 2026-06-01.

Decision: usar Nova Micro desde `eu-west-3` durante el desarrollo. Nova Lite
queda como fallback barato. La seleccion para produccion se decidira mediante el
benchmark de Fase 6. Ver `docs/modelos-bedrock.md` para la matriz completa.

## Bucket temporal de documentos

Configuracion creada y validada el 2026-06-09 con AWS MCP en `eu-south-2`:

- Nombre: `brujula-laboral-temp-docs-8fffbf8674`.
- Uso previsto: almacenamiento efimero de documentos privados subidos por el
  usuario durante una consulta.
- Acceso publico: bloqueado con `BlockPublicAcls`, `IgnorePublicAcls`,
  `BlockPublicPolicy` y `RestrictPublicBuckets` en `true`.
- Ownership: `BucketOwnerEnforced`, sin ACLs.
- Cifrado por defecto: SSE-S3 (`AES256`) por coste y simplicidad en esta fase.
- Versionado: `Suspended`, para evitar versiones no evidentes de documentos
  temporales.
- Lifecycle: regla `expire-temporary-documents` activa con expiracion a 1 dia y
  aborto de multipart uploads incompletos a 1 dia.
- Etiquetas: `Project=brujula-laboral`, `DataClass=temporary-private-documents`
  y `ManagedBy=manual-aws-mcp`.

Decision: no usar SSE-KMS todavia para evitar el coste fijo de una clave
customer-managed y mantener la configuracion simple durante el prototipo. Antes
de preproduccion o inicio de produccion, revisar si el bucket debe migrar a
SSE-KMS para separar permisos de S3 y KMS, mejorar auditoria de uso de claves y
endurecer la postura ante documentos laborales privados.

Nota operativa: S3 Lifecycle trabaja en dias. El borrado funcional previsto por
la aplicacion seguira siendo explicito y mas corto (`TEMP_DOCUMENT_TTL_MINUTES`,
actualmente 30 minutos); el lifecycle de 1 dia es una red de seguridad, no la
politica principal de retencion.

Evidencia AWS MCP:

- `s3.CreateBucket` creo el bucket en `eu-south-2`.
- `s3.PutPublicAccessBlock` configuro el bloqueo publico completo.
- `s3.PutBucketEncryption` configuro SSE-S3 con `SSEAlgorithm = AES256`.
- `s3.PutBucketLifecycleConfiguration` configuro expiracion y limpieza de
  multipart uploads incompletos a 1 dia.
- `s3.PutBucketVersioning` dejo el versionado en `Suspended`.
- `s3.PutBucketOwnershipControls` configuro `BucketOwnerEnforced`.
- Validacion posterior con `GetBucketLocation`, `GetPublicAccessBlock`,
  `GetBucketEncryption`, `GetBucketLifecycleConfiguration`,
  `GetBucketVersioning` y `GetBucketOwnershipControls` devolvio la configuracion
  esperada.

Validacion repetida el 2026-06-10 tras implementar la subida temporal de
documentos:

- Herramienta: `aws_mcp` mediante `mcp-proxy-for-aws`.
- Operaciones de solo lectura: `sts.GetCallerIdentity`, `s3.GetBucketLocation`,
  `s3.GetPublicAccessBlock`, `s3.GetBucketEncryption`,
  `s3.GetBucketLifecycleConfiguration`, `s3.GetBucketVersioning`,
  `s3.GetBucketOwnershipControls`, `s3.GetBucketTagging` y
  `s3.ListObjectsV2`.
- Resultado: bucket en `eu-south-2`, bloqueo publico completo, cifrado SSE-S3
  `AES256`, lifecycle `expire-temporary-documents` activo con expiracion a 1 dia
  y aborto de multipart uploads a 1 dia, versionado `Suspended`, ownership
  `BucketOwnerEnforced`, etiquetas esperadas y `KeyCount = 0`.
- No se enviaron documentos, texto extraido, prompts, respuestas ni secretos al
  MCP.

## CloudWatch Logs

Validacion realizada el 2026-06-10 con AWS MCP:

- Regiones revisadas: `eu-south-2`, `eu-west-1` y `eu-central-1`.
- Metodo: `logs.DescribeLogGroups` para inventariar CloudWatch Logs en cada
  region y `logs.ListTagsForResource` para localizar grupos del proyecto por
  etiqueta `Project=brujula-laboral`.
- Resultado: las tres regiones devolvieron `0` log groups.
- No se solicitaron ni leyeron mensajes de logs. La validacion se limito a
  metadatos y conteos.

Conclusion: en el estado actual no existe ningun log group de CloudWatch Logs en
las regiones revisadas, por lo que no hay prompts, respuestas, textos extraidos
ni documentos guardados en CloudWatch Logs para este proyecto.

Limitacion: esta validacion debe repetirse cuando el backend este desplegado en
AWS o cuando se habilite el flujo de documentos privados, porque entonces si
podrian crearse log groups de aplicacion.

## Uso del AWS MCP

Usarlo primero para consulta y verificacion. Siempre que este disponible, validar con AWS MCP el correcto funcionamiento o configuracion de los servicios AWS antes de dar una tarea por cerrada.

- disponibilidad regional;
- lectura de documentacion;
- inspeccion de recursos;
- validacion de comandos.

Evitar que cree arquitectura compleja automaticamente hasta estabilizar el diseno.

### Configuracion en Codex

Este proyecto incluye una configuracion local de Codex en `.codex/config.toml`
para cargar el servidor `aws_mcp` al trabajar desde este repositorio. El proyecto
debe estar marcado como confiable para que Codex cargue esa capa local.

Requisitos operativos:

- mantener una sesion AWS activa con `aws login`;
- abrir una nueva sesion de Codex o reiniciar Codex si el MCP se configuro o se
  reautentico despues de iniciar el hilo;
- no enviar prompts reales, respuestas, documentos privados, textos extraidos ni
  secretos al AWS MCP;
- mantener `default_tools_approval_mode = "prompt"` para que las acciones AWS
  potencialmente mutables pidan confirmacion.

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
