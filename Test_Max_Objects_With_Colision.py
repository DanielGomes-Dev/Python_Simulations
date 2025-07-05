import arcade
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bolas com Física Estável e Colisão"

BALL_RADIUS = 10
BALL_COUNT = 1000
BALL_LAUNCH_INTERVAL = 0.001
GRAVITY = 0.5
FRICTION = 1  # Amortecimento maior para parar as bolas
HORIZONTAL_SPEED = 3

class Ball:
    def __init__(self, x, y, change_x=0, color=arcade.color.BLUE_BELL):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.color = color
        self.change_y = 0.0
        self.change_x = change_x

    def update(self):
        self.change_y -= GRAVITY
        self.x += self.change_x
        self.y += self.change_y

        # Limita borda esquerda
        if self.x - self.radius < 0:
            self.x = self.radius
            self.change_x *= -0.6

        # Limita borda direita
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.change_x *= -0.6

        # Limita chão
        if self.y - self.radius < 0:
            self.y = self.radius
            self.change_y *= -0.4

            # Para se estiver quase parado no chão
            if abs(self.change_y) < 0.1:
                self.change_y = 0

        # Limita topo
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.change_y *= -0.4

        # Aplica fricção (amortecimento)
        self.change_y *= FRICTION
        self.change_x *= FRICTION

        # Zera velocidades muito pequenas pra parar completamente
        if abs(self.change_y) < 0.05:
            self.change_y = 0
        if abs(self.change_x) < 0.05:
            self.change_x = 0

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.LIGHT_GRAY
        self.ball_list: list[Ball] = []
        self.total_balls_created = 0
        self.time_since_last_launch = 0.0

    def setup(self):
        self.ball_list.clear()
        self.total_balls_created = 0
        self.time_since_last_launch = 0.0

    def create_new_ball(self):
        x = 100
        y = SCREEN_HEIGHT - BALL_RADIUS

        colors = [
            arcade.color.BLUE_BELL,
            arcade.color.AUBURN,
            arcade.color.BANANA_MANIA,
            arcade.color.CERULEAN,
            arcade.color.DARK_SALMON,
            arcade.color.ELECTRIC_LIME,
            arcade.color.FIREBRICK,
            arcade.color.GOLDENROD,
            arcade.color.HOT_PINK,
            arcade.color.LIME_GREEN,
        ]

        color = random.choice(colors)
        new_ball = Ball(x, y, change_x=HORIZONTAL_SPEED, color=color)

        for ball in self.ball_list:
            dist = math.hypot(ball.x - new_ball.x, ball.y - new_ball.y)
            if dist < BALL_RADIUS * 2:
                return  # Evita sobreposição inicial

        self.ball_list.append(new_ball)
        self.total_balls_created += 1

    def draw_launcher(self):
        width = 60
        height = 40
        center_x = 100
        center_y = SCREEN_HEIGHT - 20
        left = center_x - width / 2
        right = center_x + width / 2
        bottom = center_y - height / 2
        top = center_y + height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        self.draw_launcher()
        for ball in self.ball_list:
            ball.draw()

    def on_update(self, delta_time: float):
        self.time_since_last_launch += delta_time
        if self.total_balls_created < BALL_COUNT and self.time_since_last_launch >= BALL_LAUNCH_INTERVAL:
            self.create_new_ball()
            self.time_since_last_launch = 0.0

        for ball in self.ball_list:
            ball.update()

        # Colisão entre bolas com troca de velocidades
        for i in range(len(self.ball_list)):
            for j in range(i + 1, len(self.ball_list)):
                b1 = self.ball_list[i]
                b2 = self.ball_list[j]
                dx = b1.x - b2.x
                dy = b1.y - b2.y
                dist = math.hypot(dx, dy)
                min_dist = b1.radius + b2.radius

                if dist < min_dist and dist > 0:
                    overlap = 0.5 * (min_dist - dist)
                    nx = dx / dist
                    ny = dy / dist
                    b1.x += nx * overlap
                    b1.y += ny * overlap
                    b2.x -= nx * overlap
                    b2.y -= ny * overlap

                    # Troca simples das velocidades para simular colisão
                    v1n = b1.change_x * nx + b1.change_y * ny
                    v2n = b2.change_x * nx + b2.change_y * ny

                    b1.change_x += (v2n - v1n) * nx
                    b1.change_y += (v2n - v1n) * ny
                    b2.change_x += (v1n - v2n) * nx
                    b2.change_y += (v1n - v2n) * ny

def main():
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
