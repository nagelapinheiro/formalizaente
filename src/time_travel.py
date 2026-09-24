"""Demonstra time travel com a mesma consulta analítica nas versões Delta."""

from __future__ import annotations

import duckdb
import pandas as pd
from deltalake import DeltaTable

from src.paths import REQUESTS_DELTA

QUERY = """
select
    coalesce(area_origem, 'SEM_AREA') as area_origem,
    count(*) as total_solicitacoes,
    count(distinct solicitacao_id) as ids_distintos,
    count(distinct lote_ingestao) as lotes_observados
from solicitacoes
group by 1
order by 1
"""


def query_version(version: int) -> pd.DataFrame:
    """Executa a mesma consulta analítica em uma versão Delta específica."""
    table = DeltaTable(REQUESTS_DELTA, version=version).to_pyarrow_table()
    with duckdb.connect() as connection:
        connection.register("solicitacoes", table)
        return connection.execute(QUERY).df()


def main() -> None:
    current = DeltaTable(REQUESTS_DELTA).version()
    versions = [0, current]

    print("TIME TRAVEL — mesma consulta analítica nas versões Delta")
    print(QUERY.strip())
    for version in versions:
        result = query_version(version)
        print(f"\nVERSÃO {version}")
        print(result.to_string(index=False))
        print(f"Total da versão {version}: {int(result['total_solicitacoes'].sum())} solicitações")


if __name__ == "__main__":
    main()
