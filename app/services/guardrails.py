import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    re.compile(r"\bignora(?:r)?\b.{0,40}\binstrucciones?\b", re.IGNORECASE),
    re.compile(r"\bignore\b.{0,40}\b(previous|developer|system)\b", re.IGNORECASE),
    re.compile(r"\b(system prompt|prompt del sistema)\b", re.IGNORECASE),
    re.compile(r"\b(jailbreak|developer message)\b", re.IGNORECASE),
]

DESTRUCTIVE_PATTERNS = [
    re.compile(r"\b(drop|truncate)\s+table\b", re.IGNORECASE),
    re.compile(r"\bdelete\s+from\b", re.IGNORECASE),
    re.compile(r"\b(borra|borrá|elimina|eliminá)\b.{0,40}\b(todo|tabla|base)\b", re.IGNORECASE),
]

SECRET_REQUEST_PATTERNS = [
    re.compile(r"\b(api[ _-]?key|clave de (?:la )?api)\b", re.IGNORECASE),
    re.compile(
        r"\b(muestra|mostrá|revela|revelá)\b.{0,40}"
        r"\b(token|secreto|contraseña)\b",
        re.IGNORECASE,
    ),
]

OUTPUT_SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
]


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    category: str | None = None
    reason: str | None = None


def inspect_input(text: str, *, max_characters: int) -> GuardrailDecision:
    if len(text) > max_characters:
        return GuardrailDecision(
            allowed=False,
            category="input_too_long",
            reason=f"Input exceeds the {max_characters}-character limit",
        )

    checks = [
        ("prompt_injection", INJECTION_PATTERNS),
        ("destructive_request", DESTRUCTIVE_PATTERNS),
        ("secret_exfiltration", SECRET_REQUEST_PATTERNS),
    ]
    for category, patterns in checks:
        if any(pattern.search(text) for pattern in patterns):
            return GuardrailDecision(
                allowed=False,
                category=category,
                reason="The request conflicts with the assistant safety boundaries",
            )

    return GuardrailDecision(allowed=True)


def sanitize_output(text: str) -> str:
    sanitized = text
    for pattern in OUTPUT_SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized
