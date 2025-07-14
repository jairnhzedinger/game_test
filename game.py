from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Classes do Jogo ---

class Inimigo(Entity):
    """
    Classe para representar os inimigos do jogo.
    Herda de Entity e controla seu próprio comportamento e vida.
    """
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            color=color.magenta,
            position=position,
            collider='box',
            scale_y=2
        )
        self.vida = 100
        self.velocidade = 2

    def update(self):
        # Para de se mover se a vida acabar
        if self.vida <= 0:
            return

        # Segue o jogador
        try:
            direcao = (jogador.position - self.position).normalized()
            self.position += direcao * time.dt * self.velocidade
            self.look_at(jogador) # Faz o inimigo "olhar" para o jogador

            # Verifica colisão com o jogador
            if self.intersects(jogador).hit:
                jogador.sofrer_dano(20 * time.dt)
        except Exception:
            # Caso o jogador seja destruído, para de tentar encontrá-lo
            pass

class Jogador(FirstPersonController):
    """
    Classe para o jogador, herdando o controle de primeira pessoa.
    Gerencia a vida, a pontuação e as ações do jogador.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vida = 100
        self.itens_coletados = 0
        self.cooldown_tiro = 0.4
        self._tempo_ultimo_tiro = 0

        # Ativa a gravidade para o jogador
        self.gravity = 1

    def sofrer_dano(self, quantidade):
        self.vida -= quantidade
        if self.vida <= 0:
            self.vida = 0
            game_over()

    def coletar_item(self):
        self.itens_coletados += 1

    def input(self, key):
        # Ação de atirar com o mouse
        if key == 'left mouse down':
            if time.time() - self._tempo_ultimo_tiro > self.cooldown_tiro:
                self._tempo_ultimo_tiro = time.time()
                Tiro(
                    position=self.world_position + Vec3(0, 1.5, 0) + self.camera_pivot.forward * 1.5,
                    rotation=self.camera_pivot.world_rotation
                )
        # Sair do jogo
        if key == 'escape':
            application.quit()

class Tiro(Entity):
    """
    Classe para os projéteis disparados pelo jogador.
    """
    def __init__(self, **kwargs):
        super().__init__(model='sphere', color=color.red, scale=0.2, **kwargs)
        self.collider = 'box'

    def update(self):
        # Movimenta o tiro para frente
        self.position += self.forward * time.dt * 20

        # Verifica colisão com inimigos
        hit_info = self.intersects()
        if hit_info.hit:
            if isinstance(hit_info.entity, Inimigo):
                hit_info.entity.vida -= 50 # Causa 50 de dano
                if hit_info.entity.vida <= 0:
                    destroy(hit_info.entity)
                destroy(self) # Destrói o tiro ao atingir

        # Destrói o tiro se ele se afastar muito
        if distance_xz(self, jogador) > 50:
            destroy(self)

# --- Configuração Inicial do Jogo ---

app = Ursina()

# Mapa do jogo
mapa = [
    "################",
    "#.............D#",
    "#..####...E....#",
    "#..............#",
    "#.......########",
    "#..............#",
    "###............#",
    "#..............#",
    "#...*...##.....#",
    "#.......##.E...#",
    "#..............#",
    "####...........#",
    "#..............#",
    "#......#####*###",
    "#..............#",
    "################"
]

# Geração do mundo a partir do mapa
for z, linha in enumerate(mapa):
    for x, char in enumerate(linha):
        pos = (x, 1, z)
        if char == '#':
            Entity(model='cube', color=color.gray, position=pos, scale=(1, 2, 1), collider='cube', texture='brick')
        elif char == 'D':
            Entity(model='cube', color=color.orange, position=pos, scale=(1, 2, 1), collider='cube', name='porta')
        elif char == '*':
            Entity(model='sphere', color=color.yellow, position=(x, 1.5, z), scale=0.4, name='item', collider='sphere')
        elif char == 'E':
            Inimigo(position=(x, 1, z))

# Entidades do ambiente
chao = Entity(model='plane', scale=(len(mapa[0]), 1, len(mapa)), texture='grass', collider='box')

# Instância do jogador usando a classe
jogador = Jogador(position=(2, 2, 2))

# --- Interface do Usuário (HUD) ---

vida_texto = Text(text=f"Vida: {int(jogador.vida)}", position=window.top_left + Vec2(0.05, -0.05), scale=1.5)
item_texto = Text(text=f"Itens: {jogador.itens_coletados}", position=window.top_left + Vec2(0.05, -0.10), scale=1.5)
mira = Entity(model='quad', parent=camera.ui, scale=0.015, color=color.white, texture='circle')

# --- Funções de Lógica do Jogo ---

def update():
    """
    Função principal de atualização, chamada a cada frame.
    """
    # Atualiza a HUD
    vida_texto.text = f"Vida: {int(jogador.vida)}"
    item_texto.text = f"Itens: {jogador.itens_coletados}"

    # Lógica para coletar itens
    hit_info = jogador.intersects()
    if hit_info.hit and hit_info.entity.name == 'item':
        jogador.coletar_item()
        destroy(hit_info.entity)

    # Lógica para abrir portas
    if jogador.itens_coletados >= 2: # Exige 2 itens para abrir a porta
        porta = find_entity('porta')
        if porta and distance_xz(jogador, porta) < 3:
            destroy(porta)

def game_over():
    """
    Função chamada quando a vida do jogador chega a zero.
    """
    Text(text='GAME OVER', scale=5, origin=(0, 0), color=color.red)
    destroy(jogador)
    mouse.locked = False
    invoke(application.quit, delay=3) # Fecha o jogo após 3 segundos

# --- Inicia o Jogo ---
app.run()