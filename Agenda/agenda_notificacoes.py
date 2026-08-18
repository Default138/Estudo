import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO DE BANCO DE DADOS (SQLite)
# ==============================================================================

def init_db():
    conn = sqlite3.connect("agenda_tarefas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lembretes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            data_hora TEXT,
            destino TEXT,
            canal TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================================================================
# 2. SISTEMA DE ENVIO DE E-MAIL (SMTP)
# ==============================================================================

def enviar_email_alerta(destinatario, titulo_tarefa):
    """Envia um e-mail de notificação usando servidor SMTP."""
    
    # --- CONFIGURAÇÕES DE ENVIO ---
    # Para usar o Gmail, gere uma 'Senha de App' nas configurações de segurança da Google
    SEU_EMAIL = "seu_email@gmail.com"  
    SUA_SENHA_APP = "abcd efgh ijkl mnop"  # Senha de aplicativo de 16 dígitos
    
    msg = MIMEMultipart()
    msg['From'] = SEU_EMAIL
    msg['To'] = destinatario
    msg['Subject'] = f"⏰ LEMBRETE DE TAREFA: {titulo_tarefa}"
    
    corpo = f"""
    Olá!
    
    Este é o seu lembrete agendado:
    📌 Tarefa: {titulo_tarefa}
    🕒 Horário: {datetime.datetime.now().strftime('%H:%M - %d/%m/%Y')}
    
    Tenha um ótimo dia!
    """
    msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(SEU_EMAIL, SUA_SENHA_APP)
        servidor.sendmail(SEU_EMAIL, destinatario, msg.as_string())
        servidor.quit()
        print(f"✅ E-mail enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

# ==============================================================================
# 3. VERIFICADOR DE HORÁRIOS (ROBÔ EM SEGUNDO PLANO)
# ==============================================================================

def checar_e_disparar_lembretes():
    """Função executada automaticamente a cada minuto pelo APScheduler."""
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect("agenda_tarefas.db")
    cursor = conn.cursor()
    
    # Busca tarefas pendentes que coincidem com o minuto atual
    cursor.execute(
        "SELECT id, titulo, destino, canal FROM lembretes WHERE data_hora = ? AND status = 'Pendente'",
        (agora,)
    )
    tarefas_para_disparar = cursor.fetchall()
    
    for tarefa_id, titulo, destino, canal in tarefas_para_disparar:
        if canal == "E-mail":
            print(f"🚀 Disparando alerta de e-mail para: {titulo}")
            enviar_email_alerta(destino, titulo)
            
        elif canal == "WhatsApp":
            # Aqui entraria a chamada da API do Twilio ou Z-API
            print(f"📲 Simulação: Enviando mensagem no WhatsApp ({destino}) - {titulo}")

        # Atualiza o status no banco de dados para não disparar duas vezes
        cursor.execute("UPDATE lembretes SET status = 'Enviado' WHERE id = ?", (tarefa_id,))
        conn.commit()
        
    conn.close()

# Inicializa o Agendador de Tarefas em segundo plano (roda a cada 30 segundos)
@st.cache_resource
def iniciar_agendador():
    scheduler = BackgroundScheduler()
    scheduler.add_job(checar_e_disparar_lembretes, 'interval', seconds=30)
    scheduler.start()
    return scheduler

iniciar_agendador()

# ==============================================================================
# 4. INTERFACE WEB (STREAMLIT)
# ==============================================================================

st.set_page_config(page_title="Agenda de Alertas Automáticos", page_icon="🔔")

st.title("🔔 Agenda Inteligente com Alertas Automáticos")
st.write("Cadastre compromissos e receba avisos automaticamente no seu e-mail ou WhatsApp.")

col_form, col_lista = st.columns([1, 1])

with col_form:
    st.subheader("➕ Novo Agendamento")
    
    titulo = st.text_input("Título do Lembrete:", placeholder="Ex: Reunião com Cliente")
    
    col_data, col_hora = st.columns(2)
    data_selecionada = col_data.date_input("Data:", min_value=datetime.date.today())
    hora_selecionada = col_hora.time_input("Horário:")
    
    canal = st.selectbox("Forma de Aviso:", ["E-mail", "WhatsApp"])
    
    if canal == "E-mail":
        destino = st.text_input("Seu E-mail para aviso:", placeholder="exemplo@gmail.com")
    else:
        destino = st.text_input("Seu Número de WhatsApp (com DDD):", placeholder="5545999999999")
        
    if st.button("💾 Agendar Lembrete"):
        if titulo.strip() and destino.strip():
            # Une a data e hora em um formato padrão (AAAA-MM-DD HH:MM)
            data_hora_formatada = f"{data_selecionada} {hora_selecionada.strftime('%H:%M')}"
            
            conn = sqlite3.connect("agenda_tarefas.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO lembretes (titulo, data_hora, destino, canal, status) VALUES (?, ?, ?, ?, 'Pendente')",
                (titulo, data_hora_formatada, destino, canal)
            )
            conn.commit()
            conn.close()
            
            st.success(f"✅ Agendado! Você receberá o aviso em {data_hora_formatada}")
            st.rerun()
        else:
            st.warning("Preencha todos os campos antes de agendar.")

with col_lista:
    st.subheader("📋 Seus Agendamentos")
    
    conn = sqlite3.connect("agenda_tarefas.db")
    import pandas as pd
    df_lembretes = pd.read_sql_query("SELECT id, titulo, data_hora, canal, status FROM lembretes ORDER BY id DESC", conn)
    conn.close()
    
    st.dataframe(df_lembretes, use_container_width=True, hide_index=True)