"""Create equipment and incident tables.

Revision ID: 20261013_01
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "20261013_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("room", sa.String(length=60), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_equipment_code", "equipment", ["code"], unique=True)
    op.create_index("ix_equipment_room", "equipment", ["room"])
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "equipment_id", sa.Integer(), sa.ForeignKey("equipment.id"), nullable=False
        ),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reported_by", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_incidents_equipment_id", "incidents", ["equipment_id"])


def downgrade() -> None:
    op.drop_index("ix_incidents_equipment_id", table_name="incidents")
    op.drop_table("incidents")
    op.drop_index("ix_equipment_room", table_name="equipment")
    op.drop_index("ix_equipment_code", table_name="equipment")
    op.drop_table("equipment")
