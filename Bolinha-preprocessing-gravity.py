import arcade
import random
import math

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Simulação Bola - Pré-processada"

NUM_BALLS = 20  # ou 32000 para testes longos
SIMULATION_FRAMES = 300 * 60  # 5 segundos a 30fps

GRAVIDADE = 0.3  # força da gravidade

class Bola:
    def __init__(self, x, y, vx, vy, radius=10, cor=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.cor = cor or (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def mover(self):
        # Aplica a gravidade
        self.vy -= GRAVIDADE

        self.x += self.vx
        self.y += self.vy

        # Colisão com as bordas
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx *= -1
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1

        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy *= -0.8  # amortecimento no topo
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -0.8  # amortecimento no solo
            if abs(self.vy) < 0.5:
                self.vy = 0  # evita quicar infinitamente

    def desenhar(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.cor)

    def colidiu_com(self, outra):
        dx = self.x - outra.x
        dy = self.y - outra.y
        dist = math.hypot(dx, dy)
        return dist < self.radius + outra.radius

    def resolver_colisao(self, outra):
        dx = outra.x - self.x
        dy = outra.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist
        tx = -ny
        ty = nx

        v1n = self.vx * nx + self.vy * ny
        v1t = self.vx * tx + self.vy * ty
        v2n = outra.vx * nx + outra.vy * ny
        v2t = outra.vx * tx + outra.vy * ty

        v1n, v2n = v2n, v1n

        self.vx = v1n * nx + v1t * tx
        self.vy = v1n * ny + v1t * ty
        outra.vx = v2n * nx + v2t * tx
        outra.vy = v2n * ny + v2t * ty

        sobreposicao = self.radius + outra.radius - dist
        self.x -= nx * sobreposicao / 2
        self.y -= ny * sobreposicao / 2
        outra.x += nx * sobreposicao / 2
        outra.y += ny * sobreposicao / 2

def simular_frame(args):
    bolas_state, width, height = args
    bolas = [Bola(*b) for b in bolas_state]

    for bola in bolas:
        bola.mover()

    n = len(bolas)
    for i in range(n):
        for j in range(i + 1, n):
            if bolas[i].colidiu_com(bolas[j]):
                bolas[i].resolver_colisao(bolas[j])

    return [(b.x, b.y, b.vx, b.vy, b.radius, b.cor) for b in bolas]

def barra_progresso(atual, total, comprimento=40):
    proporcao = atual / total
    preenchido = int(comprimento * proporcao)
    barra = '=' * preenchido + '-' * (comprimento - preenchido)
    print(f'\r[{barra}] {atual}/{total} frames processados', end='')
    if atual == total:
        print()

def preprocessar_bolas(bolas_iniciais, num_frames):
    estados = []
    estado_atual = bolas_iniciais
    for i in range(num_frames):
        estado_atual = simular_frame((estado_atual, SCREEN_WIDTH, SCREEN_HEIGHT))
        estados.append(estado_atual)
        barra_progresso(i + 1, num_frames)
    return estados

class Jogo(arcade.Window):
    def __init__(self, estados_simulados):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        self.estados_simulados = estados_simulados
        self.frame_atual = 0
        self.direcao = 1
        self.bolas = [Bola(*b) for b in estados_simulados[0]]

    def on_draw(self):
        self.clear()
        for bola in self.bolas:
            bola.desenhar()

    def on_update(self, delta_time):
        estado = self.estados_simulados[self.frame_atual]
        for i, b in enumerate(estado):
            self.bolas[i].x, self.bolas[i].y, self.bolas[i].vx, self.bolas[i].vy, self.bolas[i].radius, self.bolas[i].cor = b

        self.frame_atual += self.direcao
        if self.frame_atual >= len(self.estados_simulados) - 1:
            self.direcao = -1
        elif self.frame_atual <= 0:
            self.direcao = 1

def main():
    bolas = []
    for _ in range(NUM_BALLS):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(200, SCREEN_HEIGHT - 50)
        vx = random.uniform(-3, 3)
        vy = random.uniform(-1, 1)  # menor velocidade vertical inicial
        radius = random.randint(2, 5)
        cor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        bolas.append((x, y, vx, vy, radius, cor))

    print("Iniciando pré-processamento dos frames...")
    estados = preprocessar_bolas(bolas, SIMULATION_FRAMES)
    print("Pré-processamento concluído!")

    janela = Jogo(estados)
    arcade.run()

if __name__ == "__main__":
    main()
