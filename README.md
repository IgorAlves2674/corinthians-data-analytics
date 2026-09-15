# ⚽ Corinthians Data Analytics

Projeto de análise de dados desenvolvido para acompanhar o desempenho do **Sport Club Corinthians Paulista no Campeonato Brasileiro de 2026**, utilizando dados públicos disponibilizados pela ESPN.

O projeto realiza extração, tratamento, validação e análise dos dados, além de disponibilizar um **dashboard interativo em Streamlit** com informações da equipe e dos jogadores.

## 🚀 Dashboard online

https://corinthians-data-analytics.streamlit.app/

## 💻 Repositório

https://github.com/IgorAlves2674/corinthians-data-analytics

---

## 📊 Principais funcionalidades

### Visão geral

- Jogos disputados
- Pontos conquistados
- Aproveitamento
- Saldo de gols
- Vitórias, empates e derrotas
- Último jogo
- Forma recente
- Evolução dos pontos
- Evolução do aproveitamento

### Jogadores

- Filtro por posição
- Filtro por minutos jogados
- Artilharia
- Ranking de assistências
- Participações em gols por 90 minutos
- Gols por 90 minutos
- Assistências por 90 minutos
- Finalizações por 90 minutos
- Perfil individual
- Comparação entre jogadores

### Partidas

- Desempenho em casa
- Desempenho fora
- Aproveitamento por mando
- Pontos conquistados
- Gols marcados e sofridos
- Histórico de partidas

---

## 🔄 Pipeline de dados

O projeto possui um pipeline automatizado para atualizar os dados e preparar as bases utilizadas pelo dashboard.

```text
ESPN
  ↓
Extração
  ↓
Tratamento
  ↓
Validação
  ↓
Criação de métricas
  ↓
Dados processados
  ↓
Dashboard
```

A atualização completa pode ser executada com:

```bash
python src/update_data.py
```

O dashboard também possui um botão para atualização dos dados.

---

## 📐 Métricas por 90 minutos

Para permitir comparações mais justas entre jogadores com diferentes tempos em campo, o projeto utiliza métricas normalizadas por 90 minutos.

Entre elas:

- Gols por 90
- Assistências por 90
- Participações em gols por 90
- Finalizações por 90
- Finalizações no gol por 90

O dashboard permite definir uma quantidade mínima de minutos para reduzir distorções em rankings de eficiência.

---

## 🛠️ Tecnologias utilizadas

- Python
- Pandas
- NumPy
- Requests
- Matplotlib
- Plotly
- Streamlit
- Git
- GitHub
- Streamlit Community Cloud

Conceitos aplicados:

- ETL
- Data Cleaning
- Data Validation
- Feature Engineering
- Análise Exploratória de Dados
- Visualização de dados
- Automação de pipeline

---

## 📈 Algumas análises geradas

### Evolução dos pontos

![Evolução dos pontos](reports/figures/evolucao_pontos.png)

### Evolução do aproveitamento

![Evolução do aproveitamento](reports/figures/evolucao_aproveitamento.png)

### Participações por 90 minutos por posição

![Participações por posição](reports/figures/participacoes_por_90_posicao.png)

---

## ⚙️ Como executar localmente

Clone o repositório:

```bash
git clone https://github.com/IgorAlves2674/corinthians-data-analytics.git
```

Entre na pasta:

```bash
cd corinthians-data-analytics
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative no Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Atualize os dados:

```bash
python src/update_data.py
```

Execute o dashboard:

```bash
python -m streamlit run dashboard/app.py
```

---

## 🌐 Fonte dos dados

Os dados utilizados no projeto são obtidos através de endpoints públicos utilizados pela ESPN para informações do Campeonato Brasileiro.

Entre os dados utilizados estão:

- Elenco
- Estatísticas dos jogadores
- Escalações
- Substituições
- Cartões
- Resultados
- Gols
- Assistências
- Finalizações

> Este projeto possui finalidade educacional e de portfólio e não possui vínculo oficial com o Sport Club Corinthians Paulista ou com a ESPN.

---

## ⚠️ Limitações

- Os endpoints utilizados não são uma API oficial documentada para desenvolvedores.
- Alterações na estrutura da fonte podem exigir ajustes no pipeline.
- Algumas posições e minutos jogados precisam ser derivados a partir dos eventos das partidas.
- Métricas avançadas como xG e xA não estão disponíveis atualmente.

---

## 🛡️ Identidade visual

O dashboard utiliza uma identidade visual inspirada no Sport Club Corinthians Paulista.

O escudo utilizado foi obtido no Wikimedia Commons.

**Autor:** Fratino.koko  
**Licença:** CC BY-SA 4.0

https://commons.wikimedia.org/wiki/File:Official_Logo_of_Sport_Club_Corinthians_Paulista_crest_2026.png

---

## 👨‍💻 Autor

**Igor Alves Santos**

LinkedIn:  
https://www.linkedin.com/in/igor-alves-santos-5364992a3/

GitHub:  
https://github.com/IgorAlves2674