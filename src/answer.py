"""Executa e exporta a resposta final sobre a camada Gold."""

from __future__ import annotations

import csv

import duckdb

from src.paths import EVIDENCE_DIR, PROJECT_ROOT, WAREHOUSE_PATH

QUERY_PATH = PROJECT_ROOT / "queries" / "resposta_negocio.sql"


def main() -> None:
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError("Warehouse ausente. Execute `dbt build` antes desta consulta.")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    sql = QUERY_PATH.read_text(encoding="utf-8")

    with duckdb.connect(str(WAREHOUSE_PATH), read_only=True) as connection:
        cursor = connection.execute(sql)
        rows = cursor.fetchall()
        columns = [item[0] for item in cursor.description]

    output_path = EVIDENCE_DIR / "resultado_completo.csv"
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(columns)
        writer.writerows(rows)

    print("\nRESPOSTA GERENCIAL")
    print(columns)
    for row in rows:
        print(row)
    print(f"\nEvidência salva em: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
