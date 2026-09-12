import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CARREGA A BASE DE PARTIDAS TRATADA
# ============================================================

df = pd.read_csv(
    "data/processed/partidas_corinthians_tratadas.csv"
)


# ============================================================
# 2. CONVERTE A DATA
# ============================================================

df["data"] = pd.to_datetime(
    df["data"]
)


# ============================================================
# 3. CRIA O RESUMO CASA X FORA
# ============================================================

casa_fora = (
    df
    .groupby("mando")
    .agg(

        jogos=(
            "partida_id",
            "count"
        ),

        vitorias=(
            "vitoria",
            "sum"
        ),

        empates=(
            "empate",
            "sum"
        ),

        derrotas=(
            "derrota",
            "sum"
        ),

        pontos=(
            "pontos",
            "sum"
        ),

        gols_feitos=(
            "gols_corinthians",
            "sum"
        ),

        gols_sofridos=(
            "gols_adversario",
            "sum"
        )
    )
)


# ============================================================
# 4. SALDO DE GOLS
# ============================================================

casa_fora["saldo_gols"] = (
    casa_fora["gols_feitos"]
    - casa_fora["gols_sofridos"]
)


# ============================================================
# 5. PONTOS POSSÍVEIS
# ============================================================

casa_fora["pontos_possiveis"] = (
    casa_fora["jogos"] * 3
)


# ============================================================
# 6. APROVEITAMENTO
# ============================================================

casa_fora["aproveitamento"] = (
    casa_fora["pontos"]
    / casa_fora["pontos_possiveis"]
    * 100
)


# ============================================================
# 7. MÉDIAS DE GOLS
# ============================================================

casa_fora["media_gols_feitos"] = (
    casa_fora["gols_feitos"]
    / casa_fora["jogos"]
)

casa_fora["media_gols_sofridos"] = (
    casa_fora["gols_sofridos"]
    / casa_fora["jogos"]
)


# ============================================================
# 8. ARREDONDAMENTO
# ============================================================

colunas_decimais = [
    "aproveitamento",
    "media_gols_feitos",
    "media_gols_sofridos"
]

casa_fora[
    colunas_decimais
] = casa_fora[
    colunas_decimais
].round(2)


# ============================================================
# 9. EXIBE CASA X FORA
# ============================================================

print(
    "\nDESEMPENHO EM CASA X FORA:\n"
)

print(
    casa_fora[
        [
            "jogos",
            "vitorias",
            "empates",
            "derrotas",
            "pontos",
            "gols_feitos",
            "gols_sofridos",
            "saldo_gols",
            "aproveitamento",
            "media_gols_feitos",
            "media_gols_sofridos"
        ]
    ]
)


# ============================================================
# 10. FORMA RECENTE - ÚLTIMOS 5 JOGOS
# ============================================================

ultimos_5 = (
    df
    .sort_values("data")
    .tail(5)
    .copy()
)


# ============================================================
# 11. RESUMO DOS ÚLTIMOS 5 JOGOS
# ============================================================

jogos_recentes = len(
    ultimos_5
)

vitorias_recentes = (
    ultimos_5["vitoria"].sum()
)

empates_recentes = (
    ultimos_5["empate"].sum()
)

derrotas_recentes = (
    ultimos_5["derrota"].sum()
)

pontos_recentes = (
    ultimos_5["pontos"].sum()
)

gols_feitos_recentes = (
    ultimos_5["gols_corinthians"].sum()
)

gols_sofridos_recentes = (
    ultimos_5["gols_adversario"].sum()
)

pontos_possiveis_recentes = (
    jogos_recentes * 3
)

aproveitamento_recente = (
    pontos_recentes
    / pontos_possiveis_recentes
    * 100
)


# ============================================================
# 12. EXIBE OS ÚLTIMOS 5 JOGOS
# ============================================================

print(
    "\nÚLTIMOS 5 JOGOS:\n"
)

print(
    ultimos_5[
        [
            "data",
            "adversario",
            "mando",
            "gols_corinthians",
            "gols_adversario",
            "resultado",
            "pontos"
        ]
    ].to_string(
        index=False
    )
)


print(
    "\nRESUMO DOS ÚLTIMOS 5 JOGOS:\n"
)

print(
    "Vitórias:",
    int(vitorias_recentes)
)

print(
    "Empates:",
    int(empates_recentes)
)

print(
    "Derrotas:",
    int(derrotas_recentes)
)

print(
    "Pontos:",
    int(pontos_recentes)
)

print(
    "Gols feitos:",
    int(gols_feitos_recentes)
)

print(
    "Gols sofridos:",
    int(gols_sofridos_recentes)
)

print(
    "Aproveitamento:",
    f"{aproveitamento_recente:.2f}%"
)


# ============================================================
# 13. GRÁFICO - EVOLUÇÃO DO APROVEITAMENTO
# ============================================================

df_grafico = (
    df
    .sort_values("jogo")
    .copy()
)


plt.figure(
    figsize=(11, 6)
)


plt.plot(
    df_grafico["jogo"],
    df_grafico["aproveitamento"],
    marker="o"
)


# ============================================================
# 14. LINHA DA MÉDIA ATUAL DO CAMPEONATO
# ============================================================

aproveitamento_atual = (
    df_grafico.iloc[-1]["aproveitamento"]
)

plt.axhline(
    y=aproveitamento_atual,
    linestyle="--",
    label=(
        f"Aproveitamento atual "
        f"({aproveitamento_atual:.2f}%)"
    )
)


# ============================================================
# 15. CONFIGURAÇÕES DO GRÁFICO
# ============================================================

plt.title(
    "Evolução do Aproveitamento do Corinthians"
)

plt.xlabel(
    "Partida"
)

plt.ylabel(
    "Aproveitamento acumulado (%)"
)

plt.xticks(
    df_grafico["jogo"]
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.legend()

plt.tight_layout()


# ============================================================
# 16. SALVA O GRÁFICO
# ============================================================

plt.savefig(
    "reports/figures/evolucao_aproveitamento.png",
    dpi=300,
    bbox_inches="tight"
)


# ============================================================
# 17. EXIBE O GRÁFICO
# ============================================================

plt.show()

# ============================================================
# 18. GRÁFICO - PONTOS ACUMULADOS
# ============================================================

plt.figure(
    figsize=(11, 6)
)

plt.plot(
    df_grafico["jogo"],
    df_grafico["pontos_acumulados"],
    marker="o"
)

plt.title(
    "Evolução dos Pontos do Corinthians"
)

plt.xlabel(
    "Partida"
)

plt.ylabel(
    "Pontos acumulados"
)

plt.xticks(
    df_grafico["jogo"]
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()


# ============================================================
# 19. SALVA O GRÁFICO
# ============================================================

plt.savefig(
    "reports/figures/evolucao_pontos.png",
    dpi=300,
    bbox_inches="tight"
)


# ============================================================
# 20. EXIBE O GRÁFICO
# ============================================================

plt.show()