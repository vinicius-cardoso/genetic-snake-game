import pygame
from game_settings import *

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
