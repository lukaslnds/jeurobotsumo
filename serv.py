import socket
import threading
import pickle  # Pour envoyer des objets Python entre serveur et client
import math  # Pour calculer la distance

# Paramètres de l'arène
ARENA_WIDTH = 800
ARENA_HEIGHT = 600
ARENA_CENTER = (ARENA_WIDTH // 2, ARENA_HEIGHT // 2)  # Centre de l'arène
ARENA_RADIUS = 250  # Rayon de l'arène
ROBOT_SIZE = 50  # Taille des robots pour la collision
PUSH_FORCE = 10  # Augmentation de la force de poussée pour un effet visible

clients = []
robots = {1: {"x": 200, "y": 300}, 2: {"x": 600, "y": 300}}  # Positions initiales

def check_collision(new_x, new_y, robot_id):
    """Vérifie si un déplacement cause une collision."""
    other_robot_id = 1 if robot_id == 2 else 2
    other_robot = robots[other_robot_id]

    # Vérifier les limites de l'arène
    if not (0 <= new_x <= ARENA_WIDTH - ROBOT_SIZE and 0 <= new_y <= ARENA_HEIGHT - ROBOT_SIZE):
        return False, None

    # Vérifier la collision avec l'autre robot
    if (abs(new_x - other_robot["x"]) < ROBOT_SIZE) and (abs(new_y - other_robot["y"]) < ROBOT_SIZE):
        return True, other_robot_id  # Collision détectée avec l'autre robot

    return False, None

def resolve_collision(robot_id, other_robot_id):
    """Pousse l'autre robot en cas de collision de manière progressive pour éviter les oscillations."""
    r1 = robots[robot_id]
    r2 = robots[other_robot_id]

    dx = r2["x"] - r1["x"]
    dy = r2["y"] - r1["y"]

    distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)  # Évite la division par zéro

    # Normalisation du vecteur directionnel
    push_x = (dx / distance) * PUSH_FORCE
    push_y = (dy / distance) * PUSH_FORCE

    # Appliquer une poussée progressive, mais éviter les petits mouvements successifs
    if abs(push_x) > 0.1 or abs(push_y) > 0.1:  # Seuil pour empêcher les petites oscillations
        new_x = r2["x"] + push_x
        new_y = r2["y"] + push_y

        # Appliquer la poussée uniquement si ça reste dans l'arène
        if 0 <= new_x <= ARENA_WIDTH - ROBOT_SIZE:
            robots[other_robot_id]["x"] = new_x
        if 0 <= new_y <= ARENA_HEIGHT - ROBOT_SIZE:
            robots[other_robot_id]["y"] = new_y

def is_outside_arena(robot_id):
    """Vérifie si le robot est sorti de l'arène."""
    robot = robots[robot_id]
    distance_from_center = math.sqrt((robot["x"] - ARENA_CENTER[0]) ** 2 + (robot["y"] - ARENA_CENTER[1]) ** 2)
    return distance_from_center > ARENA_RADIUS

def handle_client(client_socket, addr, robot_id):
    """Gère la communication avec un client."""
    print(f"[NEW CONNECTION] {addr} connected as Robot {robot_id}.")
    # Envoyer au client son numéro de robot (1 ou 2)
    client_socket.send(pickle.dumps(robot_id))

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            # Désérialiser les données envoyées par le client
            robot_data = pickle.loads(data)
            new_x, new_y = robot_data["x"], robot_data["y"]

            # Vérifier la collision
            collision, other_robot_id = check_collision(new_x, new_y, robot_id)
            if collision:
                resolve_collision(robot_id, other_robot_id)  # Pousser l'autre robot
            else:
                robots[robot_id] = {"x": new_x, "y": new_y}

            # Vérifier si un robot est sorti de l'arène et afficher le gagnant
            if is_outside_arena(robot_id):
                winner_id = 1 if robot_id == 2 else 2
                print(f"Robot {winner_id} a gagné !")
                break  # Quitter la boucle après avoir trouvé un gagnant

            # Envoyer la mise à jour à tous les clients
            game_state = {
                "robot1": robots[1],
                "robot2": robots[2],
            }

            for client in clients:
                client.send(pickle.dumps(game_state))

        except:
            print(f"[DISCONNECTED] {addr} disconnected.")
            clients.remove(client_socket)
            client_socket.close()
            break

def start_server():
    """Démarre le serveur et accepte les connexions."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(2)  # Limité à 2 joueurs
    print("Server listening on port 8080...")

    robot_id = 1  # On assigne 1 au premier joueur, 2 au deuxième

    while len(clients) < 2:
        client_socket, addr = server.accept()
        clients.append(client_socket)

        threading.Thread(target=handle_client, args=(client_socket, addr, robot_id)).start()
        robot_id += 1

if __name__ == "__main__":
    start_server()
