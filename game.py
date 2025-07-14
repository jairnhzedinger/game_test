from ursina import *
from random import uniform

app = Ursina()

# === Variáveis ===
vida = 100
itens_coletados = 0
inimigos = []
tiros = []
porta_aberta = []

# === Jogador ===
player = Entity(model='cube', color=color.azure, position=(1,1,1), scale=(1,2,1), collider='box')
camera.parent = player
camera.position = (0, 1.5, -4)
camera.rotation = (0, 0, 0)
mouse.locked = True

# === Terreno ===
chao = Entity(model='plane', texture='white_cube', scale=(32,1,32), texture_scale=(32,32), collider='box', color=color.dark_gray)

# === Mapa com paredes, portas, itens, inimigos ===
mapa = [
    "################",
    "#.............D#",
    "#..####........#",
    "#..............#",
    "#.......########",
    "#..............#",
    "###............#",
    "#..............#",
    "#...*...##.....#",
    "#.......##.....#",
    "#..............#",
    "####...........#",
    "#..............#",
    "#......#####*###",
    "#..............#",
    "################"
]

# === Constrói o mundo ===
for y, linha in enumerate(mapa):
    for x, char in enumerate(linha):
        pos = Vec3(x, 0.5, y)
        if char == '#':
            Entity(model='cube', color=color.gray, position=pos, collider='box', scale_y=2)
        elif char == 'D':
            e = Entity(model='cube', color=color.orange, position=pos, collider='box', scale_y=2, name='porta')
            porta_aberta.append(e)
        elif char == '*':
            Entity(model='sphere', color=color.yellow, position=pos + Vec3(0,0.5,0), scale=0.4, name='item', collider='box')
        elif char == 'E':
            inimigo = Entity(model='cube', color=color.magenta, position=pos + Vec3(0,0.5,0), collider='box', scale=1.2)
            inimigos.append(inimigo)

# Adiciona dois inimigos manualmente
for pos in [(5.5,5.5), (10.5,12.5)]:
    inimigo = Entity(model='cube', color=color.magenta, position=(pos[0], 0.5, pos[1]), collider='box', scale=1.2)
    inimigos.append(inimigo)

# === HUD ===
vida_texto = Text(text=f"Vida: {int(vida)}", position=window.top_left + Vec2(0.02,-0.02), scale=1.2, origin=(0,0))
item_texto = Text(text=f"Itens: {itens_coletados}", position=window.top_left + Vec2(0.02,-0.07), scale=1.2, origin=(0,0))
game_over_text = Text(text='GAME OVER', scale=3, color=color.red, origin=(0,0), enabled=False)

# === Função de disparo ===
def atirar():
    global tiros
    tiro = Entity(model='cube', color=color.red, scale=0.1, position=player.world_position + camera.forward * 1.5)
    tiro.direction = camera.forward
    tiros.append(tiro)

# === Atualização do jogo ===
def update():
    global vida, itens_coletados

    # Movimento do jogador
    speed = 5 * time.dt
    if held_keys['w']: player.position += camera.forward * speed
    if held_keys['s']: player.position -= camera.forward * speed
    if held_keys['a']: player.position -= camera.right * speed
    if held_keys['d']: player.position += camera.right * speed

    camera.rotation_x -= mouse.velocity[1] * 100
    player.rotation_y += mouse.velocity[0] * 100

    # Tiro
    if held_keys['left mouse']:
        if not hasattr(player, 'cooldown') or time.time() - player.cooldown > 0.4:
            player.cooldown = time.time()
            atirar()

    # Movimentação dos tiros
    for tiro in tiros[:]:
        tiro.position += tiro.direction * 10 * time.dt
        for inimigo in inimigos:
            if inimigo.enabled and tiro.intersects(inimigo).hit:
                destroy(inimigo)
                inimigos.remove(inimigo)
                destroy(tiro)
                tiros.remove(tiro)
                break
        if distance(tiro, player) > 20:
            destroy(tiro)
            tiros.remove(tiro)

    # Inimigos se aproximam
    for inimigo in inimigos:
        direcao = (player.position - inimigo.position).normalized()
        inimigo.position += direcao * time.dt
        if distance(inimigo, player) < 1:
            vida -= 30 * time.dt
            if vida <= 0:
                vida = 0
                game_over_text.enabled = True
                application.pause()

    # Portas se abrem
    for porta in porta_aberta:
        if distance(player, porta) < 2:
            destroy(porta)

    # Coleta de itens
    for e in scene.entities:
        if e.name == 'item' and distance(player, e) < 1:
            itens_coletados += 1
            destroy(e)

    # HUD
    vida_texto.text = f"Vida: {int(vida)}"
    item_texto.text = f"Itens: {itens_coletados}"

# === Input para sair ===
def input(key):
    if key == 'escape':
        application.quit()

app.run()
wwwwwwwwww