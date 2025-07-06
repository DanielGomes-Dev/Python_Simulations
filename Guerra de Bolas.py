import arcade
import random
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor

USE_PARALLELISM = True

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Bolas com Paralelismo por Quadrantes e Impulso"

BALL_RADIUS = 15
BALL_COUNT = 300
BALL_LAUNCH_INTERVAL = 1 / 100
FRICTION = 1

NUM_QUADS_X = 4
NUM_QUADS_Y = 2
NUM_QUADS = NUM_QUADS_X * NUM_QUADS_Y

# Cores dos quadrantes suavizadas para melhor contraste com as bolinhas
QUAD_COLORS = [
    (255, 255, 255),  # Branco para todos os quadrantes (fundo)
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
]

BALL_COLORS = [
    arcade.color.BLUE_BELL, arcade.color.AUBURN, arcade.color.BANANA_MANIA,
    arcade.color.CERULEAN, arcade.color.DARK_SALMON, arcade.color.ELECTRIC_LIME,
    arcade.color.FIREBRICK, arcade.color.GOLDENROD, arcade.color.HOT_PINK, arcade.color.LIME_GREEN,
]

MAX_BALLS_PER_COLOR = 50
COOLDOWN_SECONDS = 0.5

lock = threading.Lock()


class Ball:
    def __init__(self, x, y, change_x, change_y, color):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.color = color
        self.change_x = change_x
        self.change_y = change_y
        self.previous_quad = None
        self.last_spawn_time = 0

    @property
    def speed(self):
        return math.hypot(self.change_x, self.change_y)

    def update(self):
        self.x += self.change_x
        self.y += self.change_y

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

        self.change_x *= FRICTION
        self.change_y *= FRICTION

        if abs(self.change_x) < 0.01:
            self.change_x = 0
        if abs(self.change_y) < 0.01:
            self.change_y = 0

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)


def average_velocity(ball1, ball2):
    avg_speed_x = (ball1.change_x + ball2.change_x) / 2
    avg_speed_y = (ball1.change_y + ball2.change_y) / 2
    return avg_speed_x, avg_speed_y


def update_and_collide(balls, all_balls, game):
    balls_to_remove = set()
    balls_to_add = []

    for ball in balls:
        ball.update()

    n = len(balls)
    for i in range(n):
        b1 = balls[i]
        for j in range(i + 1, n):
            b2 = balls[j]
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

                if b1.color != b2.color:
                    speed1 = b1.speed
                    speed2 = b2.speed
                    if speed1 < speed2:
                        balls_to_remove.add(i)
                        b2.change_x *= 0.8
                        b2.change_y *= 0.8
                        break
                    else:
                        balls_to_remove.add(j)
                        b1.change_x *= 0.8
                        b1.change_y *= 0.8
                else:
                    now = time.time()
                    if now - b1.last_spawn_time >= COOLDOWN_SECONDS and now - b2.last_spawn_time >= COOLDOWN_SECONDS:
                        with lock:
                            count_color = sum(1 for ball in all_balls if ball.color == b1.color)
                            if count_color < MAX_BALLS_PER_COLOR:
                                mid_x = (b1.x + b2.x) / 2
                                mid_y = (b1.y + b2.y) / 2
                                new_cx, new_cy = average_velocity(b1, b2)
                                new_ball = Ball(mid_x, mid_y, new_cx, new_cy, b1.color)
                                balls_to_add.append(new_ball)
                                all_balls.append(new_ball)
                                b1.last_spawn_time = now
                                b2.last_spawn_time = now

    with lock:
        for index in sorted(balls_to_remove, reverse=True):
            if balls[index] in all_balls:
                all_balls.remove(balls[index])
            del balls[index]
        for ball in balls_to_add:
            balls.append(ball)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.LIGHT_GRAY
        self.ball_list = []
        self.total_balls_created = 0
        self.time_since_last_launch = 0.0
        self.executor = ThreadPoolExecutor(max_workers=NUM_QUADS)
        self.last_winner_color = None

        # Carrega a música uma vez e toca em loop
        self.music = arcade.Sound("lofi12.mp3")
        self.music_player = self.music.play(loop=True)

    def setup(self):
        self.ball_list.clear()
        self.total_balls_created = 0
        self.time_since_last_launch = 0.0
        # Não toca a música aqui para não reiniciar

    def create_new_ball(self):
        with lock:
            color_count = {}
            for ball in self.ball_list:
                color_count[ball.color] = color_count.get(ball.color, 0) + 1

            color = random.choice(BALL_COLORS)
            if color_count.get(color, 0) >= MAX_BALLS_PER_COLOR:
                return

            x = random.uniform(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
            y = random.uniform(BALL_RADIUS, SCREEN_HEIGHT - BALL_RADIUS)
            change_x = random.uniform(-4, 4)
            change_y = random.uniform(-4, 4)
            new_ball = Ball(x, y, change_x, change_y, color)

            for ball in self.ball_list:
                dist = math.hypot(ball.x - new_ball.x, ball.y - new_ball.y)
                if dist < BALL_RADIUS * 2:
                    return

            self.ball_list.append(new_ball)
            self.total_balls_created += 1

    def get_quadrant(self, ball):
        quad_w = SCREEN_WIDTH / NUM_QUADS_X
        quad_h = SCREEN_HEIGHT / NUM_QUADS_Y
        x_index = int(ball.x // quad_w)
        y_index = int(ball.y // quad_h)
        x_index = min(x_index, NUM_QUADS_X - 1)
        y_index = min(y_index, NUM_QUADS_Y - 1)
        return y_index * NUM_QUADS_X + x_index

    def on_draw(self):
        self.clear()
        quad_w = SCREEN_WIDTH / NUM_QUADS_X
        quad_h = SCREEN_HEIGHT / NUM_QUADS_Y

        # Quadrantes brancos (fundo)
        for i in range(NUM_QUADS):
            col = i % NUM_QUADS_X
            row = i // NUM_QUADS_X
            left = col * quad_w
            bottom = row * quad_h
            arcade.draw_lrbt_rectangle_filled(left, left + quad_w, bottom, bottom + quad_h, arcade.color.WHITE)

        # Desenha as linhas tracejadas separando os quadrantes
        dash_length = 10
        gap_length = 5

        # Linhas verticais tracejadas
        for i in range(1, NUM_QUADS_X):
            x = i * quad_w
            y_start = 0
            y_end = SCREEN_HEIGHT
            y = y_start
            while y < y_end:
                arcade.draw_line(x, y, x, min(y + dash_length, y_end), arcade.color.GRAY)
                y += dash_length + gap_length

        # Linhas horizontais tracejadas
        for i in range(1, NUM_QUADS_Y):
            y = i * quad_h
            x_start = 0
            x_end = SCREEN_WIDTH
            x = x_start
            while x < x_end:
                arcade.draw_line(x, y, min(x + dash_length, x_end), y, arcade.color.GRAY)
                x += dash_length + gap_length

        for ball in self.ball_list:
            ball.draw()

        arcade.draw_text(f"Bolas criadas: {self.total_balls_created}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

        counts = {}
        for ball in self.ball_list:
            counts[ball.color] = counts.get(ball.color, 0) + 1

        x = 10
        y = 10
        for color in BALL_COLORS:
            count = counts.get(color, 0)
            arcade.draw_text(f"{count}", x, y, color, 16)
            x += 60

        arcade.draw_text(f"Total: {len(self.ball_list)}", SCREEN_WIDTH - 130, 10, arcade.color.BLACK, 18)

        if self.last_winner_color is not None:
            try:
                color_index = BALL_COLORS.index(self.last_winner_color)
                nomes_cores_pt = [
                    "Azul Claro", "Auburn", "Amarelo Claro",
                    "Cerúleo", "Salmão Escuro", "Lima Elétrica",
                    "Vermelho Tijolo", "Dourado", "Rosa Forte", "Verde Lima",
                ]
                color_name = nomes_cores_pt[color_index]
            except ValueError:
                color_name = "Desconhecida"

            arcade.draw_text(
                f"Última cor vencedora: {color_name}",
                SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 40,
                arcade.color.BLACK, 20
            )

    def on_update(self, delta_time: float):
        self.time_since_last_launch += delta_time
        if self.total_balls_created < BALL_COUNT and self.time_since_last_launch >= BALL_LAUNCH_INTERVAL:
            self.create_new_ball()
            self.time_since_last_launch = 0.0

        quads = [[] for _ in range(NUM_QUADS)]
        for ball in self.ball_list:
            current_quad = self.get_quadrant(ball)

            if ball.previous_quad is not None and ball.previous_quad != current_quad:
                impulse_strength = 4.0
                angle = random.uniform(0, 2 * math.pi)
                impulse_x = math.cos(angle) * impulse_strength
                impulse_y = math.sin(angle) * impulse_strength
                ball.change_x += impulse_x
                ball.change_y += impulse_y

            ball.previous_quad = current_quad
            quads[current_quad].append(ball)

        unique_colors = set(ball.color for ball in self.ball_list)
        if len(unique_colors) == 1 and self.total_balls_created >= 10:
            self.last_winner_color = next(iter(unique_colors))
            print("Reiniciando o jogo: apenas uma cor restante.")
            self.setup()
            return

        if USE_PARALLELISM:
            futures = [self.executor.submit(update_and_collide, quad, self.ball_list, self) for quad in quads]
            for future in futures:
                future.result()
        else:
            for quad in quads:
                update_and_collide(quad, self.ball_list, self)

    def on_close(self):
        if self.music_player:
            self.music_player.stop()
        super().on_close()


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
