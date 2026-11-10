# Estudo

Meus estudos de **Python**: scripts e painéis pequenos para praticar automação, consumo de APIs, bancos de dados e interfaces. É um repositório de aprendizado, então os projetos são de tamanhos e níveis diferentes.

## O que tem aqui

| Pasta | Arquivo | O que faz |
|---|---|---|
| `Agenda` | `agenda_notificacoes.py` | Agenda de tarefas com lembretes por e-mail (SMTP), SQLite e agendamento automático. Interface em Streamlit. |
| `Agenda` | `matinal.py` | "Central Matinal": painel em Streamlit que reúne informações de APIs. |
| `Dinheiro` | `moeda.py` | Menu no terminal para consultar a cotação de moedas, converter reais e salvar o histórico em arquivo. |
| `Dinheiro` | `painel_investimentos.py` | Painel em Streamlit para consultar ativos da B3, simular aportes e acompanhar a carteira (dados do `yfinance`). |
| `cidades` | `app.py` | Buscador de cidades do mundo em Streamlit, com filtro em tempo real. |
| `cidades` | `cidades.py` | Baixa bases geográficas e gera a tabela `tabela_cidades_mundo.csv`. |
| `cidades` | `cep.py` | Consulta um endereço pelo CEP (API ViaCEP). |
| `cidades` | `clima.py` | Mostra o clima de uma cidade (API Open-Meteo). |
| `Testes` | `command_center.py` | "Enterprise Command Center": painel em Streamlit com análise de mercado e um processo de ETL. |
| `Testes` | `rede.py` | Lê informações da rede do computador. |
| `Testes` | `rpg.py` | RPG de texto no terminal, com efeito de digitação. |
| `Testes` | `jogo.py` | Jogo no terminal com `curses`. |
| `Testes` | `corrida_terminal.py` | Jogo de corrida em ASCII, só com Python (sem bibliotecas externas). |
| `Testes/DoomEternal` | `doom_terminal.py` | Experimento de renderização 3D em ASCII no terminal. |

## Como executar

Precisa do Python 3. Instale as bibliotecas usadas:

```bash
pip install streamlit pandas requests yfinance plotly apscheduler
```

Exemplos:

```bash
streamlit run Dinheiro/painel_investimentos.py   # painéis em Streamlit
streamlit run cidades/app.py
python Dinheiro/moeda.py                         # menu no terminal
python cidades/clima.py Foz do Iguaçu            # clima de uma cidade
python Testes/rpg.py
```

Os scripts que usam `curses` (como `Testes/jogo.py`) funcionam direto no Linux e no macOS. No Windows, instale antes `pip install windows-curses`.

### Agenda com e-mail

Em `Agenda/agenda_notificacoes.py`, as variáveis `SEU_EMAIL` e `SUA_SENHA_APP` estão com valores de exemplo. Para enviar e-mails de verdade, use uma **senha de aplicativo** do Gmail e **não envie sua senha para o GitHub**.

## Tecnologias

Python, Streamlit, pandas, Plotly, requests, SQLite, APScheduler, yfinance, curses
