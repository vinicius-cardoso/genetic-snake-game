import pygame
import time
import random
import numpy as np

SNAKE_SPEED = 500
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

FONT_STYLE = 'times new roman'
FONT_SIZE = 20

# Parâmetros da ACO
NUM_ANTS = 10
MAX_ITER = 5
EVAPORATION_RATE = 0.1
ALPHA = 1.0
BETA = 5.0
Q = 100  # Constante para a quantidade de feromônio

# Inicializa feromônios
pheromones = np.ones((WINDOW_X // 10, WINDOW_Y // 10))

class Ant:
    def __init__(self, ant_number):
        self.snake_position, self.snake_body = create_snake()
        self.direction = RIGHT
        self.score = 0
        self.path = []
        self.is_alive = True
        self.ant_number = ant_number

    def choose_direction(self, fruit_position):
        if not self.is_alive:
            return
        
        # Definição de probabilidades baseadas nos feromônios
        directions = [UP, DOWN, LEFT, RIGHT]
        next_positions = {
            UP: [self.snake_position[0], self.snake_position[1] - 10],
            DOWN: [self.snake_position[0], self.snake_position[1] + 10],
            LEFT: [self.snake_position[0] - 10, self.snake_position[1]],
            RIGHT: [self.snake_position[0] + 10, self.snake_position[1]]
        }

        probabilities = []
        for direction in directions:
            next_position = next_positions[direction]
            if 0 <= next_position[0] < WINDOW_X and 0 <= next_position[1] < WINDOW_Y:
                if next_position in self.snake_body:
                    probabilities.append(0)
                    continue
                x, y = next_position[0] // 10, next_position[1] // 10
                distance = np.linalg.norm(np.array(next_position) - np.array(fruit_position))
                probability = (pheromones[x, y] ** ALPHA) * ((1 / (distance + 1)) ** BETA)
                probabilities.append(probability)
            else:
                probabilities.append(0)

        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
            self.direction = random.choices(directions, probabilities)[0]
        else:
            self.direction = random.choice(directions)
        
        self.path.append(self.direction)

    def move(self, fruit_position):
        if self.direction == UP:
            self.snake_position[1] -= 10
        elif self.direction == DOWN:
            self.snake_position[1] += 10
        elif self.direction == LEFT:
            self.snake_position[0] -= 10
        elif self.direction == RIGHT:
            self.snake_position[0] += 10

        self.snake_body.insert(0, list(self.snake_position))

        if self.snake_position[0] == fruit_position[0] and self.snake_position[1] == fruit_position[1]:
            self.score += 1
            return True
        else:
            self.snake_body.pop()
            return False

    def is_dead(self):
        if (self.snake_position[0] < 0 or self.snake_position[0] >= WINDOW_X or
            self.snake_position[1] < 0 or self.snake_position[1] >= WINDOW_Y):
            return True
        for block in self.snake_body[1:]:
            if self.snake_position == block:
                return True
        return False

def create_snake():
    snake_position = [100, 50]
    snake_body = [
        [100, 50],
        [90, 50],
        [80, 50],
        [70, 50]
    ]
    return snake_position, snake_body

def create_fruit():
    fruit_position = [
        random.randrange(1, (WINDOW_X // 10)) * 10, 
        random.randrange(1, (WINDOW_Y // 10)) * 10
    ]
    return fruit_position

def show_score(choice, color, font, size, score, game_window, ant_number, iteration_number):
    score_font = pygame.font.SysFont(font, size)    
    score_surface = score_font.render('Score : ' + str(score) + ' | Ant: ' + str(ant_number) + ' | Iteration: ' + str(iteration_number), True, color)
    score_rect = score_surface.get_rect()
    score_rect.topleft = (10, WINDOW_Y - 30)
    game_window.blit(score_surface, score_rect)

def game_over(game_window, score):
    my_font = pygame.font.SysFont(FONT_STYLE, 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (WINDOW_X / 2, WINDOW_Y / 4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

def draw_game(game_window, snake_body, fruit_position):
    game_window.fill(BLACK)
    for pos in snake_body:
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, RED, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

def update_pheromones(ants):
    global pheromones
    pheromones *= (1 - EVAPORATION_RATE)
    for ant in ants:
        pheromone_deposit = Q / (1 + ant.score)
        for move in ant.path:
            if move == UP:
                x, y = ant.snake_position[0] // 10, (ant.snake_position[1] - 10) // 10
            elif move == DOWN:
                x, y = ant.snake_position[0] // 10, (ant.snake_position[1] + 10) // 10
            elif move == LEFT:
                x, y = (ant.snake_position[0] - 10) // 10, ant.snake_position[1] // 10
            elif move == RIGHT:
                x, y = (ant.snake_position[0] + 10) // 10, ant.snake_position[1] // 10
            if 0 <= x < WINDOW_X // 10 and 0 <= y < WINDOW_Y // 10:
                pheromones[x, y] += pheromone_deposit

def snake_game():
    pygame.init()
    pygame.display.set_caption('Snake')
    game_window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
    fps = pygame.time.Clock()

    for iteration_number in range(MAX_ITER):
        ants = [Ant(i) for i in range(1, NUM_ANTS + 1)]
        fruit_position = create_fruit()
        for ant in ants:
            while ant.is_alive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()

                ant.choose_direction(fruit_position)
                if ant.move(fruit_position):
                    fruit_position = create_fruit()
                if ant.is_dead():
                    ant.is_alive = False
                    break

                draw_game(game_window, ant.snake_body, fruit_position)
                show_score(1, WHITE, FONT_STYLE, FONT_SIZE, ant.score, game_window, ant.ant_number, iteration_number + 1)
                pygame.display.update()
                fps.tick(SNAKE_SPEED)

        update_pheromones(ants)
        best_ant = max(ants, key=lambda ant: ant.score)
        print(f'Best score in iteration {iteration_number + 1}: {best_ant.score}')

    best_ant = max(ants, key=lambda ant: ant.score)
    snake_position = best_ant.snake_position
    snake_body = best_ant.snake_body
    direction = best_ant.direction
    score = best_ant.score
    fruit_position = create_fruit()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if direction == UP:
            snake_position[1] -= 10
        if direction == DOWN:
            snake_position[1] += 10
        if direction == LEFT:
            snake_position[0] -= 10
        if direction == RIGHT:
            snake_position[0] += 10

        snake_body.insert(0, list(snake_position))

        if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
            score += 1
            fruit_position = create_fruit()
        else:
            snake_body.pop()

        if snake_position[0] < 0 or snake_position[0] >= WINDOW_X or snake_position[1] < 0 or snake_position[1] >= WINDOW_Y:
            game_over(game_window, score)
        
        for block in snake_body[1:]:
            if snake_position == block:
                game_over(game_window, score)

        draw_game(game_window, snake_body, fruit_position)
        show_score(1, WHITE, FONT_STYLE, FONT_SIZE, score, game_window, best_ant.ant_number, MAX_ITER)
        pygame.display.update()
        fps.tick(30)

snake_game()
