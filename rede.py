# 1. Nossa "Base de Dados": Uma lista contendo dicionários
servidores = [
    {"nome": "Servidor Web", "ip": "192.168.1.10", "ping_ms": 15},
    {"nome": "Banco de Dados", "ip": "192.168.1.20", "ping_ms": 120},       # Latência alta
    {"nome": "Servidor de Arquivos", "ip": "192.168.1.30", "ping_ms": "OFFLINE"}, # Dado problemático!
    {"nome": "Servidor de Backup", "ip": "192.168.1.40", "ping_ms": 5}
]

# 2. Função que analisa um servidor individual
def analisar_servidor(servidor):
    try:
        # Tenta converter o valor do ping para número decimal/float
        ping = float(servidor["ping_ms"])
        
        if ping < 50:
            status = "🟢 Excelente"
        elif ping < 100:
            status = "🟡 Atenção (Lento)"
        else:
            status = "🔴 Crítico (Muito Lento)"
            
        return f"[{status}] {servidor['nome']} ({servidor['ip']}) - {ping}ms"
        
    except ValueError:
        # Se a conversão falhar (ex: 'OFFLINE' não é número), o código vem para cá
        return f"[❌ FALHA] {servidor['nome']} ({servidor['ip']}) - Sem comunicação!"

# 3. Execução da Automação
print("=== INICIANDO VARREDURA DE SISTEMAS ===")

for s in servidores:
    relatorio = analisar_servidor(s)
    print(relatorio)

print("=== VARREDURA FINALIZADA ===")