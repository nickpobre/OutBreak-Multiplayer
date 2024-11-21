# settings.py
import pygame

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH = 800
HEIGHT = 400

# Configurações do mundo
WORLD_WIDTH = 8000
WORLD_HEIGHT = 6000

# Parâmetros do jogo
TIME_LIMIT = 450  # Tempo limite em segundos
POINTS_PER_ITEM = 1
RESPAWN_TIME = 150  # Tempo de respawn de pontos em milissegundos
GRID_SIZE = 40
MIN_ZOOM = 1.7
MAX_ZOOM_OUT = 0.3
MAX_PLAYER_SIZE = 600

# Definição de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)

# Configurações de fonte
MUSIC_PATH = "Resources/Sounds/Outbreak.mp3"
FONT_PATH = "Resources/Fonts/Outbreak.ttf"
FONT = pygame.font.Font(None, 36)
DEFAULT_FONT_SIZE = 36
