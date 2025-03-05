## Team roles & details
PM
- Vlad Buțcan

Tech team lead
- George-Bogdan Angheloiu

Tech team
- Daniela-Alexandra Drăgușin
- Ioana-Alexandra Pătrașcu
- Iuliana-Violeta Comșa
- Oana-Maria Băcăran
- Vladimir Bucur

Tester
- Cristian-Ștefan Sbârnea

Programming language: Python

Programming tools: PyUnit, Trello

Development methodology: Agile

Kanban board: https://trello.com/w/mpsescapethemaze

## Server
- Packets: requests
- Activate .venv:
    - Windows Git Bash: `source .venv/Scripts/activate`
    - Linux, macOS: `source .venv/bin/activate`
- Start server: `fastapi dev server.py` or `python3 -m fastapi dev server.py`

Install Fast API: https://fastapi.tiangolo.com/virtual-environments/#install-packages-directly

## Viewer
- Packets: pygame
- Start viewer: `python3 viewer.py`

## Agent
- Packets: pillow
- Start agent: `python3 agent_runner.py`


---
# Project Description

This project involves the development of a competitive game where multiple AI agents, created by teams of students, navigate through programmatically generated mazes. The student teams are responsible for both developing the AI agents (clients) and setting up a server that connects these AI agents. Additionally, the server will load the programmatically generated maze maps and function as a viewer to display the progress of the game.

## Objective
The goal is to determine the most efficient AI solution through direct competition among the AI agents, with the current positions of the players being highlighted on the screen. The player whose AI exits the maze first is declared the winner. The server will monitor win conditions and award points accordingly.

## Game Mechanics
- Visibility: Visibility: By default, each player can see a 5×5 area around their current position, indicating possible directions of movement: North (N), East (E), South (S), and West (W)
- Turn-based Movement: The game operates on a turn-based system. In each turn, the AI will send a sequence of up to 10 steps (comprising the characters N, E, S, W) to the server, which will then move the player in the specified directions. For each command that cannot be executed (e.g., due to hitting a wall), the length of the allowable sequence for the next turn will decrease by one.
- X-RAY Points: At the start of the game, each player has 10 X-RAY points. These points can be used to access an expanded view around the player. For example, an X-RAY command, of 2 will consume 2 points and expand the visibility window from 5×5 to 7×7. The X-RAY command counts as one of the steps the player is taking, and are sent to the server as X, in the character array.
- The maze can contain additional tiles with various functionalities, which can only be placed alongside the path and not the wall:
    - Fog tile: The player can see an area of only 3×3 around him (X-RAY points can still be used)
    - Tower tile: The player can see in an area of 7×7 around this tile (X-RAY points can still be used)
    - Traps, which can be seen at a max of 2 steps away from them, and are of multiple kind, with a number n assigned to them:
        - traps are not disabled when activated by walking over them
        - movement decrease: decreases the maximum number of steps you can send to the server in the next turn by n
        - rewind: the players last n moves are undone
        - pushforward: the player is forced forward based on the direction of their movement for n steps
        - pushback: the player is forced backwards based on the direction of their movement for n steps
    - Portals: They work in pairs and connect one point of the maze to another.
        - Each pair has a specific id to represent a portal
        - To activate a portal the agent must send a command “P” while on top of one
    - Consumables: X-RAY point increments

## Maze Generation Requirements
The maze must be generated according to the following constraints:
- The maze generator must function procedurally, creating mazes with a single entrance and a single exit.
- The entrance and exit of the maze can be placed anywhere in the maze, not necessarily on the borders.
- In order to have intricate possible solutitions the shortest possible walkable path from the entrance to the exit must cover at least 50% of the total area covered by paths and elements placed on path tiles
- The minimum rectangular path from the entrance to the exit must cover at least 50% of the total rectangular area of the maze.
- Teams will choose the horizontal and vertical dimensions of each generated maze within specified maximum allowable ranges.
- The maze should be able to be generated in one of the following ways:
    - completely random, based on a fixed seed, which may or may not be provided, and a set threshold that represents the maximum of special tiles that can be generated of each type.
    - semi-random, based on a fixed seed and a set number for each special tile that can be generated.
    - from an input file, which is represented by an image.
- The maze can never place two special tiles next to each other, or next to the entrance/exit
Each generated maze needs to be checked for validity to see if it respects the constraints imposed.

## Files
The maze generator must output an image, in 8bpp, grayscale format, with the following color representations for each pixel:
0 - wall
255 - path
64 - entrance
182 - exit
16 - X-RAY point increment
32 - fog tile
224 - tower tile
90 - reserved value for generic trap tiles (this is not used in generation, but will be sent to the agents during solve)
96-100 - trap movement tile with n = [1,5]
101-105 - trap rewind tile with n = [1,5]
106-110 - trap pushforward tile with n = [1,5]
111-115 - trap pushback tile with n = [1,5]
150-169 - portal ids, each value should only appear twice in a maze representing that portal pair (a maze should never have more than 20 portal pairs)

The maze generator can take the same image back as input to generate the exact same maze, or other images to generate new mazes. Obs: Images which contain undefined pixel colors are to be rejected.

## Server
The client, represented by an agent strategy, and the server will communicate with each other through a series of JSON commands. The first time a client connects to a server it gets assigned a UUID, thus the server will distinguish between a new connection and a reconnection attempt based on the UUID.

The first connection from an agent will always be an empty JSON, whereas every recconection will be a JSON containing the UUID, in the following format:
```
{
"UUID": ""
}
```
In order to simplify the problem, the server can work in a friendly mode where it communicates to an agent its initial coordinates in the maze and the maximum maze size: width, height, alongside the 5×5 tiles it sees initially. Thus, the first JSON request back from the server should be in the following format:
```
{ 
"UUID": "",
"x [optional]": "",
"y [optional]": "",
"width [optional]": "",
"height [optional]": "",
"view": "string of the matrix representation of the visible area around the agent"
"moves": "total number of moves/commands available for the agent in the first turn"
}
```
In a normal turn the agent sends a JSON to the server in the following format: {input: “string of commands up to length 10”}
The server will output back a JSON with the following format:
```
{
"command_1": {
  "name": "name of command, ex: "N"",
  "successful": "0|1",
  "view": "string of the matrix representation of the visible area around the agent after the move;"
          ex for 3x3: "[0, 255, 255; 0, 255, 0; 0, 255, 0]"
},
"command_2": {
  "name": "",
  "successful": "",
  "view": ""
},
...
"command_N": {
  "name":"",
  "successful": "",
  "view": ""
},
"moves": "total number of available moves for the next turn"
}
```
In the case of a friendly solve, the server will always output the value of a trap if it's inside the agent's visible area. However, in the case of an unfriendly solve, traps are only shown if the agent is 1 tile away from them and their type is hidden using the value of 90.

Once an agent solves a maze, or the server decides the agent is taking too long so it gets timed out, the server will send a JSON with the following format:
```
{
"end": "0|1, based on if the agent solved the maze or not"
}
```
Following a solve, the server can test the agents on a new maze, for this it sends a request in the following format:
```
{
"x [optional]": "",
"y [optional]": "",
"width [optional]": "",
"height [optional]": "",
"view": "string of the matrix representation of the visible area around the agent"
"moves": "total number of moves/commands available for the agent in the first turn"
}
```
The server can store generated mazes as images and output them back on request.

In the case where multiple agents are on the same server, they don't interact with one other, so that each agent has a fair chance at solving the maze. For this reason, every trap triggered by an agent will only affect that specific agent, so the server needs to keep track of which agent triggered which trap.

## Agents
An agent can work in one of two modes:
- real time: it sends the move commands to the server, receives back the success fail results and immediately follows with the next list of commands
- await for input: sends the list of commands, receives the results of the execution and awaits for user input before sending the next list of commands (this is done client side, not server side)

Each agents performance is measured in one of three ways:
- Least time taken to solve the maze
- Least number of turns taken to solve the maze
- Least number of moves taken to solve the maze
For the real-time mode the agents will have a maximum time allotted before sending each command. If the allotted time expires, the agent is timed out and disqualified, and the maze is considered unsolved. The maximum time can be set before each run, or be preset depending on the maze difficulty.

Each AI agents behaviour must be unique, avoid creating different agents that have only a minor part of their strategy modified.

## Viewer
The viewer should output the maze and the agents solving it in the following manner:
- 1920×1080 resolution
- 20 pixels/tile by default
- Mazes that don't fit on screen should have a scroll option.
- Zoom function
- Two possible viewing modes: view the entire maze and view what each agent has explored so far
- The colors for each tile are left to the discretion of each team to make the output more interesting.
- Traps should have their value n on top of them if possible.
- The walked path should be represented by a solid line, and the planned moves of the agent by a dashed line.
- The viewer can put the server into an await for input mode, where it doesn't output back an agents results for a move till a button is pressed in the viewer.
