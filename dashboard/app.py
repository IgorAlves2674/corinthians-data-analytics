import html
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO E CAMINHOS
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

SCRIPT_ATUALIZACAO = PROJECT_ROOT / "src" / "update_data.py"

ASSETS_DIR = PROJECT_ROOT / "assets"
ESCUDO_PATH = ASSETS_DIR / "corinthians_escudo.png"

# PNG transparente em alta resolução (Wikimedia Commons, CC BY-SA 4.0)
ESCUDO_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/6/6b/"
    "Official_Logo_of_Sport_Club_Corinthians_Paulista_crest_2026.png"
)

# Paleta inspirada no Corinthians
COR_PRETO = "#090909"
COR_GRAFITE = "#151515"
COR_GRAFITE_2 = "#1D1D1D"
COR_BORDA = "#303030"
COR_BRANCO = "#F5F5F5"
COR_CINZA = "#A8A8A8"
COR_VERMELHO = "#E41E2B"
COR_VERMELHO_ESCURO = "#B51620"
COR_VERDE = "#45D483"
COR_AMARELO = "#F1C75B"
COR_DERROTA = "#FF5C5C"


st.set_page_config(
    page_title="Corinthians Data Analytics",
    page_icon="⚽",
    layout="wide",
)


# ============================================================
# ASSET DO ESCUDO
# ============================================================

def garantir_escudo():
    """Baixa o escudo para assets/ apenas se o arquivo ainda não existir."""

    if ESCUDO_PATH.exists():
        return True

    try:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)

        response = requests.get(
            ESCUDO_URL,
            timeout=20,
        )
        response.raise_for_status()

        ESCUDO_PATH.write_bytes(response.content)
        return True

    except (requests.RequestException, OSError):
        return False


ESCUDO_DISPONIVEL = garantir_escudo()


# ============================================================
# CSS / IDENTIDADE VISUAL
# ============================================================

st.markdown(
    f"""
    <style>

    :root {{
        --sccp-red: {COR_VERMELHO};
        --sccp-black: {COR_PRETO};
        --sccp-card: {COR_GRAFITE};
        --sccp-border: {COR_BORDA};
        --sccp-white: {COR_BRANCO};
        --sccp-muted: {COR_CINZA};
    }}

    .stApp {{
        background:
            radial-gradient(circle at top right, rgba(228, 30, 43, 0.08), transparent 28%),
            #090909;
        color: var(--sccp-white);
    }}

    .block-container {{
        padding-top: 1.15rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}

    [data-testid="stSidebar"] {{
        background: #111111;
        border-right: 1px solid #242424;
    }}

    [data-testid="stSidebar"] img {{
        display: block;
        margin-left: auto;
        margin-right: auto;
    }}

    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, #191919, #131313);
        border: 1px solid #2b2b2b;
        border-top: 2px solid var(--sccp-red);
        padding: 12px 16px;
        border-radius: 13px;
        min-height: 92px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
    }}

    [data-testid="stMetricLabel"] {{
        color: #a9a9a9;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.045em;
        text-transform: uppercase;
    }}

    [data-testid="stMetricValue"] {{
        color: #ffffff;
        font-size: 1.62rem;
        font-weight: 900;
    }}

    .sccp-eyebrow {{
        color: var(--sccp-red);
        font-size: 0.74rem;
        letter-spacing: 0.14em;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 3px;
    }}

    .dashboard-title {{
        color: #ffffff;
        font-size: 2.18rem;
        line-height: 1.02;
        font-weight: 900;
        margin: 0;
    }}

    .dashboard-subtitle {{
        color: #a9a9a9;
        font-size: 0.92rem;
        margin-top: 5px;
    }}

    .season-pill {{
        display: inline-block;
        background: rgba(228, 30, 43, 0.12);
        color: #ff6771;
        border: 1px solid rgba(228, 30, 43, 0.38);
        border-radius: 999px;
        padding: 4px 10px;
        margin-top: 8px;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.06em;
    }}

    .section-title {{
        color: #ffffff;
        font-size: 1.22rem;
        font-weight: 800;
        margin-top: 0.65rem;
        margin-bottom: 0.42rem;
        padding-left: 10px;
        border-left: 4px solid var(--sccp-red);
    }}

    [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid #2a2a2a;
    }}

    [data-baseweb="tab"] {{
        background: #151515;
        border-radius: 10px 10px 0 0;
        padding-left: 18px;
        padding-right: 18px;
        color: #b7b7b7;
        font-weight: 700;
    }}

    [aria-selected="true"][data-baseweb="tab"] {{
        background: rgba(228, 30, 43, 0.12);
        color: var(--sccp-red) !important;
    }}

    [data-baseweb="tab-highlight"] {{
        background-color: var(--sccp-red) !important;
    }}

    .match-card {{
        background: linear-gradient(135deg, #181818, #111111);
        border: 1px solid #303030;
        border-left: 4px solid var(--sccp-red);
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 14px;
    }}

    .match-meta {{
        color: #8f8f8f;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}

    .scoreboard {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
        align-items: center;
        gap: 18px;
    }}

    .team-name {{
        color: #f5f5f5;
        font-size: 1.16rem;
        font-weight: 850;
    }}

    .team-left {{ text-align: right; }}
    .team-right {{ text-align: left; }}

    .score {{
        color: #ffffff;
        font-size: 2rem;
        line-height: 1;
        font-weight: 950;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }}

    .score-x {{
        color: #666;
        padding: 0 5px;
    }}

    .match-footer {{
        display: flex;
        justify-content: center;
        margin-top: 9px;
    }}

    .result-pill {{
        display: inline-block;
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 0.66rem;
        font-weight: 900;
        letter-spacing: 0.06em;
    }}

    @media (max-width: 800px) {{
        .scoreboard {{
            grid-template-columns: 1fr;
            gap: 7px;
            text-align: center;
        }}
        .team-left, .team-right {{ text-align: center; }}
    }}

    .stButton > button {{
        background: var(--sccp-red);
        color: white;
        border: 1px solid var(--sccp-red);
        border-radius: 10px;
        font-weight: 800;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        background: #ff3340;
        border-color: #ff3340;
        color: white;
        transform: translateY(-1px);
    }}

    div[data-baseweb="select"] > div {{
        background: #171717;
        border-color: #353535;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid #282828;
        border-radius: 12px;
        overflow: hidden;
    }}

    hr {{
        border-color: #292929 !important;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def cor_resultado(resultado):
    if resultado == "Vitória":
        return COR_VERDE
    if resultado == "Empate":
        return COR_AMARELO
    return COR_DERROTA


def letra_resultado(resultado):
    if resultado == "Vitória":
        return "V"
    if resultado == "Empate":
        return "E"
    return "D"


def configurar_grafico(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COR_PRETO,
        plot_bgcolor=COR_PRETO,
        font=dict(color="#E8E8E8"),
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#242424", zerolinecolor="#242424")
    fig.update_yaxes(gridcolor="#242424", zerolinecolor="#242424")
    return fig


@st.cache_data
def carregar_dados():
    partidas = pd.read_csv(ARQUIVO_PARTIDAS)
    jogadores = pd.read_csv(ARQUIVO_JOGADORES)

    partidas["data"] = pd.to_datetime(partidas["data"])

    return partidas, jogadores


partidas, jogadores = carregar_dados()


traducao_posicoes = {
    "Forward": "Atacante",
    "Midfielder": "Meio campista",
    "Defender": "Defensor",
    "Goalkeeper": "Goleiro",
    "Desconhecida": "Desconhecida",
}

jogadores["posicao_pt"] = (
    jogadores["posicao_oficial"]
    .map(traducao_posicoes)
    .fillna(jogadores["posicao_oficial"])
)


# ============================================================
# SIDEBAR
# ============================================================

if ESCUDO_DISPONIVEL:
    st.sidebar.image(str(ESCUDO_PATH), width=96)
else:
    st.sidebar.markdown("# ⚽ SCCP")

st.sidebar.markdown(
    "<div style='text-align:center;font-size:1.25rem;font-weight:900;'>"
    "Corinthians Data Analytics"
    "</div>",
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    "<div style='text-align:center;color:#999;font-size:.85rem;margin-top:4px;'>"
    "Brasileirão 2026"
    "</div>",
    unsafe_allow_html=True,
)

st.sidebar.divider()

if st.sidebar.button("🔄 Atualizar dados", use_container_width=True):
    with st.spinner("Buscando os dados mais recentes..."):
        try:
            subprocess.run(
                [sys.executable, str(SCRIPT_ATUALIZACAO)],
                cwd=PROJECT_ROOT,
                check=True,
            )
            carregar_dados.clear()
            st.sidebar.success("Dados atualizados!")
            st.rerun()

        except subprocess.CalledProcessError:
            st.sidebar.error("Erro durante a atualização.")

ultima_atualizacao = datetime.fromtimestamp(
    ARQUIVO_PARTIDAS.stat().st_mtime
)

st.sidebar.caption("Última atualização")
st.sidebar.write(
    ultima_atualizacao.strftime("%d/%m/%Y às %H:%M")
)

st.sidebar.divider()
st.sidebar.caption("Fonte estatística")
st.sidebar.write("ESPN • Brasileirão Série A")
st.sidebar.caption(
    "Escudo: Fratino.koko / Wikimedia Commons • CC BY-SA 4.0"
)


# ============================================================
# CABEÇALHO
# ============================================================

col_logo, col_header = st.columns([0.55, 5.45], vertical_alignment="center")

with col_logo:
    if ESCUDO_DISPONIVEL:
        st.image(str(ESCUDO_PATH), width=86)

with col_header:
    st.markdown(
        """
        <div class="sccp-eyebrow">Sport Club Corinthians Paulista • 1910</div>
        <div class="dashboard-title">Corinthians Data Analytics</div>
        <div class="dashboard-subtitle">
            Desempenho coletivo e individual com dados atualizados do Brasileirão.
        </div>
        <span class="season-pill">BRASILEIRÃO 2026</span>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# ABAS
# ============================================================

aba_geral, aba_jogadores, aba_partidas = st.tabs(
    ["Visão geral", "Jogadores", "Partidas"]
)


# ============================================================
# VISÃO GERAL
# ============================================================

with aba_geral:
    partidas_ordenadas = (
        partidas.sort_values("data").reset_index(drop=True)
    )
    ultima_partida = partidas_ordenadas.iloc[-1]

    jogos = int(ultima_partida["jogo"])
    pontos = int(ultima_partida["pontos_acumulados"])
    aproveitamento = float(ultima_partida["aproveitamento"])
    saldo = int(ultima_partida["saldo_acumulado"])
    gols_feitos = int(ultima_partida["gols_feitos_acumulados"])
    gols_sofridos = int(ultima_partida["gols_sofridos_acumulados"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("JOGOS", jogos)

    with col2:
        st.metric("PONTOS", pontos)

    with col3:
        st.metric("APROVEITAMENTO", f"{aproveitamento:.2f}%")

    with col4:
        st.metric("SALDO DE GOLS", f"{saldo:+d}")

    st.markdown(
        '<div class="section-title">Último jogo</div>',
        unsafe_allow_html=True,
    )

    data_ultimo = ultima_partida["data"].strftime("%d/%m/%Y")
    adversario = html.escape(str(ultima_partida["adversario"]))
    gols_corinthians = int(ultima_partida["gols_corinthians"])
    gols_adversario = int(ultima_partida["gols_adversario"])
    resultado = str(ultima_partida["resultado"])
    mando = str(ultima_partida["mando"])

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

    cor = cor_resultado(resultado)

    card_ultimo_jogo = (
        '<div class="match-card">'
        f'<div class="match-meta">{data_ultimo} • {mando.upper()}</div>'
        '<div class="scoreboard">'
        f'<div class="team-name team-left">{time_esquerda}</div>'
        f'<div class="score">{gols_esquerda}<span class="score-x">×</span>{gols_direita}</div>'
        f'<div class="team-name team-right">{time_direita}</div>'
        '</div>'
        '<div class="match-footer">'
        f'<span class="result-pill" style="color:{cor};background:{cor}18;border:1px solid {cor}55;">'
        f'{resultado.upper()}</span>'
        '</div>'
        '</div>'
    )

    st.html(card_ultimo_jogo)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Evolução dos pontos</div>',
            unsafe_allow_html=True,
        )

        fig_pontos = px.line(
            partidas_ordenadas,
            x="jogo",
            y="pontos_acumulados",
            markers=True,
            labels={"jogo": "Partida", "pontos_acumulados": "Pontos"},
            color_discrete_sequence=[COR_BRANCO],
        )
        fig_pontos.update_traces(
            line=dict(width=3),
            marker=dict(size=6, color=COR_VERMELHO),
        )
        fig_pontos.update_xaxes(dtick=1)
        configurar_grafico(fig_pontos)
        fig_pontos.update_layout(height=300)
        st.plotly_chart(fig_pontos, use_container_width=True)

    with col2:
        st.markdown(
            '<div class="section-title">Evolução do aproveitamento</div>',
            unsafe_allow_html=True,
        )

        fig_aproveitamento = px.line(
            partidas_ordenadas,
            x="jogo",
            y="aproveitamento",
            markers=True,
            labels={
                "jogo": "Partida",
                "aproveitamento": "Aproveitamento (%)",
            },
            color_discrete_sequence=[COR_VERMELHO],
        )
        fig_aproveitamento.update_traces(
            line=dict(width=3),
            marker=dict(size=6, color=COR_BRANCO),
        )
        fig_aproveitamento.update_xaxes(dtick=1)
        configurar_grafico(fig_aproveitamento)
        fig_aproveitamento.update_layout(height=300)
        st.plotly_chart(fig_aproveitamento, use_container_width=True)

    st.markdown(
        '<div class="section-title">Resumo da campanha</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("✅ Vitórias", int(ultima_partida["vitorias_acumuladas"]))

    with col2:
        st.metric("➖ Empates", int(ultima_partida["empates_acumulados"]))

    with col3:
        st.metric("❌ Derrotas", int(ultima_partida["derrotas_acumuladas"]))

    with col4:
        st.metric("🥅 Gols feitos / sofridos", f"{gols_feitos} / {gols_sofridos}")

    st.markdown(
        '<div class="section-title">Forma recente</div>',
        unsafe_allow_html=True,
    )

    ultimos_5 = partidas_ordenadas.tail(5).copy()
    pontos_recentes = int(ultimos_5["pontos"].sum())
    aproveitamento_recente = pontos_recentes / 15 * 100

    col_forma, col_aprov = st.columns([3.2, 1])

    with col_forma:
        colunas_resultados = st.columns(5)

        for coluna, (_, partida) in zip(
            colunas_resultados,
            ultimos_5.iterrows(),
        ):
            resultado_recente = str(partida["resultado"])
            letra = letra_resultado(resultado_recente)
            cor = cor_resultado(resultado_recente)
            adversario_recente = html.escape(str(partida["adversario"]))
            gols_cor = int(partida["gols_corinthians"])
            gols_adv = int(partida["gols_adversario"])
            mando_recente = str(partida["mando"])

            card_resultado = (
                '<div style="background:#151515;border:1px solid #2d2d2d;'
                f'border-top:3px solid {cor};border-radius:12px;'
                'padding:14px 8px;text-align:center;min-height:142px;">'
                f'<div style="color:{cor};font-size:28px;font-weight:900;">{letra}</div>'
                f'<div style="font-size:12px;color:#888;margin-top:2px;">{mando_recente}</div>'
                f'<div style="font-size:13px;font-weight:700;margin-top:7px;">{adversario_recente}</div>'
                f'<div style="font-size:16px;color:#ddd;font-weight:800;margin-top:7px;">'
                f'COR {gols_cor} × {gols_adv}</div>'
                '</div>'
            )

            with coluna:
                st.html(card_resultado)

    with col_aprov:
        st.metric(
            "Últimos 5",
            f"{aproveitamento_recente:.2f}%",
            f"{pontos_recentes}/15 pontos",
        )

    st.markdown("#### Últimos jogos")

    tabela_recentes = ultimos_5[
        [
            "data",
            "adversario",
            "mando",
            "gols_corinthians",
            "gols_adversario",
            "resultado",
        ]
    ].copy()

    tabela_recentes["data"] = tabela_recentes["data"].dt.strftime("%d/%m/%Y")
    tabela_recentes = tabela_recentes.rename(
        columns={
            "data": "Data",
            "adversario": "Adversário",
            "mando": "Mando",
            "gols_corinthians": "Gols Corinthians",
            "gols_adversario": "Gols adversário",
            "resultado": "Resultado",
        }
    )

    st.dataframe(
        tabela_recentes,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# JOGADORES
# ============================================================

with aba_jogadores:
    st.markdown(
        '<div class="section-title">Análise individual</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        minutos_minimos = st.slider(
            "Mínimo de minutos",
            min_value=0,
            max_value=int(jogadores["minutos"].max()),
            value=450,
            step=50,
        )

    with col2:
        opcoes_posicao = [
            "Todas",
            "Atacante",
            "Meio campista",
            "Defensor",
            "Goleiro",
            "Desconhecida",
        ]
        posicao_escolhida = st.selectbox(
            "Posição",
            opcoes_posicao,
        )

    jogadores_filtrados = jogadores[
        jogadores["minutos"] >= minutos_minimos
    ].copy()

    if posicao_escolhida != "Todas":
        jogadores_filtrados = jogadores_filtrados[
            jogadores_filtrados["posicao_pt"] == posicao_escolhida
        ]

    st.markdown(
        '<div class="section-title">Participações em gols por 90 minutos</div>',
        unsafe_allow_html=True,
    )

    ranking = (
        jogadores_filtrados
        .sort_values("participacoes_por_90", ascending=False)
        .head(10)
    )

    if ranking.empty:
        st.warning("Nenhum jogador atende aos filtros selecionados.")

    else:
        fig_ranking = px.bar(
            ranking,
            x="participacoes_por_90",
            y="nome",
            orientation="h",
            hover_data=["gols", "assistencias", "minutos"],
            labels={
                "participacoes_por_90": "Participações / 90",
                "nome": "Jogador",
            },
            color_discrete_sequence=[COR_VERMELHO],
        )
        fig_ranking.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )
        configurar_grafico(fig_ranking)
        st.plotly_chart(fig_ranking, use_container_width=True)

    if not jogadores_filtrados.empty:
        artilheiro = (
            jogadores_filtrados
            .sort_values("gols", ascending=False)
            .iloc[0]
        )
        assistente = (
            jogadores_filtrados
            .sort_values("assistencias", ascending=False)
            .iloc[0]
        )
        eficiente = (
            jogadores_filtrados
            .sort_values("participacoes_por_90", ascending=False)
            .iloc[0]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "⚽ Artilheiro",
                artilheiro["nome"],
                f'{int(artilheiro["gols"])} gols',
            )

        with col2:
            st.metric(
                "🎯 Mais assistências",
                assistente["nome"],
                f'{int(assistente["assistencias"])} assistências',
            )

        with col3:
            st.metric(
                "🔥 Maior G+A / 90",
                eficiente["nome"],
                f'{eficiente["participacoes_por_90"]:.3f}',
            )

    st.divider()

    st.markdown(
        '<div class="section-title">Perfil do jogador</div>',
        unsafe_allow_html=True,
    )

    nomes = sorted(jogadores["nome"].dropna().unique())
    jogador_escolhido = st.selectbox(
        "Selecione um jogador",
        nomes,
    )

    jogador = jogadores[
        jogadores["nome"] == jogador_escolhido
    ].iloc[0]

    st.caption(f'Posição: {jogador["posicao_pt"]}')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Jogos", int(jogador["jogos"]))

    with col2:
        st.metric("Minutos", f'{jogador["minutos"]:.0f}')

    with col3:
        st.metric("Gols", int(jogador["gols"]))

    with col4:
        st.metric("Assistências", int(jogador["assistencias"]))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gols / 90", f'{jogador["gols_por_90"]:.3f}')

    with col2:
        st.metric(
            "Assistências / 90",
            f'{jogador["assistencias_por_90"]:.3f}',
        )

    with col3:
        st.metric(
            "Participações / 90",
            f'{jogador["participacoes_por_90"]:.3f}',
        )

    st.divider()

    st.markdown(
        '<div class="section-title">Comparação entre jogadores</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Compare a produção de dois jogadores considerando o tempo efetivamente jogado."
    )

    nomes_comparacao = sorted(jogadores["nome"].dropna().unique())

    col1, col2 = st.columns(2)

    with col1:
        jogador_a_nome = st.selectbox(
            "Jogador A",
            nomes_comparacao,
            index=0,
            key="comparacao_jogador_a",
        )

    with col2:
        indice_b = 1 if len(nomes_comparacao) > 1 else 0
        jogador_b_nome = st.selectbox(
            "Jogador B",
            nomes_comparacao,
            index=indice_b,
            key="comparacao_jogador_b",
        )

    if jogador_a_nome == jogador_b_nome:
        st.warning("Selecione dois jogadores diferentes.")

    else:
        jogador_a = jogadores[
            jogadores["nome"] == jogador_a_nome
        ].iloc[0]
        jogador_b = jogadores[
            jogadores["nome"] == jogador_b_nome
        ].iloc[0]

        st.markdown("#### Resumo")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### {jogador_a_nome}")
            st.caption(jogador_a["posicao_pt"])
            a1, a2, a3 = st.columns(3)

            with a1:
                st.metric("Jogos", int(jogador_a["jogos"]))
            with a2:
                st.metric("Minutos", f'{jogador_a["minutos"]:.0f}')
            with a3:
                st.metric("Titularidades", int(jogador_a["titularidades"]))

        with col2:
            st.markdown(f"### {jogador_b_nome}")
            st.caption(jogador_b["posicao_pt"])
            b1, b2, b3 = st.columns(3)

            with b1:
                st.metric("Jogos", int(jogador_b["jogos"]))
            with b2:
                st.metric("Minutos", f'{jogador_b["minutos"]:.0f}')
            with b3:
                st.metric("Titularidades", int(jogador_b["titularidades"]))

        metricas_comparacao = {
            "Gols / 90": "gols_por_90",
            "Assistências / 90": "assistencias_por_90",
            "Participações / 90": "participacoes_por_90",
            "Finalizações / 90": "finalizacoes_por_90",
            "Finalizações no gol / 90": "finalizacoes_gol_por_90",
        }

        dados_comparacao = []

        for nome_metrica, coluna in metricas_comparacao.items():
            dados_comparacao.append(
                {
                    "Métrica": nome_metrica,
                    "Jogador": jogador_a_nome,
                    "Valor": jogador_a[coluna],
                }
            )
            dados_comparacao.append(
                {
                    "Métrica": nome_metrica,
                    "Jogador": jogador_b_nome,
                    "Valor": jogador_b[coluna],
                }
            )

        df_comparacao = pd.DataFrame(dados_comparacao)

        st.markdown("#### Métricas por 90 minutos")

        fig_comparacao = px.bar(
            df_comparacao,
            x="Métrica",
            y="Valor",
            color="Jogador",
            barmode="group",
            text_auto=".2f",
            labels={"Valor": "Valor por 90 minutos"},
            color_discrete_sequence=[COR_VERMELHO, "#E8E8E8"],
        )

        configurar_grafico(fig_comparacao)
        st.plotly_chart(fig_comparacao, use_container_width=True)

        tabela_comparacao = pd.DataFrame(
            [
                {
                    "Jogador": jogador_a_nome,
                    "Posição": jogador_a["posicao_pt"],
                    "Jogos": int(jogador_a["jogos"]),
                    "Minutos": round(jogador_a["minutos"], 1),
                    "Gols": int(jogador_a["gols"]),
                    "Assistências": int(jogador_a["assistencias"]),
                    "G+A / 90": round(jogador_a["participacoes_por_90"], 3),
                },
                {
                    "Jogador": jogador_b_nome,
                    "Posição": jogador_b["posicao_pt"],
                    "Jogos": int(jogador_b["jogos"]),
                    "Minutos": round(jogador_b["minutos"], 1),
                    "Gols": int(jogador_b["gols"]),
                    "Assistências": int(jogador_b["assistencias"]),
                    "G+A / 90": round(jogador_b["participacoes_por_90"], 3),
                },
            ]
        )

        st.dataframe(
            tabela_comparacao,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# PARTIDAS
# ============================================================

with aba_partidas:
    st.markdown(
        '<div class="section-title">Desempenho em casa e fora</div>',
        unsafe_allow_html=True,
    )

    casa_fora = (
        partidas
        .groupby("mando")
        .agg(
            jogos=("partida_id", "count"),
            vitorias=("vitoria", "sum"),
            empates=("empate", "sum"),
            derrotas=("derrota", "sum"),
            pontos=("pontos", "sum"),
            gols_feitos=("gols_corinthians", "sum"),
            gols_sofridos=("gols_adversario", "sum"),
        )
        .reset_index()
    )

    casa_fora["saldo_gols"] = (
        casa_fora["gols_feitos"] - casa_fora["gols_sofridos"]
    )

    casa_fora["aproveitamento"] = (
        casa_fora["pontos"] / (casa_fora["jogos"] * 3) * 100
    )

    casa = casa_fora[casa_fora["mando"] == "Casa"]
    fora = casa_fora[casa_fora["mando"] == "Fora"]

    col1, col2 = st.columns(2)

    if not casa.empty:
        casa = casa.iloc[0]

        with col1:
            st.markdown("### 🏠 Casa")
            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Jogos", int(casa["jogos"]))
            with c2:
                st.metric("Pontos", int(casa["pontos"]))
            with c3:
                st.metric("Aproveitamento", f'{casa["aproveitamento"]:.2f}%')

    if not fora.empty:
        fora = fora.iloc[0]

        with col2:
            st.markdown("### ✈️ Fora")
            f1, f2, f3 = st.columns(3)

            with f1:
                st.metric("Jogos", int(fora["jogos"]))
            with f2:
                st.metric("Pontos", int(fora["pontos"]))
            with f3:
                st.metric("Aproveitamento", f'{fora["aproveitamento"]:.2f}%')

    fig_casa_fora = px.bar(
        casa_fora,
        x="mando",
        y="aproveitamento",
        text_auto=".1f",
        labels={
            "mando": "Mando",
            "aproveitamento": "Aproveitamento (%)",
        },
        color="mando",
        color_discrete_map={
            "Casa": COR_VERMELHO,
            "Fora": "#D8D8D8",
        },
    )

    configurar_grafico(fig_casa_fora)
    st.plotly_chart(fig_casa_fora, use_container_width=True)

    st.markdown(
        '<div class="section-title">Partidas disputadas</div>',
        unsafe_allow_html=True,
    )

    tabela = (
        partidas
        .sort_values("data", ascending=False)
        [
            [
                "data",
                "adversario",
                "mando",
                "gols_corinthians",
                "gols_adversario",
                "resultado",
                "pontos",
            ]
        ]
        .copy()
    )

    tabela["data"] = tabela["data"].dt.strftime("%d/%m/%Y")

    tabela = tabela.rename(
        columns={
            "data": "Data",
            "adversario": "Adversário",
            "mando": "Mando",
            "gols_corinthians": "Gols Corinthians",
            "gols_adversario": "Gols adversário",
            "resultado": "Resultado",
            "pontos": "Pontos",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )
