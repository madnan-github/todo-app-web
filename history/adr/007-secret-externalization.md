# ADR-007: Secret Externalization Strategy

**Date**: 2025-12-31
**Status**: Accepted
**Decider**: Claude Code (AI-First Development)

## Context

Production deployments must not contain hardcoded secrets. JWT and authentication secrets must be sourced exclusively from environment variables with fail-fast behavior if missing.

## Decision

Implement secret externalization with the following strategy:

1. **No default values in production**: Secrets default to empty strings
2. **Fail-fast validation**: Application exits immediately if secrets missing in production
3. **Validation at startup**: Secrets checked during module import
4. **Clear error messages**: Specific indication of which secrets are missing

## Implementation

```python
# In config.py
class Settings(BaseSettings):
    jwt_secret_key: str = ""  # No default in production
    better_auth_secret: str = ""  # No default in production

    def validate_production_secrets(self) -> None:
        if self.is_production():
            missing = []
            if not self.jwt_secret_key:
                missing.append("JWT_SECRET_KEY")
            if not self.better_auth_secret:
                missing.append("BETTER_AUTH_SECRET")

            if missing:
                raise ValidationError(
                    f"Missing required secrets: {', '.join(missing)}"
                )

# At module level
try:
    settings = validate_settings()
except ValidationError as e:
    print(f"FATAL: {e}", file=sys.stderr)
    sys.exit(1)
```

## Rationale

1. **Fail-Fast**: Catches misconfiguration before deployment, not during runtime
2. **Security**: No secrets in codebase, no risk of accidental commit
3. **Clarity**: Clear error messages indicate exactly what's missing
4. **Defense in Depth**: Multiple validation layers

## Alternatives Considered

1. **Lazy validation**: Rejected - error only discovered when feature used
2. **Warnings only**: Rejected - secrets might be forgotten
3. **Default secrets with warning**: Rejected - still a security risk

## Consequences

### Positive
- Strong security guarantee
- Clear deployment requirements
- Prevents production incidents from missing secrets

### Negative
- Requires environment setup before deployment
- More strict than some frameworks (intentional)

## Environment Variables Required

| Variable | Purpose | Generation |
|----------|---------|------------|
| `JWT_SECRET_KEY` | JWT token signing | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `BETTER_AUTH_SECRET` | Better Auth sessions | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |

**Reference**: `backend/src/config.py:20-94`
