import pygame
import socket
import pickle  # Pour la sérialisation des données

# Paramètres du client
server_ip = "192.168.1.78"  # Remplace par l'IP correcte du serveur
server_port = 8080

# Initialisation de Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client - Robot Sumo")

# Chargement des images
robot_red_img = pygame.image.load("robot_red.png")
robot_blue_img = pygame.image.load("robot_blue.png")

# Couleurs
WHITE = (255, 255, 255)
BROWN_DARK = (100, 70, 50)  # Marron foncé
BROWN_LIGHT = (160, 120, 90)  # Marron clair
BLACK = (0, 0, 0)

# Position initiale des robots
ARENA_CENTER = (WIDTH // 2, HEIGHT // 2)

class Robot:
    """Classe représentant un robot dans l'arène."""
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (50, 50))  # Redimensionne l'image
        self.speed = 5  # Vitesse du robot

    def move(self, dx, dy):
        """Déplace le robot selon les entrées du joueur."""
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, win):
        """Affiche le robot sur l'écran."""
        win.blit(self.image, (self.x, self.y))

# Fonction pour envoyer les données du robot au serveur
def send_data_to_server(robot_id, robot):
    """Envoie les données du robot au serveur."""
    try:
        client_socket.send(pickle.dumps({"robot_id": robot_id, "x": robot.x, "y": robot.y}))  
    except:
        print("Erreur lors de l'envoi des données au serveur.")

def receive_data_from_server():
    """Recevoir les données du serveur pour mettre à jour l'état du jeu."""
    try:
        data = client_socket.recv(1024)
        if data:
            return pickle.loads(data)  # Désérialiser les données reçues
    except:
        return None

# Fonction pour dessiner l'arène
def draw_arena():
    """Dessine l'arène en forme de cercle et le fond en damier."""
    # Fond en damier marron clair et foncé
    tile_size = 50
    for x in range(0, WIDTH, tile_size):
        for y in range(0, HEIGHT, tile_size):
            # Alternance des couleurs du damier
            color = BROWN_LIGHT if (x + y) // tile_size % 2 == 0 else BROWN_DARK
            pygame.draw.rect(WIN, color, pygame.Rect(x, y, tile_size, tile_size))

    # Dessiner le dohyo (cercle noir avec bord blanc)
    pygame.draw.circle(WIN, BLACK, ARENA_CENTER, 250)  # Cercle noir
    pygame.draw.circle(WIN, WHITE, ARENA_CENTER, 255, 5)  # Bord blanc

# Boucle principale du jeu
def game_loop(robot_id):
    run = True
    clock = pygame.time.Clock()
    
    # Attribution des rôles
    if robot_id == 1:
        robot = Robot(ARENA_CENTER[0] - 100, ARENA_CENTER[1], robot_red_img)
        opponent = Robot(ARENA_CENTER[0] + 100, ARENA_CENTER[1], robot_blue_img)
    else:
        robot = Robot(ARENA_CENTER[0] + 100, ARENA_CENTER[1], robot_blue_img)
        opponent = Robot(ARENA_CENTER[0] - 100, ARENA_CENTER[1], robot_red_img)

    while run:
        clock.tick(60)  # 30 FPS pour correspondre au serveur
        WIN.fill(WHITE)

        # Dessin de l'arène (fond et cercle)
        draw_arena()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Gestion des touches pour déplacer le robot
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            robot.move(0, -1)
        if keys[pygame.K_s]:
            robot.move(0, 1)
        if keys[pygame.K_q]:
            robot.move(-1, 0)
        if keys[pygame.K_d]:
            robot.move(1, 0)

        # Envoi des données du robot au serveur
        send_data_to_server(robot_id, robot)

        # Mise à jour avec les données reçues du serveur
        game_data = receive_data_from_server()
        if game_data:
            robot.x = game_data[f"robot{robot_id}"]["x"]
            robot.y = game_data[f"robot{robot_id}"]["y"]
            
            opponent.x = game_data[f"robot{3 - robot_id}"]["x"]
            opponent.y = game_data[f"robot{3 - robot_id}"]["y"]

        # Affichage des robots
        robot.draw(WIN)
        opponent.draw(WIN)
        pygame.display.update()

    pygame.quit()
    client_socket.close()

# Lancer le client
if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("Connecté au serveur !")
        
        # Recevoir l'ID attribué par le serveur
        robot_id = pickle.loads(client_socket.recv(1024))  
        print(f"Je suis Robot {robot_id}")
        
        game_loop(robot_id)
    except:
        print("Impossible de se connecter au serveur.")
