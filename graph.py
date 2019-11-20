import json
import time
import requests
import csv
import sys
from termcolor import colored

class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.length():
            return self.queue.pop(0)
        else:
            return None

    def length(self):
        return len(self.queue)


class Graph:
    def __init__(self):
        self.current_node = None
        self.nodes = {}

    def init(self):
        self.get_nodes()

    def get_nodes(self):
        with open("visited.json", "r") as f:
            visited_json = json.loads(f.read())
            self.nodes = {int(key): value for (key, value)
                          in visited_json.items()}

    def dft(self, value_1, value_2):
        q = Queue()
        directions_q = Queue()
        q.enqueue([value_1])
        directions_q.enqueue([])

        while q.length():
            path = q.dequeue()
            directions = directions_q.dequeue()
            room = path[-1]

            if room == value_2:
                return (directions, path)

            for (d, n) in self.nodes[room].items():
                if n != '?' and n not in path:
                    new_path = list(path)
                    new_directions = list(directions)

                    new_path.append(n)
                    new_directions.append(d)

                    q.enqueue(new_path)
                    directions_q.enqueue(new_directions)


class Mover:
    def __init__(self):
        self.graph = None
        self.path = []
        self.directions = []
        self.rooms = {}
        self.current_room = None

    def _set_current_room(self):
        room = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/", headers={
            'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
        self.current_room = room
        print("-------------------------")
        print(colored("You've in: ", "green"), room.get('room_id'))
        print(colored("It's a: ", "green"), room.get('title'))
        print(colored("About: ", "green"), room.get('description'))
        print(colored("Additional info: ", "green"), room.get('messages'))
        print(colored("Current cooldown: ", "green"), room.get('cooldown'))
        print("-------------------------")
        time.sleep(room.get('cooldown'))

    def _set_rooms(self):
        pass

    def init(self):
        print("-------------------------")
        print(colored('Initiated', "yellow"))
        self._set_current_room()
        g = Graph()
        g.init()
        self.graph = g

    def go(self):
        for (i, d) in enumerate(self.directions):
            new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json={
                'direction': d}, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
            print(colored("You've in: ", "green"), new_room.get('room_id'))
            print(colored("It's a: ", "green"), new_room.get('title'))
            print(colored("About: ", "green"), new_room.get('description'))
            print(colored("Additional info: ", "green"), new_room.get('messages'))
            print(colored("Current cooldown: ", "green"), new_room.get('cooldown'))
            print("-------------------------")
            time.sleep(new_room.get('cooldown'))

    def hunt_treasure(self):
        pass

    def go_home(self):
        (directions, path) = self.graph.dft(
            self.current_room.get('room_id'), 0)
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        self.go()

    def go_to_shop(self):
        (directions, path) = self.graph.dft(
            self.current_room.get('room_id'), 1)
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        self.go()

    def go_to_shrine(self):
        (directions, path) = self.graph.dft(
            self.current_room.get('room_id'), 461)
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        self.go()

    def go_to_location(self, value):
        (directions, path) = self.graph.dft(
            self.current_room.get('room_id'), value)
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        self.go()

    def pray(self):
        if self.current_room.get("room_id") == 461:
           result = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/pray/", headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
           print(result)
        else:
            print(colored("You don't seem to be at the shrine", "red"))

def print_instructions():
    print(colored("\nYou need to enter a command.\n", "red"))
    print("Enter one of the following:\n")
    print("     -", colored("home", "green"), " - this will take you back to 0 from your current location")
    print("     -", colored("shop", "green"), " - this will take you to the shop from your current location")
    print("     -", colored("shrine", "green"), " - this will take you to the shrine from your current location")
    print("     -", colored("pray", "green"), "- if you are at the shrine you will play")
    print("     -", colored("location <room number>", "green"), "- this will take you to a room of your choice")


def start(inputs):
    m = Mover()
    m.init()
    if len(inputs) < 2:
        print_instructions()
    elif inputs[1] == "home":
        text = input("Are you sure you want to go home? [y or n]\n")
        if text == "y":
            print("Going home")
            m.go_home()
        elif text == "n":
            print("Ok")
        else:
            print("enter y or n")
    elif inputs[1] == "shop":
        text = input("Are you sure you want to go to the shop? [y or n]\n")
        if text == "y":
            print("Going to the shop")
            m.go_to_shop()
        elif text == "n":
            print("Ok")
        else:
            print("enter y or n")
    elif inputs[1] == "shrine":
        text = input("Are you sure you want to go to the shrine? [y or n]\n")
        if text == "y":
            print("Going to the shrine")
            m.go_to_shrine()
        elif text == "n":
            print("Ok")
        else:
            print("enter y or n")
    elif inputs[1] == "pray":
        text = input("Are you sure you want to to pray? [y or n]\n")
        if text == "y":
            print("Time to pray")
            m.pray()
        elif text == "n":
            print("Ok")
        else:
            print("enter y or n")
    elif inputs[1] == "location" or inputs[1] == "loco":
        if len(inputs) > 2:
            text = input(f"Are you sure you want to go to {inputs[2]}? [y or n]\n")
            if text == "y":
                print("Time to pray")
                m.go_to_location(inputs[2])
            elif text == "n":
                print("Ok")
            else:
                print("enter y or n")
        else: 
            print(colored("You need to enter a room number", "red"))
    else:
        print_instructions()

start(sys.argv)
