import pandas as pd


# ============================================================
# 1. CARREGAMENTO DOS DADOS POR PARTIDA
# ============================================================

df = pd.read_csv(
    "data/raw/estatisticas_por_partida_espn.csv"
)


# Padroniza o ID como texto
df["jogador_id"] = (
    df["jogador_id"]
    .astype(str)
)


# ============================================================
# 2. CONSIDERA APENAS PARTIDAS EM QUE O JOGADOR ATUOU
# ============================================================

df_jogou = df[
    df["minutos"] > 0
].copy()


# ============================================================
# 3. AGREGA OS DADOS POR JOGADOR
# ============================================================

jogadores = (
    df_jogou
    .groupby(
        [
            "jogador_id",
            "nome"
        ],
        as_index=False
    )
    .agg(

        jogos=(
            "partida_id",
            "nunique"
        ),

        titularidades=(
            "titular",
            "sum"
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

        finalizacoes=(
            "finalizacoes",
            "sum"
        ),

        finalizacoes_gol=(
            "finalizacoes_gol",
            "sum"
        ),

        cartoes_amarelos=(
            "cartoes_amarelos",
            "sum"
        ),

        cartoes_vermelhos=(
            "cartoes_vermelhos",
            "sum"
        ),

        faltas_cometidas=(
            "faltas_cometidas",
            "sum"
        ),

        faltas_sofridas=(
            "faltas_sofridas",
            "sum"
        ),

        defesas=(
            "defesas",
            "sum"
        ),

        gols_sofridos=(
            "gols_sofridos",
            "sum"
        )
    )
)


# ============================================================
# 4. CARREGA AS POSIÇÕES DO ELENCO
# ============================================================

elenco = pd.read_csv(
    "data/processed/jogadores_tratados.csv"
)


# Padroniza o ID como texto
elenco["id"] = (
    elenco["id"]
    .astype(str)
)


posicoes_elenco = elenco[
    [
        "id",
        "posicao"
    ]
].copy()


posicoes_elenco = (
    posicoes_elenco
    .rename(
        columns={
            "id": "jogador_id",
            "posicao": "posicao_elenco"
        }
    )
)


# ============================================================
# 5. JUNTA COM A POSIÇÃO DO ELENCO
# ============================================================

jogadores = jogadores.merge(
    posicoes_elenco,
    on="jogador_id",
    how="left"
)


# ============================================================
# 6. FUNÇÃO PARA SIMPLIFICAR POSIÇÕES DAS PARTIDAS
# ============================================================

def classificar_posicao(posicao):

    # Caso seja um valor vazio
    if pd.isna(posicao):
        return None


    posicao = str(
        posicao
    )


    # --------------------------------------------------------
    # Valores que não representam uma posição real
    # --------------------------------------------------------

    if posicao in [
        "Substitute",
        "Desconhecida"
    ]:
        return None


    # --------------------------------------------------------
    # GOLEIRO
    # --------------------------------------------------------

    if "Goalkeeper" in posicao:

        return "Goalkeeper"


    # --------------------------------------------------------
    # DEFENSOR
    # --------------------------------------------------------

    if (
        "Defender" in posicao
        or "Back" in posicao
    ):

        return "Defender"


    # --------------------------------------------------------
    # MEIO-CAMPISTA
    # --------------------------------------------------------

    if "Midfielder" in posicao:

        return "Midfielder"


    # --------------------------------------------------------
    # ATACANTE
    # --------------------------------------------------------

    if (
        "Forward" in posicao
        or "Striker" in posicao
        or "Winger" in posicao
    ):

        return "Forward"


    # Caso apareça uma posição que ainda não conhecemos
    return None


# ============================================================
# 7. EXTRAI AS POSIÇÕES REGISTRADAS NAS PARTIDAS
# ============================================================

posicoes_partidas = df_jogou[
    [
        "jogador_id",
        "posicao"
    ]
].copy()


posicoes_partidas["jogador_id"] = (
    posicoes_partidas[
        "jogador_id"
    ].astype(str)
)


# ============================================================
# 8. CONVERTE POSIÇÕES TÁTICAS EM POSIÇÕES GERAIS
# ============================================================

posicoes_partidas[
    "posicao_inferida"
] = (

    posicoes_partidas[
        "posicao"
    ]

    .apply(
        classificar_posicao
    )
)


# ============================================================
# 9. REMOVE POSIÇÕES QUE NÃO CONSEGUIMOS CLASSIFICAR
# ============================================================

posicoes_partidas = (
    posicoes_partidas
    .dropna(
        subset=[
            "posicao_inferida"
        ]
    )
)


# ============================================================
# 10. POSIÇÃO MAIS FREQUENTE DE CADA JOGADOR
# ============================================================

posicao_mais_frequente = (
    posicoes_partidas

    .groupby(
        "jogador_id"
    )[
        "posicao_inferida"
    ]

    .agg(
        lambda valores:
            valores.mode().iloc[0]
    )

    .reset_index()
)


# ============================================================
# 11. JUNTA A POSIÇÃO INFERIDA À BASE DOS JOGADORES
# ============================================================

jogadores = jogadores.merge(
    posicao_mais_frequente,
    on="jogador_id",
    how="left"
)


# ============================================================
# 12. DEFINE A POSIÇÃO FINAL DO JOGADOR
# ============================================================

# Primeiro tenta usar a posição do cadastro do elenco.
#
# Caso o jogador não esteja no cadastro, usa a posição
# inferida através das partidas.
#
# Caso nenhuma das duas fontes tenha informação,
# usamos "Desconhecida".

jogadores["posicao_oficial"] = (
    jogadores["posicao_elenco"]
    .fillna(
        jogadores[
            "posicao_inferida"
        ]
    )
    .fillna(
        "Desconhecida"
    )
)


# ============================================================
# 13. PARTICIPAÇÕES EM GOLS
# ============================================================

jogadores[
    "participacoes_gols"
] = (

    jogadores["gols"]
    + jogadores["assistencias"]
)


# ============================================================
# 14. EQUIVALENTE A PARTIDAS COMPLETAS DE 90 MINUTOS
# ============================================================

jogadores[
    "partidas_90"
] = (

    jogadores["minutos"]
    / 90
)


# ============================================================
# 15. MÉTRICAS POR 90 MINUTOS
# ============================================================

jogadores[
    "gols_por_90"
] = (

    jogadores["gols"]
    / jogadores["partidas_90"]
)


jogadores[
    "assistencias_por_90"
] = (

    jogadores["assistencias"]
    / jogadores["partidas_90"]
)


jogadores[
    "participacoes_por_90"
] = (

    jogadores["participacoes_gols"]
    / jogadores["partidas_90"]
)


jogadores[
    "finalizacoes_por_90"
] = (

    jogadores["finalizacoes"]
    / jogadores["partidas_90"]
)


jogadores[
    "finalizacoes_gol_por_90"
] = (

    jogadores["finalizacoes_gol"]
    / jogadores["partidas_90"]
)


# ============================================================
# 16. PERCENTUAL DE TITULARIDADE
# ============================================================

jogadores[
    "percentual_titularidade"
] = (

    jogadores["titularidades"]
    / jogadores["jogos"]
)


# ============================================================
# 17. CLASSIFICAÇÃO TITULAR / RESERVA
# ============================================================

jogadores[
    "status_elenco"
] = "Reserva"


jogadores.loc[
    jogadores[
        "percentual_titularidade"
    ] >= 0.5,

    "status_elenco"

] = "Titular"


# ============================================================
# 18. ARREDONDAMENTO
# ============================================================

colunas_decimais = [

    "minutos",

    "partidas_90",

    "gols_por_90",

    "assistencias_por_90",

    "participacoes_por_90",

    "finalizacoes_por_90",

    "finalizacoes_gol_por_90",

    "percentual_titularidade"
]


jogadores[
    colunas_decimais
] = (

    jogadores[
        colunas_decimais
    ]

    .round(3)
)


# ============================================================
# 19. REMOVE COLUNAS AUXILIARES
# ============================================================

# Essas duas colunas foram úteis apenas para determinar
# a posição final.

jogadores = jogadores.drop(
    columns=[
        "posicao_elenco",
        "posicao_inferida"
    ]
)


# ============================================================
# 20. SALVA A BASE PROCESSADA
# ============================================================

jogadores.to_csv(
    "data/processed/estatisticas_jogadores_por_90.csv",
    index=False
)


print(
    "\nBase processada salva com sucesso!"
)


# ============================================================
# 21. ESTATÍSTICAS AGREGADAS POR JOGADOR
# ============================================================

print(
    "\nESTATÍSTICAS AGREGADAS POR JOGADOR:\n"
)


print(

    jogadores[
        [
            "nome",
            "posicao_oficial",
            "jogos",
            "titularidades",
            "minutos",
            "gols",
            "assistencias",
            "participacoes_gols",
            "gols_por_90",
            "assistencias_por_90",
            "participacoes_por_90",
            "status_elenco"
        ]
    ]

    .sort_values(
        "participacoes_por_90",
        ascending=False
    )
)


# ============================================================
# 22. RANKING DE EFICIÊNCIA
# ============================================================

MINUTOS_MINIMOS = 450


ranking_eficiencia = jogadores[
    jogadores[
        "minutos"
    ] >= MINUTOS_MINIMOS
].copy()


ranking_eficiencia = (

    ranking_eficiencia

    .sort_values(
        "participacoes_por_90",
        ascending=False
    )
)


print(
    f"\nRANKING DE EFICIÊNCIA "
    f"(mínimo {MINUTOS_MINIMOS} minutos):\n"
)


print(

    ranking_eficiencia[
        [
            "nome",
            "posicao_oficial",
            "jogos",
            "minutos",
            "gols",
            "assistencias",
            "gols_por_90",
            "assistencias_por_90",
            "participacoes_por_90"
        ]
    ]

    .head(10)
)