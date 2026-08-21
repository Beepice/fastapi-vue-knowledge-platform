"""DFT knowledge postgres vector extension

Revision ID: dft002
Revises: dft001
Create Date: 2026-07-01
"""

revision = "dft002"
down_revision = "dft001" # 基于上一个迁移
branch_labels = None
depends_on = None

from typing import Tuple
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from pgvector.sqlalchemy import Vector

def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.current_timestamp(),
        ),
    )
def create_figures_documents_connection(
) -> None:
    op.create_table(
        "chunks_figures",
        sa.Column(
            "chunks_id",
            sa.Integer,
            sa.ForeignKey("document_chunks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "figures_id",
            sa.Integer,
            sa.ForeignKey("figures.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_chunks_figures",
        "chunks_figures",
        ["chunks_id", "figures_id"],
    )
    op.create_index(
        "ix_chunks_figures_chunks",
        "chunks_figures",
        ["chunks_id"]
    )

def create_figures_table(
) -> None:
    op.create_table(
        "figures",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "document_id", sa.Integer,
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("img_path", sa.Text, nullable=False),
        sa.Column("figure_content", sa.Text, nullable=True),
    )
    op.create_index(
        "idx_figures",
        "figures",
        ["document_id"]
    )

def create_document_chunk(
) -> None:
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            sa.Integer,
            primary_key=True,
        ),
        sa.Column(
            "document_id", sa.Integer,
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("context", sa.Text, nullable=False),
        sa.Column("chunk_idx", sa.Integer, nullable=False),
        sa.Column("page_start", sa.Integer, nullable=False),
        sa.Column("page_end", sa.Integer, nullable=False),
        # being basic on the model text-embedding-v4
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("figure_refs", sa.ARRAY(sa.String), nullable=True),
        sa.UniqueConstraint("document_id", "chunk_idx", name="uq_document_chunks_doc_position"),
        *timestamps()
    )

    # ivfflat is relative to the cluster
    # being based on table document_chunks,
    # uesing algorithm ivfflat to the field embedding with vector_cosine_ops(relatively to the cos)
    # which the cluster number is limited on 100.
    op.execute("""
        CREATE INDEX chunks_embedding
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    create_document_chunk()
    create_figures_table()
    create_figures_documents_connection()

def downgrade() -> None:
    op.drop_table("chunks_figures")
    op.drop_table("figures")
    op.drop_table("document_chunks")
