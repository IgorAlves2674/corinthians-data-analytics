import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CARREGAMENTO
# ============================================================

df = pd.read_csv(
    "data/processed/estatisticas_jogadores_por_90.csv"
)


# ============================================================
# 2. REMOVE GOLEIROS E POSIÇÕES DESCONHECIDAS
# ============================================================

df_linha = df[
    ~df["posicao_oficial"].isin(
        ["Goalkeeper", "Desconhecida"]
    )
].copy()


# ============================================================
# 3. AGRUPAMENTO POR POSIÇÃO
# ============================================================

comparacao_posicoes = (
    df_linha
    .groupby("posicao_oficial")
    .agg(

        jogadores=(
            "nome",
            "count"
        ),

        minutos=(
            "minutos",
            "sum"
        ),

        gols=(
            "gols",
            "sum"
        ),

        assistencias=(
            "assistencias",
            "sum"
        ),

        participacoes_gols=(
            "participacoes_gols",
            "sum"
        ),

        finalizacoes=(
            "finalizacoes",
            "sum"
        ),

        finalizacoes_gol=(
            "finalizacoes_gol",
            "sum"
        )
    )
)


# ============================================================
# 4. MÉTRICAS POR 90 DO GRUPO
# ============================================================

comparacao_posicoes["gols_por_90"] = (
    comparacao_posicoes["gols"]
    / (comparacao_posicoes["minutos"] / 90)
)

comparacao_posicoes["assistencias_por_90"] = (
    comparacao_posicoes["assistencias"]
    / (comparacao_posicoes["minutos"] / 90)
)

comparacao_posicoes["participacoes_por_90"] = (
    comparacao_posicoes["participacoes_gols"]
    / (comparacao_posicoes["minutos"] / 90)
)

comparacao_posicoes["finalizacoes_por_90"] = (
    comparacao_posicoes["finalizacoes"]
    / (comparacao_posicoes["minutos"] / 90)
)

comparacao_posicoes["finalizacoes_gol_por_90"] = (
    comparacao_posicoes["finalizacoes_gol"]
    / (comparacao_posicoes["minutos"] / 90)
)


# ============================================================
# 5. ARREDONDAMENTO
# ============================================================

colunas_decimais = [
    "minutos",
    "gols_por_90",
    "assistencias_por_90",
    "participacoes_por_90",
    "finalizacoes_por_90",
    "finalizacoes_gol_por_90"
]

comparacao_posicoes[
    colunas_decimais
] = comparacao_posicoes[
    colunas_decimais
].round(3)


# ============================================================
# 6. RESULTADO
# ============================================================

print(
    "\nCOMPARAÇÃO OFENSIVA POR POSIÇÃO:\n"
)

print(
    comparacao_posicoes
    .sort_values(
        "participacoes_por_90",
        ascending=False
    )
)

# ============================================================
# 7. GRÁFICO - PARTICIPAÇÕES POR 90 POR POSIÇÃO
# ============================================================

grafico = (
    comparacao_posicoes
    .reset_index()
    .sort_values(
        "participacoes_por_90",
        ascending=False
    )
)

plt.figure(
    figsize=(9, 6)
)

plt.bar(
    grafico["posicao_oficial"],
    grafico["participacoes_por_90"]
)

plt.title(
    "Participações em gols por 90 minutos - Por posição"
)

plt.xlabel(
    "Posição"
)

plt.ylabel(
    "Participações em gols por 90"
)

plt.tight_layout()

plt.savefig(
    "reports/figures/participacoes_por_90_posicao.png"
)

plt.show()