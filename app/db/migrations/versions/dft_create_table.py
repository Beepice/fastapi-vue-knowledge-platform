"""DFT knowledge base tables

Revision ID: dft001
Revises:
Create Date: 2026-06-05
"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

revision = "dft001"
down_revision = None # 基于上一个迁移
branch_labels = None
depends_on = None

"""触发器强制设置Update时间为当前时间"""
def create_updated_at_trigger() -> None:
    op.execute(
        """
    CREATE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS
    $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    )


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("hashed_password", sa.Text),
        sa.Column("bio", sa.Text, nullable=False, server_default=""),
        sa.Column("image", sa.Text),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

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

def create_tools_table() -> None:
    """工具表"""
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tool_name", sa.String(100), unique=True, nullable=False),
    )

def create_versions_table() -> None:
    """版本表"""
    op.create_table(
        "versions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "tool_id",
            sa.Integer,
            sa.ForeignKey("tools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tool_version", sa.String(50), nullable=False),
    )

def create_dft_tags_table() -> None:
    """DFT标签表（避免和RealWorld的tags冲突）"""
    op.create_table(
        "dft_tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
    )

def create_documents_table() -> None:
    """文档表"""
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("file_type", sa.String(10), server_default="pdf"),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column(
            "version_id",
            sa.Integer,
            sa.ForeignKey("versions.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "uploaded_by",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
        ),
        *timestamps(),
    )
    # 触发器：自动更新 updated_at
    op.execute(
        """
        CREATE TRIGGER update_document_modtime
            BEFORE UPDATE
            ON documents
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.create_unique_constraint(
        "uq_documents_title_version",
        "documents",
        ["title", "version_id"]
    )

def create_document_tags_table() -> None:
    """文档-标签关联表（多对多）"""
    op.create_table(
        "document_tags",
        sa.Column(
            "document_id",
            sa.Integer,
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            sa.Integer,
            sa.ForeignKey("dft_tags.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_document_tags",
        "document_tags",
        ["document_id", "tag_id"],
    )

def upgrade() -> None:
    op.execute("SET TIME ZONE 'Asia/Shanghai'")
    create_updated_at_trigger()
    create_users_table()
    create_tools_table()
    create_versions_table()
    create_dft_tags_table()
    create_documents_table()
    create_document_tags_table()

def downgrade() -> None:
    op.drop_table("document_tags")
    op.drop_table("documents")
    op.drop_table("dft_tags")
    op.drop_table("versions")
    op.drop_table("tools")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")