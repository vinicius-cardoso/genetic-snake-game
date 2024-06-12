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

NUMBER_OF_ANTS = 100
ITERATIONS = 100
PHEROMONE_EVAPORATION_RATE = 0.8

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

    # Recebe o comando que a cobra recebe e armazena no atributo change_to
    def change_direction(self, key):
        if key == UP:
            self.change_to = UP
        elif key == DOWN:
            self.change_to = DOWN
        elif key == LEFT:
            self.change_to = LEFT
        elif key == RIGHT:
            self.change_to = RIGHT

    # Verifica se houve uma mudança de direcao e se a direcao atual da cobra nao eh contraria
    # Armazena a nova direcao no atributo direction
    def update_direction(self):
        if self.change_to == UP: # and self.direction != DOWN:
            self.direction = UP
        elif self.change_to == DOWN: # and self.direction != UP:
            self.direction = DOWN
        elif self.change_to == LEFT: # and self.direction != RIGHT:
            self.direction = LEFT
        elif self.change_to == RIGHT: # and self.direction != LEFT:
            self.direction = RIGHT

    # Atualiza posicao da cobra de acordo com a direcao recebida
    def update_position(self):
        if self.direction == UP:
            self.position[1] -= GRID_SIZE
        elif self.direction == DOWN:
            self.position[1] += GRID_SIZE
        elif self.direction == LEFT:
            self.position[0] -= GRID_SIZE
        elif self.direction == RIGHT:
            self.position[0] += GRID_SIZE

    # Move a cobra e retorna o score
    def move(self, fruits, score, last_eat_time):
        self.update_position()
        self.body.insert(0, list(self.position))
        
        score, fruit_eaten = self.check_if_eat_fruit(fruits, score, last_eat_time)

        # Marca o tempo demorado para comer a fruta
        if fruit_eaten:
            self.last_eat_time = time.time()
        else:
            self.body.pop()

        return score, fruit_eaten

    # Checa se a cobra comeu uma fruta
    def check_if_eat_fruit(self, fruits, score, last_eat_time):
        for fruit in fruits:
            if self.position == fruit.position:
                fruit.spawn = False
                fruits.remove(fruit)

                score = self.calculate_score(score, last_eat_time)

                return score, True

        return score, False

    # Calcula a pontuacao do jogador
    def calculate_score(self, score, last_eat_time):
        # Armazena o tempo que a cobra gastou entre a ultima fruta e a atual
        elapsed_time = time.time() - last_eat_time
        # Se o tempo for maior que 5, armazena apenas como 5 para o score nao mudar
        elapsed_time = elapsed_time if elapsed_time < 5 else 5

        # Calculo da pontuacao: Cada fruta comida vale 50
        # Tempo demorado para comer - pontuacao: (0s: 50, 1s: 40,..., >5s: 0)
        score_increase = 50 + (50 - 10 * elapsed_time)
        score += max(score_increase, 0)

        return score

class Fruit:
    def __init__(self):
        # Cria a fruta em uma posicao aleatoria da tela criada
        self.position = [
            random.randrange(1, (WINDOW_X // GRID_SIZE)) * GRID_SIZE, 
            random.randrange(1, (WINDOW_Y // GRID_SIZE)) * GRID_SIZE
        ]
        self.spawn = True

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Ant Colony Optimazation - Snake')

        self.window = None
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.fruits = [Fruit() for _ in range(NUMBER_OF_FRUITS)]
        self.fruits_coordinates = ()
        self.score = 0
        self.start_time = time.time()
        self.last_eat_time = self.start_time

    # Mostra a pontuacao do jogador e o tempo desde a ultima vez que comeu uma fruta
    def show_score_and_time(self):
        font = pygame.font.SysFont(FONT_STYLE, FONT_SIZE)

        score_surface = font.render(f'Score : {self.score:.0f}', True, WHITE)
        score_rect = score_surface.get_rect()
        self.window.blit(score_surface, score_rect)

        # Mostra quanto tempo gastou desde a ultima vez que comeu a fruta
        elapsed_time = time.time() - self.last_eat_time
        time_surface = font.render(f'Time: {elapsed_time:.1f}s', True, WHITE)
        time_rect = time_surface.get_rect()
        time_rect.topleft = (0, 30)
        self.window.blit(time_surface, time_rect)

        # Mostra quantas frutas a cobra ja comeu
        fruits_surface = font.render(f'Fruits: {10 - len(self.fruits)}', True, WHITE)
        fruits_rect = fruits_surface.get_rect()
        fruits_rect.topleft = (0, 60)
        self.window.blit(fruits_surface, fruits_rect)

    # Finaliza o jogo e mostra a pontuacao final
    def game_over(self):
        end_time = time.time()
        font = pygame.font.SysFont(FONT_STYLE, 50)
        game_over_surface = font.render(f'Your Score is : {self.score:.0f}', True, RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (WINDOW_X / 2, WINDOW_Y / 4)

        self.window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)
        pygame.quit()
        quit()

    # Detecta colisoes com a parede ou consigo mesmo
    def check_collision(self, detect_self_collision=False):
        # Detecta se a cobra ultrapassou os limites do jogo
        if (
            self.snake.position[0] < 0 or self.snake.position[0] > WINDOW_X - GRID_SIZE or
            self.snake.position[1] < 0 or self.snake.position[1] > WINDOW_Y - GRID_SIZE
        ):
            self.game_over()

        # Detecta se a cobra colidiu consigo mesma, se duas partes estao sobrepostas
        if detect_self_collision:
            for block in self.snake.body[1:]:
                if self.snake.position == block:
                    self.game_over()

    # Desenha os elementos na tela: Jogo, Grade, Cobra, Frutas
    def draw_elements(self, draw_path=False):
        # Define um fundo preto
        self.window.fill(BLACK)

        # Desenha uma grade cinza na tela com tamanho 10, formando um quadriculado
        for x in range(0, WINDOW_X, GRID_SIZE):
            pygame.draw.line(self.window, GRAY, (x, 0), (x, WINDOW_Y))
        for y in range(0, WINDOW_Y, GRID_SIZE):
            pygame.draw.line(self.window, GRAY, (0, y), (WINDOW_X, y))

        # Desenha a cobra em verde
        for pos in self.snake.body:
            pygame.draw.rect(
                self.window, GREEN, pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE)
            )

        # Desenha as frutas em vermelho
        for fruit in self.fruits:
            pygame.draw.rect(
                self.window, RED, pygame.Rect(
                    fruit.position[0], fruit.position[1], GRID_SIZE, GRID_SIZE
                )
            )

        # Desenha os caminhos que a cobra faz em amarelo
        if draw_path:
            path_points = self.discrete_path(self.snake.position, self.optimal_nodes[0])

            for point in path_points:
                pygame.draw.rect(self.window, YELLOW, (point[0], point[1], GRID_SIZE, GRID_SIZE))

        self.show_score_and_time()

        # Atualiza a tela do jogo
        pygame.display.update()

    # Encontra a fruta a direita mais proxima da cobra para iniciar o caminho
    def find_closest_right_coordinate(self, coord, coord_list):
        x, y = coord

        # Filtra as coordenadas a direita
        right_coords = [c for c in coord_list if c[0] > x]

        # Retorna None se nao houver coordenadas a direita
        if not right_coords:
            return None

        # Encontrar a coordenada a direita mais próxima
        closest_right_coord = min(right_coords, key=lambda c: c[0] - x)

        return closest_right_coord

    # Acha um caminho discreto entre dois pontos através do algoritmo de Bresenham's
    def discrete_path(self, start, end):
        # Lista que armazenara o caminho
        path = []
        
        # Coordenadas dos pontos inicial e final
        x1, y1 = start
        x2, y2 = end

        # Diferencas em modulo nas coordenadas x e y
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # Direcoes de incremento/decremento para x e y
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        # Valor inicial do erro
        err = dx - dy

        while True:
            # Adiciona o ponto atual ao caminho
            path.append((x1, y1))

            # Verifica se chegou no ponto final
            if x1 == x2 and y1 == y2:
                break

            # Atualiza o erro
            e2 = 2 * err

            # Ajusta os erros e move os pontos nas direcoes x e y
            if e2 > -dy:
                err -= dy
                x1 += sx

            if e2 < dx:
                err += dx
                y1 += sy

        # Ajusta os pontos para serem multiplos do tamanho da grade
        path = [
            (round(x / GRID_SIZE) * GRID_SIZE, round(y / GRID_SIZE) * GRID_SIZE) for x, y in path
        ]

        i = 0

        # Adiciona pontos verticais ou horizontais a pontos conectados por diagonais
        while i < len(path) - 1:
            xx1, yy1 = path[i]
            xx2, yy2 = path[i + 1]

            if (xx1 != xx2 and yy1 != yy2):
                path.insert(i + 1, (xx1, yy2))

            i += 1

        return path

    # Converte a lista de pontos no caminho e converte em uma lista de direcoes
    def generate_commands(self, path_points):
        commands = []

        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            if x1 < x2:
                commands.append(RIGHT)
            elif x1 > x2:
                commands.append(LEFT)
            elif y1 < y2:
                commands.append(DOWN)
            elif y1 > y2:
                commands.append(UP)

        return commands

    # Define as coordenadas das frutas e armazena em uma tupla
    def set_fruits_coordinates(self):
        fruits_coordinates = [fruit.position for fruit in self.fruits]
        fruits_coordinates = tuple([tuple(fruit) for fruit in fruits_coordinates])

        self.fruits_coordinates = fruits_coordinates

    # Aplica o algoritmo de otimizacao por colonia de formigas para encontrar o melhor caminho
    def ant_colony_optimization(self):
        colony = AntColony(
            self.fruits_coordinates, 
            ant_count=NUMBER_OF_ANTS, 
            iterations=ITERATIONS, 
            pheromone_evaporation_rate=PHEROMONE_EVAPORATION_RATE
        )

        optimal_nodes = colony.get_path()
        optimal_nodes.pop()

        # Armazena a lista contendo o melhor caminho encontrado entre os pontos
        self.optimal_nodes = optimal_nodes

    # Define os parametros para plotar o melhor caminho encontrado pelo algoritmo ACO
    def plot_nodes(self, w=5, h=5):
        for x, y in self.fruits_coordinates:
            plt.plot(x, y, "g.", markersize=15)

        plt.axis("off")
        fig = plt.gcf()
        fig.set_size_inches([w, h])

    # Plota o melhor caminho encontrado pelo algoritmo ACO em um gráfico
    def plot_result(self):
        plt.style.use("dark_background")

        self.plot_nodes()

        for i in range(len(self.optimal_nodes) - 1):
            plt.plot(
                (self.optimal_nodes[i][0], self.optimal_nodes[i + 1][0]),
                (self.optimal_nodes[i][1], self.optimal_nodes[i + 1][1]),
            )

        plt.gca().invert_yaxis()
        plt.show(block=False)
        plt.pause(20)
        plt.close()

    # A partir da lista de direcoes que a cobra deve seguir, inicia o caminho
    def command_snake(self, keys):
        for key in keys:
            # Termina a execucao se o usuario clicar no X ou apertar a tecla 'Esc'
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()

            self.snake.change_direction(key)
            self.snake.update_direction()

            previous_score = self.score

            self.score, fruit_eaten = self.snake.move(self.fruits, self.score, self.last_eat_time)

            # se uma fruta for comida, armazena o tempo que demorou
            if fruit_eaten:
                self.last_eat_time = time.time()

            # se nao tem mais frutas, o jogo acaba
            if not self.fruits:
                self.game_over()

            self.check_collision()
            self.draw_elements()

            # Atualiza os frames do jogo
            self.clock.tick(SNAKE_SPEED)

    # Define os comandos da cobra ate a primeira fruta no inicio do jogo
    def commands_to_first_fruit(self, keys):
        # Encontra a primeira fruta e armazena seu indice
        first_fruit = self.find_closest_right_coordinate(self.snake.position, self.optimal_nodes)
        first_fruit_index = self.optimal_nodes.index(first_fruit)

        # Muda a lista do melhor caminho para que a fruta mais proxima a direita seja a primeira
        self.optimal_nodes.remove(first_fruit)
        self.optimal_nodes = [first_fruit] + self.optimal_nodes[first_fruit_index:] + self.optimal_nodes[:first_fruit_index]

        # Encontra o caminho discreto entre a cobra e a primeira fruta
        path_points = self.discrete_path(self.snake.position, self.optimal_nodes[0])

        # Converte o caminho encontrado em comandos
        keys.extend(self.generate_commands(path_points))

        return keys

    # Define os comandos da cobra da primeira fruta ate todas as outras
    def commands_to_other_fruits(self, keys):
        for i in range(len(self.optimal_nodes) - 1):
            path_points = self.discrete_path(self.optimal_nodes[i], self.optimal_nodes[i + 1])

            keys.extend(self.generate_commands(path_points))

        return keys

    # Roda o jogo
    def run(self, plot_results=False):
        self.set_fruits_coordinates()
        self.ant_colony_optimization()

        if plot_results:
            # Utiliza uma thread separada para plotar os resultados
            plot_thread = threading.Thread(target=self.plot_result)
            plot_thread.start()

        # Lista que armazenara os caminhos que a cobra deve fazer no jogo
        keys = []

        keys = self.commands_to_first_fruit(keys)
        keys = self.commands_to_other_fruits(keys)

        # Define a tela do jogo e inicia os comandos para controlar a cobra
        self.window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        self.command_snake(keys)

if __name__ == "__main__":
    game = Game()
    game.run()
