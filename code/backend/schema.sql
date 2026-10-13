-- =============================================================================
-- QUALITATIVE DATA ANALYSIS TOOL (QDAT) - DATABASE SCHEMA BLUEPRINT
-- CAPSTONE PROJECT: WSU DGSS & CPTS 421/423 (TEAM SEB / TEAM 1)
-- TARGET DBMS: POSTGRESQL 16+ WITH PGVECTOR EXTENSION
-- RESPONSIBLE: SURAKANTI SRISHANTH REDDY (BACKEND ARCHITECTURE & DATA MODELING)
-- =============================================================================

-- ENABLE REQUIRED EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- -----------------------------------------------------------------------------
-- HELPER FUNCTION: AUTO-UPDATE UPDATED_AT TIMESTAMP
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 1. PROJECTS TABLE
-- REPRESENTS INDEPENDENT QUALITATIVE ANALYSIS WORKSPACES/STUDIES (E.G., FOCUS GROUP 2026).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- 2. DOCUMENTS TABLE
-- STORES FULL QUALITATIVE SOURCE FILES (TRANSCRIPTS, SURVEY RESPONSES, FIELD NOTES).
-- EXACT SOURCE GROUNDING REFERENCES OFFSETS IN RAW_CONTENT.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL DEFAULT 'txt', -- 'TXT', 'DOCX', 'PDF'
    raw_content TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    char_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb, -- FOCUS GROUP DATE, PARTICIPANT DEMOGRAPHICS, ETC.
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_char_count_non_negative CHECK (char_count >= 0)
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE TRIGGER trg_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- 3. DOCUMENT_CHUNKS TABLE
-- STORES SEGMENTED PASSAGES OF DOCUMENTS WITH EXACT COORDINATE OFFSETS AND DENSE VECTORS.
-- EMBEDDING DIMENSION IS 384 (MATCHING ALL-MINILM-L6-V2 LOCAL SENTENCE-TRANSFORMERS).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    token_count INTEGER,
    embedding vector(384), -- 384-DIMENSIONAL DENSE VECTOR FOR SEMANTIC SIMILARITY
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_chunk_char_offsets CHECK (start_char >= 0 AND end_char > start_char),
    CONSTRAINT uq_document_chunk_order UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_coordinates ON document_chunks(document_id, start_char, end_char);

-- HNSW (HIERARCHICAL NAVIGABLE SMALL WORLD) INDEX FOR LOCAL SUB-SECOND COSINE DISTANCE SEARCHES
-- M=16 (BI-DIRECTIONAL LINKS PER NODE), EF_CONSTRUCTION=64 (BUILD EXPLORATION FACTOR)
CREATE INDEX idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- -----------------------------------------------------------------------------
-- 4. CODES TABLE (HIERARCHICAL CODEBOOK)
-- STORES QUALITATIVE CODING CATEGORIES WITH PARENT-CHILD TREE NESTING.
-- SUPPORTS DEDUCTIVE (PREDEFINED) AND INDUCTIVE (EMERGENT) QUALITATIVE CODES.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES codes(id) ON DELETE CASCADE, -- NULL INDICATES TOP-LEVEL ROOT CODE
    name VARCHAR(120) NOT NULL,
    description TEXT, -- QUALITATIVE CODING CRITERIA / DEFINITIONS
    color VARCHAR(24) NOT NULL DEFAULT '#3B82F6', -- HEX COLOR FOR SYNCHRONIZED UI HIGHLIGHTING
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_project_code_name UNIQUE (project_id, parent_id, name)
);

CREATE INDEX idx_codes_project_id ON codes(project_id);
CREATE INDEX idx_codes_parent_id ON codes(parent_id);
CREATE TRIGGER trg_codes_updated_at
BEFORE UPDATE ON codes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- 5. ANNOTATIONS TABLE (SOURCE GROUNDING & TRACEABILITY)
-- CONNECTS QUALITATIVE CODES TO EXACT TEXT LOCATIONS IN SOURCE DOCUMENTS.
-- ENABLES BIDIRECTIONAL CLICK-TO-CITE VERIFICATION BETWEEN CODES AND SOURCE TRANSCRIPTS.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE SET NULL,
    code_id UUID NOT NULL REFERENCES codes(id) ON DELETE CASCADE,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    selected_text TEXT NOT NULL, -- VERBATIM QUOTE EXCERPTED FROM RAW_CONTENT
    confidence_score REAL NOT NULL DEFAULT 1.0, -- 1.0 FOR MANUAL, (0.0-1.0) FOR AI SUGGESTION
    is_ai_suggested BOOLEAN NOT NULL DEFAULT FALSE,
    is_verified BOOLEAN NOT NULL DEFAULT TRUE, -- HUMAN-IN-THE-LOOP: TRUE ONCE APPROVED BY ANALYST
    notes TEXT, -- RESEARCHER MEMO / INTERPRETIVE COMMENT
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_annotation_char_offsets CHECK (start_char >= 0 AND end_char > start_char),
    CONSTRAINT chk_confidence_range CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0)
);

CREATE INDEX idx_annotations_document_id ON annotations(document_id);
CREATE INDEX idx_annotations_code_id ON annotations(code_id);
CREATE INDEX idx_annotations_chunk_id ON annotations(chunk_id);
CREATE INDEX idx_annotations_coordinates ON annotations(document_id, start_char, end_char);
CREATE TRIGGER trg_annotations_updated_at
BEFORE UPDATE ON annotations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- 6. CLUSTERS TABLE (UNSUPERVISED SEMANTIC THEME DISCOVERY)
-- STORES THEMATIC CLUSTERS COMPUTED VIA HDBSCAN / K-MEANS OVER VECTOR EMBEDDINGS.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    summary TEXT,
    algorithm VARCHAR(50) NOT NULL DEFAULT 'hdbscan', -- 'HDBSCAN', 'KMEANS'
    suggested_code_id UUID REFERENCES codes(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb, -- HYPER-PARAMETERS, SILHOUETTE SCORE, ETC.
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clusters_project_id ON clusters(project_id);

-- JUNCTION TABLE CONNECTING CLUSTERS TO SPECIFIC DOCUMENT CHUNKS
CREATE TABLE IF NOT EXISTS cluster_chunks (
    cluster_id UUID NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    distance_to_centroid REAL,
    is_exemplar BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (cluster_id, chunk_id)
);

CREATE INDEX idx_cluster_chunks_chunk_id ON cluster_chunks(chunk_id);

-- =============================================================================
-- SAMPLE SEED DATA (DEMONSTRATING DGSS QUALITATIVE RESEARCH TRANSCRIPT)
-- =============================================================================

INSERT INTO projects (id, name, description) VALUES
('11111111-1111-1111-1111-111111111111', 'Rural Community Infrastructure Study 2026', 'DGSS qualitative evaluation of focus group transcripts regarding municipal broadband and utilities.');

INSERT INTO documents (id, project_id, filename, file_type, raw_content, file_size_bytes, char_count, metadata) VALUES
('22222222-2222-2222-2222-222222222222', 
 '11111111-1111-1111-1111-111111111111', 
 'Focus_Group_Session_A.txt', 
 'txt', 
 'Participant 1: Our local broadband access has been completely unreliable for the past two years. The fiber installation was halted due to contractor disputes. Participant 2: In our precinct, community social trust is high, but the public utility district lacks transparency in budget allocation.', 
 295, 
 295, 
 '{"session": "A", "participants": 2, "interviewer": "Season Hoard"}'::jsonb
);

-- CHUNK 1: CHARACTERS 0 TO 157
INSERT INTO document_chunks (id, document_id, chunk_index, chunk_text, start_char, end_char, token_count) VALUES
('33333333-3333-3333-3333-333333333331', 
 '22222222-2222-2222-2222-222222222222', 
 0, 
 'Participant 1: Our local broadband access has been completely unreliable for the past two years. The fiber installation was halted due to contractor disputes.', 
 0, 
 157, 
 28
);

-- CHUNK 2: CHARACTERS 158 TO 295
INSERT INTO document_chunks (id, document_id, chunk_index, chunk_text, start_char, end_char, token_count) VALUES
('33333333-3333-3333-3333-333333333332', 
 '22222222-2222-2222-2222-222222222222', 
 1, 
 'Participant 2: In our precinct, community social trust is high, but the public utility district lacks transparency in budget allocation.', 
 158, 
 295, 
 24
);

-- ROOT CODE: INFRASTRUCTURE BARRIERS
INSERT INTO codes (id, project_id, parent_id, name, description, color, is_ai_generated) VALUES
('44444444-4444-4444-4444-444444444441', 
 '11111111-1111-1111-1111-111111111111', 
 NULL, 
 'Infrastructure Barriers', 
 'Physical, contractual, or technical obstacles affecting public community utilities.', 
 '#EF4444', 
 FALSE
);

-- CHILD CODE: BROADBAND & FIBER HURDLES (NESTED UNDER INFRASTRUCTURE BARRIERS)
INSERT INTO codes (id, project_id, parent_id, name, description, color, is_ai_generated) VALUES
('44444444-4444-4444-4444-444444444442', 
 '11111111-1111-1111-1111-111111111111', 
 '44444444-4444-4444-4444-444444444441', 
 'Broadband & Fiber Hurdles', 
 'Specific delays, outages, or contractor issues impacting rural high-speed internet.', 
 '#F97316', 
 FALSE
);

-- GROUNDED ANNOTATION LINKING THE VERBATIM EXCERPT TO THE CHILD CODE
INSERT INTO annotations (id, document_id, chunk_id, code_id, start_char, end_char, selected_text, confidence_score, is_ai_suggested, is_verified, notes) VALUES
('55555555-5555-5555-5555-555555555551', 
 '22222222-2222-2222-2222-222222222222', 
 '33333333-3333-3333-3333-333333333331', 
 '44444444-4444-4444-4444-444444444442', 
 15, 
 156, 
 'Our local broadband access has been completely unreliable for the past two years. The fiber installation was halted due to contractor disputes.', 
 1.0, 
 FALSE, 
 TRUE, 
 'Primary participant evidence of delayed broadband infrastructure rollout.'
);
