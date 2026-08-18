import streamlit as st
import pandas as pd
import yfinance as yf

# 1. Configuração da página e layout
st.set_page_config(page_title="Painel Integrado de Investimentos", page_icon="💎", layout="wide")

st.title("💎 Painel de Controle de Investimentos & B3")
st.write("Sua central unificada para consultas na B3, simulação de aportes e acompanhamento de carteira.")

# ==============================================================================
# FUNÇÃO COMPARTILHADA: BUSCA DE DADOS EM TEMPO REAL NA B3 (YFINANCE)
# ==============================================================================

@st.cache_data(ttl=1800)  # Guarda em cache por 30 minutos para deixar a navegação rápida
def buscar_dados_ativo(ticker):
    """
    Busca cotação e proventos dos últimos 12 meses de um ativo da B3.
    """
    if not ticker:
        return None
        
    ticker_limpo = ticker.strip().upper()
    ticker_sa = ticker_limpo if ticker_limpo.endswith(".SA") else f"{ticker_limpo}.SA"
    
    try:
        ativo = yf.Ticker(ticker_sa)
        
        # Histórico recente para pegar o preço de fechamento
        hist = ativo.history(period="1mo")
        if hist.empty:
            return None
            
        preco_atual = float(hist["Close"].iloc[-1])
        
        # Histórico de dividendos
        divs = ativo.dividends
        if not divs.empty:
            hoje = pd.Timestamp.now(tz=divs.index.tz)
            um_ano_atras = hoje - pd.Timedelta(days=365)
            divs_12m = float(divs[divs.index >= um_ano_atras].sum())
            dy_anual = (divs_12m / preco_atual) * 100
            dy_mensal = dy_anual / 12
        else:
            divs_12m = 0.0
            dy_anual = 0.0
            dy_mensal = 0.0

        return {
            "ticker": ticker_limpo,
            "preco": preco_atual,
            "divs_12m": divs_12m,
            "dy_anual": dy_anual,
            "dy_mensal": dy_mensal,
            "historico": hist
        }
    except Exception:
        return None


# ==============================================================================
# ESTRUTURA DE ABAS DA APLICAÇÃO
# ==============================================================================

aba_busca, aba_simulador, aba_carteira = st.tabs([
    "🔍 Consultar Ativos B3", 
    "🚀 Simulador de Aportes", 
    "📊 Minha Carteira"
])

# ------------------------------------------------------------------------------
# ABA 1: CONSULTA DE ATIVOS B3
# ------------------------------------------------------------------------------
with aba_busca:
    st.header("🔍 Consulta em Tempo Real de Ativos (FIIs, Ações, BDRs)")
    
    col_search1, col_search2 = st.columns([3, 1])
    ticker_busca = col_search1.text_input("Digite o código do ativo:", value="MXRF11", placeholder="Ex: HGLG11, PETR4, VALE3, ITUB4").upper()
    
    if ticker_busca:
        dados_ativo = buscar_dados_ativo(ticker_busca)
        
        if dados_ativo:
            st.success(f"✅ Dados de **{dados_ativo['ticker']}** obtidos da B3!")
            
            # Exibição de métricas visuais
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Preço Atual", f"R$ {dados_ativo['preco']:.2f}")
            m2.metric("Proventos (Últimos 12m)", f"R$ {dados_ativo['divs_12m']:.2f}")
            m3.metric("Dividend Yield (Ano)", f"{dados_ativo['dy_anual']:.2f}%")
            m4.metric("DY Mensal Médio", f"{dados_ativo['dy_mensal']:.2f}%")
            
            st.divider()
            st.subheader(f"📈 Gráfico do Preço Recente ({dados_ativo['ticker']})")
            st.line_chart(dados_ativo["historico"]["Close"])
            
        else:
            st.error(f"❌ Não foi possível carregar o ativo '{ticker_busca}'. Verifique se o código está correto.")

# ------------------------------------------------------------------------------
# ABA 2: SIMULADOR DE APORTES
# ------------------------------------------------------------------------------
with aba_simulador:
    st.header("🚀 Comparador de Rendimento de Novo Aporte")
    st.write("Veja quanto seu dinheiro rende no Tesouro Selic comparado a ativos da B3.")
    
    c_ap1, c_ap2, c_ap3 = st.columns(3)
    valor_aporte = c_ap1.number_input("Valor para Aportar (R$):", min_value=100.0, value=2000.0, step=100.0)
    taxa_selic_aa = c_ap2.number_input("Taxa Selic Anual (%):", value=10.5, step=0.25)
    tempo_ir = c_ap3.selectbox("Prazo de Regra IR (Tesouro):", [
        "Até 180 dias (22.5% IR)", 
        "181 a 360 dias (20.0% IR)", 
        "361 a 720 dias (17.5% IR)", 
        "Acima de 720 dias (15.0% IR)"
    ], index=3)

    tabela_ir = {
        "Até 180 dias (22.5% IR)": 0.225, 
        "181 a 360 dias (20.0% IR)": 0.20, 
        "361 a 720 dias (17.5% IR)": 0.175, 
        "Acima de 720 dias (15.0% IR)": 0.15
    }
    pct_ir = tabela_ir[tempo_ir]

    st.subheader("Selecione 2 Ativos da B3 para a Comparação:")
    c_f1, c_f2 = st.columns(2)
    fii1_code = c_f1.text_input("Código do Ativo 1:", value="MXRF11").upper()
    fii2_code = c_f2.text_input("Código do Ativo 2:", value="HGLG11").upper()

    # Cálculos do Tesouro
    selic_mensal_bruta = ((1 + (taxa_selic_aa / 100)) ** (1/12)) - 1
    rendimento_selic_liquido = (valor_aporte * selic_mensal_bruta) * (1 - pct_ir)

    # Busca ativos da B3
    d1 = buscar_dados_ativo(fii1_code)
    d2 = buscar_dados_ativo(fii2_code)

    m1_rend = valor_aporte * (d1["dy_mensal"] / 100) if d1 else 0.0
    m2_rend = valor_aporte * (d2["dy_mensal"] / 100) if d2 else 0.0

    st.divider()

    # Exibição das métricas de comparação
    col_comp1, col_comp2, col_comp3 = st.columns(3)
    col_comp1.metric("Tesouro Selic (Líquido)", f"R$ {rendimento_selic_liquido:.2f} / mês")
    col_comp2.metric(f"{fii1_code} (DY Histórico)", f"R$ {m1_rend:.2f} / mês" if d1 else "N/A")
    col_comp3.metric(f"{fii2_code} (DY Histórico)", f"R$ {m2_rend:.2f} / mês" if d2 else "N/A")

    # Tabela Resumo
    dados_tabela = [
        {"Ativo": "Tesouro Selic", "Categoria": "Renda Fixa", "Preço Atual": "N/A", "Rendimento Mensal (R$)": rendimento_selic_liquido, "Imposto": f"{pct_ir*100}% IR"},
        {"Ativo": d1['ticker'] if d1 else fii1_code, "Categoria": "B3 / Variável", "Preço Atual": f"R$ {d1['preco']:.2f}" if d1 else "Erro", "Rendimento Mensal (R$)": m1_rend, "Imposto": "Isento"},
        {"Ativo": d2['ticker'] if d2 else fii2_code, "Categoria": "B3 / Variável", "Preço Atual": f"R$ {d2['preco']:.2f}" if d2 else "Erro", "Rendimento Mensal (R$)": m2_rend, "Imposto": "Isento"}
    ]

    st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# ABA 3: MINHA CARTEIRA DE INVESTIMENTOS (VERSÃO ATUALIZADA)
# ------------------------------------------------------------------------------
with aba_carteira:
    st.header("📊 Acompanhamento de Carteira & Renda Passiva")
    st.info("💡 **Dica:** Após alterar qualquer valor na tabela, pressione **Enter** ou clique fora da célula para atualizar os cálculos!")

    # Tabela padrão para edição
    dados_carteira_padrao = pd.DataFrame([
        {"Ativo": "Tesouro Selic", "Tipo": "Renda Fixa", "Valor Investido (R$)": 250000.0, "Rendimento Mensal Est. (%)": 0.72},
        {"Ativo": "MXRF11", "Tipo": "FII", "Valor Investido (R$)": 250000.0, "Rendimento Mensal Est. (%)": 0.95}
    ])

    st.subheader("📝 1. Edite seus Ativos e Valores Abaixo:")
    df_carteira = st.data_editor(
        dados_carteira_padrao, 
        num_rows="dynamic", 
        use_container_width=True
    )

    # --- CÁLCULOS AUTOMÁTICOS ---
    # Garantindo que os dados sejam tratados como números antes da conta
    df_carteira["Valor Investido (R$)"] = pd.to_numeric(df_carteira["Valor Investido (R$)"], errors="coerce").fillna(0)
    df_carteira["Rendimento Mensal Est. (%)"] = pd.to_numeric(df_carteira["Rendimento Mensal Est. (%)"], errors="coerce").fillna(0)

    # Cálculo do rendimento mensal em Reais para cada linha
    df_carteira["Renda Passiva Mensal (R$)"] = df_carteira["Valor Investido (R$)"] * (df_carteira["Rendimento Mensal Est. (%)"] / 100)
    
    # Totais gerais
    total_patrimonio = df_carteira["Valor Investido (R$)"].sum()
    total_renda_mensal = df_carteira["Renda Passiva Mensal (R$)"].sum()
    total_renda_anual = total_renda_mensal * 12

    st.divider()

    # --- EXIBIÇÃO DOS RESULTADOS ---
    st.subheader("💰 2. Resumo Consolidado do Seu Patrimônio:")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Patrimônio Total", f"R$ {total_patrimonio:,.2f}")
    kpi2.metric("Renda Passiva Mensal", f"R$ {total_renda_mensal:,.2f} / mês")
    kpi3.metric("Renda Passiva Anual (Est.)", f"R$ {total_renda_anual:,.2f} / ano")

    st.subheader("📋 3. Rendimento Calculado por Ativo:")
    # Prepara uma versão formatada da tabela para exibir os resultados linha a linha
    df_resultado = df_carteira.copy()
    df_resultado["Valor Investido (R$)"] = df_resultado["Valor Investido (R$)"].apply(lambda x: f"R$ {x:,.2f}")
    df_resultado["Rendimento Mensal Est. (%)"] = df_resultado["Rendimento Mensal Est. (%)"].apply(lambda x: f"{x:.2f}%")
    df_resultado["Renda Passiva Mensal (R$)"] = df_resultado["Renda Passiva Mensal (R$)"].apply(lambda x: f"R$ {x:,.2f} / mês")
    
    st.dataframe(df_resultado, use_container_width=True, hide_index=True)