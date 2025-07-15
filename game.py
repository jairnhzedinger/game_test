import pygame
import math
import sys
import random

pygame.init()
largura, altura = 1920, 1080
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("DOOMzinho - Melhorado com Minimapa e IA")

fonte = pygame.font.SysFont("Courier New", 12)
relogio = pygame.time.Clock()

mapa = (
    '########################',
    '#......#.....#........E#',
    '#.####.#.###.#.######..#',
    '#.#....#.#...#.#....#..#',
    '#.#.####.#.###.#.##.#..#',
    '#.#......#.....#.#..#..#',
    '#.########.#####.#.###.#',
    '#..........#.....#...#.#',
    '#.######.#.#.#######.#.#',
    '#.#....#.#.#.......#.#.#',
    '#.#.##.#.#.#######.#.#.#',
    '#.#..#.#.#.....#...#.#.#',
    '#.##.#.#.#####.#.###.#.#',
    '#....#.#.....#.#.....#.#',
    '####.#.#####.#.#######.#',
    '#..#.#.....#.#.#.......#',
    '#..#.#####.#.#.#.#####.#',
    '#..#.....#.#.#.#.....#.#',
    '#.#######.#.#.#######.#.',
    '#.......#.#.#.........#.',
    '#.#####.#.#.#########.#.',
    '#.#...#.#.#.......#..*#.',
    '#.#.#.#.#.#######.###.#.',
    '########################'
)

mapa_largura = len(mapa[0])
mapa_altura = len(mapa)

# Jogador
pos_x, pos_y = 14.0, 14.0
angulo = 0.0
fov = math.pi / 3
vel = 5.0
sens = 2.5
dist_max = 16.0
vida = 100
itens_coletados = 0
tempo_disparo = 0
arma_sprite = fonte.render("\u253B\u2526\u2524\u2500", True, (255, 255, 255))
particulas = []
game_over = False

# Inimigos
inimigos = [
    {'x': 5.5, 'y': 5.5, 'vivo': True},
    {'x': 10.5, 'y': 12.5, 'vivo': True}
]

def gerar_textura(dist, col):
    chars = ['█', '▓', '▒', '░', '.']
    idx = min(int(dist / (dist_max / len(chars))), len(chars) - 1)
    cor_base = max(0, 255 - int((dist / dist_max) * 255))
    cor_r = max(0, cor_base - (col % 100))
    cor = (cor_r, cor_base, cor_base)
    return fonte.render(chars[idx], True, cor)

def desenhar_chao():
    for y in range(altura // 2, altura, 12):
        profundidade = (y - altura / 2) / (altura / 2)
        dist = dist_max * profundidade
        for x in range(0, largura, 6):
            floor_x = pos_x + math.sin(angulo) * dist
            floor_y = pos_y + math.cos(angulo) * dist
            checker = int(floor_x % 2) ^ int(floor_y % 2)
            char = '.' if checker else ':'
            brilho = max(0, 255 - int(dist * 15))
            cor = (brilho, brilho, brilho)
            texto = fonte.render(char, True, cor)
            tela.blit(texto, (x, y))

def desenhar_mundo():
    for x in range(0, largura, 6):
        raio = (angulo - fov / 2) + (x / largura) * fov
        dist = 0
        acerto = False
        olho_x = math.sin(raio)
        olho_y = math.cos(raio)
        while not acerto and dist < dist_max:
            dist += 0.05
            tx = int(pos_x + olho_x * dist)
            ty = int(pos_y + olho_y * dist)
            if tx < 0 or tx >= mapa_largura or ty < 0 or ty >= mapa_altura:
                acerto = True
                dist = dist_max
            elif mapa[ty][tx] in ['#', 'D']:
                acerto = True
        altura_coluna = int(altura / (dist + 0.1))
        y_offset = altura // 2 - altura_coluna // 2
        for y in range(0, altura_coluna, 12):
            textura = gerar_textura(dist, x)
            tela.blit(textura, (x, y_offset + y))

def atualizar_particulas(dt):
    novas = []
    for (x, y, vida_p) in particulas:
        vida_p -= dt
        y -= 40 * dt
        if vida_p > 0:
            novas.append((x, y, vida_p))
    if random.random() < 0.3:
        novas.append((random.randint(0, largura), altura, 1.5))
    return novas

def desenhar_particulas():
    for (x, y, vida_p) in particulas:
        cor = (255, 180, 80)
        char = fonte.render('*', True, cor)
        tela.blit(char, (x, y))

def desenhar_hud():
    pygame.draw.rect(tela, (100, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(tela, (255, 0, 0), (20, 20, 2 * vida, 20))
    tela.blit(fonte.render(f"VIDA: {int(vida)}", True, (255, 255, 255)), (230, 18))
    tela.blit(fonte.render(f"ITENS: {itens_coletados}", True, (255, 255, 0)), (20, 45))

def desenhar_arma():
    x = largura // 2 - arma_sprite.get_width() // 2
    y = altura - 60
    tela.blit(arma_sprite, (x, y))

def desenhar_minimapa():
    tam_celula = 10
    tamanho = 160
    centro_x = int(pos_x * tam_celula)
    centro_y = int(pos_y * tam_celula)
    mapa_surf = pygame.Surface((tamanho, tamanho))
    mapa_surf.fill((20, 20, 20))
    offset_x = centro_x - tamanho // 2
    offset_y = centro_y - tamanho // 2
    for y in range(mapa_altura):
        for x in range(mapa_largura):
            px = x * tam_celula - offset_x
            py = y * tam_celula - offset_y
            if 0 <= px < tamanho and 0 <= py < tamanho:
                cor = (60, 60, 60)
                if mapa[y][x] == '#':
                    cor = (200, 200, 200)
                elif mapa[y][x] == 'D':
                    cor = (0, 120, 255)
                elif mapa[y][x] == '*':
                    cor = (255, 255, 0)
                pygame.draw.rect(mapa_surf, cor, (px, py, tam_celula, tam_celula))
    pygame.draw.rect(mapa_surf, (255, 0, 0), (centro_x - offset_x, centro_y - offset_y, 6, 6))
    for e in inimigos:
        if e['vivo']:
            ex = int(e['x'] * tam_celula) - offset_x
            ey = int(e['y'] * tam_celula) - offset_y
            if 0 <= ex < tamanho and 0 <= ey < tamanho:
                pygame.draw.rect(mapa_surf, (255, 0, 255), (ex, ey, 6, 6))
    tela.blit(mapa_surf, (largura - tamanho - 10, 10))

def abrir_portas():
    global mapa
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            px = int(pos_x) + dx
            py = int(pos_y) + dy
            if 0 <= px < mapa_largura and 0 <= py < mapa_altura:
                if mapa[py][px] == 'D':
                    mapa[py] = mapa[py][:px] + '.' + mapa[py][px + 1:]

def coletar_itens():
    global mapa, itens_coletados
    px, py = int(pos_x), int(pos_y)
    if mapa[py][px] == '*':
        mapa[py] = mapa[py][:px] + '.' + mapa[py][px + 1:]
        itens_coletados += 1

def atualizar_inimigos(dt):
    global vida, game_over
    for inimigo in inimigos:
        if not inimigo['vivo']:
            continue
        dx = pos_x - inimigo['x']
        dy = pos_y - inimigo['y']
        dist = math.hypot(dx, dy)
        if dist < 0.4:
            vida -= 30 * dt
            if vida <= 0:
                game_over = True
        elif dist < 6:
            direcao_x = dx / dist
            direcao_y = dy / dist
            novo_x = inimigo['x'] + direcao_x * dt
            novo_y = inimigo['y'] + direcao_y * dt
            if mapa[int(novo_y)][int(novo_x)] != '#':
                inimigo['x'] = novo_x
                inimigo['y'] = novo_y

def desenhar_inimigos():
    sprite_inimigo = [
        "ಠ_ಠ",
        "\\|/",
        "/ \\",
    ]
    for inimigo in inimigos:
        if inimigo['vivo']:
            dx = inimigo['x'] - pos_x
            dy = inimigo['y'] - pos_y
            dist = math.hypot(dx, dy)
            if dist < 6:
                ix = largura // 2 + int(dx * 30)
                iy = altura // 2 + int(dy * 30)
                for i, linha in enumerate(sprite_inimigo):
                    txt = fonte.render(linha, True, (255, 0, 255))
                    tela.blit(txt, (ix, iy + i * 12))

def atirar():
    global tempo_disparo
    for inimigo in inimigos:
        if inimigo['vivo']:
            dx = inimigo['x'] - pos_x
            dy = inimigo['y'] - pos_y
            dist = math.hypot(dx, dy)
            ang = math.atan2(dx, dy)
            dif = abs(ang - angulo)
            if dist < 5 and dif < 0.2:
                inimigo['vivo'] = False
                break
    tempo_disparo = 0.1

# Loop principal
while True:
    dt = relogio.tick(60) / 1000
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_over:
        teclas = pygame.key.get_pressed()
        clique = pygame.mouse.get_pressed()[0]
        if teclas[pygame.K_a]:
            angulo -= sens * dt
        if teclas[pygame.K_d]:
            angulo += sens * dt
        dx = math.sin(angulo) * vel * dt
        dy = math.cos(angulo) * vel * dt
        if teclas[pygame.K_w]:
            if mapa[int(pos_y + dy)][int(pos_x + dx)] not in ['#', 'D']:
                pos_x += dx
                pos_y += dy
        if teclas[pygame.K_s]:
            if mapa[int(pos_y - dy)][int(pos_x - dx)] not in ['#', 'D']:
                pos_x -= dx
                pos_y -= dy
        if (teclas[pygame.K_SPACE] or clique) and tempo_disparo <= 0:
            atirar()

        abrir_portas()
        coletar_itens()
        atualizar_inimigos(dt)
        particulas[:] = atualizar_particulas(dt)

    tela.fill((0, 0, 0))
    desenhar_chao()
    desenhar_mundo()
    desenhar_particulas()
    desenhar_hud()
    desenhar_inimigos()
    desenhar_arma()
    desenhar_minimapa()

    if tempo_disparo > 0:
        overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, int(tempo_disparo * 255)))
        tela.blit(overlay, (0, 0))
        tempo_disparo -= dt

    if game_over:
        texto = fonte.render("GAME OVER", True, (255, 0, 0))
        tela.blit(texto, (largura // 2 - 40, altura // 2 - 10))

    pygame.display.flip()
