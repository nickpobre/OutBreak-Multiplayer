import socket
from _thread import *
import pickle
from settings import WORLD_WIDTH, WORLD_HEIGHT
from Modules.player import Survivor, Zombie
from Modules.point import Point
import random

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

players = {}
points = [Point() for _ in range(20)] 

def threaded_client(conn, player_id):
    conn.send(pickle.dumps(player_id))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player_id] = data

            if not data:
                print("Disconnected")
                break
            else:
                reply = {
                    'players': players,
                    'points': points
                }

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

current_player = 0

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    if current_player % 2 == 0:
        players[current_player] = Survivor(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT), 10)
    else:
        players[current_player] = Zombie(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT), 10)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1
