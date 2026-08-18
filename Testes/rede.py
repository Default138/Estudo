import socket
import subprocess
import re
import urllib.request
import json
import platform

# --- 1. FUNÇÕES DE LEITURA DA REDE REAL ---

def obter_ip_local_e_hostname():
    """Obtém o nome do seu computador e o IP da sua placa de rede local."""
    hostname = socket.gethostname()
    try:
        # Cria uma conexão temporária para descobrir o IP local ativo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except Exception:
        ip_local = "127.0.0.1 (Sem rede local)"
    return hostname, ip_local


def obter_ip_publico():
    """Consulta a internet para saber qual é o seu IP Público (IP da operadora)."""
    try:
        url = "https://api.ipify.org?format=json"
        requisicao = urllib.request.urlopen(url, timeout=3)
        dados = json.loads(requisicao.read().decode('utf-8'))
        return dados['ip']
    except Exception:
        return "Desconectado da Internet"


def obter_dados_wifi():
    """Lê o nome do Wi-Fi (SSID) e a senha salva no Windows."""
    if platform.system() != "Windows":
        return "Recurso apenas para Windows", "N/A"
    
    try:
        # Comando do Windows para mostrar a interface Wi-Fi ativa
        output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding="utf-8", errors="ignore")
        
        # Procura a linha do SSID (Evitando a linha do BSSID)
        match_ssid = re.search(r"\bSSID\s*:\s*(.+)", output)
        
        if not match_ssid:
            return "Conectado via Cabo (Ethernet) ou Wi-Fi desligado", "N/A"
        
        ssid = match_ssid.group(1).strip()
        
        # Comando para buscar a senha do SSID encontrado
        cmd_senha = f'netsh wlan show profile name="{ssid}" key=clear'
        output_senha = subprocess.check_output(cmd_senha, shell=True, encoding="utf-8", errors="ignore")
        
        # Procura a senha em português ou inglês
        match_senha = re.search(r"(?:Conteúdo da Chave|Key Content)\s*:\s*(.+)", output_senha)
        senha = match_senha.group(1).strip() if match_senha else "Senha não encontrada / Rede Aberta"
        
        return ssid, senha
    except Exception:
        return "Não foi possível ler os dados do Wi-Fi", "N/A"


def medir_ping_real(host="8.8.8.8"):
    """Dispara um PING real para o servidor do Google e mede o tempo de resposta."""
    try:
        # Define o parâmetro do comando ping (-n no Windows, -c no Linux/Mac)
        parametro = "-n" if platform.system().lower() == "windows" else "-c"
        comando = ["ping", parametro, "1", host]
        
        # Executa o comando e captura o resultado
        resposta = subprocess.check_output(comando, encoding="utf-8", errors="ignore")
        
        # Extrai o tempo em milissegundos (ex: tempo=15ms ou time=15ms)
        match = re.search(r"(?:tempo|time)[=<](\d+)ms", resposta, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return "OFFLINE"
    except Exception:
        return "OFFLINE"


def analisar_status_ping(ping):
    """Sua função original de classificação mantida!"""
    if isinstance(ping, (int, float)):
        if ping < 50:
            return f"🟢 Excelente ({ping}ms)"
        elif ping < 100:
            return f"🟡 Atenção / Lento ({ping}ms)"
        else:
            return f"🔴 Crítico ({ping}ms)"
    return "❌ Sem Comunicação (OFFLINE)"


# --- 2. EXECUÇÃO DA AUTOMAÇÃO ---

print("\n" + "="*50)
print(" 🔍 DIAGNÓSTICO EM TEMPO REAL DA SUA CONEXÃO")
print("="*50)

# Coletando informações do sistema
hostname, ip_local = obter_ip_local_e_hostname()
ip_publico = obter_ip_publico()
nome_wifi, senha_wifi = obter_dados_wifi()
ping_atual = medir_ping_real("8.8.8.8")  # Ping testado contra o DNS do Google

print(f"🖥️  Nome do Computador : {hostname}")
print(f"🏠 IP Local (Sua Rede) : {ip_local}")
print(f"🌐 IP Público (Internet): {ip_publico}")
print(f"📶 Rede Wi-Fi Atual    : {nome_wifi}")
print(f"🔑 Senha do Wi-Fi       : {senha_wifi}")
print(f"📊 Qualidade da Conexão : {analisar_status_ping(ping_atual)}")
print("="*50 + "\n")