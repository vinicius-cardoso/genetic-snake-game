import pygame
import random
import time
import matplotlib.pyplot as plt
import threading
from aco import AntColony


SNAKE_SPEED = 10
SNAKE_INITIAL_POSITION = [40, 0]
SNAKE_INITIAL_BODY = [[40, 0], [30, 0], [20, 0], [10, 0]]

NUMBER_OF_FRUITS = 10

ANT_COUNT = 100
ITERATIONS = 100

WINDOW_X = 500
WINDOW_Y = 500
GRID_SIZE = 10

UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
GRAY = pygame.Color(50, 50, 50)
YELLOW = pygame.Color(255, 255, 0)

FONT_STYLE = 'arial'
FONT_SIZE = 20

class Snake:
    def __init__(self):
        self.position = SNAKE_INITIAL_POSITION
        self.body = SNAKE_INITIAL_BODY
        self.direction = RIGHT
        self.change_to = self.direction

    def change_direction(self, key):
        if key == 'UP':
            self.change_to = UP
        elif key == 'DOWN':
            self.change_to = DOWN
        elif key == 'LEFT':
            self.change_to = LEFT
        elif key == 'RIGHT':
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

    def move(self, fruits, score, last_capture_time):
        if self.direction == UP:
            self.position[1] -= GRID_SIZE
        elif self.direction == DOWN:
            self.position[1] += GRID_SIZE
        elif self.direction == LEFT:
            self.position[0] -= GRID_SIZE
        elif self.direction == RIGHT:
            self.position[0] += GRID_SIZE

        self.body.insert(0, list(self.position))

        for fruit in fruits:
            if self.position == fruit.position:
                fruit.spawn = False
                fruits.remove(fruit)
                elapsed_time = time.time() - last_capture_time
                elapsed_time = elapsed_time if elapsed_time < 5 else 5
                score_increase = 50 + (50 - 10 * elapsed_time)
                score += max(score_increase, 0)
                return score, True
        else:
            self.body.pop()

        return score, False

class Fruit:
    def __init__(self):
        self.position = [
            random.randrange(1, (WINDOW_X // GRID_SIZE)) * GRID_SIZE, 
            random.randrange(1, (WINDOW_Y // GRID_SIZE)) * GRID_SIZE
        ]
        self.spawn = True

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Snake')

        self.window = None
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.fruits = [Fruit() for _ in range(NUMBER_OF_FRUITS)]
        self.fruits_coordinates = ()
        self.score = 0
        self.start_time = time.time()
        self.last_capture_time = self.start_time  # Track the time of the last capture

    def show_score_and_time(self):
        font = pygame.font.SysFont(FONT_STYLE, FONT_SIZE)

        score_surface = font.render(f'Score : {self.score:.0f}', True, WHITE)
        score_rect = score_surface.get_rect()
        self.window.blit(score_surface, score_rect)

        # Calculate the elapsed time since the last capture
        elapsed_time = time.time() - self.last_capture_time
        time_surface = font.render(f'Time: {elapsed_time:.1f}s', True, WHITE)
        time_rect = time_surface.get_rect()
        time_rect.topleft = (0, 30)
        self.window.blit(time_surface, time_rect)

        # Show how many fruits user have captured
        fruits_surface = font.render(f'Fruits: {10 - len(self.fruits)}', True, WHITE)
        fruits_rect = fruits_surface.get_rect()
        fruits_rect.topleft = (0, 60)
        self.window.blit(fruits_surface, fruits_rect)

    def game_over(self):
        end_time = time.time()
        total_time = end_time - self.start_time
        font = pygame.font.SysFont(FONT_STYLE, 50)
        game_over_surface = font.render(f'Your Score is : {self.score:.0f}', True, RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (WINDOW_X / 2, WINDOW_Y / 4)

        self.window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)
        pygame.quit()
        quit()

    def check_collision(self):
        if (
            self.snake.position[0] < 0 or self.snake.position[0] > WINDOW_X - GRID_SIZE or
            self.snake.position[1] < 0 or self.snake.position[1] > WINDOW_Y - GRID_SIZE
        ):
            self.game_over()

        # for block in self.snake.body[1:]:
        #     if self.snake.position == block:
        #         self.game_over()

    def draw_elements(self):
        self.window.fill(BLACK)

        for x in range(0, WINDOW_X, GRID_SIZE):
            pygame.draw.line(self.window, GRAY, (x, 0), (x, WINDOW_Y))
        for y in range(0, WINDOW_Y, GRID_SIZE):
            pygame.draw.line(self.window, GRAY, (0, y), (WINDOW_X, y))

        for pos in self.snake.body:
            pygame.draw.rect(
                self.window, GREEN, pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE)
            )

        for fruit in self.fruits:
            pygame.draw.rect(
                self.window, RED, pygame.Rect(
                    fruit.position[0], fruit.position[1], GRID_SIZE, GRID_SIZE
                )
            )

        # path_points = self.discrete_path(self.snake.position, self.optimal_nodes[0])

        # for point in path_points:
        #     pygame.draw.rect(self.window, YELLOW, (point[0], point[1], GRID_SIZE, GRID_SIZE))

        self.show_score_and_time()
        pygame.display.update()

    def find_closest_right_coordinate(self, coord, coord_list):
        x, y = coord

        # Filtrar coordenadas à direita
        right_coords = [c for c in coord_list if c[0] > x]

        if not right_coords:
            return None  # Retorna None se não houver coordenadas à direita

        # Encontrar a coordenada à direita mais próxima
        closest_right_coord = min(right_coords, key=lambda c: c[0] - x)

        return closest_right_coord

    def discrete_path(self, start, end):
        path = []
        x1, y1 = start
        x2, y2 = end
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            path.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        # Adjust path points to be multiples of 10
        path = [
            (round(x / GRID_SIZE) * GRID_SIZE, round(y / GRID_SIZE) * GRID_SIZE) for x, y in path
        ]

        i = 0

        while i < len(path) - 1:
            xx1, yy1 = path[i]
            xx2, yy2 = path[i + 1]

            if (xx1 != xx2 and yy1 != yy2):
                path.insert(i + 1, (xx1, yy2))

            i += 1

        return path

    def generate_commands(self, path_points):
        commands = []

        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            if x1 < x2:
                commands.append('RIGHT')
            elif x1 > x2:
                commands.append('LEFT')
            elif y1 < y2:
                commands.append('DOWN')
            elif y1 > y2:
                commands.append('UP')
 
        return commands

    def set_fruits_coordinates(self):
        fruits_coordinates = [fruit.position for fruit in self.fruits]
        fruits_coordinates = tuple([tuple(fruit) for fruit in fruits_coordinates])

        self.fruits_coordinates = fruits_coordinates

    def ant_colony_optimization(self):
        colony = AntColony(self.fruits_coordinates, ant_count=ANT_COUNT, iterations=ITERATIONS)
        optimal_nodes = colony.get_path()
        optimal_nodes.pop()

        self.optimal_nodes = optimal_nodes

    def plot_nodes(self, w=5, h=5):
        for x, y in self.fruits_coordinates:
            plt.plot(x, y, "g.", markersize=15)

        plt.axis("off")
        fig = plt.gcf()
        fig.set_size_inches([w, h])
    
    def plot_result(self):
        plt.style.use("dark_background")

        self.plot_nodes()

        for i in range(len(self.optimal_nodes) - 1):
            plt.plot(
                (self.optimal_nodes[i][0], self.optimal_nodes[i + 1][0]),
                (self.optimal_nodes[i][1], self.optimal_nodes[i + 1][1]),
            )

        plt.gca().invert_yaxis()
        # plt.show()
        plt.show(block=False)
        plt.pause(15)
        plt.close()

    def command_snake(self, keys):
        for key in keys:
            self.snake.change_direction(key)
            self.snake.update_direction()

            previous_score = self.score

            self.score, captured = self.snake.move(self.fruits, self.score, self.last_capture_time)

            if captured:
                self.last_capture_time = time.time()

            if not self.fruits:
                self.game_over()

            self.check_collision()
            self.draw_elements()
            self.clock.tick(SNAKE_SPEED)

    def run(self):
        self.set_fruits_coordinates()
        self.ant_colony_optimization()

        # Plot the result in a separate thread
        # plot_thread = threading.Thread(target=self.plot_result)
        # plot_thread.start()

        keys = []

        first_fruit = self.find_closest_right_coordinate(self.snake.position, self.optimal_nodes)
        first_fruit_index = self.optimal_nodes.index(first_fruit)

        self.optimal_nodes.remove(first_fruit)
        self.optimal_nodes = [first_fruit] + self.optimal_nodes[first_fruit_index:] + self.optimal_nodes[:first_fruit_index]

        path_points = self.discrete_path(self.snake.position, self.optimal_nodes[0])

        keys.extend(self.generate_commands(path_points))

        for i in range(len(self.optimal_nodes) - 1):
            path_points = self.discrete_path(self.optimal_nodes[i], self.optimal_nodes[i + 1])

            keys.extend(self.generate_commands(path_points))

        self.window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        self.command_snake(keys)

if __name__ == "__main__":
    game = Game()
    game.run()
