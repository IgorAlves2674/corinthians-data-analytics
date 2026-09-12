import pandas as pd


# ============================================================
# 1. CARREGAMENTO DOS DADOS BRUTOS
# ============================================================

df = pd.read_csv(
    "data/raw/estatisticas_jogadores_espn.csv"
)


# ============================================================
# 2. INSPEÇÃO INICIAL DOS DADOS
# ============================================================

print("DADOS BRUTOS:")
print(df.head())

print("\nCOLUNAS:")
print(df.columns)

print("\nTIPOS DOS DADOS:")
print(df.dtypes)

print("\nVALORES AUSENTES POR COLUNA:")
print(df.isna().sum())

print("\nJOGADORES SEM IDADE:")
print(
    df[df["idade"].isna()][
        ["nome", "idade", "posicao"]
    ]
)


# ============================================================
# 3. TRATAMENTO DOS TIPOS DE DADOS
# ============================================================

# Converte a data de nascimento para tipo datetime
df["data_nascimento"] = pd.to_datetime(
    df["data_nascimento"],
    errors="coerce"
)

# Colunas que devem ser números inteiros
colunas_inteiras = [
    "idade",
    "jogos",
    "entradas_reserva",
    "gols",
    "assistencias",
    "cartoes_amarelos",
    "cartoes_vermelhos"
]

# Int64 do Pandas aceita valores ausentes
for coluna in colunas_inteiras:
    df[coluna] = df[coluna].astype("Int64")


# ============================================================
# 4. CRIAÇÃO DE MÉTRICAS OFENSIVAS
# ============================================================

# Gols + assistências
df["participacoes_gols"] = (
    df["gols"] + df["assistencias"]
)

# Inicializa as médias com zero
df["gols_por_jogo"] = 0.0
df["assistencias_por_jogo"] = 0.0

# Seleciona apenas quem entrou em campo
mascara_jogou = df["jogos"] > 0

# Calcula gols por jogo
df.loc[
    mascara_jogou,
    "gols_por_jogo"
] = (
    df.loc[mascara_jogou, "gols"]
    / df.loc[mascara_jogou, "jogos"]
)

# Calcula assistências por jogo
df.loc[
    mascara_jogou,
    "assistencias_por_jogo"
] = (
    df.loc[mascara_jogou, "assistencias"]
    / df.loc[mascara_jogou, "jogos"]
)


# ============================================================
# 5. TITULARIDADES E RESERVAS
# ============================================================

# Se o jogador disputou 20 jogos e entrou como reserva em 5,
# entendemos que começou 15 partidas como titular.
df["titularidades"] = (
    df["jogos"] - df["entradas_reserva"]
)

# Inicializa com zero
df["percentual_titularidade"] = 0.0

# Calcula a proporção de partidas como titular
df.loc[
    mascara_jogou,
    "percentual_titularidade"
] = (
    df.loc[mascara_jogou, "titularidades"]
    / df.loc[mascara_jogou, "jogos"]
)

# Por padrão, quem não jogou fica como "Sem jogos"
df["status_elenco"] = "Sem jogos"

# Titular:
# começou pelo menos 50% das partidas em que atuou
df.loc[
    (df["jogos"] > 0)
    & (df["percentual_titularidade"] >= 0.5),
    "status_elenco"
] = "Titular"

# Reserva:
# jogou, mas começou menos de 50% como titular
df.loc[
    (df["jogos"] > 0)
    & (df["percentual_titularidade"] < 0.5),
    "status_elenco"
] = "Reserva"


# ============================================================
# 6. CONFERÊNCIA DOS DADOS
# ============================================================

print("\nTIPOS APÓS TRATAMENTO:")
print(df.dtypes)

print("\nDADOS TRATADOS:")
print(df.head())

print("\nNOVAS MÉTRICAS:")
print(
    df[
        [
            "nome",
            "jogos",
            "gols",
            "assistencias",
            "participacoes_gols",
            "gols_por_jogo",
            "assistencias_por_jogo"
        ]
    ].head(10)
)

print("\nTITULARES E RESERVAS:")
print(
    df[
        [
            "nome",
            "jogos",
            "entradas_reserva",
            "titularidades",
            "percentual_titularidade",
            "status_elenco"
        ]
    ].head(20)
)


# ============================================================
# 7. SALVAMENTO DOS DADOS PROCESSADOS
# ============================================================

df.to_csv(
    "data/processed/jogadores_tratados.csv",
    index=False
)

print("\nDados tratados salvos com sucesso!")