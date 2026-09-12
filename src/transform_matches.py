import pandas as pd


# ============================================================
# 1. CARREGAMENTO
# ============================================================

df = pd.read_csv(
    "data/raw/partidas_corinthians_espn.csv"
)


# ============================================================
# 2. CONVERTE E ORDENA AS DATAS
# ============================================================

df["data"] = pd.to_datetime(
    df["data"]
)

df = (
    df
    .sort_values("data")
    .reset_index(drop=True)
)


# ============================================================
# 3. NÚMERO DA PARTIDA
# ============================================================

df["jogo"] = range(
    1,
    len(df) + 1
)


# ============================================================
# 4. CRIA INDICADORES DE RESULTADO
# ============================================================

df["vitoria"] = (
    df["resultado"] == "Vitória"
).astype(int)

df["empate"] = (
    df["resultado"] == "Empate"
).astype(int)

df["derrota"] = (
    df["resultado"] == "Derrota"
).astype(int)


# ============================================================
# 5. RESULTADOS ACUMULADOS
# ============================================================

df["vitorias_acumuladas"] = (
    df["vitoria"].cumsum()
)

df["empates_acumulados"] = (
    df["empate"].cumsum()
)

df["derrotas_acumuladas"] = (
    df["derrota"].cumsum()
)


# ============================================================
# 6. PONTOS ACUMULADOS
# ============================================================

df["pontos_acumulados"] = (
    df["pontos"].cumsum()
)


# ============================================================
# 7. GOLS ACUMULADOS
# ============================================================

df["gols_feitos_acumulados"] = (
    df["gols_corinthians"].cumsum()
)

df["gols_sofridos_acumulados"] = (
    df["gols_adversario"].cumsum()
)

df["saldo_acumulado"] = (
    df["gols_feitos_acumulados"]
    - df["gols_sofridos_acumulados"]
)


# ============================================================
# 8. PONTOS MÁXIMOS POSSÍVEIS
# ============================================================

df["pontos_possiveis"] = (
    df["jogo"] * 3
)


# ============================================================
# 9. APROVEITAMENTO ACUMULADO
# ============================================================

df["aproveitamento"] = (
    df["pontos_acumulados"]
    / df["pontos_possiveis"]
    * 100
)

df["aproveitamento"] = (
    df["aproveitamento"]
    .round(2)
)


# ============================================================
# 10. MÉDIA DE GOLS POR JOGO
# ============================================================

df["media_gols_feitos"] = (
    df["gols_feitos_acumulados"]
    / df["jogo"]
)

df["media_gols_sofridos"] = (
    df["gols_sofridos_acumulados"]
    / df["jogo"]
)

df["media_gols_feitos"] = (
    df["media_gols_feitos"]
    .round(2)
)

df["media_gols_sofridos"] = (
    df["media_gols_sofridos"]
    .round(2)
)


# ============================================================
# 11. SALVA A BASE PROCESSADA
# ============================================================

df.to_csv(
    "data/processed/partidas_corinthians_tratadas.csv",
    index=False
)


# ============================================================
# 12. RESUMO ATUAL
# ============================================================

ultima_linha = df.iloc[-1]

print(
    "\nRESUMO DO CORINTHIANS NO BRASILEIRÃO:\n"
)

print(
    "Jogos:",
    int(ultima_linha["jogo"])
)

print(
    "Vitórias:",
    int(ultima_linha["vitorias_acumuladas"])
)

print(
    "Empates:",
    int(ultima_linha["empates_acumulados"])
)

print(
    "Derrotas:",
    int(ultima_linha["derrotas_acumuladas"])
)

print(
    "Pontos:",
    int(ultima_linha["pontos_acumulados"])
)

print(
    "Gols feitos:",
    int(ultima_linha["gols_feitos_acumulados"])
)

print(
    "Gols sofridos:",
    int(ultima_linha["gols_sofridos_acumulados"])
)

print(
    "Saldo de gols:",
    int(ultima_linha["saldo_acumulado"])
)

print(
    "Aproveitamento:",
    f'{ultima_linha["aproveitamento"]}%'
)

print(
    "Média de gols feitos:",
    ultima_linha["media_gols_feitos"]
)

print(
    "Média de gols sofridos:",
    ultima_linha["media_gols_sofridos"]
)


# ============================================================
# 13. EVOLUÇÃO PARTIDA A PARTIDA
# ============================================================

print(
    "\nEVOLUÇÃO:\n"
)

print(
    df[
        [
            "jogo",
            "data",
            "adversario",
            "resultado",
            "pontos",
            "pontos_acumulados",
            "saldo_acumulado",
            "aproveitamento"
        ]
    ].to_string(
        index=False
    )
)