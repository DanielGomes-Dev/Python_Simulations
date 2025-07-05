import arcade
import random
import math

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Colisão de Bolas com Ângulo Realista"

class Bola:
    def __init__(self, x, y, vx, vy, radius=10, cor=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = random.randint(5, 10)
        self.cor = cor or (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def mover(self):
        self.x += self.vx
        self.y += self.vy

        # colisão com as paredes
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx *= -1
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy *= -1
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1

    def desenhar(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.cor)

    def colidiu_com(self, outra):
        dx = self.x - outra.x
        dy = self.y - outra.y
        dist = math.hypot(dx, dy)
        return dist < self.radius + outra.radius

    def resolver_colisao(self, outra):
        # Vetor de distância
        dx = outra.x - self.x
        dy = outra.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return  # evita divisão por zero

        # Vetor normal (direção da colisão)
        nx = dx / dist
        ny = dy / dist

        # Vetor tangente (perpendicular ao normal)
        tx = -ny
        ty = nx

        # Decompor velocidades nos eixos normal e tangente
        v1n = self.vx * nx + self.vy * ny
        v1t = self.vx * tx + self.vy * ty
        v2n = outra.vx * nx + outra.vy * ny
        v2t = outra.vx * tx + outra.vy * ty

        # Troca apenas os componentes normais (massa igual e colisão elástica)
        v1n, v2n = v2n, v1n

        # Recompõe as velocidades nos eixos x e y
        self.vx = v1n * nx + v1t * tx
        self.vy = v1n * ny + v1t * ty
        outra.vx = v2n * nx + v2t * tx
        outra.vy = v2n * ny + v2t * ty

        # Separar para evitar que fiquem grudadas
        sobreposicao = self.radius + outra.radius - dist
        self.x -= nx * sobreposicao / 2
        self.y -= ny * sobreposicao / 2
        outra.x += nx * sobreposicao / 2
        outra.y += ny * sobreposicao / 2


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        self.bolas = []

        for _ in range(200):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 3)
            self.bolas.append(Bola(x, y, vx, vy))

    def on_draw(self):
        self.clear()
        for bola in self.bolas:
            bola.desenhar()

    def on_update(self, delta_time):
        # mover todas
        for bola in self.bolas:
            bola.mover()

        # checar colisões
        for i in range(len(self.bolas)):
            for j in range(i + 1, len(self.bolas)):
                b1 = self.bolas[i]
                b2 = self.bolas[j]
                if b1.colidiu_com(b2):
                    b1.resolver_colisao(b2)


def main():
    game = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()
