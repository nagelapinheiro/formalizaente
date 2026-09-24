from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

# Delta Lake tables persisted in the Bronze layer.
REQUESTS_DELTA = BRONZE_DIR / "solicitacoes"
NORMATIVE_DELTA = BRONZE_DIR / "listas_normativas"
AREAS_DELTA = BRONZE_DIR / "areas_referencia"

# Technical snapshots of the current Bronze state used only to register DuckDB views.
# They remain inside the Bronze layer so the visible storage continues to follow:
# data/raw -> data/bronze -> data/silver -> data/gold.
BRONZE_EXPORT_DIR = BRONZE_DIR / "_current"

WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "formalizaente.duckdb"
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "evidence"
