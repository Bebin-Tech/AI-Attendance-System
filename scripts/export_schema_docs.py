"""Export the schema dictionary and full ER source without connecting to a database."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy.dialects import postgresql  # noqa: E402

from app.models import metadata  # noqa: E402

target = ROOT / "docs/database"
target.mkdir(parents=True, exist_ok=True)
dictionary = [
    "# Schema dictionary",
    "",
    "Generated from SQLAlchemy metadata. Historical migrations are frozen separately.",
    "",
]
diagram = ["erDiagram"]
for name, table in sorted(metadata.tables.items()):
    dictionary.extend(
        [
            f"## {name}",
            "",
            "| Column | PostgreSQL type | Nullable | Default |",
            "| --- | --- | --- | --- |",
        ]
    )
    diagram.extend([f"    {name} {{", "        uuid id PK"])
    if "institution_id" in table.c:
        diagram.append("        uuid institution_id FK")
    diagram.append("    }")
    for column in table.c:
        kind = str(column.type.compile(dialect=postgresql.dialect()))
        default = str(column.server_default.arg) if column.server_default else "—"
        dictionary.append(
            f"| {column.name} | {kind} | {'yes' if column.nullable else 'no'} | {default} |"
        )
    dictionary.extend(["", "Constraints:", ""])
    for constraint in sorted(table.constraints, key=lambda item: str(item.name)):
        expression = getattr(constraint, "sqltext", None)
        value = (
            str(expression)
            if expression is not None
            else ", ".join(constraint.columns.keys())
        )
        dictionary.append(
            f"- `{constraint.name}` ({type(constraint).__name__}): {value}"
        )
    for foreign_key in sorted(
        table.foreign_key_constraints, key=lambda item: str(item.name)
    ):
        columns = [
            item.parent.name
            for item in foreign_key.elements
            if item.parent.name != "institution_id"
        ]
        parent = foreign_key.referred_table.name
        diagram.append(
            f'    {parent} ||--o{{ {name} : "{", ".join(columns) or "institution_id"}"'
        )
    dictionary.extend(["", "Indexes:", ""])
    for index in sorted(table.indexes, key=lambda item: str(item.name)):
        ddl = ""
        predicate = index.dialect_options["postgresql"].get("where")
        if predicate is not None:
            ddl = " WHERE " + str(predicate)
        dictionary.append(
            f"- `{index.name}` ({', '.join(index.columns.keys())})"
            f"{' UNIQUE' if index.unique else ''}{ddl}"
        )
    dictionary.append("")
(target / "schema.md").write_text("\n".join(dictionary).rstrip() + "\n", encoding="utf-8")
(target / "schema.mmd").write_text("\n".join(diagram) + "\n", encoding="utf-8")
print(f"Exported dictionary and ER source for {len(metadata.tables)} tables")
