"""One-time Phase 2 authoring tool. Refuses to overwrite the frozen initial revision.

Run with backend/.venv/Scripts/python.exe scripts/freeze-initial-migration.py.
Later schema changes MUST use new Alembic revisions, not this script.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from alembic.autogenerate import render_python_code  # noqa: E402
from alembic.operations import ops  # noqa: E402
from alembic.migration import MigrationContext  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402

from app.models import metadata  # noqa: E402

tables = list(metadata.sorted_tables)
operations = []
for table in tables:
    operations.append(ops.CreateTableOp.from_table(table))
    for index in sorted(table.indexes, key=lambda item: str(item.name)):
        operations.append(ops.CreateIndexOp.from_index(index))

context = MigrationContext.configure(dialect=postgresql.dialect())
upgrades = render_python_code(ops.UpgradeOps(operations), migration_context=context)
downgrades = render_python_code(
    ops.DowngradeOps([ops.DropTableOp.from_table(table) for table in reversed(tables)]),
    migration_context=context,
)
output = ROOT / "backend/migrations/versions/0001_initial_schema.py"
with output.open("x", encoding="utf-8", newline="\n") as stream:
    stream.write('''"""Initial PostgreSQL schema, frozen independently of application metadata.

Revision ID: 0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
''')
    stream.write(upgrades + "\n")
    stream.write('''    op.execute("""
        CREATE FUNCTION public.aifams_touch_updated_at() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
            NEW.updated_at := statement_timestamp();
            RETURN NEW;
        END $$
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION public.aifams_touch_updated_at()")
''')
    stream.write(downgrades + "\n")
print(f"Frozen {len(tables)} tables in {output.relative_to(ROOT)}")
