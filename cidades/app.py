import streamlit as st
import pandas as pd

# 1. Configuração do título e layout da página no navegador
st.set_page_config(page_title="Buscador de Cidades", page_icon="🌍", layout="centered")

st.title("🌍 Buscador Interativo de Cidades Mundiais")
st.write("Digite o nome de uma cidade ou país para filtrar a lista em tempo real.")

# 2. Carrega a tabela de cidades (usando cache para o carregamento ser instantâneo)
@st.cache_data
def carregar_dados():
    return pd.read_csv("tabela_cidades_mundo.csv")

try:
    df = carregar_dados()

    # 3. Campo de texto para filtro instantâneo
    termo_busca = st.text_input(
        "🔍 Digite para pesquisar:",
        placeholder="Exemplo: New York, Tokyo, Brazil..."
    )

    # 4. Lógica de Filtragem (vai eliminando o que não corresponde ao texto digitado)
    if termo_busca:
        # Filtra a coluna 'Cidade_Pais' ignorando maiúsculas e minúsculas
        dados_filtrados = df[df["Cidade_Pais"].str.contains(termo_busca, case=False, na=False)]
    else:
        # Se nada for digitado, mostra as primeiras cidades como padrão
        dados_filtrados = df

    # Exibe quantas cidades correspondem à busca atual
    st.caption(f"📊 {len(dados_filtrados):,} cidades encontradas.")

    # 5. Menu Seletor (Dropdown) que contém APENAS as cidades filtradas
    if not dados_filtrados.empty:
        cidade_selecionada = st.selectbox(
            "Selecione a cidade desejada na lista filtrada:",
            options=dados_filtrados["Cidade_Pais"].tolist()
        )

        # 6. Exibe os detalhes da cidade escolhida
        if cidade_selecionada:
            # Busca a linha correspondente no banco de dados
            info = df[df["Cidade_Pais"] == cidade_selecionada].iloc[0]

            st.divider()
            st.success(f"### 📍 Cidade Selecionada: {cidade_selecionada}")

            # Organiza as informações complementares em cartões lado a lado
            col1, col2, col3 = st.columns(3)
            col1.metric("Cidade", info["City"])
            col2.metric("País", info["Country"])
            col3.metric("Continente", str(info["Continent"]))

    else:
        st.warning("⚠️ Nenhuma cidade encontrada com esse nome.")

except FileNotFoundError:
    st.error("❌ O arquivo 'tabela_cidades_mundo.csv' não foi encontrado! Execute o script de geração do arquivo primeiro.")