"""Dashboard web do FormalizaEnte.

Camada de consumo da PoC: o app lê somente modelos Gold produzidos pelo dbt.
As métricas executivas, percentuais e recortes vêm prontos da Gold; o dashboard
não cria regra de negócio, não calcula classificação e não consulta Raw/Bronze/Silver.

Execução, na raiz do projeto:
    streamlit run app/dashboard.py
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = PROJECT_ROOT / "warehouse" / "formalizaente.duckdb"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

st.set_page_config(
    page_title="FormalizaEnte | Dashboard Gold",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.18);}
        .fe-header {padding: 1.25rem 1.4rem; border: 1px solid rgba(128,128,128,.20); border-radius: 18px; margin-bottom: 1rem; background: linear-gradient(135deg, rgba(31,111,235,.10), rgba(9,105,218,.03));}
        .fe-title {font-size: 2rem; font-weight: 760; margin: 0; line-height: 1.05;}
        .fe-subtitle {opacity: .76; margin-top: .45rem; font-size: .97rem;}
        .metric-card {border: 1px solid rgba(128,128,128,.20); border-radius: 16px; padding: .95rem 1rem; min-height: 112px; background: rgba(255,255,255,.02);}
        .metric-label {font-size: .82rem; opacity: .67; margin-bottom: .38rem;}
        .metric-value {font-size: 1.85rem; font-weight: 760; line-height: 1.1;}
        .metric-note {font-size: .76rem; opacity: .64; margin-top: .32rem;}
        .section-title {font-size: 1.12rem; font-weight: 720; margin: .25rem 0 .7rem 0;}
        .small-muted {font-size: .82rem; opacity: .66;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _read_gold_table(connection: duckdb.DuckDBPyConnection, table: str) -> pd.DataFrame:
    """Lê uma tabela Gold pelo catálogo ou, como fallback, pelo Parquet físico."""
    try:
        return connection.execute(f"select * from gold.{table}").df()
    except duckdb.Error:
        parquet = GOLD_DIR / f"{table}.parquet"
        if not parquet.exists():
            raise FileNotFoundError(
                f"Modelo Gold não encontrado: gold.{table} / {parquet}. "
                "Execute `python -m src.pipeline` e `dbt build` na raiz do projeto."
            )
        safe_path = parquet.resolve().as_posix().replace("'", "''")
        return connection.execute(f"select * from read_parquet('{safe_path}')").df()


@st.cache_data(show_spinner=False)
def carregar_gold() -> dict[str, pd.DataFrame]:
    """Carrega somente modelos Gold para o dashboard."""
    if WAREHOUSE.exists():
        connection = duckdb.connect(str(WAREHOUSE), read_only=True)
    else:
        connection = duckdb.connect()

    tabelas = [
        "agg_cobertura_geral",
        "agg_cobertura_mensal",
        "agg_cobertura_area",
        "agg_cobertura_categoria",
        "agg_distribuicao_esfera",
        "agg_resposta_gerencial",
        "fct_solicitacoes",
    ]
    try:
        dados = {tabela: _read_gold_table(connection, tabela) for tabela in tabelas}
    finally:
        connection.close()

    if "mes_referencia" in dados["agg_cobertura_mensal"].columns:
        dados["agg_cobertura_mensal"]["mes_referencia"] = pd.to_datetime(
            dados["agg_cobertura_mensal"]["mes_referencia"], errors="coerce"
        )
    if "data_solicitacao" in dados["fct_solicitacoes"].columns:
        dados["fct_solicitacoes"]["data_solicitacao"] = pd.to_datetime(
            dados["fct_solicitacoes"]["data_solicitacao"], errors="coerce"
        )
    return dados


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    gold = carregar_gold()
except Exception as exc:
    st.error("Não foi possível carregar a camada Gold.")
    st.code("python -m src.pipeline\ndbt build\nstreamlit run app/dashboard.py", language="bash")
    st.exception(exc)
    st.stop()


geral = gold["agg_cobertura_geral"].iloc[0]
mensal = gold["agg_cobertura_mensal"].sort_values("mes_referencia")
area = gold["agg_cobertura_area"].sort_values("taxa_cobertura_pct")
categoria = gold["agg_cobertura_categoria"].sort_values("taxa_cobertura_pct")
esfera = gold["agg_distribuicao_esfera"].sort_values("total_solicitacoes", ascending=False)
resposta = gold["agg_resposta_gerencial"].sort_values(["ordem_exibicao", "recorte"])
fato = gold["fct_solicitacoes"]

st.markdown(
    """
    <div class="fe-header">
      <div class="fe-title">FormalizaEnte · Dashboard Gold</div>
      <div class="fe-subtitle">
        Visualização da camada de consumo. KPIs, percentuais e recortes são lidos prontos da Gold; o app não aplica regra de negócio.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Governança")
    st.caption("Fonte exclusiva: modelos Gold produzidos pelo dbt.")
    st.code("python -m src.pipeline\ndbt build", language="bash")
    st.divider()
    st.markdown("**Modelos usados**")
    st.write("`gold.agg_cobertura_geral`")
    st.write("`gold.agg_cobertura_mensal`")
    st.write("`gold.agg_cobertura_area`")
    st.write("`gold.agg_cobertura_categoria`")
    st.write("`gold.agg_distribuicao_esfera`")
    st.write("`gold.agg_resposta_gerencial`")
    if st.button("Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    metric_card("Solicitações válidas", f"{int(geral['total_solicitacoes_validas'])}", "gold.agg_cobertura_geral")
with m2:
    metric_card("Cobertas", f"{int(geral['solicitacoes_atendidas'])}", "encontradas em ≥ 1 lista")
with m3:
    metric_card("Não encontradas", f"{int(geral['solicitacoes_nao_encontradas'])}", "sem correspondência")
with m4:
    metric_card("Cobertura", f"{float(geral['taxa_cobertura_pct']):.2f}%", "calculada na Gold")
with m5:
    metric_card("Ambíguas", f"{int(geral['solicitacoes_com_ambiguidade'])}", "presentes em > 1 lista")
with m6:
    metric_card("Ambiguidade", f"{float(geral['taxa_ambiguidade_pct']):.2f}%", "calculada na Gold")

st.caption(
    "Este dashboard não recalcula taxa de cobertura, taxa de ambiguidade ou esfera de resolução. "
    "Essas decisões ficam no dbt; aqui há apenas leitura, ordenação e exibição."
)

aba_visao, aba_recortes, aba_resposta, aba_detalhes = st.tabs(
    ["Visão executiva", "Recortes Gold", "Resposta gerencial", "Detalhes Gold"]
)

with aba_visao:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Evolução mensal da cobertura</div>', unsafe_allow_html=True)
        fig = px.line(
            mensal,
            x="mes_referencia",
            y="taxa_cobertura_pct",
            markers=True,
            hover_data={"total_solicitacoes": True, "solicitacoes_atendidas": True, "taxa_cobertura_pct": ":.2f"},
            labels={"mes_referencia": "Mês", "taxa_cobertura_pct": "Cobertura (%)"},
        )
        fig.update_yaxes(range=[0, 100])
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown('<div class="section-title">Distribuição por esfera</div>', unsafe_allow_html=True)
        fig = px.pie(
            esfera,
            names="esfera_resolucao",
            values="total_solicitacoes",
            hole=0.52,
            hover_data={"percentual_solicitacoes": ":.2f"},
        )
        fig.update_traces(textposition="inside", textinfo="label+percent")
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20), legend_title_text="Esfera")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with aba_recortes:
    esquerda, direita = st.columns(2)
    with esquerda:
        st.markdown('<div class="section-title">Cobertura por área</div>', unsafe_allow_html=True)
        fig = px.bar(
            area,
            x="taxa_cobertura_pct",
            y="area_origem",
            orientation="h",
            text="taxa_cobertura_pct",
            hover_data={"total_solicitacoes": True, "solicitacoes_atendidas": True},
            labels={"area_origem": "Área", "taxa_cobertura_pct": "Cobertura (%)"},
        )
        fig.update_traces(texttemplate="%{text:.2f}%")
        fig.update_xaxes(range=[0, 100])
        fig.update_layout(height=410, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with direita:
        st.markdown('<div class="section-title">Cobertura por categoria</div>', unsafe_allow_html=True)
        fig = px.bar(
            categoria,
            x="taxa_cobertura_pct",
            y="categoria",
            orientation="h",
            text="taxa_cobertura_pct",
            hover_data={"total_solicitacoes": True, "solicitacoes_atendidas": True},
            labels={"categoria": "Categoria", "taxa_cobertura_pct": "Cobertura (%)"},
        )
        fig.update_traces(texttemplate="%{text:.2f}%")
        fig.update_xaxes(range=[0, 100])
        fig.update_layout(height=410, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-title">Tabelas de recorte calculadas na Gold</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Mensal", "Área", "Categoria"])
    with t1:
        st.dataframe(mensal, use_container_width=True, hide_index=True)
    with t2:
        st.dataframe(area, use_container_width=True, hide_index=True)
    with t3:
        st.dataframe(categoria, use_container_width=True, hide_index=True)

with aba_resposta:
    st.markdown('<div class="section-title">Consulta de resposta, pronta para o gestor</div>', unsafe_allow_html=True)
    st.caption("Equivalente ao resultado da consulta `queries/resposta_negocio.sql` sobre `gold.agg_resposta_gerencial`.")
    st.dataframe(resposta, use_container_width=True, hide_index=True, height=470)

with aba_detalhes:
    st.markdown('<div class="section-title">Fato Gold para auditoria visual</div>', unsafe_allow_html=True)
    colunas = [
        "solicitacao_id",
        "data_solicitacao",
        "item_solicitado_original",
        "categoria",
        "area_origem",
        "responsavel",
        "esfera_resolucao",
        "indicador_atendida",
        "indicador_ambiguidade",
        "existe_remume",
        "existe_resme",
        "existe_rename",
    ]
    existentes = [col for col in colunas if col in fato.columns]
    tabela = fato[existentes].sort_values(["data_solicitacao", "solicitacao_id"])
    st.dataframe(tabela, use_container_width=True, hide_index=True, height=520)

    csv = tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar fato Gold (CSV)",
        data=csv,
        file_name="formalizaente_fct_solicitacoes_gold.csv",
        mime="text/csv",
        use_container_width=False,
    )

st.divider()
st.caption(
    "FormalizaEnte · Dashboard acadêmico · Dados sintéticos. "
    "O painel não representa cobertura oficial de listas do SUS."
)
