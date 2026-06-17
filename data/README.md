# Data Directory

This directory contains all application data for the Catholic Sovereign Knowledge System.

## Contents

### kbmd/ (82 MB)
Normalized markdown documents organized by category:
- `scripture/` - 73 books of the Bible (Douay-Rheims)
- `magisterium/ccc/` - Catechism of the Catholic Church (17 parts)
- `canonlaw/` - Code of Canon Law (7 books)
- `liturgy/` - GIRM and liturgical texts (7 documents)
- `fathers/` - Ante-Nicene and Nicene Fathers (27 volumes)
- `doctorate/` - Church Doctor writings (16 documents)
- `magisterium/encyclicals/` - Papal encyclicals (26 documents)
- `magisterium/exhortations/` - Apostolic exhortations (8 documents)
- `magisterium/vatican_ii/` - Vatican II documents (13 documents)
- `social-teaching/` - Catholic social teaching (5 documents)
- `mariology/` - Marian documents (13 documents)
- `manifest.json` - Document manifest with metadata

### kb-index/ (183 MB)
Generated indexes and embeddings:
- `catalog.json` - Complete document catalog (212 documents)
- `chunks/` - Chunked documents by category
- `embeddings/` - Vector embeddings (index.bin + chunks.json)
- `topic-index.json` - Topic to document mapping
- `cross-references.json` - Cross-reference links between documents
- `scripture-refs.json` - Scripture references
- `ccc-refs.json` - CCC paragraph references
- `canon-refs.json` - Canon law references
- `doc-refs.json` - Document references

### sources/ (41 MB)
Raw and normalized source documents:
- `raw/` - Original HTML downloads from authoritative sources
- `normalized/` - Processed markdown files (empty until build runs)

### outputs/
Generated artifacts (empty until queries produce results):
- `study-guides/`
- `timelines/`
- `comparisons/`
- `doctrinal-briefs/`

### .env
Environment configuration for Ollama and directory paths.

## Usage

To rebuild the knowledge base from this data:

```bash
# 1. Copy this data directory to a new location
cp -r data/ /path/to/new/location/

# 2. Update .env if needed
cd /path/to/new/location/

# 3. Rebuild indexes
python3 kb-tools/build-indexes.py

# 4. Start web UI
python3 kb-tools/server.py
```

## Source Statistics

| Category | Documents | Size |
|----------|-----------|------|
| Scripture | 73 | 11.5 MB |
| Magisterium (CCC) | 17 | 3.9 MB |
| Canon Law | 7 | 0.7 MB |
| Liturgy | 7 | 0.9 MB |
| Church Fathers | 27 | 62.7 MB |
| Church Doctors | 16 | 0.2 MB |
| Encyclicals | 26 | 2.6 MB |
| Exhortations | 8 | 0.6 MB |
| Vatican II | 13 | 0.8 MB |
| Social Teaching | 5 | 1.1 MB |
| Mariology | 13 | 0.2 MB |
| **Total** | **212** | **85.2 MB** |
