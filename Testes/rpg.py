import sys
import time


def digitar(texto, velocidade=0.02):
    """Exibe o texto letra por letra para dar efeito de narrativa."""
    for letra in texto:
        sys.stdout.write(letra)
        sys.stdout.flush()
        time.sleep(velocidade)
    print()


def mostrar_inventario(inventario):
    """Exibe os itens atuais do jogador."""
    if inventario:
        print(f"\n🎒 [Inventário]: {', '.join(inventario)}")
    else:
        print("\n🎒 [Inventário]: Vazio")


def jogo():
    inventario = []

    digitar("==========================================")
    digitar("        A CRIPTA DE ELDORIA              ")
    digitar("==========================================")
    digitar(
        "Você é um caçador de relíquias em busca do Lendário Amuleto do Sol."
    )
    digitar("Sua jornada o trouxe até as ruínas esquecidas no topo da montanha.\n")

    # --- CENA 1: A ENTRADA ---
    while True:
        mostrar_inventario(inventario)
        digitar("\n--- ENTRADA DA CRIPTA ---")
        digitar(
            "Você está diante de uma pesada porta de pedra semiaberta. O interior é uma escuridão breu."
        )
        digitar("Ao redor da entrada, há uma vegetação densa e escombros.")
        print("\n1. Entrar diretamente na cripta.")
        print("2. Investigar os arbustos e escombros ao redor.")

        escolha = input("\n> O que você faz? (1 ou 2): ").strip()

        if escolha == "1":
            break
        elif escolha == "2":
            if "Tocha" not in inventario:
                digitar(
                    "\n[!] Você vasculha as plantas e encontra uma **Tocha apagada** e uma **Chave de Ferro**!"
                )
                digitar(
                    "Você decide acender a tocha com seu isqueiro antes de prosseguir."
                )
                inventario.append("Tocha Acesa")
                inventario.append("Chave de Ferro")
            else:
                digitar(
                    "\nVocê já vasculhou este local e não sobrou nada de útil."
                )
        else:
            digitar("\n[Opção inválida! Escolha 1 ou 2.]")

    # --- CENA 2: O SALÃO PRINCIPAL ---
    while True:
        mostrar_inventario(inventario)
        digitar("\n--- SALÃO PRINCIPAL ---")

        # Checagem de requisito de item (Tocha)
        if "Tocha Acesa" not in inventario:
            digitar(
                "Você dá alguns passos na escuridão cega do salão..."
            )
            digitar(
                "Sem enxergar onde pisa, você aciona um piso falso e cai em um fosso com estacas!"
            )
            digitar("\n☠️  *** FIM DE JOGO - VOCÊ MORREU NO ESCURO ***")
            digitar(
                "Dica: Talvez fosse prudente investigar os arredores antes de entrar em um local escuro."
            )
            return

        digitar(
            "Com a sua **Tocha Acesa**, você ilumina o salão de pedra. O ar é úmido e frio."
        )
        digitar(
            "No centro da sala, há um **Baú Trancado**. Ao fundo, uma imponente **Porta Mística**."
        )
        print("\n1. Examinar o Baú Trancado.")
        print("2. Ir até a Porta Mística.")

        escolha = input("\n> O que você faz? (1 ou 2): ").strip()

        if escolha == "1":
            digitar("\nVocê se aproxima do baú reforçado com tiras de metal.")
            # Opções dinâmicas baseadas no inventário
            if "Chave de Ferro" in inventario:
                digitar(
                    "1. Usar a **Chave de Ferro** no cadeado do baú."
                )
                digitar("2. Voltar.")
                sub_esc = input("\n> Escolha (1 ou 2): ").strip()

                if sub_esc == "1":
                    digitar(
                        "\n[!] *CLIQUE!* A chave gira e o baú se abre!"
                    )
                    digitar(
                        "Dentro dele, reluz o dourado **Amuleto do Sol**!"
                    )
                    inventario.append("Amuleto do Sol")
                    inventario.remove("Chave de Ferro")  # Consome a chave
            elif "Amuleto do Sol" in inventario:
                digitar("O baú já está aberto e vazio.")
            else:
                digitar(
                    "O baú possui um cadeado antigo. Você precisa de uma chave para abri-lo."
                )

        elif escolha == "2":
            digitar(
                "\nVocê caminha até a grande Porta Mística. Ela possui uma cavidade circular no centro."
            )

            # Opções dinâmicas baseadas no item lendário
            if "Amuleto do Sol" in inventario:
                print("1. Encaixar o **Amuleto do Sol** na cavidade.")
                print("2. Voltar para o centro da sala.")
                sub_esc = input("\n> Escolha (1 ou 2): ").strip()

                if sub_esc == "1":
                    digitar(
                        "\n[!] O Amuleto se encaixa perfeitamente! Uma luz dourada vibra pelas paredes."
                    )
                    digitar(
                        "Os portões se abrem lentamente, revelando a lendária câmara de tesouros de Eldoria!"
                    )
                    digitar(
                        "\n🏆 *** FIM DE JOGO - VITÓRIA MAGNÍFICA! ***"
                    )
                    return
            else:
                print("1. Tentar forçar a porta com as mãos.")
                print("2. Voltar para o centro da sala.")
                sub_esc = input("\n> Escolha (1 ou 2): ").strip()

                if sub_esc == "1":
                    digitar(
                        "\nA porta não se move nem um milímetro. Há um entalhe no centro que parece exigir um objeto específico."
                    )
        else:
            digitar("\n[Opção inválida! Escolha 1 ou 2.]")


if __name__ == "__main__":
    jogo()