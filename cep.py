import requests

def buscar_endereco_por_cep(cep):
    # Remove pontos, hífens e espaços extras
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    
    # Validação rápida: CEP precisa ter 8 dígitos e ser só números
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return "❌ Formato inválido! O CEP deve conter exatamente 8 números.\n"

    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    
    try:
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()
        
        if "erro" in dados:
            return "❌ O CEP digitado não existe na base de dados.\n"
            
        resultado = (
            f"\n📍 Endereço Encontrado:\n"
            f"  • Logradouro: {dados.get('logradouro', 'Não informado')}\n"
            f"  • Bairro:     {dados.get('bairro', 'Não informado')}\n"
            f"  • Cidade:     {dados.get('localidade')}/{dados.get('uf')}\n"
            f"  • DDD:        {dados.get('ddd')}\n"
        )
        return resultado

    except requests.exceptions.RequestException:
        return "❌ Erro de conexão com o servidor. Verifique sua internet.\n"


# --- Loop Principal da Automação ---
print("=== CONSULTA DE CEP ===")

while True:
    # O script para aqui e espera você digitar algo no terminal
    entrada = input("Digite um CEP (ou 'sair' para encerrar): ")
    
    # Condição para fechar o programa
    if entrada.lower().strip() == "sair":
        print("Encerrando o sistema... Até mais!")
        break  # Interrompe o loop 'while'
        
    print("Buscando dados...")
    relatorio = buscar_endereco_por_cep(entrada)
    print(relatorio)