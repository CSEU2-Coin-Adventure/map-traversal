import json
import time
import requests


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
        self.rooms = []
        self.current_room = None

    def _set_current_room(self):
        room = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/", headers={
            'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
        self.current_room = room
        print("Current room: ", self.current_room)

    def _get_rooms(self):
        pass

    def init(self):
        print('Initiated')
        self._set_current_room()
        g = Graph()
        g.init()
        self.graph = g

    def go(self):
        for (i, d) in enumerate(self.directions):
            new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json={
                'direction': d}, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
            print(new_room)
            time.sleep(new_room.get('cooldown'))

    def hunt_treasure(self):
        pass

    def go_home(self):
        (directions, path) = self.graph.dft(self.current_room.get('room_id'), 0)
        self.directions = directions
        self.path = [str(num) for num in path]
        print("Directions: ", self.directions)
        print("Path", self.path)
    
    def go_to_shop(self):
        (directions, path) = self.graph.dft(self.current_room.get('room_id'), 1)
        self.path = [str(num) for num in path]
        print("Directions: ", self.directions)
        print("Path", self.path)

m = Mover()
m.init()
m.go_home()
