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

URL_SUMMARY = (
    "https://site.api.espn.com/apis/site/v2/"
    "sports/soccer/bra.1/summary"
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

partidas = dados["events"]

print(
    f"Partidas encontradas no calendário: {len(partidas)}"
)


# ============================================================
# 2. LISTA ONDE GUARDAREMOS JOGADOR X PARTIDA
# ============================================================

registros = []


# ============================================================
# 3. PERCORRE TODAS AS PARTIDAS
# ============================================================

for partida in partidas:

    competicao = partida["competitions"][0]

    status = competicao["status"]["type"]["name"]

    boxscore_disponivel = competicao["boxscoreAvailable"]

    # Processa somente partidas concluídas
    # e que possuem boxscore disponível
    if (
        status != "STATUS_FULL_TIME"
        or not boxscore_disponivel
    ):
        continue

    partida_id = partida["id"]

    data_partida = partida["date"]

    print(
        f"Processando: {partida['shortName']}"
    )


    # ========================================================
    # 4. IDENTIFICA ADVERSÁRIO E MANDO
    # ========================================================

    adversario = None
    mando = None

    for time in competicao["competitors"]:

        if str(time["id"]) == TEAM_ID:

            mando = (
                "Casa"
                if time["homeAway"] == "home"
                else "Fora"
            )

        else:

            adversario = time[
                "team"
            ]["displayName"]


    # ========================================================
    # 5. BUSCA O RESUMO COMPLETO DA PARTIDA
    # ========================================================

    response_summary = requests.get(
        URL_SUMMARY,
        params={
            "event": partida_id
        },
        timeout=30
    )

    response_summary.raise_for_status()

    resumo = response_summary.json()


    # ========================================================
    # 6. LOCALIZA O ELENCO DO CORINTHIANS
    # ========================================================

    corinthians = None

    for time in resumo.get(
        "rosters",
        []
    ):

        if str(
            time["team"]["id"]
        ) == TEAM_ID:

            corinthians = time

            break


    # Caso não encontre o elenco
    if corinthians is None:

        print(
            "AVISO: elenco do Corinthians "
            "não encontrado."
        )

        continue


    jogadores = corinthians["roster"]


    # ========================================================
    # 7. EXTRAI MINUTOS DAS SUBSTITUIÇÕES E EXPULSÕES
    # ========================================================

    minutos_entrada = {}

    minutos_saida = {}

    minutos_expulsao = {}


    for evento in resumo.get(
        "keyEvents",
        []
    ):

        tipo = evento.get(
            "type",
            {}
        ).get(
            "type",
            ""
        )


        evento_team_id = str(
            evento.get(
                "team",
                {}
            ).get(
                "id",
                ""
            )
        )


        # Ignora eventos do adversário
        if evento_team_id != TEAM_ID:

            continue


        # ====================================================
        # SUBSTITUIÇÕES
        # ====================================================

        if tipo == "substitution":

            participantes = evento.get(
                "participants",
                []
            )

            if len(participantes) < 2:

                continue


            # A ESPN fornece o tempo em segundos
            minuto = (
                evento["clock"]["value"]
                / 60
            )


            # Padronizamos o máximo em 90 minutos
            minuto = min(
                minuto,
                90
            )


            # Primeiro participante = entrou
            jogador_entrou = str(
                participantes[0][
                    "athlete"
                ]["id"]
            )


            # Segundo participante = saiu
            jogador_saiu = str(
                participantes[1][
                    "athlete"
                ]["id"]
            )


            minutos_entrada[
                jogador_entrou
            ] = minuto


            minutos_saida[
                jogador_saiu
            ] = minuto


        # ====================================================
        # CARTÕES VERMELHOS
        # ====================================================

        elif tipo == "red-card":

            participantes = evento.get(
                "participants",
                []
            )

            if len(participantes) < 1:

                continue


            minuto = (
                evento["clock"]["value"]
                / 60
            )


            minuto = min(
                minuto,
                90
            )


            jogador_expulso = str(
                participantes[0][
                    "athlete"
                ]["id"]
            )


            minutos_expulsao[
                jogador_expulso
            ] = minuto


    # ========================================================
    # 8. PERCORRE OS JOGADORES DA PARTIDA
    # ========================================================

    for jogador in jogadores:

        atleta = jogador["athlete"]

        jogador_id = str(
            atleta["id"]
        )

        nome = atleta[
            "displayName"
        ]

        titular = jogador.get(
            "starter",
            False
        )

        entrou_reserva = jogador.get(
            "subbedIn",
            False
        )

        saiu = jogador.get(
            "subbedOut",
            False
        )


        # ====================================================
        # 9. CALCULA O MINUTO DE ENTRADA
        # ====================================================

        if titular:

            minuto_inicio = 0

        elif entrou_reserva:

            minuto_inicio = (
                minutos_entrada.get(
                    jogador_id
                )
            )

        else:

            minuto_inicio = None


        # ====================================================
        # 10. CALCULA OS MINUTOS JOGADOS
        # ====================================================

        if minuto_inicio is None:

            minutos_jogados = 0

        else:

            # Por padrão consideramos
            # que o jogador terminou a partida
            minuto_fim = 90


            # Se foi substituído
            if jogador_id in minutos_saida:

                minuto_fim = (
                    minutos_saida[
                        jogador_id
                    ]
                )


            # Se foi expulso
            if jogador_id in minutos_expulsao:

                minuto_fim = min(
                    minuto_fim,
                    minutos_expulsao[
                        jogador_id
                    ]
                )


            minutos_jogados = (
                minuto_fim
                - minuto_inicio
            )


            # Proteção contra valores negativos
            minutos_jogados = max(
                minutos_jogados,
                0
            )


    # ========================================================
        # 11. TRANSFORMA STATS EM DICIONÁRIO
        # ====================================================

        estatisticas = {}


        for estatistica in jogador.get(
            "stats",
            []
        ):

            nome_estatistica = (
                estatistica["name"]
            )

            valor = estatistica[
                "value"
            ]

            estatisticas[
                nome_estatistica
            ] = valor


        # ====================================================
        # 12. MONTA A LINHA JOGADOR X PARTIDA
        # ====================================================

        registro = {

            "partida_id": partida_id,

            "data": data_partida,

            "adversario": adversario,

            "mando": mando,

            "jogador_id": jogador_id,

            "nome": nome,

            "posicao": jogador.get(
                "position",
                {}
            ).get(
                "displayName",
                "Desconhecida"
            ),

            "titular": titular,

            "entrou_reserva": entrou_reserva,

            "saiu": saiu,

            "minutos": round(
                minutos_jogados,
                2
            ),

            "gols": estatisticas.get(
                "totalGoals",
                0
            ),

            "assistencias": estatisticas.get(
                "goalAssists",
                0
            ),

            "finalizacoes": estatisticas.get(
                "totalShots",
                0
            ),

            "finalizacoes_gol": estatisticas.get(
                "shotsOnTarget",
                0
            ),

            "cartoes_amarelos": estatisticas.get(
                "yellowCards",
                0
            ),

            "cartoes_vermelhos": estatisticas.get(
                "redCards",
                0
            ),

            "faltas_cometidas": estatisticas.get(
                "foulsCommitted",
                0
            ),

            "faltas_sofridas": estatisticas.get(
                "foulsSuffered",
                0
            ),

            "defesas": estatisticas.get(
                "saves",
                0
            ),

            "gols_sofridos": estatisticas.get(
                "goalsConceded",
                0
            )
        }


        registros.append(
            registro
        )


# ============================================================
# 13. TRANSFORMA EM DATAFRAME
# ============================================================

df = pd.DataFrame(
    registros
)


# ============================================================
# 14. SALVA O DADO BRUTO
# ============================================================

df.to_csv(
    "data/raw/estatisticas_por_partida_espn.csv",
    index=False
)


# ============================================================
# 15. RESULTADO FINAL
# ============================================================

print(
    "\nExtração concluída!"
)

print(
    "Quantidade de registros:",
    len(df)
)

print(
    "Quantidade de partidas:",
    df["partida_id"].nunique()
)

print(
    "Quantidade de jogadores:",
    df["jogador_id"].nunique()
)


print(
    "\nPRIMEIRAS LINHAS:"
)

print(
    df[
        [
            "data",
            "adversario",
            "nome",
            "titular",
            "minutos",
            "gols",
            "assistencias"
        ]
    ].head(20)
)