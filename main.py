import pygame
import math
import time
import asyncio

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Sumo")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (100, 70, 50)
LIGHT_BROWN = (160, 120, 90)

# Paramètres de l'arène
ARENA_CENTER = (WIDTH // 2, HEIGHT // 2)
INITIAL_ARENA_RADIUS = 250
SHRINK_RATE = 4  # 📉 Zone rétrécit lentement (~42s)

# Paramètres des robots
ROBOT_RADIUS = 35  # 📏 Ajusté pour des sprites 70x70
ROBOT_SPEED = 2

# Chargement des sprites (70x70 pixels)
robot_red_img = pygame.image.load("robot_red.png")
robot_blue_img = pygame.image.load("robot_blue.png")

robot_red_img = pygame.transform.scale(robot_red_img, (70, 70))
robot_blue_img = pygame.transform.scale(robot_blue_img, (70, 70))


class Robot:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.alive = True

    def draw(self, win):
        if self.alive:
            win.blit(self.sprite, (int(self.x) - ROBOT_RADIUS, int(self.y) - ROBOT_RADIUS))  # Centrage ajusté

    def move(self, dx, dy):
        if self.alive:
            self.x += dx * ROBOT_SPEED
            self.y += dy * ROBOT_SPEED

    def check_collision(self, other):
        distance = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        return distance < 2 * ROBOT_RADIUS

    def resolve_collision(self, other):
        if self.check_collision(other):
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance == 0:
                return

            overlap = 2 * ROBOT_RADIUS - distance
            push_x = (dx / distance) * (overlap / 2)
            push_y = (dy / distance) * (overlap / 2)

            self.x += push_x
            self.y += push_y
            other.x -= push_x
            other.y -= push_y

    def check_arena_boundary(self, arena_radius):
        distance_from_center = math.sqrt((self.x - ARENA_CENTER[0]) ** 2 + (self.y - ARENA_CENTER[1]) ** 2)
        if distance_from_center + ROBOT_RADIUS > arena_radius:
            self.alive = False


def draw_checkerboard(win):
    """ Dessine un sol en damier pour un effet esthétique """
    tile_size = 50
    for row in range(HEIGHT // tile_size + 1):
        for col in range(WIDTH // tile_size + 1):
            color = DARK_BROWN if (row + col) % 2 == 0 else LIGHT_BROWN
            pygame.draw.rect(win, color, (col * tile_size, row * tile_size, tile_size, tile_size))


def draw_arena(win, radius):
    """ Dessine l'arène : Cercle noir avec un contour blanc """
    pygame.draw.circle(win, BLACK, ARENA_CENTER, int(radius))  # Cercle noir
    pygame.draw.circle(win, WHITE, ARENA_CENTER, int(radius), 5)  # Contour blanc épais


def game_over_screen(win, winner, duration):
    """ Affiche l'écran de fin du jeu avec l'option de rejouer ou quitter """
    font = pygame.font.SysFont(None, 40)  # Texte plus petit
    text = font.render(f"{winner} a gagné !", True, WHITE)
    
    # Créer une surface semi-transparente
    transparent_surface = pygame.Surface((WIDTH, HEIGHT))
    transparent_surface.set_alpha(180)  # Transparence à 180 (sur 255)
    transparent_surface.fill(WHITE)  # Remplir avec la couleur blanche

    # Dessiner le fond semi-transparent
    win.blit(transparent_surface, (0, 0))
    
    # Affichage du texte
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

    replay_text = font.render("Appuyez sur 'R' pour rejouer", True, WHITE)
    win.blit(replay_text, (WIDTH // 2 - replay_text.get_width() // 2, HEIGHT // 2 + 20))

    # Affichage du temps écoulé
    time_text = font.render(f"Temps : {duration:.2f} secondes", True, WHITE)
    win.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.update()

    # Enregistrer l'historique dans un fichier texte
    with open("historique_partie.txt", "a") as file:
        from datetime import datetime
        now = datetime.now()
        file.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Victoire : {winner} - Temps : {duration:.2f} secondes\n")


def reset_game(robot1, robot2):
    """Réinitialise les robots et l'arène"""
    robot1.x, robot1.y = ARENA_CENTER[0] - 100, ARENA_CENTER[1]
    robot2.x, robot2.y = ARENA_CENTER[0] + 100, ARENA_CENTER[1]
    robot1.alive = True
    robot2.alive = True
    return pygame.time.get_ticks(), time.time()  # Réinitialiser les timers


async def game_loop():
    run = True
    clock = pygame.time.Clock()

    robot1 = Robot(ARENA_CENTER[0] - 100, ARENA_CENTER[1], robot_red_img)
    robot2 = Robot(ARENA_CENTER[0] + 100, ARENA_CENTER[1], robot_blue_img)

    arena_radius = INITIAL_ARENA_RADIUS
    start_ticks = pygame.time.get_ticks()
    game_start_time = time.time()  # Temps de départ du jeu

    while run:
        clock.tick(60)
        WIN.fill(WHITE)

        # Dessiner le sol en damier
        draw_checkerboard(WIN)

        # Réduction lente de l'arène (~42s)
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        if robot1.alive and robot2.alive:  # Seulement réduire si les robots sont toujours en jeu
            arena_radius = max(50, INITIAL_ARENA_RADIUS - SHRINK_RATE * seconds)

        draw_arena(WIN, arena_radius)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if robot1.alive:
            if keys[pygame.K_w]:
                robot1.move(0, -1)
            if keys[pygame.K_s]:
                robot1.move(0, 1)
            if keys[pygame.K_a]:
                robot1.move(-1, 0)
            if keys[pygame.K_d]:
                robot1.move(1, 0)

        if robot2.alive:
            if keys[pygame.K_UP]:
                robot2.move(0, -1)
            if keys[pygame.K_DOWN]:
                robot2.move(0, 1)
            if keys[pygame.K_LEFT]:
                robot2.move(-1, 0)
            if keys[pygame.K_RIGHT]:
                robot2.move(1, 0)

        # Vérification des collisions et rebond
        robot1.resolve_collision(robot2)

        # Vérification des limites de l'arène
        robot1.check_arena_boundary(arena_radius)   
        robot2.check_arena_boundary(arena_radius)

        # Affichage des robots
        robot1.draw(WIN)
        robot2.draw(WIN)

        # Affichage du chronomètre
        elapsed_time = time.time() - game_start_time
        font = pygame.font.SysFont(None, 30)
        time_text = font.render(f"Temps : {elapsed_time:.2f}s", True, WHITE)
        WIN.blit(time_text, (10, 10))

        pygame.display.update()

        # Fin du jeu si un des robots est éliminé
        if not robot1.alive or not robot2.alive:
            winner = "Le robot rouge" if not robot2.alive else "Le robot bleu"
            game_over_screen(WIN, winner, elapsed_time)
            while True:  # Mettre en pause jusqu'à ce que l'utilisateur choisisse
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            start_ticks, game_start_time = reset_game(robot1, robot2)
                            break  # Rejouer
                else:
                    await asyncio.sleep(0.01)  # Yield control
                    continue
                break

        await asyncio.sleep(0.01)  # Yield control


# Vérifier si une boucle d'événements est déjà en cours
if __name__ == "__main__":
    try:
        # Si un événement est déjà en cours, exécuter la boucle asyncio sans asyncio.run()
        asyncio.get_event_loop().create_task(game_loop())
    except RuntimeError:
        # Si l'on est dans un environnement comme Jupyter, l'événement est déjà en cours
        asyncio.run(game_loop())
