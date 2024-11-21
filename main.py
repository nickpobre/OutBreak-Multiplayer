import pygame
from settings import WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, RESPAWN_TIME, TIME_LIMIT, MAX_ZOOM_OUT, MAX_PLAYER_SIZE, MIN_ZOOM, POINTS_PER_ITEM, WHITE, BLACK
from Modules.ui import menu, settings_menu, character_selection
from Modules.player import Survivor, Zombie
from Modules.star import create_star_field, draw_star_field
from Modules.point import Point
from Modules.particle import create_explosion
from Modules.camera import draw_grid, display_score
import socket
import pickle

class Network:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

# Função principal do jogo
def main():
    pygame.init()
    pygame.mixer.init() 
    
    pygame.mixer.music.load("Resources/Sounds/Outbreak.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
     
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Outbreak")
    FONT = pygame.font.Font(None, 36)

    star_field = create_star_field()
    
    running = True
    mode_selected = False
    player = None
    points = []
    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, RESPAWN_TIME)
    
    start_ticks = pygame.time.get_ticks()
    global particles
    particles = []

    game_over = False
    victory_message = ""

    network = Network("localhost", 5555) 
    player_id = network.connect()

    while running:
        screen.fill((0, 0, 0))
        
        if player:
            game_state = network.send(player.serialize())
            players = game_state['players']
            points = [Point.deserialize(p) if isinstance(p, dict) else p for p in game_state['points']]

            if isinstance(players[player_id], dict):
                if players[player_id]['type'] == 'Survivor':
                    player = Survivor.deserialize(players[player_id])
                else:
                    player = Zombie.deserialize(players[player_id])
            else:
                player = players[player_id]
        else:
            game_state = None
            players = {}
            points = []

        if not mode_selected and not game_over:
            survival_tdm_button, settings_button, horde_button, flag_button = menu(screen, star_field)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if survival_tdm_button.collidepoint(mouse_pos):
                        mode_selected = "survival_tdm"
                    elif settings_button.collidepoint(mouse_pos):
                        mode_selected = "settings"
            continue

        if mode_selected == "settings":
            back_button = settings_menu(screen, star_field)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        mode_selected = False
            continue

        if mode_selected == "survival_tdm":
            survivor_button, zombie_button, back_button = character_selection(screen, star_field)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if survivor_button.collidepoint(mouse_pos):
                        player = Survivor(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, 10)
                        mode_selected = "survival"
                        game_over = False
                        pygame.mixer.music.stop()
                        start_ticks = pygame.time.get_ticks()
                    elif zombie_button.collidepoint(mouse_pos):
                        player = Zombie(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, 10)
                        mode_selected = "zombie"
                        game_over = False
                        pygame.mixer.music.stop()
                        start_ticks = pygame.time.get_ticks()
                    elif back_button.collidepoint(mouse_pos):
                        mode_selected = False
            continue

        if game_over:
            draw_star_field(screen, star_field)
            
            message_surface = FONT.render(victory_message, True, WHITE)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(message_surface, message_rect)

            back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
            mouse_pos = pygame.mouse.get_pos()
            
            if back_button.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (200, 50, 50), back_button, border_radius=10)
                pygame.draw.rect(screen, WHITE, back_button, 3, border_radius=10)
            else:
                pygame.draw.rect(screen, (255, 0, 0), back_button, border_radius=10)
                pygame.draw.rect(screen, BLACK, back_button, 3, border_radius=10)
            
            back_text = FONT.render("Voltar ao Menu", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            screen.blit(back_text, back_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        mode_selected = False
                        game_over = False
                        pygame.mixer.music.play(-1)
            pygame.display.flip()
            clock.tick(60)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == spawn_event:
                points.append(Point())
        
        if player:
            zoom = max(MAX_ZOOM_OUT, MIN_ZOOM - 0.005 * min(player.size, MAX_PLAYER_SIZE))
            camera_x = max(0, min(WORLD_WIDTH - WIDTH / zoom, player.x - WIDTH / (2 * zoom)))
            camera_y = max(0, min(WORLD_HEIGHT - HEIGHT / zoom, player.y - HEIGHT / (2 * zoom)))

            player.move(camera_x, camera_y, zoom)
            
            draw_grid(screen, camera_x, camera_y, zoom)
            draw_star_field(screen, star_field)

            for pid, player_data in players.items():
                if isinstance(player_data, dict):
                    if player_data['type'] == 'Survivor':
                        player_obj = Survivor.deserialize(player_data)
                    else:
                        player_obj = Zombie.deserialize(player_data)
                else:
                    player_obj = player_data
                player_obj.draw(screen, camera_x, camera_y, zoom)

            for point in points:
                if isinstance(point, dict):
                    point = Point.deserialize(point)
                point.draw(screen, camera_x, camera_y, zoom)
                if (player.x - point.x)**2 + (player.y - point.y)**2 < (player.size + point.size)**2:
                    if player.size < MAX_PLAYER_SIZE:
                        growth_factor = POINTS_PER_ITEM / (1 + player.size * 0.05)
                        player.size += growth_factor
                        player.points += POINTS_PER_ITEM
                        create_explosion(particles, point.x, point.y, point.color)

            for particle in particles[:]:
                particle.update()
                particle.draw(screen, camera_x, camera_y, zoom)
                if particle.lifetime <= 0:
                    particles.remove(particle)

            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            minutes = (TIME_LIMIT - int(elapsed_time)) // 60
            seconds = (TIME_LIMIT - int(elapsed_time)) % 60
            timer_text = FONT.render(f"Tempo: {minutes:02}:{seconds:02}", True, WHITE)
            screen.blit(timer_text, (10, 10))

            display_score(screen, player)

            if game_state.get('game_over'):
                game_over = True
                victory_message = game_state['victory_message']

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

