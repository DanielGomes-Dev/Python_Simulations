import arcade
import random
import math

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Bolas Soltas com Rebote e Colisão"

BALL_RADIUS = 10
BALL_COUNT = 1000
BALL_LAUNCH_INTERVAL = 0.01
FRICTION = 0.99  # Pode deixar próximo de 1 para pouca perda de velocidade

class Ball:
    def __init__(self, x, y, change_x, change_y, color=arcade.color.BLUE_BELL):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.color = color
        self.change_x = change_x
        self.change_y = change_y

    def update(self):
        self.x += self.change_x
        self.y += self.change_y

        # Rebote nas bordas com inversão da velocidade
        if self.x - self.radius < 0:
            self.x = self.radius
            self.change_x *= -1
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.change_x *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.change_y *= -1
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.change_y *= -1

        # Fricção para desacelerar levemente com o tempo (opcional)
        self.change_x *= FRICTION
        self.change_y *= FRICTION

        # Zera velocidades muito pequenas para parar completamente (opcional)
        if abs(self.change_x) < 0.01:
            self.change_x = 0
        if abs(self.change_y) < 0.01:
            self.change_y = 0

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
        x = random.uniform(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
        y = random.uniform(BALL_RADIUS, SCREEN_HEIGHT - BALL_RADIUS)

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

        change_x = random.uniform(-4, 4)
        change_y = random.uniform(-4, 4)

        color = random.choice(colors)
        new_ball = Ball(x, y, change_x, change_y, color)

        for ball in self.ball_list:
            dist = math.hypot(ball.x - new_ball.x, ball.y - new_ball.y)
            if dist < BALL_RADIUS * 2:
                return

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

        # Desenha o contador no topo esquerdo
        contador_texto = f"Bolas criadas: {self.total_balls_created}"
        arcade.draw_text(contador_texto, 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

        # Desenha o FPS no topo direito
        fps = arcade.get_fps()
        fps_text = f"FPS: {fps:.1f}"
        arcade.draw_text(fps_text, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

    def on_update(self, delta_time: float):
        self.time_since_last_launch += delta_time
        if self.total_balls_created < BALL_COUNT and self.time_since_last_launch >= BALL_LAUNCH_INTERVAL:
            self.create_new_ball()
            self.time_since_last_launch = 0.0

        for ball in self.ball_list:
            ball.update()

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
