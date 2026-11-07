# Person 1 Assumptions Register

1. Authoritative agencies may update values post-publication; supersession logic must retain history.
2. Tier C sources are signal-only and cannot directly produce confirmed status.
3. Unknown values are preserved as `null` and never imputed for critical fields.
4. Event IDs can be pre-assigned by upstream ingestion or deterministically generated.
5. Location naming may vary across sources; normalization does not erase original source text.
6. Published timestamps are trusted only when parseable and logically ordered (`published <= retrieved`).
7. Initial confidence calibration is policy-driven; future calibration requires retrospective evaluation data.
8. This pipeline supports decision support, not autonomous life-safety command decisions.

