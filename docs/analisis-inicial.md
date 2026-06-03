# Análisis de viabilidad y diseño técnico

> Revisión: este documento versiona el análisis inicial del proyecto en `docs/`. Las decisiones de arquitectura, privacidad y alcance se consideran base de trabajo; las referencias a precios, modelos y disponibilidad regional deben revalidarse antes de cualquier decisión operativa.

Documento fuente conservado en `docs/analisis-inicial.docx`.

Asistente público para consultas laborales y sindicales en España

Enfoque propuesto: herramienta gratuita, sin fricción, orientada a derechos laborales, sindicales y convenios colectivos; con RAG propio y modelos gestionados mediante AWS Bedrock.

| Fecha | 3 de junio de 2026 |
| --- | --- |
| Estado | Documento de análisis y propuesta técnica |
| Ámbito | España; consultas laborales, sindicales y convenios colectivos |
| Decisión base | AWS Bedrock como proveedor de modelos gestionados; RAG y datos bajo control propio |

> Nota importante: este documento no es asesoramiento jurídico, fiscal, de ciberseguridad ni de protección de datos. Sirve como base para decidir arquitectura, alcance y próximos pasos. Antes de operar públicamente con documentos privados, conviene hacer revisión legal/RGPD y, probablemente, una evaluación de impacto si el riesgo lo exige.

## 1. Resumen ejecutivo

La idea es viable si se acota correctamente: no como "abogado automático", sino como una infraestructura pública de orientación laboral y sindical para España, basada en fuentes verificables, con privacidad por diseño y con advertencias claras sobre sus límites. La especialización inicial debería centrarse en Estatuto de los Trabajadores, derechos sindicales, funcionamiento de la representación legal de las personas trabajadoras, guías oficiales y un conjunto priorizado de convenios colectivos.

La decisión de usar AWS Bedrock tiene sentido por tres motivos: reduce la complejidad de operar GPUs propias, permite pago por uso, y mantiene el proyecto dentro de un entorno AWS ya conocido. Bedrock no ofrece los modelos propietarios GPT-5.x de OpenAI, pero sí ofrece un abanico amplio de modelos de Anthropic, Amazon, Mistral, Meta, Qwen, OpenAI OSS y otros proveedores. AWS documenta además que los proveedores de modelos no tienen acceso a las cuentas de despliegue de Bedrock ni a los prompts/completions de clientes, lo que es una ventaja relevante frente a llamar a APIs directas de cada proveedor. [S2]

La recomendación final para un MVP serio es: AWS Bedrock + RAG propio + backend privado en AWS + almacenamiento temporal cifrado para documentos + no guardar prompts/respuestas/documentos + métricas agregadas + VPC con PrivateLink para Bedrock si se van a procesar contratos, nóminas u otros documentos privados.

| Decisión | Recomendación |
| --- | --- |
| Posicionamiento | Herramienta pública, gratuita, sin login obligatorio, orientada a acceso a derechos laborales y sindicales. |
| Modelo de IA | AWS Bedrock como capa gestionada. Probar primero modelos coste/calidad: Mistral Large/Ministral, Claude Haiku/Sonnet, Amazon Nova, Qwen si está disponible en región adecuada. |
| RAG | Priorizar RAG sobre fine-tuning. El corpus y los metadatos son más importantes que entrenar un modelo jurídico. |
| Documentos privados | No guardarlos por defecto. Procesamiento efímero, cifrado y borrado automático. |
| VPC | No estrictamente obligatoria para una demo sin documentos, pero sí recomendable para un MVP que procese documentos privados. |
| Coste | Muy variable por modelo y uso. Con modelos económicos de Bedrock, el coste de inferencia puede ser muy bajo; los costes fijos vendrán de RAG, endpoints privados, logs, almacenamiento y monitorización. |

## 2. Idea general y enfoque de producto

La propuesta consiste en una web con interfaz tipo chat, sin fricción, para que cualquier persona pueda hacer consultas laborales y sindicales en España. La herramienta debería priorizar claridad, trazabilidad y prudencia. No debe venderse como sustituto de un abogado, graduado social, sindicato o inspección de trabajo, sino como un primer punto de orientación basado en fuentes públicas.

### 2.1. Diferenciación frente a herramientas legales comerciales

El hueco del proyecto no está en competir con bases jurídicas profesionales ni con productos legaltech para despachos. La diferencia estaría en combinar: acceso gratuito, foco ciudadano, ausencia de registro obligatorio, privacidad estricta, lenguaje claro, fuentes oficiales y orientación sindical/laboral práctica.

| Dimensión | Herramientas jurídicas comerciales | Propuesta del proyecto |
| --- | --- | --- |
| Usuario objetivo | Abogados, asesorías, departamentos legales. | Ciudadanía, personas trabajadoras, secciones sindicales, delegados/as, sindicatos pequeños. |
| Modelo de negocio | Suscripción, demo, registro, captación comercial. | Uso gratuito, donativos, posible apoyo de entidades. |
| Fricción | Alta o media: registro, email, prueba, pago. | Mínima: sin cuenta para consultas básicas. |
| Privacidad | Depende del proveedor y contrato. | Parte central del producto: no guardar conversaciones ni documentos por defecto. |
| Contenido | Amplio, jurídico profesional. | Laboral/sindical español, convenios y guías prácticas. |

### 2.2. Alcance inicial del MVP

- Consultas sobre derechos laborales generales: jornada, permisos, vacaciones, despido, baja, modificación de condiciones, salario, contrato, horas extra.
- Consultas sindicales básicas: qué es un sindicato, cómo afiliarse, derechos de representación, comités de empresa, delegados de personal, secciones sindicales, garantías básicas.
- Consultas sobre convenios colectivos: cómo identificar el convenio, qué prevalece entre Estatuto y convenio, búsqueda por sector/provincia/empresa cuando sea posible.
- Respuestas siempre con fuentes y con distinción entre norma general, convenio aplicable y orientación práctica.
- Sin login obligatorio, sin historial persistente, sin analíticas invasivas.

### 2.3. Funciones a posponer

- Análisis masivo de jurisprudencia: CENDOJ tiene restricciones y no debe convertirse en el núcleo del MVP sin revisión formal.
- Cuentas de usuario, carpetas de casos y seguimiento avanzado de procesos laborales.
- Automatización completa de descarga de todos los convenios.

## 3. Corpus documental y RAG

La pieza diferencial no es solo el modelo, sino el corpus y su estructura. Un RAG mediocre puede hacer que un modelo muy bueno responda mal. En cambio, un RAG bien curado permite usar modelos más baratos y mantener trazabilidad.

### 3.1. Fuentes prioritarias

| Fuente | Uso en el sistema | Observaciones |
| --- | --- | --- |
| BOE - legislación consolidada | Estatuto de los Trabajadores, LOLS, LGSS, LPRL, LRJS y normativa complementaria. | El BOE ofrece API para acceso, descarga y reutilización de legislación consolidada. [S9] |
| REGCON | Convenios colectivos, acuerdos colectivos, planes de igualdad. | Útil para localizar textos de convenios y metadatos. [S10] |
| CCNCC - Mapa de Negociación Colectiva | Ayuda para orientar convenio aplicable por actividad/CNAE. | Debe tratarse como orientativo, no como verdad absoluta. [S11] |
| Guía Laboral del Ministerio / SEPE / Seguridad Social | Explicaciones oficiales para ciudadanía. | Útil para respuestas divulgativas y de contexto. |
| Webs sindicales | Afiliación y funcionamiento interno de sindicatos concretos. | Se debe separar marco general de información específica de cada sindicato. |
| CENDOJ | Jurisprudencia futura. | No recomendable para MVP masivo sin revisar condiciones de reutilización. |

### 3.2. Estructura del índice RAG

El chunking debería hacerse por unidad jurídica o funcional, no por páginas de PDF. Para legislación, la unidad natural suele ser artículo/apartado; para convenios, cláusula/capítulo/artículo; para guías, sección de pregunta-respuesta o bloque temático.

| Metadato | Motivo |
| --- | --- |
| tipo_fuente | Distinguir ley, convenio, guía oficial, fuente sindical, sentencia, FAQ propia. |
| fuente_url | Permitir cita verificable. |
| fecha_publicacion / fecha_actualizacion | Evitar respuestas basadas en textos obsoletos. |
| vigente_desde / vigente_hasta | Fundamental para convenios y normas consolidadas. |
| ámbito_territorial | España, comunidad autónoma, provincia, empresa. |
| ámbito_funcional / sector / CNAE | Clave para identificar convenio aplicable. |
| jerarquia | Ley, convenio, acuerdo, guía, FAQ; ayuda a resolver conflictos. |
| codigo_convenio / identificador BOE / ELI | Trazabilidad técnica y jurídica. |

### 3.3. Estrategia de recuperación

Clasificar la consulta: laboral general, convenio, sindical, documento privado, alta sensibilidad, fuera de alcance.

Extraer datos clave: provincia, sector, empresa, contrato, fecha del problema, tipo de relación laboral, convenio indicado por el usuario.

Recuperar fuentes por capas: primero normativa general, luego convenio aplicable, luego guía oficial o FAQ.

Rerank de resultados para evitar meter contexto irrelevante.

Generar respuesta con citas y señalando incertidumbre cuando falten datos.

## 4. Estrategia de modelos: AWS Bedrock frente a OpenAI

AWS Bedrock es una API gestionada que permite invocar modelos de distintos proveedores desde un único entorno AWS. Según la página de precios de Bedrock, el servicio incluye proveedores como Amazon, Anthropic, Cohere, DeepSeek, Google, Meta, Mistral AI, Moonshot AI, NVIDIA, OpenAI OSS Models, Qwen, Stability AI, Writer y Z AI. [S1]

### 4.1. Qué significa usar modelos en Bedrock

La principal ventaja es que no tienes que administrar GPUs ni servidores de inferencia. Tu backend llama a Bedrock por API, paga por uso y puede cambiar de modelo según coste/calidad. Además, Bedrock encapsula el acceso a modelos de terceros dentro de AWS, lo que facilita IAM, CloudTrail, KMS, VPC endpoints y monitorización.

| Ventaja | Impacto |
| --- | --- |
| Pago por uso | Evita pagar una GPU 24/7 desde el inicio. |
| Escalabilidad gestionada | Bedrock absorbe la infraestructura de inferencia. |
| Multi-proveedor | Permite probar Claude, Mistral, Nova, Llama, Qwen, gpt-oss, etc. |
| Privacidad frente a proveedores de modelos | AWS documenta que los proveedores no acceden a logs, prompts ni completions de clientes en Bedrock. [S2] |
| Integración AWS | IAM, CloudTrail, VPC endpoints, KMS, S3, WAF, API Gateway, Lambda/ECS. |

### 4.2. Comparativa cualitativa Bedrock vs OpenAI/Azure OpenAI

| Criterio | AWS Bedrock | OpenAI / Azure OpenAI |
| --- | --- | --- |
| Calidad frontera | Muy alta con Claude/otros modelos, pero no incluye los GPT-5.x propietarios como tal. | OpenAI GPT-5.5/GPT-5.4 probablemente sigue siendo referencia en tareas frontier según sus propios benchmarks. [S6] |
| Coste | Puede ser muy bajo con Mistral/Nova/modelos pequeños; depende de región y modelo. | GPT-5.4 mini es razonable; GPT-5.5 es caro para uso masivo. [S7] |
| Privacidad operativa | Muy buena si ya estás en AWS y usas Bedrock + IAM + VPC endpoint. | Muy buena en Azure OpenAI, pero te saca de AWS. |
| Experiencia del desarrollador | Muy buena si ya conoces AWS. | Muy buena si ya conoces OpenAI API. |
| Modelo open-weight | Sí: Llama, Qwen, Mistral, gpt-oss, etc. según región. | OpenAI propietario en API; Azure ofrece modelos OpenAI gestionados. |

### 4.3. Modelos candidatos en Bedrock

La recomendación no es elegir por nombre, sino crear un benchmark propio con preguntas reales. Aun así, el primer conjunto de pruebas debería incluir:

| Categoría | Modelos candidatos | Uso previsto |
| --- | --- | --- |
| Principal económico | Ministral 14B, Amazon Nova Lite/Pro, Claude Haiku, Qwen 32B si región/precio encaja. | Consultas generales y sindicales sencillas. |
| Principal equilibrado | Mistral Large 3, Claude Sonnet, Amazon Nova Pro/Premier, Qwen 235B si disponible. | Consultas laborales con más matices y RAG complejo. |
| Premium puntual | Claude Opus o modelos de máxima capacidad disponibles en Bedrock. | Casos delicados, validación, segunda opinión, evaluación interna. |
| Auxiliares | Cohere Rerank/Embed, Titan Embeddings, Safeguard, modelos pequeños. | Reranking, embeddings, clasificación y seguridad. |

### 4.4. Relación con OpenAI GPT-5.x

Bedrock incluye modelos OpenAI OSS como gpt-oss-20b y gpt-oss-120b en algunas regiones, pero no son equivalentes a GPT-5.5/GPT-5.4 propietarios. La página oficial de OpenAI lista GPT-5.5 a 5 USD/M input y 30 USD/M output, GPT-5.4 a 2,5 USD/M input y 15 USD/M output, y GPT-5.4 mini a 0,75 USD/M input y 4,5 USD/M output. [S7]

## 5. Costes estimados

Las cifras siguientes son orientativas. Deben validarse en AWS Pricing Calculator y en la consola de Bedrock para la región elegida, porque la disponibilidad de modelos y precios varía por región, tier y fecha.

### 5.1. Supuesto base de cálculo

| Variable | Valor usado |
| --- | --- |
| Tokens de entrada por consulta | 8.000 tokens: pregunta + instrucciones + fragmentos RAG + metadatos. |
| Tokens de salida por consulta | 1.500 tokens. |
| Objetivo de respuesta | Respuesta detallada con citas, no excesivamente larga. |
| RAG optimizado | Objetivo futuro: bajar a 4.000-5.000 tokens de entrada cuando sea posible. |

| Modelo | Input/M | Output/M | Coste consulta | 10k consultas | 100k consultas | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| Bedrock Mistral - Ministral 14B EU | $0.24 | $0.24 | $0.00228 | $23 | $228 | Precio Europa Irlanda/Milán según AWS Bedrock pricing. [S5] |
| Bedrock Mistral - Magistral Small EU | $0.59 | $1.76 | $0.00736 | $74 | $736 | Precio Europa Irlanda/Milán según AWS Bedrock pricing. [S5] |
| Bedrock Mistral - Mistral Large 3 ref. | $0.5 | $1.5 | $0.00625 | $62 | $625 | Referencia US/Sydney; validar disponibilidad/precio en región europea concreta. [S5] |
| Bedrock OpenAI OSS 120B ref. | $0.1545 | $0.618 | $0.00216 | $22 | $216 | Referencia publicada para Sydney; validar región. [S12] |
| OpenAI GPT-5.4 mini ref. | $0.75 | $4.5 | $0.01275 | $128 | $1275 | Referencia API OpenAI; no es Bedrock. [S7] |
| OpenAI GPT-5.4 ref. | $2.5 | $15 | $0.04250 | $425 | $4250 | Referencia API OpenAI; no es Bedrock. [S7] |
| OpenAI GPT-5.5 ref. | $5 | $30 | $0.08500 | $850 | $8500 | Referencia API OpenAI; no es Bedrock. [S7] |

### 5.2. Lectura de costes

Con modelos económicos de Bedrock, el coste por consulta puede estar por debajo de 0,01 USD incluso con contexto RAG amplio. Esto cambia mucho la viabilidad frente a autoalojar una GPU 24/7. En cambio, usar modelos frontera de OpenAI como referencia puede superar el coste de una GPU dedicada cuando el volumen crece. Para una herramienta gratuita, la clave será enrutar: modelo barato para la mayoría, modelo medio para casos complejos, modelo premium solo para validación o consultas delicadas.

| Escenario | Consultas/mes | Modelo principal | Coste inferencia aprox. | Infra adicional MVP | Total orientativo |
| --- | --- | --- | --- | --- | --- |
| Beta pequeña | 1.000 | Ministral 14B / Nova / Haiku | $2-$15 | 50-150 EUR | 60-170 EUR/mes |
| Beta pública | 10.000 | Ministral 14B + algunos casos modelo medio | $25-$150 | 80-220 EUR | 110-370 EUR/mes |
| MVP con uso real | 50.000 | Modelo barato + 10-20% modelo medio | $150-$700 | 150-400 EUR | 300-1.100 EUR/mes |
| Escala alta | 100.000+ | Enrutado multi-modelo | $300-$1.500+ | 250-700 EUR | 600-2.300+ EUR/mes |

## 6. Arquitectura técnica recomendada

Arquitectura propuesta para un MVP con procesamiento de documentos privados:

Usuario -> CloudFront/API Gateway -> Backend Lambda/ECS -> S3 temporal cifrado -> extracción de texto efímera -> RAG propio -> Bedrock Runtime vía VPC Endpoint -> respuesta con citas -> borrado automático del documento y texto extraído.

| Capa | Servicio AWS sugerido | Notas de diseño |
| --- | --- | --- |
| Frontend | S3 + CloudFront o Amplify | Web estática tipo chat. Evitar trackers externos. |
| Entrada/API | API Gateway + WAF opcional | Rate limit, protección básica contra abuso, CORS controlado. |
| Backend | Lambda al inicio; ECS/Fargate si crece | Orquestación RAG, validaciones, llamada a Bedrock, borrado de temporales. |
| Documentos temporales | S3 cifrado con KMS | Bucket separado, lifecycle corto, sin backups, sin logs de contenido. |
| Extracción | Lambda/ECS worker | PDF/text/docx; evitar OCR salvo necesidad. |
| RAG | Aurora/PostgreSQL + pgvector, OpenSearch Serverless o FAISS gestionado por app | Para MVP, PostgreSQL+pgvector suele ser simple y suficiente. |
| Modelo | Amazon Bedrock Runtime | Invocación por API gestionada. Preferible con VPC endpoint si hay documentos privados. |
| Logs | CloudWatch | Solo logs técnicos: latencia, error codes, tokens, coste. Nunca prompt/documento/respuesta. |
| Secretos | AWS Secrets Manager o SSM Parameter Store | Credenciales, configuración, tokens internos. |
| Seguridad | IAM, KMS, VPC, Security Groups, CloudTrail | Principio de mínimo privilegio. |

### 6.1. Flujo de consulta sin documento

El usuario introduce una pregunta laboral/sindical.

El backend clasifica la consulta y detecta datos faltantes.

El RAG recupera fragmentos de normativa, convenio y guías oficiales.

El backend construye un prompt con instrucciones, contexto y fuentes.

Bedrock genera la respuesta.

El backend valida formato básico, añade citas y devuelve respuesta.

Se guardan solo métricas agregadas.

### 6.2. Flujo de consulta con documento privado *

El usuario sube contrato, nómina, carta de despido u otro documento.

El archivo se guarda temporalmente en S3 cifrado con KMS o se procesa en memoria si el tamaño lo permite.

Se extrae texto en un worker privado.

El texto extraído se usa solo para esa consulta.

El texto NO se indexa en el RAG global.

La respuesta se genera con el documento como contexto temporal y fuentes oficiales como soporte.

Se borra el archivo y el texto extraído mediante lifecycle/borrado explícito.

Se guardan únicamente métricas agregadas no identificativas.

* A falta de revisar como recomienda hacerlo aws para documentos adjuntados al prompt

## 7. Protección de datos y privacidad

El proyecto trataría potencialmente datos personales y, en algunos casos, datos especialmente sensibles o de alto impacto: salud, afiliación sindical, conflictos laborales, sanciones, salarios, documentos de identidad, contratos, nóminas y comunicaciones empresariales. Por tanto, el diseño debe aplicar minimización, privacidad por defecto, cifrado, no retención y separación estricta entre corpus público y documentos privados.

### 7.1. Bedrock y acceso de proveedores al contenido

AWS documenta que Bedrock usa cuentas de despliegue por región y proveedor, operadas por el equipo de Bedrock. Los proveedores de modelos no tienen acceso a esas cuentas ni a los logs de Bedrock, por lo que no tienen acceso a prompts ni completions de clientes. [S2]

Esto no elimina tus obligaciones: sigues siendo responsable de la configuración, de los datos que decides enviar a Bedrock, de tus logs, de la retención, de los permisos IAM y de informar correctamente a usuarios. AWS recuerda que aplica el modelo de responsabilidad compartida: AWS protege la infraestructura cloud; tú proteges la configuración y el contenido que subes o procesas. [S2]

### 7.2. Ubicación de datos y RGPD

AWS permite elegir las regiones donde se almacena el contenido y afirma que no mueve ni replica contenido fuera de las regiones elegidas sin acuerdo, salvo lo necesario para prestar servicios iniciados por el cliente o por obligación legal. [S8]

Para España, la recomendación sería operar en regiones de la UE cuando el modelo elegido lo permita: Irlanda, Frankfurt, París, Milán, Estocolmo o España según disponibilidad. En la práctica, la disponibilidad de modelos Bedrock puede variar por región, por lo que conviene validar la región final modelo a modelo.

### 7.3. Política de datos recomendada

| Dato | Tratamiento recomendado |
| --- | --- |
| Prompt del usuario | No guardar. Solo en memoria durante la petición. |
| Respuesta del modelo | No guardar salvo consentimiento explícito en una función futura de historial. |
| Documento subido | Guardar solo temporalmente; cifrado; borrado automático; no incluir en backups. |
| Texto extraído del documento | No persistir. No indexar. No entrenar. No loguear. |
| Métricas | Guardar agregadas: tokens, coste, latencia, errores, modelo usado, categoría de consulta. |
| IP | Evitar guardar IP completa; usar rate limit con hash temporal o mecanismos no persistentes cuando sea posible. |
| Historial de chat | No en MVP. En futuro, solo con cuenta, consentimiento y controles claros. |

### 7.4. Aviso al usuario antes de subir documentos

- No subas documentos que no sean necesarios para la consulta.
- Oculta o elimina datos irrelevantes si puedes.
- El documento se procesa de forma temporal y no se conserva por defecto.
- No se usa para entrenar modelos ni mejorar el sistema.
- La respuesta es orientación informativa y no sustituye asesoramiento profesional.

## 8. VPC, PrivateLink y costes de red

Una VPC no es "un producto de seguridad mágico"; es una red privada virtual donde puedes aislar recursos, definir subredes públicas/privadas, controlar tráfico con security groups y enrutar llamadas a servicios AWS mediante endpoints privados.

### 8.1. ¿Es obligatoria?

Para una demo sin documentos privados, no es estrictamente obligatoria. Lambda puede llamar a Bedrock por endpoint público regional usando TLS e IAM. Para un MVP que procese contratos, nóminas u otros documentos laborales privados, sí es recomendable usar VPC + PrivateLink para Bedrock Runtime y endpoint privado/gateway para S3.

| Arquitectura | Seguridad | Coste | Recomendación |
| --- | --- | --- | --- |
| Sin VPC/PrivateLink | TLS + IAM; endpoint público regional. | Más barato y simple. | Aceptable para prototipo sin documentos. |
| VPC sin NAT + endpoints | Tráfico privado hacia Bedrock/S3; mejor aislamiento. | Moderado si se usan pocos endpoints. | Recomendado para MVP con documentos. |
| VPC + NAT Gateway | Permite salida a internet desde subred privada. | Puede encarecerse por hora y GB. | Evitar al inicio salvo necesidad clara. |
| VPC multi-AZ completa | Más disponibilidad y resiliencia. | Más endpoints/NAT/ALB/logs. | Cuando haya uso real o requisitos de disponibilidad. |

### 8.2. Qué aporta PrivateLink para Bedrock

AWS documenta que PrivateLink permite crear una conexión privada entre tu VPC y Bedrock, acceder a Bedrock como si estuviera en tu VPC, sin internet gateway, NAT, VPN ni Direct Connect, y sin que las instancias necesiten IP pública. [S3]

- Reduce exposición de red: el backend no necesita salir a internet para invocar Bedrock.
- Permite endpoint policies para limitar acciones como InvokeModel e InvokeModelWithResponseStream.
- Permite private DNS: el código puede seguir llamando al endpoint regional estándar y AWS enruta por el endpoint privado.
- Facilita una postura de privacidad más defendible cuando se procesan documentos sensibles.

### 8.3. Costes que preocupan

La VPC como concepto no suele ser el gran coste. Lo que encarece son NAT Gateway, múltiples endpoints por AZ, balanceadores, tráfico entre AZs, logs excesivos, IPs públicas y servicios gestionados sobredimensionados.

| Elemento | Cómo se cobra | Impacto |
| --- | --- | --- |
| NAT Gateway | Hora provisionada + GB procesado. AWS muestra ejemplo de 0,045 USD/h y 0,045 USD/GB en una región de ejemplo. [S4] | Puede ser caro si se usa para todo el tráfico saliente. |
| S3 Gateway Endpoint | AWS indica que evita el cargo de NAT para tráfico hacia S3 y que no tiene cargos horarios/de procesamiento en el ejemplo citado. [S4] | Muy recomendable. |
| Interface Endpoint / PrivateLink | Hora por endpoint/AZ + GB procesado. PrivateLink lista 0,01 USD/GB para el primer PB mensual. [S13] | Moderado si usas pocos endpoints. |
| Public IPv4 | 0,005 USD/h por IP pública en uso o idle. [S4] | Evitar IPs públicas innecesarias. |
| CloudWatch Logs | Por ingesta/retención. | Controlar volumen y nunca loguear contenido sensible. |

## 9. Controles de seguridad mínimos

| Control | Decisión recomendada |
| --- | --- |
| IAM | Roles mínimos por servicio. Bedrock InvokeModel solo para backend/worker concreto. |
| KMS | Cifrado de S3, bases de datos y secretos con claves gestionadas o customer-managed según madurez. |
| S3 | Bucket temporal separado, bloqueo de acceso público, lifecycle corto, políticas estrictas. |
| Logs | No prompts, no respuestas, no textos extraídos, no documentos, no datos personales en tags. |
| CloudTrail | Activado para auditoría de acciones AWS. |
| Macie | Valorar para detectar datos sensibles en S3 si se guardan documentos temporalmente. AWS lo recomienda como servicio gestionado para descubrir datos sensibles en S3. [S2] |
| WAF/rate limit | Proteger API pública contra abuso y scraping. |
| Separación de entornos | dev/pre/pro separados; datos reales solo en pro. |
| Backups | Solo corpus público y configuración; nunca documentos temporales de usuario. |
| DPIA/EIPD | Valorar evaluación de impacto por tratar documentos laborales privados. |

## 10. Roadmap técnico

| Fase | Objetivo | Entregables |
| --- | --- | --- |
| 0. Prueba local | Validar RAG y prompts sin usuarios. | Corpus BOE básico, 20-50 preguntas test, benchmark de modelos Bedrock. |
| 1. MVP sin documentos | Consulta laboral/sindical con fuentes. | Frontend simple, backend, RAG, Bedrock, citas, métricas agregadas. |
| 2. MVP con documentos efímeros | Permitir subir contrato/carta/nómina de forma temporal. | S3 temporal cifrado, extracción, VPC endpoint Bedrock, borrado automático, aviso usuario. |
| 3. Convenios priorizados | Mejorar valor real del producto. | Ingesta manual/semiautomática de convenios prioritarios por sector/provincia. |
| 4. Calidad y evaluación | Reducir errores y alucinaciones. | Dataset de evaluación, LLM-as-judge interno, validaciones, guardrails. |
| 5. Historial opcional | Carpetas/casos para usuarios que quieran seguimiento. | Cuenta opcional, consentimiento, retención configurable, exportar/borrar datos. |

### 10.1. Benchmark recomendado

Antes de fijar modelo, crear un dataset de 100-200 preguntas reales y evaluarlas con varios modelos. Cada respuesta debe puntuarse por exactitud, citas, claridad, prudencia y capacidad para detectar datos faltantes.

| Criterio | Peso |
| --- | --- |
| No inventa fuentes ni normas | Muy alto |
| Cita correctamente fragmentos recuperados | Muy alto |
| Distingue ley, convenio y orientación práctica | Muy alto |
| Detecta que falta provincia/convenio/sector/fecha | Muy alto |
| No da consejo jurídico tajante cuando no procede | Alto |
| Explica en lenguaje claro | Alto |
| Coste y latencia | Medio |

## 11. Riesgos principales y mitigaciones

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Respuesta incorrecta en asunto laboral sensible | Alto | Citas obligatorias, abstención, pedir datos faltantes, benchmark, disclaimer y recomendación de acudir a sindicato/asesoría en casos críticos. |
| Filtración o retención accidental de documentos | Muy alto | S3 temporal, KMS, no logs de contenido, lifecycle, revisión de buckets, pruebas de borrado. |
| Guardar datos personales sin base clara | Alto | No guardar prompts/respuestas/documentos en MVP; métricas agregadas. |
| Elegir convenio incorrecto | Alto | Función específica de detección de convenio, pedir CNAE/provincia/empresa, señalar incertidumbre. |
| Costes inesperados | Medio/alto | Budgets, alarms, límites de tokens, rate limit, modelo barato por defecto, logs controlados. |
| Abuso del servicio gratuito | Medio/alto | Rate limits, WAF, captcha no invasivo si hace falta, cuotas temporales por IP hash. |
| Prompt injection en documentos | Medio | Tratar documentos como datos no confiables; instrucciones del sistema fuertes; no ejecutar instrucciones dentro de documentos. |
| Dependencia de AWS/Bedrock | Medio | Abstraer proveedor de modelo en backend; mantener prompts y RAG portables. |

## 12. Recomendación final de arquitectura para el MVP

La recomendación final es empezar con AWS Bedrock, no con GPU autoalojada. Permite validar la idea con menor complejidad, pago por uso y buena postura de privacidad dentro de AWS. Para el primer MVP público con documentos privados, usaría VPC + PrivateLink, pero evitando NAT Gateway al inicio salvo que sea necesario.

| Decisión | Propuesta concreta |
| --- | --- |
| Proveedor IA | AWS Bedrock. |
| Región | UE cuando el modelo esté disponible: Irlanda/Frankfurt/París/Milán/Estocolmo/España según disponibilidad. |
| Modelo principal | Probar Ministral 14B / Mistral Large 3 / Amazon Nova / Claude Haiku o Sonnet. |
| Modelo premium | Claude Sonnet/Opus u otro modelo de alta capacidad para casos complejos. |
| RAG | Propio; no usar documentos de usuario para entrenar ni indexar globalmente. |
| Privacidad | No guardar contenido de usuario. Procesamiento efímero. Métricas agregadas. |
| Red | API pública mínima + backend privado + VPC endpoint bedrock-runtime + S3 gateway endpoint. |
| Coste objetivo inicial | 100-400 EUR/mes para beta pequeña; 300-1.100 EUR/mes con más uso según modelo/enrutado. |

## Anexo A. Checklist de implementación inicial

- Crear cuenta/entorno AWS separado para el proyecto.
- Definir región y validar modelos Bedrock disponibles.
- Crear budgets y alarmas de coste desde el día 1.
- Crear frontend estático sin trackers.
- Crear API con rate limit básico.
- Crear bucket de corpus público y bucket temporal separado para documentos privados.
- Cifrar S3 con KMS y bloquear acceso público.
- Implementar RAG con metadatos fuertes.
- Implementar no-logging de prompts/respuestas/documentos.
- Implementar borrado explícito y lifecycle corto en S3 temporal.
- Crear VPC endpoint bedrock-runtime si se procesan documentos privados.
- Crear S3 Gateway Endpoint para evitar NAT en acceso a S3.
- Crear dataset de evaluación antes de abrir públicamente.
- Redactar aviso legal, política de privacidad y condiciones de uso.

## Anexo B. Preguntas de evaluación de calidad

- ¿Me pueden despedir estando de baja?
- ¿Qué prevalece, el Estatuto de los Trabajadores o mi convenio?
- Trabajo en comercio en Barcelona, ¿qué convenio puede aplicarme?
- ¿Puede mi empresa saber que estoy afiliado a un sindicato?
- ¿Qué es un delegado sindical y qué garantías tiene?
- ¿Cuántos días me corresponden por mudanza?
- Me han cambiado el horario de un día para otro, ¿pueden hacerlo?
- ¿Qué diferencia hay entre delegado de personal, comité de empresa y sección sindical?
- ¿Puedo negarme a hacer horas extra?
- ¿Qué pasos debería seguir si me sancionan en el trabajo?

## Anexo C. Fuentes consultadas

> [S1] AWS Bedrock Pricing - lista de proveedores y modelos: https://aws.amazon.com/bedrock/pricing/

> [S2] Amazon Bedrock - Data protection: https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html

> [S3] Amazon Bedrock - VPC interface endpoints / AWS PrivateLink: https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html

> [S4] Amazon VPC Pricing: https://aws.amazon.com/vpc/pricing/

> [S5] Amazon Bedrock Pricing - Mistral AI models: https://aws.amazon.com/bedrock/pricing/

> [S6] OpenAI - Introducing GPT-5.5: https://openai.com/index/introducing-gpt-5-5/

> [S7] OpenAI API Pricing: https://openai.com/api/pricing/

> [S8] AWS Data Privacy FAQ: https://aws.amazon.com/compliance/data-privacy-faq/

> [S9] BOE - API de datos abiertos: https://www.boe.es/datosabiertos/api/api.php

> [S10] REGCON - Registro y Depósito de Convenios Colectivos: https://expinterweb.mites.gob.es/regcon/index.htm

> [S11] CCNCC - Mapa de Negociación Colectiva: https://ccncc.mites.gob.es/mapa-de-negociacion-colectiva

> [S12] Amazon Bedrock Pricing - OpenAI OSS models: https://aws.amazon.com/bedrock/pricing/

> [S13] AWS PrivateLink Pricing: https://aws.amazon.com/privatelink/pricing/

> [S14] AEPD - Recomendaciones para usuarios de chatbots con IA: https://www.aepd.es/infografias/info-recomendaciones-chatbots-ia.pdf

> Limitaciones del documento: Los precios y la disponibilidad de modelos cambian con frecuencia. Antes de tomar una decisión definitiva se debe comprobar la consola de AWS Bedrock, AWS Pricing Calculator, la región elegida y los términos contractuales aplicables. Las referencias a OpenAI GPT-5.x se incluyen como comparación de calidad/coste, no como recomendación de uso en este proyecto si la decisión es operar sobre AWS Bedrock.
