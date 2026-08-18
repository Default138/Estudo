import sqlite3
import datetime
import requests
import os
import platform
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. ARQUITETURA DE BANCO DE DADOS (SQLite - Persistência de Dados)
# ==============================================================================

class DatabaseManager:
    """Classe responsável por gerenciar a conexão e operações no Banco de Dados SQLite."""
    def __init__(self, db_path="enterprise_system.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Tabela de Logs de Auditoria do Sistema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    modulo TEXT,
                    acao TEXT,
                    status TEXT
                )
            """)
            # Tabela de Tarefas e Metas da Central
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    prioridade TEXT,
                    status TEXT,
                    data_criacao TEXT
                )
            """)
            conn.commit()

    def registrar_log(self, modulo, acao, status="INFO"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO audit_logs (timestamp, modulo, acao, status) VALUES (?, ?, ?, ?)",
                (now, modulo, acao, status)
            )
            conn.commit()

    def carregar_logs(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50", conn)

    def adicionar_tarefa(self, titulo, prioridade):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO tarefas (titulo, prioridade, status, data_criacao) VALUES (?, ?, 'Pendente', ?)",
                (titulo, prioridade, now)
            )
            conn.commit()
            self.registrar_log("Tarefas", f"Nova tarefa criada: {titulo}")

    def carregar_tarefas(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM tarefas ORDER BY id DESC", conn)

# ==============================================================================
# 2. MOTOR DE INTELIGÊNCIA FINANCEIRA & APIS
# ==============================================================================

class MarketIntelligence:
    """Classe responsável pelo consumo de APIs e geração de gráficos financeiros."""
    
    @staticmethod
    @st.cache_data(ttl=300)
    def buscar_cotacoes_completas():
        url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,CAD-BRL"
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
            dados = res.json()
            
            # Reformatação dos dados em DataFrame Pandas
            lista = []
            for chave, info in dados.items():
                lista.append({
                    "Par": info["code"] + "/" + info["codein"],
                    "Nome": info["name"].split("/")[0],
                    "Preço (R$)": float(info["bid"]),
                    "Variação (%)": float(info["pctChange"]),
                    "Máxima": float(info["high"]),
                    "Mínima": float(info["low"])
                })
            return pd.DataFrame(lista)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def gerar_grafico_comparativo(df_cotacoes):
        if df_cotacoes.empty:
            return None
        fig = px.bar(
            df_cotacoes, 
            x="Nome", 
            y="Preço (R$)", 
            color="Variação (%)",
            title="Cotação de Ativos Estrangeiros x Real",
            text_auto=".2f",
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(template="plotly_dark")
        return fig

# ==============================================================================
# 3. ENGINE DE DIAGNÓSTICO DE INFRAESTRUTURA
# ==============================================================================

class InfrastructureEngine:
    """Módulo de monitoramento de servidor e conectividade de rede."""
    
    @staticmethod
    def testar_latencia(host):
        parametro = "-n" if platform.system().lower() == "windows" else "-c"
        try:
            output = subprocess.check_output(["ping", parametro, "1", host], encoding="utf-8", errors="ignore")
            if "tempo=" in output.lower() or "time=" in output.lower():
                import re
                match = re.search(r"(?:tempo|time)[=<](\d+)ms", output, re.IGNORECASE)
                return float(match.group(1)) if match else 10.0
            return None
        except Exception:
            return None

    @classmethod
    def executar_varredura_matriz(cls):
        alvos = {
            "Google DNS": "8.8.8.8",
            "Cloudflare": "1.1.1.1",
            "AWS US-East": "dynamodb.us-east-1.amazonaws.com",
            "Servidor ViaCEP": "viacep.com.br"
        }
        resultados = []
        for nome, host in alvos.items():
            ping = cls.testar_latencia(host)
            resultados.append({
                "Serviço": nome,
                "Endereço Host": host,
                "Ping (ms)": ping if ping is not None else 999,
                "Status": "🟢 Operacional" if ping and ping < 100 else ("🟡 Instável" if ping else "🔴 Offline")
            })
        return pd.DataFrame(resultados)

# ==============================================================================
# 4. INTERFACE GRÁFICA & CONTROLE DE FLUXO (STREAMLIT)
# ==============================================================================

def main():
    st.set_page_config(page_title="Enterprise Command Center", page_icon="🛡️", layout="wide")
    
    # Inicialização do Banco de Dados
    db = DatabaseManager()
    db.registrar_log("Sistema", "Sessão iniciada na Central de Comando")

    # BARRA LATERAL - NAVEGAÇÃO
    st.sidebar.title("🛡️ Central de Comando")
    st.sidebar.markdown("---")
    
    opcao_menu = st.sidebar.radio(
        "Módulos Operacionais:",
        [
            "📊 Mercado & Inteligência Financeira",
            "⚙️ Engine de ETL & Análise de Dados",
            "🌐 Monitor de Infraestrutura de Rede",
            "🗄️ Gestão de Banco de Dados & Logs"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🖥️ OS: {platform.system()} {platform.release()}")
    st.sidebar.caption(f"🕒 Servidor: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # --------------------------------------------------------------------------
    # MÓDULO 1: MERCADO & INTELIGÊNCIA FINANCEIRA
    # --------------------------------------------------------------------------
    if opcao_menu == "📊 Mercado & Inteligência Financeira":
        st.title("📊 Painel de Inteligência de Mercado")
        st.write("Análise em tempo real de ativos globais e métricas técnicas.")
        
        with st.spinner("Atualizando feed da API Financeira..."):
            df_cotacoes = MarketIntelligence.buscar_cotacoes_completas()

        if not df_cotacoes.empty:
            # Exibição de KPIs no topo
            cols = st.columns(len(df_cotacoes))
            for idx, row in df_cotacoes.iterrows():
                cols[idx].metric(
                    label=row["Par"], 
                    value=f"R$ {row['Preço (R$)']:.2f}", 
                    delta=f"{row['Variação (%)']}%"
                )
            
            st.divider()
            
            col_graf, col_tb = st.columns([1.5, 1])
            with col_graf:
                st.subheader("Visualização Gráfica")
                fig = MarketIntelligence.gerar_grafico_comparativo(df_cotacoes)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_tb:
                st.subheader("Dados Detalhados")
                st.dataframe(df_cotacoes, hide_index=True, use_container_width=True)
        else:
            st.error("Falha ao comunicar com os servidores de cotação.")

    # --------------------------------------------------------------------------
    # MÓDULO 2: ENGINE DE ETL & ANÁLISE DE DADOS (Estatística / Outliers)
    # --------------------------------------------------------------------------
    elif opcao_menu == "⚙️ Engine de ETL & Análise de Dados":
        st.title("⚙️ Engine de Processamento de Dados (ETL)")
        st.write("Faça upload de um arquivo CSV/Excel para limpeza, detecção de anomalias e geração de relatórios.")

        arquivo_enviado = st.file_uploader("Selecione um arquivo de dados:", type=["csv", "xlsx"])

        if arquivo_enviado is not None:
            try:
                if arquivo_enviado.name.endswith('.csv'):
                    df_user = pd.read_csv(arquivo_enviado)
                else:
                    df_user = pd.read_excel(arquivo_enviado)

                db.registrar_log("ETL", f"Arquivo processado: {arquivo_enviado.name}")

                st.success(f"Arquivo carregado com sucesso! ({len(df_user)} linhas, {len(df_user.columns)} colunas)")
                
                tab1, tab2, tab3 = st.tabs(["📋 Visão Geral", "📊 Análise Exploratória", "⚠️ Anomalias / Outliers"])

                with tab1:
                    st.dataframe(df_user.head(100), use_container_width=True)

                with tab2:
                    st.subheader("Resumo Estatístico das Colunas Numéricas")
                    colunas_numericas = df_user.select_dtypes(include=['float64', 'int64']).columns.tolist()
                    if colunas_numericas:
                        st.dataframe(df_user[colunas_numericas].describe(), use_container_width=True)
                        
                        eixo_x = st.selectbox("Eixo X:", options=df_user.columns)
                        eixo_y = st.selectbox("Eixo Y (Numérico):", options=colunas_numericas)
                        
                        fig_scatter = px.scatter(df_user, x=eixo_x, y=eixo_y, color_discrete_sequence=["#00E676"])
                        fig_scatter.update_layout(template="plotly_dark")
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.warning("Nenhuma coluna numérica encontrada para análise.")

                with tab3:
                    st.subheader("Detecção de Outliers via Algoritmo de Amplitude Interquartil (IQR)")
                    if colunas_numericas:
                        col_alvo = st.selectbox("Selecione a coluna para auditagem de anomalias:", options=colunas_numericas)
                        
                        # Cálculo matemático do IQR
                        Q1 = df_user[col_alvo].quantile(0.25)
                        Q3 = df_user[col_alvo].quantile(0.75)
                        IQR = Q3 - Q1
                        limite_inferior = Q1 - 1.5 * IQR
                        limite_superior = Q3 + 1.5 * IQR

                        outliers = df_user[(df_user[col_alvo] < limite_inferior) | (df_user[col_alvo] > limite_superior)]
                        
                        st.write(f"**Limites de Normalidade:** Entre `{limite_inferior:.2f}` e `{limite_superior:.2f}`")
                        st.write(f"**Anomalias Detectadas:** `{len(outliers)}` registro(s)")
                        
                        if not outliers.empty:
                            st.dataframe(outliers, use_container_width=True)
                        
                        fig_box = px.box(df_user, y=col_alvo, points="outliers", title=f"Boxplot de Anomalias - {col_alvo}")
                        fig_box.update_layout(template="plotly_dark")
                        st.plotly_chart(fig_box, use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")
        else:
            st.info("👆 Faça o upload de um arquivo para iniciar a pipeline de dados.")

    # --------------------------------------------------------------------------
    # MÓDULO 3: MONITOR DE INFRAESTRUTURA DE REDE
    # --------------------------------------------------------------------------
    elif opcao_menu == "🌐 Monitor de Infraestrutura de Rede":
        st.title("🌐 Diagnóstico & Matriz de Latência de Rede")
        st.write("Varredura em tempo real dos nós de comunicação e servidores críticos.")

        if st.button("🚀 Executar Varredura de Rede Agora"):
            with st.spinner("Disparando pacotes ICMP para os servidores mundiais..."):
                df_rede = InfrastructureEngine.executar_varredura_matriz()
                db.registrar_log("Infraestrutura", "Varredura de rede realizada")

            st.dataframe(df_rede, use_container_width=True, hide_index=True)

            fig_ping = px.bar(
                df_rede, 
                x="Serviço", 
                y="Ping (ms)", 
                color="Status",
                title="Matriz de Resposta de Servidores (Milissegundos)",
                text_auto=True
            )
            fig_ping.update_layout(template="plotly_dark")
            st.plotly_chart(fig_ping, use_container_width=True)

    # --------------------------------------------------------------------------
    # MÓDULO 4: GESTÃO DE BANCO DE DADOS & LOGS (CRUD & Auditaria)
    # --------------------------------------------------------------------------
    elif opcao_menu == "🗄️ Gestão de Banco de Dados & Logs":
        st.title("🗄️ Gerenciador do Banco de Dados SQLite")
        st.write("Interface interna para auditoria de logs e gestão de tarefas.")

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📌 Cadastro de Tarefas (CRUD)")
            nova_tarefa = st.text_input("Título da Tarefa:")
            prio = st.selectbox("Prioridade:", ["Baixa", "Média", "Alta", "CRÍTICA"])
            
            if st.button("Cadastrar Tarefa no SQLite"):
                if nova_tarefa.strip():
                    db.adicionar_tarefa(nova_tarefa, prio)
                    st.success("Tarefa gravada no Banco de Dados com sucesso!")
                    st.rerun()

            st.subheader("Tarefas Registradas")
            df_tarefas = db.carregar_tarefas()
            st.dataframe(df_tarefas, use_container_width=True, hide_index=True)

        with col_right:
            st.subheader("📜 Logs de Auditoria do Sistema")
            df_logs = db.carregar_logs()
            st.dataframe(df_logs, use_container_width=True, hide_index=True)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    main()