# Pattern: Source Hierarchy

## Description
The system uses a hierarchical source authority model for Catholic doctrinal content.

## Implementation
- Vatican.va documents have highest priority
- USCCB.org provides US-specific pastoral guidance
- EWTN.com offers approved Catholic media content
- New Advent provides historical theological texts
- Project Gutenberg hosts public domain scripture

## Usage
```bash
# Source priority order
sources=(
  "vatican.va"
  "usccb.org"
  "ewtn.com"
  "newadvent.org"
  "gutenberg.org"
)
```

## Validation
- All source URLs must be verified before ingestion
- Duplicate content across sources resolved by hierarchy
- Non-authoritative sources (blogs, opinions) are rejected
