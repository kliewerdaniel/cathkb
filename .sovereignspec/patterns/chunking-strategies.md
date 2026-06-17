# Pattern: Chunking Strategies

## Description
Documents are chunked into searchable pieces using different strategies based on content type.

## Strategies

### Chapter-Based
- Split on `##` headers
- Best for books, manuals, structured documents
- Used for: encyclicals, exhortations, Church Fathers

### Section-Based
- Split on `##` with size limits
- Best for long documents with multiple sections
- Used for: Vatican II documents, Canon Law

### Paragraph-Based
- Group ~20-30 paragraphs together
- Best for narrative content
- Used for: some theological texts

### File-Based
- One chunk per file
- Best for small files (< 2000 tokens)
- Used for: short documents, prayers

### None
- No chunking
- For very small reference files
- Used for: index files, metadata

## Configuration
```yaml
[categories]
default: chapter
liturgy: section
scripture: file
```

## Token Limits
- Maximum: 2000 tokens per chunk
- Overlap: Optional (for context preservation)
- Metadata: Always preserved (title, source, category)
