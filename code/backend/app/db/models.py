"""SQLALCHEMY ORM MODELS REPRESENTING THE QDAT RELATIONAL AND VECTOR SCHEMA."""
import uuid
from datetime import datetime
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Project(Base):
    """REPRESENTS A QUALITATIVE STUDY WORKSPACE (E.G. DGSS FOCUS GROUPS 2026)."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    codes = relationship("Code", back_populates="project", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    """STORES A QUALITATIVE SOURCE FILE (TRANSCRIPT, SURVEY RESPONSES, FIELD NOTES)."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False, default="txt")
    raw_content = Column(Text, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False, default=0)
    char_count = Column(Integer, nullable=False, default=0)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index")
    annotations = relationship("Annotation", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("char_count >= 0", name="chk_char_count_non_negative"),
    )


class DocumentChunk(Base):
    """SEGMENTED TEXT CHUNK WITH EXACT CHARACTER OFFSETS AND 384-D DENSE VECTOR EMBEDDINGS."""
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=True)
    embedding = Column(Vector(384), nullable=True)  # ALL-MINILM-L6-V2 DENSE VECTOR
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="chunks")
    annotations = relationship("Annotation", back_populates="chunk")
    cluster_links = relationship("ClusterChunk", back_populates="chunk", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("start_char >= 0 AND end_char > start_char", name="chk_chunk_char_offsets"),
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_order"),
    )


class Code(Base):
    """HIERARCHICAL QUALITATIVE CODEBOOK ITEM SUPPORTING TREE STRUCTURES AND UI COLORS."""
    __tablename__ = "codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("codes.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(24), nullable=False, default="#3B82F6")
    is_ai_generated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="codes")
    parent = relationship("Code", remote_side=[id], backref="children")
    annotations = relationship("Annotation", back_populates="code", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "parent_id", "name", name="uq_project_code_name"),
    )


class Annotation(Base):
    """LINKS QUALITATIVE CODES TO EXACT COORDINATES IN SOURCE TEXT FOR SOURCE GROUNDING."""
    __tablename__ = "annotations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True, index=True)
    code_id = Column(UUID(as_uuid=True), ForeignKey("codes.id", ondelete="CASCADE"), nullable=False, index=True)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    selected_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False, default=1.0)
    is_ai_suggested = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=True)  # HUMAN-IN-THE-LOOP GOVERNANCE
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    document = relationship("Document", back_populates="annotations")
    chunk = relationship("DocumentChunk", back_populates="annotations")
    code = relationship("Code", back_populates="annotations")

    __table_args__ = (
        CheckConstraint("start_char >= 0 AND end_char > start_char", name="chk_annotation_char_offsets"),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="chk_confidence_range"),
    )


class Cluster(Base):
    """UNSUPERVISED THEMATIC CLUSTER DISCOVERED BY HDBSCAN / K-MEANS."""
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    summary = Column(Text, nullable=True)
    algorithm = Column(String(50), nullable=False, default="hdbscan")
    suggested_code_id = Column(UUID(as_uuid=True), ForeignKey("codes.id", ondelete="SET NULL"), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="clusters")
    suggested_code = relationship("Code")
    chunks = relationship("ClusterChunk", back_populates="cluster", cascade="all, delete-orphan")


class ClusterChunk(Base):
    """JUNCTION TABLE ASSOCIATING THEMATIC CLUSTERS WITH DOCUMENT CHUNKS."""
    __tablename__ = "cluster_chunks"

    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id", ondelete="CASCADE"), primary_key=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="CASCADE"), primary_key=True, index=True)
    distance_to_centroid = Column(Float, nullable=True)
    is_exemplar = Column(Boolean, nullable=False, default=False)

    cluster = relationship("Cluster", back_populates="chunks")
    chunk = relationship("DocumentChunk", back_populates="cluster_links")
