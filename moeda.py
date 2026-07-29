import datetime  # Módulo nativo para trabalhar com datas e horários
import requests  # Módulo para realizar requisições HTTP à API

# --- CONFIGURAÇÕES FIXAS ---
# Criamos um dicionário contendo as moedas disponíveis e seus códigos na API
MOEDAS_DISPONIVEIS = {
    "1": ("USD-BRL", "Dólar Americano", "USDBRL"),
    "2": ("EUR-BRL", "Euro", "EURBRL"),
    "3": ("BTC-BRL", "Bitcoin", "BTCBRL"),
    "4": ("GBP-BRL", "Libra Esterlina", "GBPBRL")
}

def buscar_cotacao(par_moeda, chave_json):
    """
    Busca a cotação em tempo real na API.
    Retorna o dicionário de dados da moeda ou None se algo der errado.
    """
    url = f"https://economia.awesomeapi.com.br/last/{par_moeda}"
    
    try:
        # Envia a requisição GET com um limite de tempo (timeout) de 5 segundos
        resposta = requests.get(url, timeout=5)
        
        # Dispara erro automaticamente se o status HTTP for 4xx ou 5xx
        resposta.raise_for_status()
        
        # Transforma a resposta da API (JSON) em um dicionário Python
        dados = resposta.json()
        
        # A API retorna um objeto onde a chave principal é a junção do par (ex: 'USDBRL')
        return dados[chave_json]
        
    except requests.exceptions.RequestException as erro:
        print(f"\n❌ [ERRO DE CONEXÃO]: Não foi possível consultar a API. Detalhes: {erro}")
        return None


def salvar_em_log(texto_relatorio):
    """
    Salva uma linha de texto no arquivo 'historico_conversoes.txt'.
    Se o arquivo não existir, o Python cria automaticamente.
    """
    try:
        # O modo 'a' (append) adiciona conteúdo ao FINAL do arquivo sem apagar o que já existe
        with open("historico_conversoes.txt", "a", encoding="utf-8") as arquivo:
            # Captura a data e hora atual formatada (Ex: 29/07/2026 14:30:00)
            data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Grava a mensagem no arquivo e pula uma linha (\n)
            arquivo.write(f"[{data_hora}] {texto_relatorio}\n")
            
        print("💾 [AUTOMAÇÃO]: Registro salvo com sucesso em 'historico_conversoes.txt'!")
        
    except IOError as erro:
        print(f"❌ [ERRO DE ARQUIVO]: Não foi possível salvar o registro. {erro}")


def executar_painel():
    """Função principal que controla a navegação e o menu do sistema."""
    
    while True:
        print("\n" + "="*45)
        print("   🤖 AUTOMAÇÃO: PAINEL FINANCEIRO DE COTAÇÕES")
        print("="*45)
        print("1. Consultar Cotação de Moeda")
        print("2. Converter Reais (R$) para Moeda Estrangeira")
        print("3. Sair")
        print("="*45)
        
        opcao = input("Escolha uma opção (1, 2 ou 3): ").strip()
        
        # Se a opção for válida para operação com moedas (1 ou 2)
        if opcao in ["1", "2"]:
            print("\nMoedas Disponíveis:")
            for chave, dados_moeda in MOEDAS_DISPONIVEIS.items():
                print(f"  [{chave}] {dados_moeda[1]}")
                
            escolha_moeda = input("Selecione a moeda desejada: ").strip()
            
            # Valida se a opção de moeda existe na nossa lista
            if escolha_moeda not in MOEDAS_DISPONIVEIS:
                print("⚠️ Opção de moeda inválida! Retornando ao menu principal...")
                continue  # 'continue' faz o loop 'while' voltar para o início imediatamente
                
            # Desempacota os dados da moeda escolhida
            par_codigo, nome_moeda, chave_json = MOEDAS_DISPONIVEIS[escolha_moeda]
            
            print(f"\n⌛ Acessando API para buscar dados do {nome_moeda}...")
            dados_cotacao = buscar_cotacao(par_codigo, chave_json)
            
            # Se a busca falhou (ex: sem internet), voltamos ao menu
            if not dados_cotacao:
                continue
                
            # Extrai o preço atual de compra (campo 'bid' da API) e converte para número
            preco_atual = float(dados_cotacao["bid"])
            variacao = dados_cotacao["pctChange"]
            
            # --- FLUXO 1: Apenas Consulta ---
            if opcao == "1":
                mensagem = f"CONSULTA: {nome_moeda} está valendo R$ {preco_atual:.2f} (Variação no dia: {variacao}%)"
                print(f"\n📊 {mensagem}")
                salvar_em_log(mensagem)
                
            # --- FLUXO 2: Conversão de Valores ---
            elif opcao == "2":
                try:
                    # Solicita o valor ao usuário e tenta converter para float (número decimal)
                    valor_brl = float(input(f"\nDigite o valor em Reais (R$) para converter em {nome_moeda}: "))
                    
                    # Cálculo da conversão
                    valor_convertido = valor_brl / preco_atual
                    
                    resumo = (
                        f"CONVERSÃO: R$ {valor_brl:.2f} -> "
                        f"{valor_convertido:.4f} em {nome_moeda} (Cotação: R$ {preco_atual:.2f})"
                    )
                    
                    print(f"\n💸 {resumo}")
                    salvar_em_log(resumo)
                    
                except ValueError:
                    # Trata o erro se o usuário digitar letras ou símbolos inválidos no valor
                    print("❌ [ERRO]: Você precisa digitar apenas números válidos (Exemplo: 150.50)!")
                    
        elif opcao == "3":
            print("\n👋 Encerrando o sistema de automação. Até logo!")
            break  # Quebra o laço 'while' e encerra o programa
            
        else:
            print("⚠️ Opção inválida! Por favor, escolha 1, 2 ou 3.")

# --- PONTO DE ENTRADA DO SCRIPT ---
# Garante que o script só roda se for executado diretamente pelo usuário
if __name__ == "__main__":
    executar_painel()