# ADR-002: Authoritative Source Hierarchy

## Status
Accepted

## Date
2026-06-15

## Context
Catholic doctrine has varying levels of authority. The knowledge system must distinguish between infallible dogma, authoritative teaching, and theological opinion. Sources must be vetted to ensure doctrinal accuracy.

## Decision
Implement a strict source hierarchy:
1. **Vatican.va** - Official Holy See documents (highest authority)
2. **USCCB.org** - United States Conference of Catholic Bishops
3. **EWTN.com** - Eternal Word Television Network (approved Catholic media)
4. **New Advent** - Historical Church Fathers and theological texts
5. **Project Gutenberg** - Public domain texts (Douay-Rheims Bible)

## Rationale
1. **Doctrinal Safety**: Only approved sources for theological claims
2. **Hierarchical Authority**: Vatican > USCCB > EWTN > New Advent
3. **Citation Traceability**: Every claim must reference a specific document
4. **Gap Honesty**: System admits when sources are insufficient

## Alternatives Considered
- **Open-ended web scraping**: Rejected due to risk of non-authoritative sources
- **Academic databases**: Rejected for accessibility and copyright concerns
- **User-provided sources**: Rejected for quality control

## Consequences
- Limited to approved Catholic institutional domains
- Must maintain source URL mappings
- Requires periodic verification of source availability
- System cannot answer questions outside approved corpus
