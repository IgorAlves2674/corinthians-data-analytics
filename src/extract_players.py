import requests
import pandas as pd

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/teams/874/roster"

response = requests.get(url)

dados = response.json()

print("Status:", response.status_code)

# Lista de jogadores retornada pela ESPN
jogadores = dados["athletes"]

# Aqui vamos guardar os jogadores já tratados
lista_jogadores = []

for jogador in jogadores:

    estatisticas = {}

    # Alguns jogadores podem não ter estatísticas disponíveis
    if jogador.get("statistics"):

        categorias = jogador["statistics"]["splits"]["categories"]

        for categoria in categorias:
            for estatistica in categoria["stats"]:

                nome = estatistica["name"]
                valor = estatistica["value"]

                estatisticas[nome] = valor

    # Monta uma linha limpa para esse jogador
    dados_jogador = {
        "id": jogador["id"],
        "nome": jogador["fullName"],
        "idade": jogador.get("age"),
        "data_nascimento": jogador.get("dateOfBirth"),
        "camisa": jogador.get("jersey"),
        "posicao": jogador["position"]["displayName"],
        "jogos": estatisticas.get("appearances", 0),
        "gols": estatisticas.get("totalGoals", 0),
        "entradas_reserva": estatisticas.get("subIns", 0),
        "assistencias": estatisticas.get("goalAssists", 0),
        "cartoes_amarelos": estatisticas.get("yellowCards", 0),
        "cartoes_vermelhos": estatisticas.get("redCards", 0),
    }

    # Adiciona o jogador na nossa lista
    lista_jogadores.append(dados_jogador)

# Transforma a lista inteira em DataFrame
df = pd.DataFrame(lista_jogadores)

print("\nDADOS DOS JOGADORES:")
print(df)

df.to_csv(
    "data/raw/estatisticas_jogadores_espn.csv",
    index=False
)

print("\nArquivo salvo com sucesso!")