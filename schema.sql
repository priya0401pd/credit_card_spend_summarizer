-- Enable PGVector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents Registry
CREATE TABLE IF NOT EXISTS documents (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
filename TEXT UNIQUE NOT NULL,
source_path TEXT,
ingested_at TIMESTAMP DEFAULT NOW()
);

-- Multimodal Chunks
CREATE TABLE IF NOT EXISTS multimodal_chunks (
id BIGSERIAL PRIMARY KEY,

```
doc_id UUID NOT NULL
REFERENCES documents(id)
ON DELETE CASCADE,

chunk_type TEXT NOT NULL,
element_type TEXT,

content TEXT NOT NULL,

image_path TEXT,
mime_type TEXT,

page_number INT,
section TEXT,
source_file TEXT,

position JSONB,
metadata JSONB,

content_hash TEXT UNIQUE,

embedding VECTOR(1536)
```

);

CREATE INDEX idx_chunks_doc
ON multimodal_chunks(doc_id);

CREATE INDEX idx_chunks_section
ON multimodal_chunks(section);

CREATE INDEX idx_chunks_page
ON multimodal_chunks(page_number);

CREATE INDEX idx_chunks_embedding
ON multimodal_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
