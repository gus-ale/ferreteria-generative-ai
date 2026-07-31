# Modelo de seguridad

## Activos protegidos

- Claves del proveedor.
- Credencial administrativa.
- Datos de productos.
- Historial de conversaciones.
- Documentos indexados.
- Disponibilidad y presupuesto.

## Amenazas consideradas

- Prompt injection directa.
- Instrucciones maliciosas dentro de documentos.
- Extracción de secretos.
- Herramientas no autorizadas.
- Argumentos inválidos.
- Bucles de agente.
- Entradas excesivas.
- Duplicación de documentos.
- Errores externos filtrados al usuario.

## Controles

| Riesgo | Control |
|---|---|
| Prompt injection | Guardrail de entrada y separación de instrucciones |
| Inyección indirecta | Documentos tratados como datos no confiables |
| Herramienta peligrosa | Allowlist de solo lectura |
| Argumento incorrecto | Pydantic y límites |
| Secreto en salida | Redacción de patrones |
| Acción administrativa | `X-Admin-Key` |
| Bucle | `MAX_AGENT_TURNS` |
| Entrada extensa | Longitud Pydantic y guardrail |
| Error externo | Excepciones de dominio controladas |
| Abuso de costo | Modo demo, límites y métricas |

## Límites

Las expresiones regulares no garantizan resistencia completa contra prompt
injection. En producción se deben combinar:

- Autenticación real.
- Principio de menor privilegio.
- Aprobaciones humanas.
- Rate limiting.
- Moderación según el dominio.
- Evals adversariales.
- Auditoría de herramientas.
- Revisión periódica de permisos y secretos.

## Divulgación

No incluir secretos reales en issues. Usar el mecanismo indicado en
`SECURITY.md`.
