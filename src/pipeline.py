"""Ingestão sem regra de negócio e preservação da camada Bronze em Delta Lake.

Pode ser executado repetidamente com ``python -m src.pipeline``. A execução
reconstrói apenas artefatos derivados do projeto; ``data/raw`` permanece imutável.

A arquitetura física segue o padrão Medallion usado na disciplina:
``data/raw`` -> ``data/bronze`` -> ``data/silver`` -> ``data/gold``.
Limpeza, validação, deduplicação e regras de negócio pertencem ao dbt.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from deltalake import DeltaTable, write_deltalake

from src.paths import (
    AREAS_DELTA,
    BRONZE_DIR,
    BRONZE_EXPORT_DIR,
    EVIDENCE_DIR,
    GOLD_DIR,
    NORMATIVE_DELTA,
    PROJECT_ROOT,
    RAW_DIR,
    REQUESTS_DELTA,
    SILVER_DIR,
    WAREHOUSE_PATH,
)


def _remove_derived_path(path: Path) -> None:
    """Remove somente caminhos derivados previamente autorizados."""
    resolved = path.resolve()
    allowed = {
        BRONZE_DIR.resolve(),
        SILVER_DIR.resolve(),
        GOLD_DIR.resolve(),
        WAREHOUSE_PATH.resolve(),
        WAREHOUSE_PATH.with_suffix(".duckdb.wal").resolve(),
    }
    if resolved not in allowed:
        raise ValueError(f"Recusa de remoção fora dos artefatos derivados: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


def _ensure_layer_dirs() -> None:
    """Garante que as quatro camadas físicas existam no repositório."""
    for path in (RAW_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR, BRONZE_EXPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if path in (SILVER_DIR, GOLD_DIR) and not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def reset_derived_data() -> None:
    """Reinicia Bronze, Silver, Gold e warehouse sem tocar nas fontes brutas."""
    for path in (
        BRONZE_DIR,
        SILVER_DIR,
        GOLD_DIR,
        WAREHOUSE_PATH,
        WAREHOUSE_PATH.with_suffix(".duckdb.wal"),
    ):
        _remove_derived_path(path)
    _ensure_layer_dirs()


def load_normative_source(ingested_at: str) -> pa.Table:
    """Lê o JSON e apenas o converte em linhas persistíveis, sem limpeza."""
    source_path = RAW_DIR / "listas_normativas.json"
    with source_path.open(encoding="utf-8") as source_file:
        payload = json.load(source_file)

    rows: list[dict[str, str | int]] = []
    for row_number, item in enumerate(payload["itens"], start=1):
        rows.append(
            {
                # A ingestão preserva o valor textual recebido na fonte.
                # Normalização, validação e classificação acontecem no dbt.
                "lista": item.get("lista", ""),
                "codigo": item.get("codigo", ""),
                "item": item.get("item", ""),
                "categoria": item.get("categoria", ""),
                "fonte_declarada": item.get("fonte_declarada", ""),
                "source_row_number": row_number,
                "_source_file": source_path.name,
                "_ingested_at_utc": ingested_at,
            }
        )
    return pa.Table.from_pylist(rows)


def load_requests_source(ingested_at: str) -> pd.DataFrame:
    """Lê o CSV integralmente como texto; defeitos permanecem na Bronze."""
    source_path = RAW_DIR / "solicitacoes.csv"
    frame = pd.read_csv(source_path, dtype=str, keep_default_na=False)
    frame.insert(0, "source_row_number", range(1, len(frame) + 1))
    frame["_source_file"] = source_path.name
    frame["_ingested_at_utc"] = ingested_at
    return frame


def load_areas_source(ingested_at: str) -> pd.DataFrame:
    """Lê a planilha XLSX como texto, preservando valores e defeitos da fonte."""
    source_path = RAW_DIR / "areas_referencia.xlsx"
    frame = pd.read_excel(
        source_path,
        sheet_name="areas",
        dtype=str,
        keep_default_na=False,
    )
    frame.insert(0, "source_row_number", range(1, len(frame) + 1))
    frame["_source_file"] = source_path.name
    frame["_ingested_at_utc"] = ingested_at
    return frame


def write_bronze(normative: pa.Table, requests: pd.DataFrame, areas: pd.DataFrame) -> None:
    """Grava as fontes na Bronze; os lotes do CSV geram versões Delta 0 e 1+."""
    write_deltalake(NORMATIVE_DELTA, normative, mode="overwrite")
    write_deltalake(
        AREAS_DELTA,
        pa.Table.from_pandas(areas, preserve_index=False),
        mode="overwrite",
    )

    batches = list(dict.fromkeys(requests["lote_ingestao"].tolist()))
    if len(batches) < 2:
        raise ValueError("A fonte de solicitações deve conter pelo menos dois lotes de ingestão.")

    persisted_rows = 0
    for index, batch in enumerate(batches):
        # Seleção exclusivamente técnica: cada lote vira um commit Delta para
        # demonstrar time travel. Todos os lotes são persistidos, nenhuma linha
        # é descartada e nenhuma regra de negócio é aplicada na ingestão.
        batch_frame = requests.loc[requests["lote_ingestao"] == batch].copy()
        persisted_rows += len(batch_frame)
        mode = "overwrite" if index == 0 else "append"
        write_deltalake(
            REQUESTS_DELTA,
            pa.Table.from_pandas(batch_frame, preserve_index=False),
            mode=mode,
        )

    if persisted_rows != len(requests):
        raise RuntimeError(
            "Falha de reconciliação Raw -> Bronze: nem todas as solicitações foram gravadas."
        )


def export_current_snapshots() -> None:
    """Exporta o estado atual de cada Delta para views Bronze locais do DuckDB."""
    mappings = {
        NORMATIVE_DELTA: BRONZE_EXPORT_DIR / "listas_normativas.parquet",
        REQUESTS_DELTA: BRONZE_EXPORT_DIR / "solicitacoes.parquet",
        AREAS_DELTA: BRONZE_EXPORT_DIR / "areas_referencia.parquet",
    }
    BRONZE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for delta_path, parquet_path in mappings.items():
        pq.write_table(DeltaTable(delta_path).to_pyarrow_table(), parquet_path)


def register_bronze_sources() -> None:
    """Registra views Bronze no DuckDB para que apareçam como source nodes na DAG dbt."""
    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(WAREHOUSE_PATH)) as connection:
        connection.execute("create schema if not exists bronze")
        for table_name, filename in (
            ("solicitacoes", "solicitacoes.parquet"),
            ("listas_normativas", "listas_normativas.parquet"),
            ("areas_referencia", "areas_referencia.parquet"),
        ):
            parquet_path = (BRONZE_EXPORT_DIR / filename).resolve().as_posix().replace("'", "''")
            connection.execute(
                f"create or replace view bronze.{table_name} as "
                f"select * from read_parquet('{parquet_path}')"
            )


def write_ingestion_evidence() -> dict[str, object]:
    """Registra contagens e versões Delta para auditoria da execução."""
    tables = {
        "solicitacoes": DeltaTable(REQUESTS_DELTA),
        "listas_normativas": DeltaTable(NORMATIVE_DELTA),
        "areas_referencia": DeltaTable(AREAS_DELTA),
    }
    evidence: dict[str, object] = {
        "executado_em_utc": datetime.now(UTC).isoformat(),
        "projeto": PROJECT_ROOT.name,
        "fontes": ["solicitacoes.csv", "listas_normativas.json", "areas_referencia.xlsx"],
        "camadas_storage": ["data/raw", "data/bronze", "data/silver", "data/gold"],
    }
    for name, delta in tables.items():
        evidence[name] = {
            "versao_atual": delta.version(),
            "total_versoes": len(delta.history()),
            "total_registros_atual": delta.to_pyarrow_table().num_rows,
        }

    output_path = EVIDENCE_DIR / "ingestao.json"
    output_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence


def main() -> None:
    reset_derived_data()
    ingested_at = datetime.now(UTC).isoformat()

    normative = load_normative_source(ingested_at)
    requests = load_requests_source(ingested_at)
    areas = load_areas_source(ingested_at)

    write_bronze(normative, requests, areas)
    export_current_snapshots()
    register_bronze_sources()
    evidence = write_ingestion_evidence()

    request_metadata = evidence["solicitacoes"]
    print("Pipeline de ingestão concluído.")
    print("Fontes: CSV + JSON + XLSX")
    print("Camadas físicas: data/raw -> data/bronze -> data/silver -> data/gold")
    print(f"Bronze de solicitações: {request_metadata['total_registros_atual']} registros")
    print(
        "Histórico Delta de solicitações: "
        f"{request_metadata['total_versoes']} versões "
        f"(atual={request_metadata['versao_atual']})"
    )
    print("Views Bronze registradas no DuckDB para linhagem dbt.")


if __name__ == "__main__":
    main()
