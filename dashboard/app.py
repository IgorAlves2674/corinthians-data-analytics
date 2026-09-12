import subprocess
import sys
import html
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARQUIVO_PARTIDAS = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "partidas_corinthians_tratadas.csv"
)

ARQUIVO_JOGADORES = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "estatisticas_jogadores_por_90.csv"
)

SCRIPT_ATUALIZACAO = (
    PROJECT_ROOT
    / "src"
    / "update_data.py"
)


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Corinthians Data Analytics",
    page_icon="⚽",
    layout="wide"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0e0e0e;
        color: #f5f5f5;
    }

    [data-testid="stSidebar"] {
        background-color: #171717;
    }

    [data-testid="stMetric"] {
        background-color: #181818;
        border: 1px solid #303030;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 15px;
    }

    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }

    .dashboard-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .dashboard-subtitle {
        color: #aaaaaa;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def cor_resultado(resultado):

    if resultado == "Vitória":
        return "#59d17d"

    if resultado == "Empate":
        return "#f3c969"

    return "#ff6961"


def letra_resultado(resultado):

    if resultado == "Vitória":
        return "V"

    if resultado == "Empate":
        return "E"

    return "D"


def configurar_grafico(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#0e0e0e",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    return fig


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():

    partidas = pd.read_csv(
        ARQUIVO_PARTIDAS
    )

    jogadores = pd.read_csv(
        ARQUIVO_JOGADORES
    )

    partidas["data"] = pd.to_datetime(
        partidas["data"]
    )

    return partidas, jogadores


partidas, jogadores = carregar_dados()


# ============================================================
# POSIÇÕES EM PORTUGUÊS
# ============================================================

traducao_posicoes = {

    "Forward":
        "Atacante",

    "Midfielder":
        "Meio campista",

    "Defender":
        "Defensor",

    "Goalkeeper":
        "Goleiro",

    "Desconhecida":
        "Desconhecida"
}


jogadores["posicao_pt"] = (
    jogadores["posicao_oficial"]
    .map(traducao_posicoes)
    .fillna(
        jogadores["posicao_oficial"]
    )
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚽ Corinthians"
)

st.sidebar.caption(
    "Data Analytics • Brasileirão 2026"
)

st.sidebar.divider()


if st.sidebar.button(
    "🔄 Atualizar dados",
    use_container_width=True
):

    with st.spinner(
        "Buscando os dados mais recentes..."
    ):

        try:

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_ATUALIZACAO)
                ],
                cwd=PROJECT_ROOT,
                check=True
            )

            carregar_dados.clear()

            st.sidebar.success(
                "Dados atualizados!"
            )

            st.rerun()

        except subprocess.CalledProcessError:

            st.sidebar.error(
                "Erro durante a atualização."
            )


ultima_atualizacao = datetime.fromtimestamp(
    ARQUIVO_PARTIDAS.stat().st_mtime
)


st.sidebar.caption(
    "Última atualização"
)

st.sidebar.write(
    ultima_atualizacao.strftime(
        "%d/%m/%Y às %H:%M"
    )
)


st.sidebar.divider()

st.sidebar.caption(
    "Fonte dos dados"
)

st.sidebar.write(
    "ESPN • Brasileirão Série A"
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        Corinthians Data Analytics
    </div>

    <div class="dashboard-subtitle">
        Análise de desempenho coletivo e individual
        no Brasileirão 2026
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ABAS
# ============================================================

aba_geral, aba_jogadores, aba_partidas = st.tabs(
    [
        "📊 Visão geral",
        "👤 Jogadores",
        "⚽ Partidas"
    ]
)


# ============================================================
# ============================================================
# VISÃO GERAL
# ============================================================
# ============================================================

with aba_geral:

    partidas_ordenadas = (
        partidas
        .sort_values("data")
        .reset_index(drop=True)
    )

    ultima_partida = (
        partidas_ordenadas
        .iloc[-1]
    )


    # ========================================================
    # RESUMO DA TEMPORADA
    # ========================================================

    jogos = int(
        ultima_partida["jogo"]
    )

    pontos = int(
        ultima_partida["pontos_acumulados"]
    )

    aproveitamento = float(
        ultima_partida["aproveitamento"]
    )

    saldo = int(
        ultima_partida["saldo_acumulado"]
    )

    gols_feitos = int(
        ultima_partida[
            "gols_feitos_acumulados"
        ]
    )

    gols_sofridos = int(
        ultima_partida[
            "gols_sofridos_acumulados"
        ]
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Jogos",
            jogos
        )


    with col2:

        st.metric(
            "Pontos",
            pontos
        )


    with col3:

        st.metric(
            "Aproveitamento",
            f"{aproveitamento:.2f}%"
        )


    with col4:

        st.metric(
            "Saldo de gols",
            f"{saldo:+d}"
        )


    # ========================================================
    # ÚLTIMO JOGO
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Último jogo'
        '</div>',
        unsafe_allow_html=True
    )


    data_ultimo = (
        ultima_partida["data"]
        .strftime("%d/%m/%Y")
    )

    adversario = html.escape(
        str(
            ultima_partida[
                "adversario"
            ]
        )
    )

    gols_corinthians = int(
        ultima_partida[
            "gols_corinthians"
        ]
    )

    gols_adversario = int(
        ultima_partida[
            "gols_adversario"
        ]
    )

    resultado = str(
        ultima_partida[
            "resultado"
        ]
    )

    mando = str(
        ultima_partida[
            "mando"
        ]
    )


    # Organiza o placar conforme o mando
    if mando == "Casa":

        time_esquerda = "Corinthians"
        gols_esquerda = gols_corinthians

        time_direita = adversario
        gols_direita = gols_adversario

    else:

        time_esquerda = adversario
        gols_esquerda = gols_adversario

        time_direita = "Corinthians"
        gols_direita = gols_corinthians


    cor = cor_resultado(
        resultado
    )


    card_ultimo_jogo = (
        '<div style="'
        'background:#181818;'
        'border:1px solid #303030;'
        'border-radius:14px;'
        'padding:26px;'
        'margin-bottom:25px;'
        '">'
        f'<div style="color:#aaaaaa;font-size:14px;margin-bottom:12px;">'
        f'{data_ultimo} • {mando}'
        '</div>'
        '<div style="'
        'font-size:28px;'
        'font-weight:700;'
        'margin-bottom:12px;'
        '">'
        f'{time_esquerda} '
        f'{gols_esquerda} '
        f'× '
        f'{gols_direita} '
        f'{time_direita}'
        '</div>'
        f'<div style="color:{cor};font-size:18px;font-weight:700;">'
        f'{resultado}'
        '</div>'
        '</div>'
    )


    st.html(
        card_ultimo_jogo
    )


    # ========================================================
    # GRÁFICOS DA TEMPORADA
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            '<div class="section-title">'
            'Evolução dos pontos'
            '</div>',
            unsafe_allow_html=True
        )


        fig_pontos = px.line(
            partidas_ordenadas,
            x="jogo",
            y="pontos_acumulados",
            markers=True,
            labels={
                "jogo":
                    "Partida",

                "pontos_acumulados":
                    "Pontos"
            }
        )


        fig_pontos.update_xaxes(
            dtick=1
        )


        configurar_grafico(
            fig_pontos
        )


        st.plotly_chart(
            fig_pontos,
            use_container_width=True
        )


    with col2:

        st.markdown(
            '<div class="section-title">'
            'Evolução do aproveitamento'
            '</div>',
            unsafe_allow_html=True
        )


        fig_aproveitamento = px.line(
            partidas_ordenadas,
            x="jogo",
            y="aproveitamento",
            markers=True,
            labels={
                "jogo":
                    "Partida",

                "aproveitamento":
                    "Aproveitamento (%)"
            }
        )


        fig_aproveitamento.update_xaxes(
            dtick=1
        )


        configurar_grafico(
            fig_aproveitamento
        )


        st.plotly_chart(
            fig_aproveitamento,
            use_container_width=True
        )


    # ========================================================
    # CAMPANHA
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Resumo da campanha'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Vitórias",
            int(
                ultima_partida[
                    "vitorias_acumuladas"
                ]
            )
        )


    with col2:

        st.metric(
            "Empates",
            int(
                ultima_partida[
                    "empates_acumulados"
                ]
            )
        )


    with col3:

        st.metric(
            "Derrotas",
            int(
                ultima_partida[
                    "derrotas_acumuladas"
                ]
            )
        )


    with col4:

        st.metric(
            "Gols feitos / sofridos",
            f"{gols_feitos} / {gols_sofridos}"
        )


    # ========================================================
    # FORMA RECENTE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Forma recente'
        '</div>',
        unsafe_allow_html=True
    )


    ultimos_5 = (
        partidas_ordenadas
        .tail(5)
        .copy()
    )


    pontos_recentes = int(
        ultimos_5[
            "pontos"
        ].sum()
    )


    aproveitamento_recente = (
        pontos_recentes
        / 15
        * 100
    )


    col1, col2 = st.columns(
        [3, 1]
    )


    # ========================================================
    # CARDS DOS ÚLTIMOS 5 JOGOS
    # ========================================================

    with col1:

        colunas_resultados = st.columns(5)


        for coluna, (_, partida) in zip(
            colunas_resultados,
            ultimos_5.iterrows()
        ):

            resultado_recente = str(
                partida["resultado"]
            )

            letra = letra_resultado(
                resultado_recente
            )

            cor = cor_resultado(
                resultado_recente
            )

            adversario_recente = html.escape(
                str(
                    partida[
                        "adversario"
                    ]
                )
            )

            gols_cor = int(
                partida[
                    "gols_corinthians"
                ]
            )

            gols_adv = int(
                partida[
                    "gols_adversario"
                ]
            )


            if partida["mando"] == "Casa":

                placar = (
                    f"{gols_cor} × {gols_adv}"
                )

            else:

                placar = (
                    f"{gols_adv} × {gols_cor}"
                )


            card_resultado = (
                '<div style="'
                'background:#181818;'
                'border:1px solid #303030;'
                'border-radius:12px;'
                'padding:15px 10px;'
                'text-align:center;'
                'min-height:125px;'
                '">'
                f'<div style="color:{cor};font-size:28px;font-weight:800;">'
                f'{letra}'
                '</div>'
                f'<div style="font-size:13px;font-weight:600;margin-top:6px;">'
                f'{adversario_recente}'
                '</div>'
                '<div style="color:#aaaaaa;font-size:13px;margin-top:6px;">'
                f'{placar}'
                '</div>'
                '</div>'
            )


            with coluna:

                st.html(
                    card_resultado
                )


    with col2:

        st.metric(
            "Aproveitamento nos últimos 5",
            f"{aproveitamento_recente:.2f}%"
        )


    # ========================================================
    # TABELA DOS ÚLTIMOS JOGOS
    # ========================================================

    st.markdown(
        "#### Últimos jogos"
    )


    tabela_recentes = ultimos_5[
        [
            "data",
            "adversario",
            "mando",
            "gols_corinthians",
            "gols_adversario",
            "resultado"
        ]
    ].copy()


    tabela_recentes[
        "data"
    ] = (
        tabela_recentes[
            "data"
        ]
        .dt.strftime(
            "%d/%m/%Y"
        )
    )


    tabela_recentes = (
        tabela_recentes
        .rename(
            columns={
                "data":
                    "Data",

                "adversario":
                    "Adversário",

                "mando":
                    "Mando",

                "gols_corinthians":
                    "Gols Corinthians",

                "gols_adversario":
                    "Gols adversário",

                "resultado":
                    "Resultado"
            }
        )
    )


    st.dataframe(
        tabela_recentes,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ============================================================
# JOGADORES
# ============================================================
# ============================================================

with aba_jogadores:

    st.markdown(
        '<div class="section-title">'
        'Análise individual'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # FILTROS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        minutos_minimos = st.slider(
            "Mínimo de minutos",
            min_value=0,
            max_value=int(
                jogadores[
                    "minutos"
                ].max()
            ),
            value=450,
            step=50
        )


    with col2:

        opcoes_posicao = [
            "Todas",
            "Atacante",
            "Meio campista",
            "Defensor",
            "Goleiro",
            "Desconhecida"
        ]


        posicao_escolhida = (
            st.selectbox(
                "Posição",
                opcoes_posicao
            )
        )


    # ========================================================
    # FILTRAGEM
    # ========================================================

    jogadores_filtrados = (
        jogadores[
            jogadores[
                "minutos"
            ] >= minutos_minimos
        ]
        .copy()
    )


    if posicao_escolhida != "Todas":

        jogadores_filtrados = (
            jogadores_filtrados[
                jogadores_filtrados[
                    "posicao_pt"
                ]
                == posicao_escolhida
            ]
        )


    # ========================================================
    # RANKING
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Participações em gols por 90 minutos'
        '</div>',
        unsafe_allow_html=True
    )


    ranking = (
        jogadores_filtrados
        .sort_values(
            "participacoes_por_90",
            ascending=False
        )
        .head(10)
    )


    if ranking.empty:

        st.warning(
            "Nenhum jogador atende aos filtros selecionados."
        )


    else:

        fig_ranking = px.bar(
            ranking,
            x="participacoes_por_90",
            y="nome",
            orientation="h",
            hover_data=[
                "gols",
                "assistencias",
                "minutos"
            ],
            labels={
                "participacoes_por_90":
                    "Participações / 90",

                "nome":
                    "Jogador"
            }
        )


        fig_ranking.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )


        configurar_grafico(
            fig_ranking
        )


        st.plotly_chart(
            fig_ranking,
            use_container_width=True
        )


    # ========================================================
    # DESTAQUES
    # ========================================================

    if not jogadores_filtrados.empty:

        artilheiro = (
            jogadores_filtrados
            .sort_values(
                "gols",
                ascending=False
            )
            .iloc[0]
        )


        assistente = (
            jogadores_filtrados
            .sort_values(
                "assistencias",
                ascending=False
            )
            .iloc[0]
        )


        eficiente = (
            jogadores_filtrados
            .sort_values(
                "participacoes_por_90",
                ascending=False
            )
            .iloc[0]
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Artilheiro",
                artilheiro["nome"],
                f'{int(artilheiro["gols"])} gols'
            )


        with col2:

            st.metric(
                "Mais assistências",
                assistente["nome"],
                (
                    f'{int(assistente["assistencias"])} '
                    f'assistências'
                )
            )


        with col3:

            st.metric(
                "Maior G+A / 90",
                eficiente["nome"],
                (
                    f'{eficiente["participacoes_por_90"]:.3f}'
                )
            )


    # ========================================================
    # PERFIL DO JOGADOR
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Perfil do jogador'
        '</div>',
        unsafe_allow_html=True
    )


    nomes = sorted(
        jogadores[
            "nome"
        ]
        .dropna()
        .unique()
    )


    jogador_escolhido = st.selectbox(
        "Selecione um jogador",
        nomes
    )


    jogador = (
        jogadores[
            jogadores[
                "nome"
            ] == jogador_escolhido
        ]
        .iloc[0]
    )


    st.caption(
        f'Posição: '
        f'{jogador["posicao_pt"]}'
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Jogos",
            int(
                jogador["jogos"]
            )
        )


    with col2:

        st.metric(
            "Minutos",
            f'{jogador["minutos"]:.0f}'
        )


    with col3:

        st.metric(
            "Gols",
            int(
                jogador["gols"]
            )
        )


    with col4:

        st.metric(
            "Assistências",
            int(
                jogador[
                    "assistencias"
                ]
            )
        )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "Gols / 90",
            (
                f'{jogador["gols_por_90"]:.3f}'
            )
        )


    with col2:

        st.metric(
            "Assistências / 90",
            (
                f'{jogador["assistencias_por_90"]:.3f}'
            )
        )


    with col3:

        st.metric(
            "Participações / 90",
            (
                f'{jogador["participacoes_por_90"]:.3f}'
            )
        )


    # ========================================================
    # COMPARAÇÃO ENTRE JOGADORES
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Comparação entre jogadores'
        '</div>',
        unsafe_allow_html=True
    )


    st.caption(
        "Compare a produção de dois jogadores "
        "considerando o tempo efetivamente jogado."
    )


    nomes_comparacao = sorted(
        jogadores[
            "nome"
        ]
        .dropna()
        .unique()
    )


    col1, col2 = st.columns(2)


    with col1:

        jogador_a_nome = st.selectbox(
            "Jogador A",
            nomes_comparacao,
            index=0,
            key="comparacao_jogador_a"
        )


    with col2:

        indice_b = (
            1
            if len(nomes_comparacao) > 1
            else 0
        )


        jogador_b_nome = st.selectbox(
            "Jogador B",
            nomes_comparacao,
            index=indice_b,
            key="comparacao_jogador_b"
        )


    if jogador_a_nome == jogador_b_nome:

        st.warning(
            "Selecione dois jogadores diferentes."
        )


    else:

        jogador_a = (
            jogadores[
                jogadores[
                    "nome"
                ] == jogador_a_nome
            ]
            .iloc[0]
        )


        jogador_b = (
            jogadores[
                jogadores[
                    "nome"
                ] == jogador_b_nome
            ]
            .iloc[0]
        )


        # ====================================================
        # RESUMO DOS JOGADORES
        # ====================================================

        st.markdown(
            "#### Resumo"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                f"### {jogador_a_nome}"
            )

            st.caption(
                jogador_a[
                    "posicao_pt"
                ]
            )


            a1, a2, a3 = st.columns(3)


            with a1:

                st.metric(
                    "Jogos",
                    int(
                        jogador_a[
                            "jogos"
                        ]
                    )
                )


            with a2:

                st.metric(
                    "Minutos",
                    (
                        f'{jogador_a["minutos"]:.0f}'
                    )
                )


            with a3:

                st.metric(
                    "Titularidades",
                    int(
                        jogador_a[
                            "titularidades"
                        ]
                    )
                )


        with col2:

            st.markdown(
                f"### {jogador_b_nome}"
            )

            st.caption(
                jogador_b[
                    "posicao_pt"
                ]
            )


            b1, b2, b3 = st.columns(3)


            with b1:

                st.metric(
                    "Jogos",
                    int(
                        jogador_b[
                            "jogos"
                        ]
                    )
                )


            with b2:

                st.metric(
                    "Minutos",
                    (
                        f'{jogador_b["minutos"]:.0f}'
                    )
                )


            with b3:

                st.metric(
                    "Titularidades",
                    int(
                        jogador_b[
                            "titularidades"
                        ]
                    )
                )


        # ====================================================
        # MÉTRICAS POR 90
        # ====================================================

        metricas_comparacao = {

            "Gols / 90":
                "gols_por_90",

            "Assistências / 90":
                "assistencias_por_90",

            "Participações / 90":
                "participacoes_por_90",

            "Finalizações / 90":
                "finalizacoes_por_90",

            "Finalizações no gol / 90":
                "finalizacoes_gol_por_90"
        }


        dados_comparacao = []


        for (
            nome_metrica,
            coluna
        ) in metricas_comparacao.items():

            dados_comparacao.append(
                {
                    "Métrica":
                        nome_metrica,

                    "Jogador":
                        jogador_a_nome,

                    "Valor":
                        jogador_a[
                            coluna
                        ]
                }
            )


            dados_comparacao.append(
                {
                    "Métrica":
                        nome_metrica,

                    "Jogador":
                        jogador_b_nome,

                    "Valor":
                        jogador_b[
                            coluna
                        ]
                }
            )


        df_comparacao = pd.DataFrame(
            dados_comparacao
        )


        st.markdown(
            "#### Métricas por 90 minutos"
        )


        fig_comparacao = px.bar(
            df_comparacao,
            x="Métrica",
            y="Valor",
            color="Jogador",
            barmode="group",
            text_auto=".2f",
            labels={
                "Valor":
                    "Valor por 90 minutos"
            }
        )


        fig_comparacao.update_layout(
            legend_title_text=""
        )


        configurar_grafico(
            fig_comparacao
        )


        st.plotly_chart(
            fig_comparacao,
            use_container_width=True
        )


        # ====================================================
        # TABELA DE COMPARAÇÃO
        # ====================================================

        tabela_comparacao = pd.DataFrame(
            [
                {
                    "Jogador":
                        jogador_a_nome,

                    "Posição":
                        jogador_a[
                            "posicao_pt"
                        ],

                    "Jogos":
                        int(
                            jogador_a[
                                "jogos"
                            ]
                        ),

                    "Minutos":
                        round(
                            jogador_a[
                                "minutos"
                            ],
                            1
                        ),

                    "Gols":
                        int(
                            jogador_a[
                                "gols"
                            ]
                        ),

                    "Assistências":
                        int(
                            jogador_a[
                                "assistencias"
                            ]
                        ),

                    "G+A / 90":
                        round(
                            jogador_a[
                                "participacoes_por_90"
                            ],
                            3
                        )
                },

                {
                    "Jogador":
                        jogador_b_nome,

                    "Posição":
                        jogador_b[
                            "posicao_pt"
                        ],

                    "Jogos":
                        int(
                            jogador_b[
                                "jogos"
                            ]
                        ),

                    "Minutos":
                        round(
                            jogador_b[
                                "minutos"
                            ],
                            1
                        ),

                    "Gols":
                        int(
                            jogador_b[
                                "gols"
                            ]
                        ),

                    "Assistências":
                        int(
                            jogador_b[
                                "assistencias"
                            ]
                        ),

                    "G+A / 90":
                        round(
                            jogador_b[
                                "participacoes_por_90"
                            ],
                            3
                        )
                }
            ]
        )


        st.dataframe(
            tabela_comparacao,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ============================================================
# PARTIDAS
# ============================================================
# ============================================================

with aba_partidas:

    st.markdown(
        '<div class="section-title">'
        'Desempenho em casa e fora'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # AGREGAÇÃO CASA X FORA
    # ========================================================

    casa_fora = (
        partidas
        .groupby(
            "mando"
        )
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
        .reset_index()
    )


    casa_fora["saldo_gols"] = (
        casa_fora["gols_feitos"]
        - casa_fora["gols_sofridos"]
    )


    casa_fora["aproveitamento"] = (
        casa_fora["pontos"]
        / (
            casa_fora["jogos"]
            * 3
        )
        * 100
    )


    # ========================================================
    # CARDS CASA X FORA
    # ========================================================

    casa = (
        casa_fora[
            casa_fora[
                "mando"
            ] == "Casa"
        ]
    )


    fora = (
        casa_fora[
            casa_fora[
                "mando"
            ] == "Fora"
        ]
    )


    col1, col2 = st.columns(2)


    if not casa.empty:

        casa = casa.iloc[0]

        with col1:

            st.markdown(
                "### 🏠 Casa"
            )

            c1, c2, c3 = (
                st.columns(3)
            )

            with c1:

                st.metric(
                    "Jogos",
                    int(
                        casa[
                            "jogos"
                        ]
                    )
                )

            with c2:

                st.metric(
                    "Pontos",
                    int(
                        casa[
                            "pontos"
                        ]
                    )
                )

            with c3:

                st.metric(
                    "Aproveitamento",
                    (
                        f'{casa["aproveitamento"]:.2f}%'
                    )
                )


    if not fora.empty:

        fora = fora.iloc[0]

        with col2:

            st.markdown(
                "### ✈️ Fora"
            )

            f1, f2, f3 = (
                st.columns(3)
            )

            with f1:

                st.metric(
                    "Jogos",
                    int(
                        fora[
                            "jogos"
                        ]
                    )
                )

            with f2:

                st.metric(
                    "Pontos",
                    int(
                        fora[
                            "pontos"
                        ]
                    )
                )

            with f3:

                st.metric(
                    "Aproveitamento",
                    (
                        f'{fora["aproveitamento"]:.2f}%'
                    )
                )


    # ========================================================
    # GRÁFICO CASA X FORA
    # ========================================================

    fig_casa_fora = px.bar(
        casa_fora,
        x="mando",
        y="aproveitamento",
        text_auto=".1f",
        labels={
            "mando":
                "Mando",

            "aproveitamento":
                "Aproveitamento (%)"
        }
    )


    configurar_grafico(
        fig_casa_fora
    )


    st.plotly_chart(
        fig_casa_fora,
        use_container_width=True
    )


    # ========================================================
    # TODAS AS PARTIDAS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Partidas disputadas'
        '</div>',
        unsafe_allow_html=True
    )


    tabela = (
        partidas
        .sort_values(
            "data",
            ascending=False
        )
        [
            [
                "data",
                "adversario",
                "mando",
                "gols_corinthians",
                "gols_adversario",
                "resultado",
                "pontos"
            ]
        ]
        .copy()
    )


    tabela["data"] = (
        tabela["data"]
        .dt.strftime(
            "%d/%m/%Y"
        )
    )


    tabela = (
        tabela
        .rename(
            columns={

                "data":
                    "Data",

                "adversario":
                    "Adversário",

                "mando":
                    "Mando",

                "gols_corinthians":
                    "Gols Corinthians",

                "gols_adversario":
                    "Gols adversário",

                "resultado":
                    "Resultado",

                "pontos":
                    "Pontos"
            }
        )
    )


    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True
    )