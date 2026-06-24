# Modelos Bedrock para desarrollo

Estado validado el 2026-06-24 en la cuenta AWS del proyecto.

## Configuracion activa

```env
AI_PROVIDER=bedrock
AWS_REGION=eu-south-2
BEDROCK_REGION=eu-west-3
BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
```

`AWS_REGION` sigue apuntando a Espana para el bucket S3 temporal y los recursos
generales. `BEDROCK_REGION` selecciona Paris como region de entrada de Bedrock
Runtime. El perfil `eu.*` es geografico europeo: AWS puede procesar la solicitud
en las regiones europeas incluidas en el perfil, pero no fuera de esa geografia.

## Modelo por defecto

Amazon Nova Micro es el modelo de desarrollo por defecto porque es el mas barato
de los modelos de texto verificados y es suficiente para validar integracion,
prompts, RAG, citas y experiencia web.

Precio on-demand observado con AWS Price List API para `eu-west-3`, efectivo
desde el 2026-06-01:

| Modelo | Entrada por 1M tokens | Salida por 1M tokens | Uso previsto |
| --- | ---: | ---: | --- |
| Nova Micro | 0.052 USD | 0.208 USD | Desarrollo por defecto |
| Nova Lite | 0.088 USD | 0.352 USD | Alternativa barata con mas capacidad |
| Nova Pro | 1.18 USD | 4.72 USD | Solo pruebas comparativas posteriores |

Los precios no incluyen impuestos y pueden cambiar. Antes de un benchmark o
despliegue publico se deben consultar de nuevo AWS Pricing y la consola.

## Acceso verificado

Se hicieron invocaciones sinteticas de pocos tokens mediante
`bedrock-runtime.Converse`; no se enviaron consultas reales ni documentos.

| Region de entrada | Perfil o modelo | Resultado |
| --- | --- | --- |
| `eu-west-3` | `eu.amazon.nova-micro-v1:0` | Operativo |
| `eu-west-3` | `eu.amazon.nova-lite-v1:0` | Operativo |
| `eu-west-3` | `eu.amazon.nova-pro-v1:0` | Operativo |
| `eu-west-2` | `amazon.nova-lite-v1:0` | Operativo in-region |
| `eu-west-2` | `amazon.nova-pro-v1:0` | Operativo in-region |
| `eu-west-3` | `eu.anthropic.claude-haiku-4-5-20251001-v1:0` | Operativo |
| `eu-west-3` | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` | Operativo |
| `eu-west-3` | `eu.anthropic.claude-sonnet-4-20250514-v1:0` | No usar: modelo Legacy |
| `eu-south-2` | `eu.amazon.nova-micro-v1:0` | Bloqueado por cuota diaria de la cuenta |

Que un perfil aparezca en `ListInferenceProfiles` no garantiza que la cuenta
pueda invocarlo. La tabla refleja llamadas reales, no solo visibilidad en el
catalogo.

## Criterio temporal

- Mantener Nova Micro durante el desarrollo para minimizar gasto.
- Usar Nova Lite solo cuando Micro no permita evaluar correctamente una tarea.
- No seleccionar Claude, Nova Pro ni otro modelo como predeterminado hasta tener
  el benchmark de Fase 6.
- Mantener `mock` para tests deterministas y trabajo sin conexion.
- Mantener Ollama solo como alternativa local opcional; ya no es necesario para
  sortear el bloqueo de Bedrock.

## Fuentes oficiales

- Precios: https://aws.amazon.com/bedrock/pricing/
- Ficha de Nova Micro:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html
- Inferencia geografica europea:
  https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html
- Compatibilidad regional:
  https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html
