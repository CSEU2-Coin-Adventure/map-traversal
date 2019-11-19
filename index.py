import pymongo
import requests
import time
import json

from pymongo import MongoClient
client = MongoClient("mongodb://mattshardman:mappymap12@ds039211.mlab.com:39211/cs_map_project?retryWrites=false")

db = client.cs_map_project
posts = db.rooms
graph = db.rooms_graph

opposites = {
    'n': 's',
    'e': 'w',
    's': 'n',
    'w': 'e'
}

rooms = {}

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.insert(0, value)

    def pop(self):
        if self.length():
            return self.stack.pop(0)
        else:
            return None

    def length(self):
        return len(self.stack)

def GetVisited():
    with open("visited.json", "r") as f:
        return json.loads(f.read())

visited_loaded = GetVisited()

def traverse_map():
    # create path array
    path = []
    # call server and get json
    new_room = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/", headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
    print(new_room)
    result = posts.insert_one(new_room)
    print('One post: {0}'.format(result.inserted_id))

    time.sleep(new_room.get('cooldown'))
    # create stack
    stack = Stack()
    # create hansel stack
    hansel_stack = Stack()
    # create direction_stack
    direction_stack = Stack()
    # create visited dict
    visited = visited_loaded or {}
    # save previous room
    previous_room = None
    # push the first room onto the stack
    stack.push(new_room)
    # loop while stack is not empty
    while stack.length() or hansel_stack.length():
        if stack.length():
            # pop the stack and set to room
            room = stack.pop()
            rooms[room.get('room_id')] = room
            # pop direction stack
            direction_from = direction_stack.pop()
            # if the room has not been visited before or 
            if room.get('room_id') not in visited or '?' in visited[room.get('room_id')].values():
                # create exits array
                exits = room.get('exits')
                # if room number is not already in rooms add it
                if room.get('room_id') not in visited:
                    room_exits = {}
                    for r in exits:
                        room_exits[r] = '?'
                    # store response in dict (for now) with room_id as key and all info as value
                    visited[room.get('room_id')] = room_exits
                    # save visited to json
                    with open('visited.json', 'w') as outfile:
                        json.dump(visited, outfile)
                # add direction to path array and opposite to hansel stack also add room number that goes with that direction to stack
                if direction_from != None and previous_room != None:
                    # add item to visited array with exists as value room number as key
                    path.append(direction_from)
                    hansel_stack.push((opposites[direction_from], previous_room))
                    # set direction to previous room number for current room
                    visited[room.get('room_id')][opposites[direction_from]] = previous_room
                    visited[previous_room][direction_from] = room.get('room_id')
                    # save visited to file
                    with open('visited.json', 'w') as outfile:
                        json.dump(visited, outfile)
                # loop through exits array on item
                for (d, i) in visited[room.get('room_id')].items():
                    # if unexplored add to stack
                    if i == '?':
                        # call the api with each of the directions
                        new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json = { 'direction': d }, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c' }).json()
                        print(new_room)
                        
                        time.sleep(new_room.get('cooldown'))

                        if 'tiny treasure' in new_room.get('items'):
                            treasure = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/take/", json = { 'name': 'treasure' }, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c' }).json()
                            print(treasure)
                            time.sleep(20)

                        print(new_room.get('errors'))
                        if len(new_room.get('errors')):
                            time.sleep(20)

                        result = posts.insert_one(new_room)
                        print('One post: {0}'.format(result.inserted_id))
                        
                        # add room to stack
                        stack.push(new_room)
                        direction_stack.push(d)
                        break

                previous_room = room.get('room_id')
                    
        # else 
            # pop hansel stack and travel this direction
        else:
            (d, r) = hansel_stack.pop()
            print("return_direction", d, "return room", r)
            # go in direction of hansel_stack
            new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json = { 'direction': d }, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
            print(new_room)
            if len(new_room.get('errors')):
                time.sleep(20)
            time.sleep(new_room.get('cooldown'))
            # add direction to path
            path.append(d)
            # push new_room on to stack
            stack.push(new_room)

    return visited

visited = traverse_map()

result = graph.insert_one(visited)
print('Added all visited: {0}'.format(result.inserted_id))
