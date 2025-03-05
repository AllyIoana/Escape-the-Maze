from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager
from PIL import Image
from io import BytesIO
import asyncio
import timeit

import numpy as np
import sys
import time
sys.path.append('../maze_generator/random_generation')
import random_generation


class Agent:
    def __init__(self, uuid, position):
        self.uuid = uuid
        self.position = position
        self.move_history = [self.position]
        self.visibility_history = [5]
        self.planned_moves = ""
        self.xray_points = 10
        self.visibility = 5
        self.movement = 10
        self.reset = False
        self.first_move = True

        # performance variables
        self.time_needed_to_solve = 0
        self.turns_taken_to_solve = 0
        self.moves_taken_to_solve = 0 

    def valid_position(self, maze, position):
        if position[0] >= 0 and position[0] < maze.shape[0]:
            if position[1] >= 0 and position[1] < maze.shape[1]:
                return True
        return False
    
    def view(self, maze, size, position, friendly):
        view = [[0 for i in range(size)] for j in range(size)]
        for i in range(size):
            for j in range(size):
                # valid position in maze
                if self.valid_position(maze, (position[0] - int(size/2) + i, position[1] - int(size/2) + j)):
                    view[i][j] = maze[position[0] - int(size/2) + i][position[1] - int(size/2) + j]
                    # in the case of an unfriendly solve,traps are only shown if the agent is 
                    # 1 tile away from them and their type is hidden using the value of 90
                    if not friendly:
                        if view[i][j] not in [0, 255, 64, 182]:
                            if abs(i - size/2) > 1 and abs(j - size/2) > 1:
                                view[i][j] = 255
                            else:
                                view[i][j] = 90
                # if the position is invalid, consider it a wall
                else:
                    view[i][j] = 0
        
        # transform view in string
        response = "["
        for i in range(size):
            for j in range(size):
                response += str(view[i][j])
                if j == size-1:
                    if i != size-1:
                        response += "; "
                else:
                    response += ", "
        response += "]"
        return response

    def move(self, command, maze, portals, position = None):
        x = self.position[0]
        y = self.position[1]

        if position != None:
            x = position[0]
            y = position[1]
            
        view = ""

        # first analize the unsuccessful cases
        successful = 0

        # portal case
        if command == "P":
            # 150-169 - portal ids
            if maze[x][y] in range(150, 170):
                if (x, y) == portals[maze[x][y]][0]:
                    self.position = portals[maze[x][y]][1]
                else:
                    self.position = portals[maze[x][y]][0]
                view = self.view(maze, self.visibility, self.position, app.friendly)
                successful = 1
                return self, successful, view
            else:
                view = self.view(maze, self.visibility, self.position, app.friendly)
                return self, successful, view
        
        # xray usage case
        if command == "X":
            # check if the agent has enough xray points
            if self.xray_points >= 2:
                self.xray_points -= 2
                self.visibility += 2
                view = self.view(maze, self.visibility, self.position, app.friendly)
                # TODO: try to keep the visibility with x-ray points forever
                # else -> self.visibility -= 2
                return self, successful, view
            else:
                view = self.view(maze, self.visibility, self.position, app.friendly)
                successful = 0
                return self, successful, view
        
        # direction case or trap pushforward or pushback (T)
        delta = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1), "T": (0, 0)}
        if x + delta[command][0] < 0 or x + delta[command][0] >= maze.shape[0] or y + delta[command][1] < 0 or y + delta[command][1] >= maze.shape[1]:
            view = self.view(maze, self.visibility, self.position, app.friendly)
            return self, successful, view

        # analize the new position
        x += delta[command][0]
        y += delta[command][1]

        # 0 - wall
        if maze[x][y] == 0:
            view = self.view(maze, self.visibility, self.position, app.friendly)
            return self, successful, view
        
        # 255 - path, 64 - entrance, 182 - exit
        elif maze[x][y] in [255, 64, 182]:
            successful = 1

        # 16 - X-RAY point increment
        elif maze[x][y] == 16:
            self.xray_points += 1
            successful = 1

        # 32 - fog tile
        elif maze[x][y] == 32:
            self.visibility = 3
            successful = 1

        # 224 - tower tile
        elif maze[x][y] == 224:
            self.visibility = 7
            successful = 1

        # 96-100 - trap movement tile with n = [1,5]
        elif maze[x][y] in range(96, 101):
            self.movement -= int(maze[x][y]) - 95
            successful = 1

        # 101-105 - trap rewind tile with n = [1,5]
        elif maze[x][y] in range(101, 106):
            n = int(maze[x][y]) - 100
            self.position = self.move_history[-n]
            self.move_history = self.move_history[:-n]
            self.visibility_history = self.visibility_history[:-n]
            successful = 1
            return self, successful, self.view(maze, self.visibility, self.position, app.friendly)

        # 106-110 - trap pushforward tile with n = [1,5]
        elif maze[x][y] in range(106, 111):
            n = int(maze[x][y]) - 105
            x += n * delta[command][0]
            y += n * delta[command][1]
            return self.move("T", maze, portals, position=(x, y))

        # 111-115 - trap pushback tile with n = [1,5]
        elif maze[x][y] in range(111, 116):
            n = int(maze[x][y]) - 110
            x -= n * delta[command][0]
            y -= n * delta[command][1]
            return self.move("T", maze, portals, position=(x, y))
        
        # 150-169 - portal tile
        elif maze[x][y] in range(150, 170):
            successful = 1
        
        # save status
        self.position = (x, y)
        self.move_history.append(self.position)
        self.visibility_history.append(self.visibility)
        view = self.view(maze, self.visibility, self.position, app.friendly)
        return self, successful, view

''' Define variables before running the server '''
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.friendly = True
    app.uuid = -1
    app.agents = []
    app.input_mode = False

    # variable used to limit the movement history for every agent
    app.agent_steps = 100
    
    # Event to manage waiting for input
    app.wait_for_input_event = asyncio.Event()
    app.wait_for_input_event.set()

    maze_info = random_generation.generate_maze()
    app.maze = np.array(list(maze_info[4])).reshape(100, 100)
    app.portals = {code: [] for code in range(150, 170)}
    for i in range(100):
        for j in range(100):
            if app.maze[i][j] in range(150, 170) and (i, j) not in app.portals[app.maze[i][j]]:
                app.portals[app.maze[i][j]].append((i, j))

    app.entrance = maze_info[0]
    app.exit = maze_info[1]
    yield

app = FastAPI(lifespan=lifespan)

''' Main route: agent strategy '''
@app.post("/")
async def command(request: Request):
    body = await request.json()

    # UUID is not given: create new agent
    if "UUID" not in body:
        app.uuid += 1
        app.agents.append(Agent(app.uuid, app.entrance))
        app.agents[-1].first_move = False
        app.agents[-1].time_needed_to_solve = time.time()
        # friendly server
        if app.friendly:
            return {"UUID": str(app.uuid),
                    "x": str(app.entrance[0]),
                    "y": str(app.entrance[1]),
                    "width": str(app.maze.shape[0]),
                    "height": str(app.maze.shape[1]),
                    "view": app.agents[app.uuid].view(app.maze, 5, app.entrance, app.friendly),
                    "moves": "10"}
        # unfriendly server
        return {"UUID": str(app.uuid),
                "view": app.agents[app.uuid].view(app.maze, 5, app.entrance, app.friendly),
                "moves": "10"} 
    
    # UUID is invalid
    if int(body["UUID"]) > app.uuid:
        raise HTTPException(status_code=404, detail="invalid UUID")

    # UUID is given and valid: an agent has returned    
    # identify the agent
    agent = None
    for i in range(len(app.agents)):
        if app.agents[i].uuid == int(body["UUID"]):
            agent = app.agents[i]
            break

    # check if the agent is reset
    if agent.reset:
        agent.reset = False
        return {"end": "0"}
    
    # check if the agent is on the first move
    if agent.first_move:
        agent.first_move = False
        # save the moment when the agent started the solve
        agent.time_needed_to_solve = time.time()

        if app.friendly:
            return {"x": str(app.entrance[0]),
                    "y": str(app.entrance[1]),
                    "width": str(app.maze.shape[0]),
                    "height": str(app.maze.shape[1]),
                    "view": app.agents[app.uuid].view(app.maze, 5, app.entrance, app.friendly),
                    "moves": "10"}
        # unfriendly server
        return {"view": app.agents[app.uuid].view(app.maze, 5, app.entrance, app.friendly),
                "moves": "10"} 

    # Save planned moves of the agent
    if "input" in body:
        agent.planned_moves = body["input"]
    
    # Wait for the event before processing the move (this will wait until the button is pressed)
    if app.input_mode:
        await app.wait_for_input_event.wait()
        app.wait_for_input_event.clear() 

    # check if the input is in the correct format and calculate the resulted json
    if "input" not in body:
        if agent.position == app.exit:
            return {"end": "1"}

    input = body["input"]
    agent.movement = 10
    if len(input) > agent.movement:
        raise HTTPException(status_code=400, detail="Input given by the agent is too long")
    result = {}

    # save the number of turns taken to solve the maze
    agent.turns_taken_to_solve += 1

    # iterate through the input
    for i in range(len(input)):
        if input[i] not in ["N", "S", "E", "W", "P", "X"]:
            raise HTTPException(status_code=400, detail=f"Input contains invalid command: {input[i]}")
        # move agent and update the movement if unsuccessful
        agent.visibility = 5
        move = agent.move(input[i], app.maze, app.portals)
        agent.moves_taken_to_solve += 1
        if move[1] == 0:
            agent.movement -= 1
        # clean the planned moves until the next input
        agent.planned_moves = ""
        
        # check if the agent has reached the exit
        if agent.position == app.exit:
            # save the moment when the agent finished the solve
            # calculate the time needed to solve
            agent.time_needed_to_solve = time.time() - agent.time_needed_to_solve
            return {"end": "1"}
        # save result
        result[f"command_{i+1}"] = {"name": f"{input[i]}",
                                   "successful": f"{move[1]}",
                                   "view": f"{move[2]}"}
    result["moves"] = str(agent.movement)
    return result
 
''' Generate Maze Route '''
@app.post("/maze")
async def generate_maze(request: Request):
    # Generate maze to obtain maze_info
    body = await request.json()
    seed = None
    width = 10
    height = 10
    max_threshold = 1
    no_special_tiles = False
    if "seed" in body:
        seed = body["seed"]
    if "width" in body:
        width = body["width"]
    if "height" in body:
        height = body["height"]
    if "max_threshold" in body:
        max_threshold = body["max_threshold"]
    if "no_special_tiles" in body:
        no_special_tiles = body["no_special_tiles"]
    maze_info = random_generation.generate_maze(seed, width, height, max_threshold, False, no_special_tiles)

    # Save maze (in a matrix)
    app.maze = np.array(list(maze_info[4])).reshape(width, height)

    # Save portals: dictionary with key = portal code and value = list of portal positions
    app.portals = {code: [] for code in range(150, 170)}
    for i in range(width):
        for j in range(height):
            if app.maze[i][j] in range(150, 170) and (i, j) not in app.portals[app.maze[i][j]]:
                app.portals[app.maze[i][j]].append((i, j))
    
    # Save entrance and exit
    app.entrance = maze_info[0]
    app.exit = maze_info[1]

    # reset the agents
    for a in app.agents:
        a.position = app.entrance
        a.move_history = [a.position]
        a.visibility_history = [5]
        a.planned_moves = ""
        a.xray_points = 10
        a.visibility = 5
        a.movement = 10
        a.reset = True
        a.first_move = True

    bytes_io = BytesIO()

    # Save maze as an image
    img = Image.fromarray(app.maze, mode="L")
    img.save(bytes_io, format="PNG")
    bytes_io.seek(0)
    return Response(bytes_io.read(), media_type="image/png")


''' Get Maze Route'''
@app.get("/maze/{filename}")
async def get_maze(filename):
    return FileResponse(f"./{filename}")

@app.get("/maze")
async def get_maze():
    # Return current maze as image
    bytes_io = BytesIO()

    # Save maze as an image
    img = Image.fromarray(app.maze, mode="L")
    img.save(bytes_io, format="PNG")
    bytes_io.seek(0)
    return Response(bytes_io.read(), media_type="image/png")

@app.get("/agents")
async def get_agents():
    return app.agents


''' Get an agent Route: based on given UUID '''
@app.get("/agent/{uuid}")
async def get_agent(uuid):
    for agent in app.agents:
        if agent.uuid == int(uuid):
            return agent
    raise HTTPException(status_code=400, detail=f"Invalid UUID: {uuid}")


''' Toggle Route for friendly / unfriendly mode '''
@app.post("/toggle_friendly_mode")
async def toggle_signal():
    if app.friendly == False:
        app.friendly = True
    else:
        app.friendly = False
        app.wait_for_input_event.set()
    return app.friendly


''' Toggle Route for input mode '''
@app.post("/toggle_input_mode")
async def toggle_signal():
    if app.input_mode == False:
        app.input_mode = True
    else:
        app.input_mode = False
        app.wait_for_input_event.set()
    return app.input_mode


''' Continue Route for input mode: used for one action of the agents when input mode is activated '''
@app.post("/continue_input_mode")
async def continue_signal():
    # Set the event to allow the next move to proceed
    app.wait_for_input_event.set()
    return {"message": "Continue signal received"}


''' Get agents performance Route: least time, least number of turns, least number of moves taken to solve the maze '''
@app.get("/agents_performance")
async def get_agents_performance():
    best_time = app.agents[0].time_needed_to_solve
    best_time_agent = app.agents[0].uuid
    best_turns = app.agents[0].turns_taken_to_solve
    best_turns_agent = app.agents[0].uuid
    best_moves = app.agents[0].moves_taken_to_solve
    best_moves_agent = app.agents[0].uuid

    for agent in app.agents:
        if agent.time_needed_to_solve < best_time:
            best_time = agent.time_needed_to_solve
            best_time_agent = agent.uuid
        if agent.turns_taken_to_solve < best_turns:
            best_turns = agent.turns_taken_to_solve
            best_turns_agent = agent.uuid
        if agent.moves_taken_to_solve < best_moves:
            best_moves = agent.moves_taken_to_solve
            best_moves_agent = agent.uuid
    return {"best time": f"{best_time} seconds, agent {best_time_agent}",
            "best turns": f"{best_turns} turns, agent {best_turns_agent}",
            "best moves": f"{best_moves} moves, agent {best_moves_agent}"}
