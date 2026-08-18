# -*- coding: utf-8 -*-
"""
======================================================================
           NEED FOR TERMINAL: POLICE PURSUIT (Jogo de Corrida ASCII)
======================================================================
Requisitos: Apenas Python 3 (sem bibliotecas externas)
Controles:
  [W] / [Seta para Cima]    - Acelerar / Nitro
  [S] / [Seta para Baixo]   - Frear
  [A] / [Seta para Esquerda]- Mover para Esquerda
  [D] / [Seta para Direita] - Mover para Direita
  [Q]                       - Sair do Jogo
======================================================================
"""

import os
import sys
import time
import random

# --- Ativação de Cores ANSI no Windows ---
if os.name == 'nt':
    os.system('')

# --- Cores ANSI ---
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"
C_GREY    = "\033[90m"
BG_GREEN  = "\033[42m"
BG_GREY   = "\033[100m"

# --- Sistema de Leitura do Teclado (Cross-Platform) ---
if os.name == 'nt':
    import msvcrt

    def init_input(): pass
    def cleanup_input(): pass

    def get_input():
        if msvcrt.kbhit():
            try:
                ch = msvcrt.getch()
                # b'\x00' e b'\xe0' indicam teclas especiais (como as setas) no Windows
                if ch in (b'\x00', b'\xe0'):
                    ch = msvcrt.getch()
                    if ch == b'K': return 'left'
                    if ch == b'M': return 'right'
                    if ch == b'H': return 'up'
                    if ch == b'P': return 'down'
                key = ch.decode('utf-8', errors='ignore').lower()
                if key in ('a', 'left'): return 'left'
                if key in ('d', 'right'): return 'right'
                if key in ('w', 'up'): return 'up'
                if key in ('s', 'down'): return 'down'
                if key == 'q': return 'quit'
            except:
                pass
        return None
else:
    import termios, tty, select
    old_settings = None

    def init_input():
        global old_settings
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except:
            pass

    def cleanup_input():
        if old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass

    def get_input():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            try:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    dr2, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if dr2:
                        seq = sys.stdin.read(2)
                        if seq == '[D': return 'left'
                        if seq == '[C': return 'right'
                        if seq == '[A': return 'up'
                        if seq == '[B': return 'down'
                key = ch.lower()
                if key == 'a': return 'left'
                if key == 'd': return 'right'
                if key == 'w': return 'up'
                if key == 's': return 'down'
                if key == 'q': return 'quit'
            except:
                pass
        return None


class RacingGame:
    def __init__(self):
        # Dimensões do Cenário
        self.height = 18
        self.grass_width = 10
        self.lane_width = 5
        self.num_lanes = 3
        self.road_width = self.lane_width * self.num_lanes + (self.num_lanes - 1)  # 17 cols
        
        # Posição do Jogador (0 a 16 dentro da pista)
        self.player_x = 7  # Pista central
        self.player_y = 13 # Linha fixa perto do fundo
        
        # Estado do jogo
        self.speed = 100 # km/h
        self.score = 0
        self.distance_traveled = 0
        self.police_dist = 6.0 # Distância da polícia (0 = preso!)
        self.frame_count = 0
        self.siren_state = True
        
        # Objetos
        self.left_margin = []
        self.right_margin = []
        self.obstacles = [] # List de dicts {'x', 'y', 'type', 'symbol', 'color'}
        
        # Efeitos
        self.message = ""
        self.message_timer = 0
        self.is_sliding = False

        self._init_margins()

    def _init_margins(self):
        # Preenche os acostamentos iniciais com grama e algumas árvores
        for i in range(self.height):
            self.left_margin.append(self._generate_margin_row())
            self.right_margin.append(self._generate_margin_row())

    def _generate_margin_row(self):
        row = []
        for _ in range(self.grass_width):
            r = random.random()
            if r < 0.12:
                row.append(f"{C_GREEN}♣{C_RESET}")  # Árvore
            elif r < 0.20:
                row.append(f"{C_GREEN}🌲{C_RESET}") # Árvore 2
            elif r < 0.35:
                row.append(f"{C_GREY}.{C_RESET}")   # Pedrinha/Grama
            else:
                row.append(" ")
        return row

    def spawn_obstacle(self):
        # Gera carros de trânsito ou poças de óleo
        lanes_x = [1, 7, 13] # Centros das 3 pistas
        chosen_lane = random.choice(lanes_x)
        
        # Não gera se já tiver um obstáculo no topo nessa pista
        for obs in self.obstacles:
            if obs['y'] <= 2 and abs(obs['x'] - chosen_lane) < 4:
                return

        r = random.random()
        if r < 0.70:
            types = [
                {'symbol': '[🚘]', 'color': C_CYAN, 'name': 'Carro'},
                {'symbol': '[🚚]', 'color': C_YELLOW, 'name': 'Caminhão'},
                {'symbol': '[🚙]', 'color': C_MAGENTA, 'name': 'SUV'}
            ]
            t = random.choice(types)
            self.obstacles.append({
                'x': chosen_lane,
                'y': 0,
                'symbol': t['symbol'],
                'color': t['color'],
                'is_oil': False
            })
        elif r < 0.90:
            self.obstacles.append({
                'x': chosen_lane,
                'y': 0,
                'symbol': '(🛢️)',
                'color': C_GREY,
                'is_oil': True
            })

    def update(self, action):
        self.frame_count += 1
        self.siren_state = not self.siren_state

        # --- PROCESSAR CONTROLES ---
        if self.is_sliding:
            # Deslizando na pista por causa do óleo
            self.player_x += random.choice([-1, 1])
            self.is_sliding = False
            self.message = "⚠️ DERRAPOU NO ÓLEO! ⚠️"
            self.message_timer = 5
        elif action == 'left':
            self.player_x -= 2
        elif action == 'right':
            self.player_x += 2
        elif action == 'up':
            self.speed = min(180, self.speed + 5)
            self.police_dist = min(9.0, self.police_dist + 0.25)
        elif action == 'down':
            self.speed = max(40, self.speed - 8)
            self.police_dist -= 0.35

        # Velocidade base afeta a distância da polícia
        if action != 'up' and action != 'down':
            if self.speed > 110:
                self.police_dist = min(9.0, self.police_dist + 0.1)
            elif self.speed < 80:
                self.police_dist -= 0.15

        # Manter jogador nos limites da tela
        self.player_x = max(-2, min(self.road_width - 1, self.player_x))

        # --- ROLAGEM DO CENÁRIO ---
        self.left_margin.pop()
        self.left_margin.insert(0, self._generate_margin_row())
        self.right_margin.pop()
        self.right_margin.insert(0, self._generate_margin_row())

        # Spawn de novos obstáculos
        if random.random() < 0.35:
            self.spawn_obstacle()

        # Mover obstáculos para baixo
        move_step = 1 if self.speed >= 80 else (1 if self.frame_count % 2 == 0 else 0)
        for obs in self.obstacles:
            obs['y'] += move_step
        
        # Remover obstáculos que saíram da tela
        self.obstacles = [obs for obs in self.obstacles if obs['y'] < self.height]

        # --- VERIFICAÇÃO DE COLISÕES ---
        # 1. Colisão com o acostamento (Árvores)
        if self.player_x < 0 or self.player_x > self.road_width - 3:
            self.speed = 30
            self.police_dist -= 0.6
            self.message = "💥 BATEU NA ÁRVORE/GRAMA! 💥"
            self.message_timer = 5

        # 2. Colisão com obstáculos
        for obs in self.obstacles:
            if obs['y'] in (self.player_y, self.player_y - 1):
                if abs(obs['x'] - self.player_x) <= 2:
                    if obs['is_oil']:
                        self.is_sliding = True
                    else:
                        self.speed = 20
                        self.police_dist -= 1.2
                        self.message = "💥 COLISÃO NO TRÂNSITO! 💥"
                        self.message_timer = 5
                        obs['y'] = 99 # Remove obstáculo

        # Posição da polícia perseguindo horizontalmente
        police_x_target = self.player_x
        police_x = police_x_target

        # Atualizar pontuação
        self.score += int(self.speed / 10)
        self.distance_traveled += self.speed / 3600

        if self.message_timer > 0:
            self.message_timer -= 1

        # CONDIÇÃO DE PERSEGUIÇÃO / GAME OVER
        if self.police_dist <= 0:
            return "BUSTED"
        return "RUNNING"

    def render(self):
        lines = []
        
        # CABEÇALHO / HUD
        siren_light = f"{C_RED}🚨 POLÍCIA EM PERSEGUIÇÃO 🚨{C_RESET}" if self.siren_state else f"{C_BLUE}🚨 POLÍCIA EM PERSEGUIÇÃO 🚨{C_RESET}"
        lines.append(f"  {siren_light}".center(60))
        lines.append("═" * 54)
        
        dist_bar_filled = max(0, min(9, int(self.police_dist)))
        dist_bar = f"[{C_RED}{'█'*dist_bar_filled}{C_GREY}{'░'*(9-dist_bar_filled)}{C_RESET}]"
        
        lines.append(f" 🏎️  VELOCIDADE: {C_YELLOW}{self.speed} km/h{C_RESET} | 🚔 DISTÂNCIA POLÍCIA: {dist_bar}")
        lines.append(f" 🏆 PONTOS: {C_GREEN}{self.score}{C_RESET} | 🛣️  DISTÂNCIA: {self.distance_traveled:.2f} km")
        lines.append("═" * 54)

        # RENDERIZAR PISTA E CENÁRIO
        police_row_idx = int(self.player_y + self.police_dist)

        for y in range(self.height):
            line_buf = []
            
            # Acostamento Esquerdo
            line_buf.append("".join(self.left_margin[y]))
            
            # Guia/Meio-fio Esquerdo
            curb_color = C_RED if (y + self.frame_count) % 2 == 0 else C_WHITE
            line_buf.append(f"{curb_color}║{C_RESET}")

            # Construção da Rodovia (17 colunas)
            road_chars = [" "] * self.road_width
            
            # Marcas de Pista (Linhas Tracejadas)
            dash = "┆" if (y + self.frame_count) % 2 == 0 else " "
            road_chars[5] = f"{C_GREY}{dash}{C_RESET}"
            road_chars[11] = f"{C_GREY}{dash}{C_RESET}"

            # Desenhar Obstáculos
            for obs in self.obstacles:
                if obs['y'] == y:
                    x = max(0, min(self.road_width - 3, obs['x']))
                    symbol = f"{obs['color']}{obs['symbol']}{C_RESET}"
                    for idx, char in enumerate(symbol):
                        if x + idx < self.road_width:
                            road_chars[x + idx] = char

            # Desenhar Carro do Jogador
            if y == self.player_y:
                px = max(0, min(self.road_width - 3, self.player_x))
                player_str = f"{C_BOLD}{C_GREEN}[🏎️]{C_RESET}"
                for idx, char in enumerate(player_str):
                    if px + idx < self.road_width:
                        road_chars[px + idx] = char

            # Desenhar Carro da Polícia (Atrás do jogador)
            if y == police_row_idx and police_row_idx < self.height:
                pol_color = C_RED if self.siren_state else C_BLUE
                pol_x = max(0, min(self.road_width - 3, self.player_x))
                police_str = f"{C_BOLD}{pol_color}[🚔]{C_RESET}"
                for idx, char in enumerate(police_str):
                    if pol_x + idx < self.road_width:
                        road_chars[pol_x + idx] = char

            line_buf.append("".join(road_chars))

            # Guia/Meio-fio Direito
            line_buf.append(f"{curb_color}║{C_RESET}")
            
            # Acostamento Direito
            line_buf.append("".join(self.right_margin[y]))

            lines.append("".join(line_buf))

        lines.append("═" * 54)
        
        # MENSAGENS E CONTROLES
        if self.message_timer > 0:
            lines.append(f"  {C_RED}{C_BOLD}{self.message}{C_RESET}".center(65))
        else:
            lines.append(f" Controles: {C_YELLOW}[W]{C_RESET} Nitro  {C_YELLOW}[S]{C_RESET} Freio  {C_YELLOW}[A/D]{C_RESET} Volante  {C_YELLOW}[Q]{C_RESET} Sair")

        # Limpar tela e imprimir frame
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n".join(lines))


def main():
    init_input()
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{C_RED}{C_BOLD}")
        print(r"""
  _  _ ___ ___ ___   ___ ___  ___   _____ ___ ___ __  __ ___ _  _   _   _    
 | \| | __| __|   \ | __/ _ \| _ \ |_   _| __| _ \  \/  |_ _| \| | /_\ | |   
 | .` | _|| _|| |) || _| (_) |   /   | | | _||   / |\/| || || .` |/ _ \| |__ 
 |_|\_|___|___|___/ |_| \___/|_|_\   |_| |___|_|_\_|  |_|___|_|\_/_/ \_\____|
                                POLICE PURSUIT
        """)
        print(f"{C_RESET}")
        print(" 🏎️   Você está fugindo da polícia em alta velocidade!")
        print(" 🌲  Cuidado com as árvores no acostamento e carros na pista.")
        print(" 🛢️   Cuidado com poças de óleo para não derrapar!\n")
        print(" Pressione qualquer tecla para dar a partida...")
        
        # Esperar tecla
        while True:
            k = get_input()
            if k: break
            time.sleep(0.10)

        game = RacingGame()
        
        while True:
            action = get_input()
            if action == 'quit':
                print(f"\n{C_YELLOW}Você encostou o carro e desistiu da fuga!{C_RESET}")
                break

            status = game.update(action)
            game.render()

            if status == "BUSTED":
                print(f"\n{C_RED}{C_BOLD}🚨 PRESO PELA POLÍCIA! 🚨{C_RESET}")
                print(f"Você rodou {game.distance_traveled:.2f} km antes de ser pego.")
                print(f"Pontuação Final: {C_GREEN}{game.score}{C_RESET} pontos.\n")
                break

            time.sleep(0.10) # ~10 FPS

    finally:
        cleanup_input()

if __name__ == "__main__":
    main()