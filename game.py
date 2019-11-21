import json
import time
import requests
import csv
import sys
import random
import hashlib
from termcolor import colored
import argparse
from cpu import *

parser = argparse.ArgumentParser()

api_key = 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c' # [API_KEY_HERE]

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
        self.rooms = {}

    def init(self):
        self.get_nodes()
        self.get_rooms()

    def get_nodes(self):
        with open("visited.json", "r") as f:
            visited_json = json.loads(f.read())
            self.nodes = {int(key): value for (key, value)
                          in visited_json.items()}

    def get_rooms(self):
        with open("rooms.json") as f:
            rooms = json.loads(f.read())
            rooms_dict = {}
            for r in rooms:
                rooms_dict[r.get('room_id')] = r.get('items')
            self.rooms = rooms_dict

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

    def dft_treasure(self, value_1, value_2):
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

        self.treasure = False
        self.dash = False

    def _set_current_room(self):
        room = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/", headers={
            'Authorization': api_key}).json()
        self.current_room = room
        print("-------------------------")
        print(room)
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

    def _pick_treasure(self):
        if "tiny treasure" in self.current_room.get('items') or "small treasure" in self.current_room.get('items'):
            treasure = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/take/", json={
                                     'name': 'treasure'}, headers={'Authorization': api_key}).json()
            print(colored("You've picked up some treasure", "blue"))
            print("-------------------------")
            time.sleep(20)

    def _dash_map(self):
        path = self.path[1:]

        dash_directions = [[]]
        dash_path = [[]]
        current_index = 0

        for (i, d) in enumerate(self.directions):
            if i == 0:
                dash_directions[current_index].append(d)
                dash_path[current_index].append(path[i])
            elif not len(dash_directions[current_index]) or d == self.directions[i -1]:
                dash_path[current_index].append(path[i])
                dash_directions[current_index].append(d)
            else:
                dash_directions.append([d])
                dash_path.append([path[i]])
                current_index += 1

        return (dash_directions, dash_path)

    def _print_room(self, new_room):
        print(colored("You've in: ", "green"), new_room.get('room_id'))
        print(colored("It's a: ", "green"), new_room.get('title'))
        print(colored("About: ", "green"), new_room.get('description'))
        print(colored("It has these things in: ",
                        "green"), new_room.get('items'))
        print(colored("Additional info: ", "green"),
                new_room.get('messages'))
        print(colored("Current cooldown: ", "green"),
                new_room.get('cooldown'))
        print("-------------------------")

    def go_dash(self):
        (dash_directions, dash_path) = self._dash_map()

        for (i, d) in enumerate(dash_directions):

            if len(d) > 1:
                directions_str = ""
                for (idx, p) in enumerate(dash_path[i]):
                    if not idx == len(dash_path[i]) - 1:
                        directions_str += p + ","
                    else:
                        directions_str += p
                
                new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/dash/", json={
                    "direction": d[0], "num_rooms": str(len(dash_path[i])), "next_room_ids": directions_str }, headers={'Authorization': api_key }).json()  
                self.current_room = new_room
                self._print_room(new_room)
                time.sleep(new_room.get('cooldown'))
            else:
                new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json={
                "direction": d[0], "next_room_id": dash_path[i][0] }, headers={'Authorization': api_key }).json()
                self.current_room = new_room
                self._print_room(new_room)
                time.sleep(new_room.get('cooldown'))         

    def go(self):
        # loop through directions
        # if the next one is the same add it to list if it's not create a new list

        for (i, d) in enumerate(self.directions):
            new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json={
                "direction": d, "next_room_id": self.path[i + 1] }, headers={'Authorization': api_key }).json()
            self.current_room = new_room
            self._print_room(new_room)
            time.sleep(new_room.get('cooldown'))

            if self.treasure:
                self._pick_treasure()

    def hunt_treasure(self):
        value = random.randint(0, 499)
        (directions, path) = self.graph.dft_treasure(
            self.current_room.get('room_id'), value)
        (directions_back, path_back) = self.graph.dft_treasure(value,
                                                               1)
        self.directions = directions + directions_back
        total_path = path + path_back
        self.path = [str(num) for num in total_path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        self.go()

    def go_to_location(self, value):
        (directions, path) = self.graph.dft(
            self.current_room.get('room_id'), int(value))
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", colored(self.directions, "blue"))
        print("Path", colored(self.path, "blue"))
        if self.dash:
            self.go_dash()
        else:
            self.go()

    def sell(self):
        if self.current_room.get("room_id") == 1:
            status = self.status()
            inventory = status.get('inventory')

            for i in range(len(inventory)):
                
                if inventory[i] == 'small treasure' or inventory[i] == 'tiny treasure':
                    result = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/", json={
                                            'name': 'treasure'}, headers={
                                    'Authorization': api_key}).json()
                    time.sleep(result.get('cooldown'))

                    confirmation = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/", json={
                                            'name': 'treasure', "confirm": "yes"}, headers={
                                    'Authorization': api_key}).json()
                    print("-------------------------")
                    print(colored("Treasure sold", "blue"))
                    print(colored(confirmation.get('messages'), "blue"))
                    print("-------------------------")
                    time.sleep(result.get('cooldown'))
            self.status()
        else:
            print(colored("You're not in the shop", "red"))

    def pray(self):
        if self.current_room.get("room_id") == 461:
            result = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/pray/", headers={
                                   'Authorization': api_key}).json()
            print(result)
        else:
            print(colored("You don't seem to be at the shrine", "red"))

    def change_name(self, new_name):
        confirmation = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/change_name/", json={
                                        'name': new_name }, headers={
                                'Authorization': api_key}).json()
        time.sleep(confirmation.get('cooldown'))

        confirmation = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/change_name/", json={
                                        'name': new_name, 'confirm': 'aye' }, headers={
                                'Authorization': api_key}).json()
        print("-------------------------")
        print(confirmation)
        print(colored("You've changed your name to: ", "blue"), new_name)
        print("-------------------------")
        self.status()

    def _check_proof(self, value, difficulty):
        return value[:difficulty] == "0" * difficulty
            
    def _get_proof(self):
        proof = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/", headers={
                                'Authorization': api_key}).json()
        previous_proof = proof.get('proof')
        difficulty = proof.get('difficulty')
        print(proof)
        nonce = 0

        while True:
            nonce += 1
            guess = f'{previous_proof}{nonce}'.encode()
            hash_value = hashlib.sha256(guess).hexdigest()
   
            if self._check_proof(hash_value, difficulty):
                return nonce

    def mine(self):
        proof = self._get_proof()

        result = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/", json={
                                        'proof': proof }, headers={
                                'Authorization': api_key}).json()

        print(result)

    def transmogrify(self, name):
        result = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/transmogrify/", json={
                                        'name': name }, headers={
                                'Authorization': api_key}).json()
        print(result)
        time.sleep(confirmation.get('cooldown'))        

    def examine(self):
        examination = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/examine", json={
                                        'name': 'well' }, headers={
                                'Authorization': api_key}).json()
        code = examination.get('description')
        code = code.split('...')
        code = code[1].split('\n')

        with open('machine-code.txt', 'w') as f:
            for line in code:
                f.write("%s\n" % line)

        cpu = CPU()
        cpu.load()
        cpu.run()

    def status(self):
        current_status = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/status/", headers={
            'Authorization': api_key}).json()

        print("-------------------------")
        print(current_status)
        print(colored("Name: ", "green"), current_status.get("name"))
        print(colored("Gold: ", "yellow"), current_status.get("gold"))
        print(colored("Inventory: ", "green"), current_status.get("inventory"))

        return current_status

    def balance(self):
        balance = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/bc/get_balance/", headers={
            'Authorization': api_key}).json()

        print(balance)

def print_info():
    print(colored("-i", "green"))
    print(colored("Possible arguments:", "blue"))
    print('home')
    print('shop')
    print('shrine')
    print('well')
    print('pray')
    print('move (must also use -r flag)')
    print('pirates')
    print('trans')
    print('hunt')
    print('status')
    print('examine')
    print('balance')
    print('mine\n')
    print(colored('-r', "green"))
    print(colored("Sets a room (to use with move)", "blue"))
    print("E.g. -i move -r 210\n")
    print(colored('-d', "green"))
    print(colored("Sets dash to true\n", "blue"))
    print(colored('-t', "green"))
    print(colored("Sets treasure to true\n", "blue"))

def call_methods(m, arg):

    rooms = {
        'home': 0,
        'shop': 1,
        'shrine': 461,
        'well': 55,
        'pray': None,
        'move': arg.room,
        'pirates': 467,
        'trans': 495,
        'hunt': None,
        'status': None,
        'examine': None,
        'mine': None,
        'sell': None,
        'balance': None,
        'transmog': arg.item
    }

    methods = {
        'home': m.go_to_location,
        'shop': m.go_to_location,
        'shrine': m.go_to_location,
        'well': m.go_to_location,
        'pray': m.pray,
        'move': m.go_to_location,
        'pirates': m.go_to_location,
        'trans': m.go_to_location,
        'hunt': m.hunt_treasure,
        'status': m.status,
        'examine': m.examine,
        'mine': m.mine,
        'sell': m.sell,
        'balance': m.balance
    }

    x = rooms[arg.instruction]
    if x:
        methods[arg.instruction](x)
    else:
        methods[arg.instruction]()

def start():
    parser.add_argument("-i", "--instruction", help="Give instruction")
    parser.add_argument("-d", action='store_true', help="Set dash")
    parser.add_argument("-r", "--room", help="Choose room")
    parser.add_argument("-t", action='store_true', help="Collect treasure")
    parser.add_argument("-item", "--item", help="Select Item")
    parser.add_argument("-help", action='store_true')

    args = parser.parse_args()

    if len(sys.argv) < 2:
        return print(colored("No arguments, enter -help flag to see options", "red"))

    if args.help:
        return print_info()

    m = Mover()
    m.init()

    if args.t:
        m.treasure = True

    if args.d:
        m.dash = True

    call_methods(m, args)

start()
