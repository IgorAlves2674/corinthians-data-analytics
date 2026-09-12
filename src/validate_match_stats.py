import pandas as pd


# ============================================================
# 1. CARREGAMENTO
# ============================================================

df = pd.read_csv(
    "data/raw/estatisticas_por_partida_espn.csv"
)


# ============================================================
# 2. INFORMAÇÕES BÁSICAS
# ============================================================

print("\nQUANTIDADE DE LINHAS:")
print(len(df))

print("\nQUANTIDADE DE PARTIDAS:")
print(df["partida_id"].nunique())

print("\nQUANTIDADE DE JOGADORES:")
print(df["jogador_id"].nunique())


# ============================================================
# 3. VALORES AUSENTES
# ============================================================

print("\nVALORES AUSENTES:")
print(df.isna().sum())


# ============================================================
# 4. REGISTROS DUPLICADOS
# ============================================================

duplicados = df.duplicated(
    subset=[
        "partida_id",
        "jogador_id"
    ]
)

print("\nREGISTROS DUPLICADOS:")
print(duplicados.sum())


# ============================================================
# 5. MINUTOS INVÁLIDOS
# ============================================================

minutos_invalidos = df[
    (df["minutos"] < 0)
    | (df["minutos"] > 90)
]

print("\nJOGADORES COM MINUTOS INVÁLIDOS:")
print(
    minutos_invalidos[
        [
            "data",
            "nome",
            "minutos"
        ]
    ]
)


# ============================================================
# 6. QUANTIDADE DE JOGADORES POR PARTIDA
# ============================================================

jogadores_por_partida = (
    df.groupby("partida_id")
    .size()
)

print("\nJOGADORES REGISTRADOS POR PARTIDA:")
print(jogadores_por_partida)


# ============================================================
# 7. JOGADORES QUE REALMENTE ENTRARAM EM CAMPO
# ============================================================

jogaram_por_partida = (
    df[df["minutos"] > 0]
    .groupby("partida_id")
    .size()
)

print("\nJOGADORES QUE ENTRARAM EM CAMPO POR PARTIDA:")
print(jogaram_por_partida)

# ============================================================
# 8. JOGADORES COM CARTÃO VERMELHO
# ============================================================

expulsos = df[
    df["cartoes_vermelhos"] > 0
]

print("\nJOGADORES EXPULSOS:")

print(
    expulsos[
        [
            "partida_id",
            "data",
            "adversario",
            "nome",
            "titular",
            "minutos",
            "cartoes_vermelhos"
        ]
    ]
)