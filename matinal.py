import datetime
import requests
import streamlit as st

# 1. Configuração da página Web
st.set_page_config(page_title="Central Matinal", page_icon="☕", layout="wide")

# --- FUNÇÕES DE CONEXÃO COM AS APIs ---

@st.cache_data(ttl=300) # Cache de 5 minutos para evitar chamadas excessivas às APIs
def buscar_financas():
    """Busca cotações de Dólar, Euro, Bitcoin e Libra na AwesomeAPI."""
    url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        dados = res.json()
        return {
            "USD": float(dados["USDBRL"]["bid"]),
            "EUR": float(dados["EURBRL"]["bid"]),
            "BTC": float(dados["BTCBRL"]["bid"]),
            "GBP": float(dados["GBPBRL"]["bid"])
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def buscar_clima(cidade):
    """Busca dados meteorológicos via Open-Meteo API."""
    try:
        # Busca coordenadas da cidade
        url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
        res_geo = requests.get(url_geo, timeout=5).json()
        
        if not res_geo.get("results"):
            return None
            
        local_info = res_geo["results"][0]
        lat, lon = local_info["latitude"], local_info["longitude"]
        nome_cidade = local_info["name"]
        pais = local_info.get("country", "")

        # Busca temperatura atual
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res_clima = requests.get(url_clima, timeout=5).json()
        temp = res_clima["current_weather"]["temperature"]
        
        return {"local": f"{nome_cidade}, {pais}", "temp": temp}
    except Exception:
        return None

def buscar_conselho():
    """Busca frase inspiradora da AdviceSlip API."""
    try:
        res = requests.get("https://api.adviceslip.com/advice", timeout=5).json()
        return res["slip"]["advice"]
    except Exception:
        return "Concentre-se no progresso, não na perfeição!"

# --- INTERFACE GRÁFICA INTERATIVA (STREAMLIT) ---

st.title("☕ Central de Briefing Matinal & Produtividade")
st.write("Personalize os parâmetros na barra lateral para gerar seu relatório diário em tempo real.")

# Barra Lateral (Menu de Configuração Interativo)
st.sidebar.header("⚙️ Configurações do Relatório")

# Input de Cidade
cidade_input = st.sidebar.text_input("Sua Cidade:", value="São Paulo")

# Seletor de Moedas a Monitorar
moedas_selecionadas = st.sidebar.multiselect(
    "Selecione as Moedas:",
    options=["USD", "EUR", "BTC", "GBP"],
    default=["USD", "EUR", "BTC"]
)

# Adicionar Tarefas/Metas Pessoais do Dia
st.sidebar.subheader("📌 Suas Metas para Hoje")
tarefas_texto = st.sidebar.text_area(
    "Digite suas prioridades (uma por linha):",
    value="• Revisar código Python\n• Responder e-mails prioritários\n• Fazer exercício físico"
)

st.divider()

# --- PROCESSAMENTO E EXIBIÇÃO NO PAINEL ---

col_esquerda, col_direita = st.columns([1, 1])

# COLUNA 1: Clima e Finanças
with col_esquerda:
    st.subheader("🌤️ Clima em Tempo Real")
    dados_clima = buscar_clima(cidade_input)
    if dados_clima:
        st.metric(label=dados_clima["local"], value=f"{dados_clima['temp']} °C")
    else:
        st.warning(f"Não foi possível encontrar a cidade '{cidade_input}'.")

    st.subheader("📈 Mercado Financeiro")
    dados_financas = buscar_financas()
    
    if dados_financas and moedas_selecionadas:
        # Exibe métricas em colunas dinâmicas
        cols_moedas = st.columns(len(moedas_selecionadas))
        for i, m in enumerate(moedas_selecionadas):
            valor = dados_financas[m]
            formato = f"R$ {valor:,.2f}" if m != "BTC" else f"R$ {valor:,.0f}"
            cols_moedas[i].metric(label=f"Moeda {m}", value=formato)
    elif not moedas_selecionadas:
        st.info("Nenhuma moeda selecionada no menu lateral.")
    else:
        st.error("Falha ao carregar cotações.")

# COLUNA 2: Mensagem e Metas
with col_direita:
    st.subheader("💡 Conselho do Dia")
    conselho = buscar_conselho()
    st.info(f'"{conselho}"')

    st.subheader("🎯 Suas Metas Prioritárias")
    st.markdown(tarefas_texto)

# --- GERADOR DE RELATÓRIO PARA DOWNLOAD ---

st.divider()
st.subheader("📄 Exportar Briefing Matinal")

hoje = datetime.date.today().strftime('%d/%m/%Y')

# Montando o texto do arquivo
relatorio_txt = f"""==================================================
📋 BRIEFING EXECUTIVO MATINAL - {hoje}
==================================================

🌤️ CLIMA LOCAL:
• {dados_clima['local'] if dados_clima else cidade_input}: {str(dados_clima['temp']) + '°C' if dados_clima else 'N/A'}

💰 COTAÇÕES DE MERCADO:
"""

if dados_financas:
    for m in moedas_selecionadas:
        relatorio_txt += f"  • {m}: R$ {dados_financas[m]:,.2f}\n"

relatorio_txt += f"""
💡 CONSELHO DIÁRIO:
  "{conselho}"

🎯 METAS E TAREFAS DO DIA:
{tarefas_texto}

==================================================
Relatório gerado automaticamente via Painel Python.
"""

# Caixa de Prévia Expandível
with st.expander("👁️ Clique aqui para ver a prévia do relatório em texto puro"):
    st.code(relatorio_txt, language="text")

# Botão Interativo de Download nativo do Streamlit
st.download_button(
    label="💾 Baixar Relatório (.txt)",
    data=relatorio_txt,
    file_name=f"Briefing_Matinal_{datetime.date.today()}.txt",
    mime="text/plain"
)