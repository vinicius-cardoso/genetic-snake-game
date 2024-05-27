import random
from game_settings import *

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
