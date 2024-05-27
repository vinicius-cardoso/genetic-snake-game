import pygame
import random
import time

SNAKE_SPEED = 30
SNAKE_INITIAL_POSITION = [100, 50]
SNAKE_INITIAL_BODY = [[100, 50], [90, 50], [80, 50], [70, 50]]

WINDOW_X = 480
WINDOW_Y = 480

UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)

FONT_STYLE = 'arial'
FONT_SIZE = 20

class Snake:
    def __init__(self):
        self.position = SNAKE_INITIAL_POSITION
        self.body = SNAKE_INITIAL_BODY
        self.direction = RIGHT
        self.change_to = self.direction

    def change_direction(self, event):
        if event.key == pygame.K_UP:
            self.change_to = UP
        elif event.key == pygame.K_DOWN:
            self.change_to = DOWN
        elif event.key == pygame.K_LEFT:
            self.change_to = LEFT
        elif event.key == pygame.K_RIGHT:
            self.change_to = RIGHT

    def update_direction(self):
        if self.change_to == UP and self.direction != DOWN:
            self.direction = UP
        elif self.change_to == DOWN and self.direction != UP:
            self.direction = DOWN
        elif self.change_to == LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif self.change_to == RIGHT and self.direction != LEFT:
            self.direction = RIGHT

    def move(self, fruit, score):
        if self.direction == UP:
            self.position[1] -= 10
        elif self.direction == DOWN:
            self.position[1] += 10
        elif self.direction == LEFT:
            self.position[0] -= 10
        elif self.direction == RIGHT:
            self.position[0] += 10

        self.body.insert(0, list(self.position))

        if self.position == fruit.position:
            fruit.spawn = False
            score += 1
        else:
            self.body.pop()

        return score

class Fruit:
    def __init__(self):
        self.position = [
            random.randrange(1, (WINDOW_X // 10)) * 10, 
            random.randrange(1, (WINDOW_Y // 10)) * 10
        ]
        self.spawn = True

    def respawn(self):
        if not self.spawn:
            self.position = [
                random.randrange(1, (WINDOW_X // 10)) * 10, 
                random.randrange(1, (WINDOW_Y // 10)) * 10
            ]

        self.spawn = True

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Snake')

        self.window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.fruit = Fruit()
        self.score = 0

    def show_score(self):
        font = pygame.font.SysFont(FONT_STYLE, FONT_SIZE)
        score_surface = font.render('Score : ' + str(self.score), True, WHITE)
        score_rect = score_surface.get_rect()

        self.window.blit(score_surface, score_rect)

    def game_over(self):
        font = pygame.font.SysFont(FONT_STYLE, 50)
        game_over_surface = font.render('Your Score is : ' + str(self.score), True, RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (WINDOW_X / 2, WINDOW_Y / 4)

        self.window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)
        pygame.quit()
        quit()

    def check_collision(self):
        if (
            self.snake.position[0] < 0 or self.snake.position[0] > WINDOW_X - 10 or
            self.snake.position[1] < 0 or self.snake.position[1] > WINDOW_Y - 10
        ):
            self.game_over()

        for block in self.snake.body[1:]:
            if self.snake.position == block:
                self.game_over()

    def draw_elements(self):
        self.window.fill(BLACK)

        for pos in self.snake.body:
            pygame.draw.rect(self.window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

        pygame.draw.rect(
            self.window, RED, pygame.Rect(self.fruit.position[0], self.fruit.position[1], 10, 10)
        )
        self.show_score()
        pygame.display.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.snake.change_direction(event)

            self.snake.update_direction()
            self.score = self.snake.move(self.fruit, self.score)
            self.fruit.respawn()
            self.check_collision()
            self.draw_elements()
            self.clock.tick(SNAKE_SPEED)

if __name__ == "__main__":
    game = Game()
    game.run()
