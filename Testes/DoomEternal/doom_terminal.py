import math
import os
import sys
import time

WIDTH = 80
HEIGHT = 30
FOV = math.pi / 3

# Mapa da fase (1 = Parede, 0 = Espaço Vazio)
MAP = [
    "1111111111111111",
    "1000000000001001",
    "1011110011111001",
    "1010000000001001",
    "1010111111001001",
    "1000100001000001",
    "1010100001001001",
    "1111111111111111"
]
MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)

player_x = 3.5
player_y = 3.5
player_a = 0.0

# --- Sistema de leitura do teclado por Sistema Operacional ---
if os.name == 'nt':  # Windows
    import msvcrt

    def set_raw():
        pass

    def restore_raw():
        pass

    def get_key():
        if msvcrt.kbhit():
            try:
                return msvcrt.getch().decode('utf-8', errors='ignore').lower()
            except:
                return None
        return None
else:  # Linux / macOS
    import select
    import termios
    import tty

    old_settings = None

    def set_raw():
        global old_settings
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def restore_raw():
        if old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def get_key():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1).lower()
        return None

def render():
    screen = []
    
    for x in range(WIDTH):
        ray_angle = (player_a - FOV / 2) + (x / WIDTH) * FOV
        distance = 0.0
        hit_wall = False
        
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        
        while not hit_wall and distance < 16.0:
            distance += 0.05
            test_x = int(player_x + cos_a * distance)
            test_y = int(player_y + sin_a * distance)
            
            if test_x < 0 or test_x >= MAP_WIDTH or test_y < 0 or test_y >= MAP_HEIGHT:
                hit_wall = True
                distance = 16.0
            elif MAP[test_y][test_x] == '1':
                hit_wall = True

        # Correção do efeito "Olho de Peixe" (Fisheye Lens)
        corrected_dist = distance * math.cos(ray_angle - player_a)
        if corrected_dist < 0.1:
            corrected_dist = 0.1

        ceiling = int((HEIGHT / 2.0) - HEIGHT / float(corrected_dist))
        floor = HEIGHT - ceiling
        
        # Sombreamento ASCII por profundidade
        if distance <= 2.0: shade = '█'
        elif distance <= 4.0: shade = '▓'
        elif distance <= 6.0: shade = '▒'
        elif distance <= 8.0: shade = '░'
        else: shade = ' '
        
        column = []
        for y in range(HEIGHT):
            if y < ceiling:
                column.append(' ')
            elif ceiling <= y <= floor:
                column.append(shade)
            else:
                column.append('.')
        screen.append(column)
        
    os.system('cls' if os.name == 'nt' else 'clear')
    output = []
    for y in range(HEIGHT):
        row = ''.join([screen[x][y] for x in range(WIDTH)])
        output.append(row)
    print('\n'.join(output))

def main():
    global player_x, player_y, player_a

    MOVE_SPEED = 0.15
    ROT_SPEED = 0.1

    set_raw()
    try:
        print("Iniciando DOOM no Terminal...")
        print("Controles: W/S (Avançar/Recuar), A/D (Girar), Q (Sair)")
        time.sleep(1.5)

        while True:
            render()
            
            key = get_key()
            if key == 'q':
                break
            elif key == 'w':
                # Move para frente com colisão
                new_x = player_x + math.cos(player_a) * MOVE_SPEED
                new_y = player_y + math.sin(player_a) * MOVE_SPEED
                if MAP[int(player_y)][int(new_x)] != '1': player_x = new_x
                if MAP[int(new_y)][int(player_x)] != '1': player_y = new_y
            elif key == 's':
                # Move para trás com colisão
                new_x = player_x - math.cos(player_a) * MOVE_SPEED
                new_y = player_y - math.sin(player_a) * MOVE_SPEED
                if MAP[int(player_y)][int(new_x)] != '1': player_x = new_x
                if MAP[int(new_y)][int(player_x)] != '1': player_y = new_y
            elif key == 'a':
                # Gira para a esquerda
                player_a -= ROT_SPEED
            elif key == 'd':
                # Gira para a direita
                player_a += ROT_SPEED

            time.sleep(0.02)

    finally:
        restore_raw()
        print("\nJogo encerrado!")

if __name__ == '__main__':
    main()