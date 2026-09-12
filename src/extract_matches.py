import requests
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TEAM_ID = "874"

URL_SCHEDULE = (
    "https://site.api.espn.com/apis/site/v2/"
    "sports/soccer/bra.1/teams/874/schedule"
)


# ============================================================
# 1. BUSCA O CALENDÁRIO DO CORINTHIANS
# ============================================================

response = requests.get(
    URL_SCHEDULE,
    timeout=30
)

response.raise_for_status()

dados = response.json()

partidas = dados.get(
    "events",
    []
)

print(
    f"Partidas encontradas: {len(partidas)}"
)


# ============================================================
# 2. LISTA PARA ARMAZENAR AS PARTIDAS
# ============================================================

registros = []


# ============================================================
# 3. PERCORRE TODAS AS PARTIDAS
# ============================================================

for partida in partidas:

    competicao = partida[
        "competitions"
    ][0]

    status = competicao[
        "status"
    ][
        "type"
    ][
        "name"
    ]


    # Queremos somente jogos encerrados
    if status != "STATUS_FULL_TIME":
        continue


    partida_id = partida[
        "id"
    ]

    data = partida[
        "date"
    ]


    # ========================================================
    # 4. IDENTIFICA CORINTHIANS E ADVERSÁRIO
    # ========================================================

    gols_corinthians = None
    gols_adversario = None

    adversario = None
    mando = None


    for time in competicao[
        "competitors"
    ]:

        time_id = str(
            time["id"]
        )

        gols = int(
            time[
                "score"
            ][
                "displayValue"
            ]
        )


        # Corinthians
        if time_id == TEAM_ID:

            gols_corinthians = gols

            if time[
                "homeAway"
            ] == "home":

                mando = "Casa"

            else:

                mando = "Fora"


        # Adversário
        else:

            adversario = time[
                "team"
            ][
                "displayName"
            ]

            gols_adversario = gols


    # ========================================================
    # 5. DEFINE O RESULTADO
    # ========================================================

    if gols_corinthians > gols_adversario:

        resultado = "Vitória"

    elif gols_corinthians < gols_adversario:

        resultado = "Derrota"

    else:

        resultado = "Empate"


    # ========================================================
    # 6. SALDO DE GOLS
    # ========================================================

    saldo_gols = (
        gols_corinthians
        - gols_adversario
    )


    # ========================================================
    # 7. PONTOS CONQUISTADOS
    # ========================================================

    if resultado == "Vitória":

        pontos = 3

    elif resultado == "Empate":

        pontos = 1

    else:

        pontos = 0


    # ========================================================
    # 8. MONTA O REGISTRO DA PARTIDA
    # ========================================================

    registro = {

        "partida_id": partida_id,

        "data": data,

        "adversario": adversario,

        "mando": mando,

        "gols_corinthians": gols_corinthians,

        "gols_adversario": gols_adversario,

        "saldo_gols": saldo_gols,

        "resultado": resultado,

        "pontos": pontos
    }


    registros.append(
        registro
    )


# ============================================================
# 9. TRANSFORMA EM DATAFRAME
# ============================================================

df = pd.DataFrame(
    registros
)


# ============================================================
# 10. CONVERTE A DATA
# ============================================================

df["data"] = pd.to_datetime(
    df["data"]
)


# Ordena cronologicamente
df = df.sort_values(
    "data"
)


# ============================================================
# 11. SALVA O ARQUIVO
# ============================================================

df.to_csv(
    "data/raw/partidas_corinthians_espn.csv",
    index=False
)


# ============================================================
# 12. RESULTADO
# ============================================================

print(
    "\nExtração concluída!"
)

print(
    "Partidas processadas:",
    len(df)
)

print(
    "\nPARTIDAS:\n"
)

print(
    df[
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