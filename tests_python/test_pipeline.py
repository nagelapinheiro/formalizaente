from pathlib import Path

import duckdb
import pandas as pd
from deltalake import DeltaTable

from src.paths import AREAS_DELTA, GOLD_DIR, RAW_DIR, REQUESTS_DELTA, SILVER_DIR, WAREHOUSE_PATH
from src.time_travel import query_version


def test_raw_sources_use_three_formats() -> None:
    assert (RAW_DIR / "listas_normativas.json").is_file()
    assert (RAW_DIR / "solicitacoes.csv").is_file()
    assert (RAW_DIR / "areas_referencia.xlsx").is_file()


def test_synthetic_dataset_has_two_ingestion_batches() -> None:
    requests = pd.read_csv(RAW_DIR / "solicitacoes.csv", dtype=str, keep_default_na=False)
    assert requests["lote_ingestao"].nunique() >= 2


def test_medallion_storage_directories_exist() -> None:
    assert RAW_DIR.is_dir()
    assert REQUESTS_DELTA.parent.is_dir()
    assert SILVER_DIR.is_dir()
    assert GOLD_DIR.is_dir()


def test_delta_history_has_at_least_two_versions() -> None:
    delta = DeltaTable(REQUESTS_DELTA)
    assert delta.version() >= 1
    assert len(delta.history()) >= 2


def test_all_raw_sources_are_persisted_in_delta() -> None:
    assert DeltaTable(REQUESTS_DELTA).to_pyarrow_table().num_rows > 0
    assert DeltaTable(AREAS_DELTA).to_pyarrow_table().num_rows > 0


def test_time_travel_current_version_contains_more_rows() -> None:
    current_version = DeltaTable(REQUESTS_DELTA).version()
    version_zero = query_version(0)
    current = query_version(current_version)
    assert int(current["total_solicitacoes"].sum()) > int(version_zero["total_solicitacoes"].sum())
    assert int(current["lotes_observados"].max()) > int(version_zero["lotes_observados"].max())


def test_gold_totals_reconcile_with_quarantine() -> None:
    assert Path(WAREHOUSE_PATH).is_file()
    with duckdb.connect(str(WAREHOUSE_PATH), read_only=True) as connection:
        bronze_total = connection.execute("select count(*) from bronze.solicitacoes").fetchone()[0]
        valid_total = connection.execute("select count(*) from gold.fct_solicitacoes").fetchone()[0]
        quarantine_total = connection.execute(
            "select count(*) from silver.quarantine_solicitacoes"
        ).fetchone()[0]
    assert bronze_total == valid_total + quarantine_total


def test_final_metric_is_mathematically_consistent() -> None:
    with duckdb.connect(str(WAREHOUSE_PATH), read_only=True) as connection:
        total, attended, rate = connection.execute(
            """
            select total_solicitacoes_validas, solicitacoes_atendidas, taxa_cobertura_pct
            from gold.agg_cobertura_geral
            """
        ).fetchone()
    assert rate == round(100 * attended / total, 2)


def test_final_query_reads_only_gold_without_where() -> None:
    query_path = Path(__file__).parents[1] / "queries" / "resposta_negocio.sql"
    query = query_path.read_text(encoding="utf-8").lower()
    executable = "\n".join(
        line for line in query.splitlines() if not line.lstrip().startswith("--")
    )
    assert "gold.agg_resposta_gerencial" in executable
    assert " bronze." not in executable
    assert " silver." not in executable
    assert " where " not in f" {executable.replace(chr(10), ' ')} "
