# Jeu de Sumo Robotique en Python

Ce projet est une simulation d’un combat de sumo entre robots autonomes, réalisée lors d’un projet tuteuré à l’IUT d’Évry Val d’Essonne.

Les robots s’affrontent dans une arène circulaire, avec gestion des collisions et tentative de pousser l’adversaire hors du ring.

---

## Fonctionnalités

- Combat entre robots autonomes  
- Gestion des collisions  
- Interface graphique avec Pygame  
- Mode multi-joueur en réseau via sockets  

---

## Prérequis

- Python 3.x installé  
- Librairie Pygame  

---

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/lukaslnds/jeurobotsumo.git
cd jeurobotsumo

```
2. Installer pygame
```pip install pygame```
3. Lancer sur la machine serveur le fichier ```serv.py```
4. Lancer le jeu sur les machines clients avec le fichier ```client.py```
