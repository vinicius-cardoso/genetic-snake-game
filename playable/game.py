import pygame
import time

from snake import Snake
from fruit import Fruit
from game_settings import *

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
