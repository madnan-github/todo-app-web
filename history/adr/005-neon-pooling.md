# ADR-005: Neon PostgreSQL Connection Pooling Configuration

**Date**: 2025-12-31
**Status**: Accepted
**Decider**: Claude Code (AI-First Development)

## Context

The TaskFlow backend uses Neon PostgreSQL, a serverless database platform. Neon uses PgBouncer for connection pooling, and the application must be configured to work efficiently with this architecture.

## Decision

Configure SQLAlchemy async engine with the following pool settings for production:

```python
engine = create_async_engine(
    database_url,
    pool_size=10,           # Base connections
    max_overflow=2,         # Burst capacity
    pool_pre_ping=True,     # Verify before use
    pool_recycle=3600,      # Recycle after 1 hour
)
```

## Rationale

1. **pool_size=10**: Recommended for serverless platforms to balance connection availability with Neon limits
2. **max_overflow=2**: Allows 2 additional connections during traffic spikes without exhausting Neon's connection limits
3. **pool_pre_ping=True**: Verifies connection health before each request, preventing stale connection errors
4. **pool_recycle=3600**: Prevents connections from becoming stale due to Neon compute suspend/resume cycles

## Alternatives Considered

1. **Default pool settings**: Rejected - too aggressive for serverless, may exhaust Neon connections
2. **PgBouncer sidecar**: Rejected - over-engineering for free tier, adds complexity
3. **Transaction mode pooling**: Rejected - handled by Neon automatically

## Neon Connection Limits

| Compute Size | Max Connections | Formula |
|--------------|-----------------|---------|
| Free (0.25 CU) | ~100 | `max(100, min(4000, 450.5 * compute_size))` |
| Paid tiers | Higher | Same formula |

Our settings use 10 base + 2 overflow = 12 max connections, well within free tier limits.

## Consequences

### Positive
- Efficient connection utilization
- Handles Neon suspend/resume gracefully
- Prevents connection exhaustion

### Negative
- Slightly higher latency on connection creation (mitigated by pooling)

## Implementation

Configuration is in `backend/src/database.py:24-38`, applied conditionally when:
- `environment == "production"`
- Connection string contains "neon"

**Reference**: `backend/src/database.py:19-45`
