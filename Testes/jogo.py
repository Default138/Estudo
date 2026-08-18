import curses
import random
import time

def jogo(stdscr):
    # Configurações do Curses para alta performance
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(30)  # ~33 FPS para fluidez total

    # Esconde o cursor de digitação
    try:
        curses.noecho()
    except curses.error:
        pass

    # Dimensões da tela do terminal
    max_h, max_w = stdscr.getmaxyx()

    # Como emojis ocupam 2 colunas de largura, mapeamos uma grade virtual
    grid_w = (max_w - 4) // 2
    grid_h = max_h - 3

    # Posições iniciais na grade (Capivara)
    py, px = grid_h // 2, grid_w // 2

    score = 0
    vidas = 3

    # Posição inicial do Café
    cafe_y = random.randint(1, grid_h - 1)
    cafe_x = random.randint(1, grid_w - 1)

    # Definição dos Emojis
    EMOJI_CAPIVARA = "🦫"
    EMOJI_JACARE   = "🐊"
    EMOJI_CAFE     = "☕"

    # Criando os Jacarés com movimento contínuo
    jacares = []
    for _ in range(3):
        jy = random.randint(1, grid_h - 1)
        jx = random.randint(1, grid_w - 1)
        while abs(jy - py) < 3 and abs(jx - px) < 3:
            jy = random.randint(1, grid_h - 1)
            jx = random.randint(1, grid_w - 1)
        
        jacares.append({
            'y': float(jy),
            'x': float(jx),
            'vy': random.choice([-0.2, 0.2]), # Velocidade vertical suave
            'vx': random.choice([-0.2, 0.2])  # Velocidade horizontal suave
        })

    def desenhar_emoji(y, x_grid, emoji):
        """Converte as coordenadas da grade para o terminal com suporte a emoji."""
        screen_x = x_grid * 2 + 1
        screen_y = y + 1
        try:
            stdscr.addstr(screen_y, screen_x, emoji)
        except curses.error:
            pass

    while True:
        # Usa erase() ao invés de clear() para evitar flicker/pisca-pisca
        stdscr.erase()

        # Moldura em volta do jogo
        stdscr.box()

        # Cabeçalho / HUD
        hud = f" ☕ CAPIVARA RUN | Pontos: {score} | Vidas: {'❤️ ' * vidas}"
        try:
            stdscr.addstr(0, max(1, (max_w - len(hud)) // 2), hud[:max_w - 2], curses.A_BOLD)
        except curses.error:
            pass

        # Rodapé de Instruções
        rodape = " Setas: Mover | Q: Sair "
        try:
            stdscr.addstr(max_h - 1, max(1, (max_w - len(rodape)) // 2), rodape, curses.A_DIM)
        except curses.error:
            pass

        # Desenhar Elementos do Jogo
        desenhar_emoji(cafe_y, cafe_x, EMOJI_CAFE)

        for j in jacares:
            desenhar_emoji(int(j['y']), int(j['x']), EMOJI_JACARE)

        desenhar_emoji(py, px, EMOJI_CAPIVARA)

        stdscr.refresh()

        # Leitura dos Controles (instantâneo)
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break

        if key == curses.KEY_UP and py > 1:
            py -= 1
        elif key == curses.KEY_DOWN and py < grid_h - 1:
            py += 1
        elif key == curses.KEY_LEFT and px > 1:
            px -= 1
        elif key == curses.KEY_RIGHT and px < grid_w - 1:
            px += 1

        # Colisão com o Café
        if py == cafe_y and px == cafe_x:
            score += 10
            cafe_y = random.randint(1, grid_h - 1)
            cafe_x = random.randint(1, grid_w - 1)

            # Adiciona jacaré a cada 30 pontos
            if score % 30 == 0:
                jacares.append({
                    'y': float(random.randint(1, grid_h - 1)),
                    'x': float(random.randint(1, grid_w - 1)),
                    'vy': random.choice([-0.25, 0.25]),
                    'vx': random.choice([-0.25, 0.25])
                })

        # Movimentação Suave dos Jacarés
        for j in jacares:
            j['y'] += j['vy']
            j['x'] += j['vx']

            # Quicar nas paredes
            if j['y'] <= 1 or j['y'] >= grid_h - 1:
                j['vy'] *= -1
                j['y'] += j['vy']
            if j['x'] <= 1 or j['x'] >= grid_w - 1:
                j['vx'] *= -1
                j['x'] += j['vx']

            # Colisão Jacaré vs Capivara
            if py == int(j['y']) and px == int(j['x']):
                vidas -= 1
                py, px = grid_h // 2, grid_w // 2  # Respawn no centro
                time.sleep(0.3)
                break

        # Tela de Game Over
        if vidas <= 0:
            stdscr.erase()
            msg1 = "=== GAME OVER ==="
            msg2 = "A Capivara virou lanche de Jacaré! 🐊"
            msg3 = f"Pontuação Final: {score} pontos"
            msg4 = "Pressione 'Q' para sair"

            try:
                stdscr.addstr(max_h // 2 - 2, max(0, (max_w - len(msg1)) // 2), msg1, curses.A_BOLD)
                stdscr.addstr(max_h // 2 - 1, max(0, (max_w - len(msg2)) // 2), msg2)
                stdscr.addstr(max_h // 2 + 1, max(0, (max_w - len(msg3)) // 2), msg3, curses.A_BOLD)
                stdscr.addstr(max_h // 2 + 3, max(0, (max_w - len(msg4)) // 2), msg4, curses.A_DIM)
            except curses.error:
                pass

            stdscr.refresh()
            stdscr.nodelay(False)
            while True:
                k = stdscr.getch()
                if k in [ord('q'), ord('Q')]:
                    break
            break

if __name__ == "__main__":
    curses.wrapper(jogo)