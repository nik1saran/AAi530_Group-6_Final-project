# Person 1 Threat Model and Mitigations

## Primary Threats
1. Misinformation injection from low-credibility sources.
2. Source spoofing / lookalike domains.
3. Conflicting casualty and location figures across trusted and semi-trusted feeds.
4. Stale data being treated as current truth.
5. Duplicate records causing double-counted impact.
6. Pipeline failure under provider outages and transient network errors.

## Mitigations Implemented
- Tiered source trust model (`tier_a`, `tier_b`, `tier_c`) with status hard blocks.
- Explicit conflict detection with field-level flags.
- Supersession metadata (`is_superseded`) and freshness precedence checks.
- Idempotency key deduplication in fixture pipeline.
- Validation gates that fail on unsupported confirmations.
- Run-manifest logging for replay and auditability.

## Remaining Risks
- Live API connectors require production hardening for auth/rate-limit quotas.
- Entity normalization for multilingual and cross-border location aliases remains iterative.
- Semantic contradiction detection beyond structured fields requires additional NLP controls.

