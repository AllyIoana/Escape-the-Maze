import pygame
import numpy as np
import sys
import requests
from pygame.locals import *
from image_reader import load_maze_from_image, load_maze_from_server
from image_reader import color_mapping
from threading import Thread
from time import sleep

running = True
agents = []

# Toggle for legend visibility
legend_visible = True

controls_text = [
    "L - Toggle Legend",
    "V - Switch Viewing Mode",
    "Navigation keys - Scroll up/",
    "down/left/right",
    "(Ctrl +) - / + - Zoom",
    "Mouse Drag - Scroll",
    "Mouse Wheel - Scroll",
    "Esc - Quit",
    "A - Toggle input mode",
    "C - Send continue signal"
]

waiting_for_input = False
def send_continue_signal():
    """Send a signal to the server to proceed with the next move."""
    global waiting_for_input
    global agents
    if waiting_for_input:
        url = "http://127.0.0.1:8000/continue_input_mode"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                print("Continue signal sent.")
                print(agents)
            else:
                print(f"Failed to send continue signal: {response.status_code} {response.text}")           
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the server: {e}")

    else:
        print("Server is not waiting for input yet.")
        

# TODO 1: Implement the fetch_agents function
def fetch_agents():
    """Fetch agent data from the server."""
    url = "http://127.0.0.1:8000/agents"
    global running
    global agents
    global waiting_for_input
    while running:
            sleep(0.2)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    agents = response.json()
                    # print(f"Agents fetched: {agents}")
                else:
                    print(f"Failed to fetch agents: {response.status_code} {response.text}")
                    agents = []
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to the server: {e}")
                agents = []
        

def get_color_name(color_key):
    """Attempts to provide a descriptive name for a color based on the color mapping."""
    if color_key == 0:
        return "Wall"
    elif color_key == 255:
        return "Path"
    elif color_key == 64:
        return "Entrance"
    elif color_key == 182:
        return "Exit"
    elif color_key == 16:
        return "X-RAY Point Increment"
    elif color_key == 32:
        return "Fog"
    elif color_key == 224:
        return "Tower"
    elif 96 <= color_key <= 100:
        return f"Movement decrease {color_key - 95}"
    elif 101 <= color_key <= 105:
        return f"Rewind {color_key - 100}"
    elif 106 <= color_key <= 110:
        return f"Pushforward {color_key - 105}"
    elif 111 <= color_key <= 115:
        return f"Pushback {color_key - 110}"
    elif 150 <= color_key <= 169:
        return f"Portal {color_key - 150}"
    else:
        return "Generic Trap"
    
def create_legend_items(color_mapping):
    """Creates legend items with the desired dictionary structure."""
    legend_items = []
    seen_descriptions = set()  # Keep track of descriptions to avoid duplicates

    for key, color in color_mapping.items():
        description = get_color_name(key)
        if description not in seen_descriptions:  # Add only unique descriptions
            legend_items.append({"color": color, "description": description})
            seen_descriptions.add(description)
            
    
    return legend_items

def draw_legend(screen, legend_data, controls_text):
    """Draws the legend with two main columns: Controls and Pixel Types."""
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 42)  # Slightly larger font for the titles
    max_items_per_column = 24  # Increase this to reduce the number of columns for pixel types
    column_width = 320
    item_height = 30
    padding = 20
    x_margin = 200  # Margin from the screen's right edge
    y_margin = 130  # Margin from the screen's top edge

    # Calculate the number of sub-columns needed for pixel types
    num_columns = (len(legend_data) + max_items_per_column - 1) // max_items_per_column

    # Calculate overall dimensions for each section
    controls_width = column_width
    pixel_types_width = num_columns * column_width + (num_columns - 1) * padding
    total_width = controls_width + pixel_types_width + padding  # Combine both main columns

    # Calculate height based on the largest section
    controls_height = len(controls_text) * item_height + 50  # Extra space for the title
    pixel_types_height = min(len(legend_data), max_items_per_column) * item_height + 50  # Pixel types title + items
    total_height = max(controls_height, pixel_types_height) + 20

    # Top-left corner position of the legend
    x = screen.get_width() - total_width - x_margin
    y = y_margin

    # Background rectangle
    pygame.draw.rect(screen, (50, 50, 50), (x, y, total_width, total_height), border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), (x, y, total_width, total_height), width=2, border_radius=10)

    # Render "Controls" section
    controls_x = x + 10
    controls_y = y + 10
    controls_title = title_font.render("Controls", True, (255, 255, 255))
    screen.blit(controls_title, (controls_x, controls_y))

    for i, text in enumerate(controls_text):
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (controls_x, controls_y + 40 + i * item_height))

    # Render "Pixel Types" section
    pixel_types_x = x + controls_width + padding
    pixel_types_y = y + 10
    pixel_types_title = title_font.render("Pixel Types", True, (255, 255, 255))
    screen.blit(pixel_types_title, (pixel_types_x, pixel_types_y))

    for idx, item in enumerate(legend_data):
        column = idx // max_items_per_column
        row = idx % max_items_per_column

        # Calculate position for the current item
        item_x = pixel_types_x + column * (column_width + padding)
        item_y = pixel_types_y + 40 + row * item_height

        # Draw color box and description
        color_rect = pygame.Rect(item_x, item_y, 20, 20)
        pygame.draw.rect(screen, item["color"], color_rect)

        text_surface = font.render(item["description"], True, (255, 255, 255))
        screen.blit(text_surface, (item_x + 30, item_y))
        
# Direction mapping for relative moves
DIRECTION_MAP = {
    'N': (-1, 0),  # North
    'S': (1, 0),   # South
    'E': (0, 1),   # East
    'W': (0, -1),  # West
    'P': (0, 0),   # Portal (stays in the same place, modify if needed)
    "X": (0, 0)
}

def parse_planned_moves(start_position, planned_moves):
    """Convert relative moves into absolute positions."""
    positions = [start_position]
    current_pos = list(start_position)

    for move in planned_moves:
        if move in DIRECTION_MAP:
            dx, dy = DIRECTION_MAP[move]
            current_pos[0] += dx
            current_pos[1] += dy
            positions.append(tuple(current_pos))
    
    return positions
        
def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10, width=3):
    """Draw a dashed line from start_pos to end_pos."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length
    
    if x1 == x2:  # Vertical line
        y_coords = np.arange(y1, y2, dl if y1 < y2 else -dl)
        x_coords = np.full(y_coords.shape, x1)
    elif y1 == y2:  # Horizontal line
        x_coords = np.arange(x1, x2, dl if x1 < x2 else -dl)
        y_coords = np.full(x_coords.shape, y1)
    else:  # Diagonal line
        length = np.hypot(x2 - x1, y2 - y1)
        dash_count = int(length // dl)
        x_coords = np.linspace(x1, x2, dash_count)
        y_coords = np.linspace(y1, y2, dash_count)
    
    for i in range(0, len(x_coords) - 1, 2):
        start = (int(x_coords[i]), int(y_coords[i]))
        end = (int(x_coords[i + 1]), int(y_coords[i + 1]))
        pygame.draw.line(surface, color, start, end, width)    


 
def render_maze(screen, tiles, zoom_level, scroll_x, scroll_y, agents, tile_size=20, view_mode='entire_maze'):
    
    # print(agents)
    
    scaled_tile_size = int(tile_size * zoom_level)
    font = pygame.font.Font(None, scaled_tile_size)

    # Creează un dicționar pentru tipurile de tile-uri pentru acces rapid
    tile_map = {(x, y): color_index for x, y, color_index, _, _ in tiles}

    # Setul de tile-uri explorate pe baza mișcărilor și vizibilității agenților
    explored_tiles = set()
    if view_mode == 'explored_view' and agents:
        for agent in agents:
            if 'move_history' in agent and 'visibility_history' in agent:
                for i in range(0, len(agent['move_history'])):
                    move = agent['move_history'][i]
                    visibility = agent['visibility_history'][i]
                    half_visibility = visibility // 2  # Vizibilitate redusă pentru margini
                    cx, cy = move[1], move[0]  # Convertire la (x, y)

                    # Adaugă toate tile-urile dintr-un pătrat exact `visibility x visibility`
                    for dx in range(-half_visibility, half_visibility + 1):
                        for dy in range(-half_visibility, half_visibility + 1):
                            explored_tiles.add((cx + dx, cy + dy))

    for x, y, color_index, pixel_value, n_value in tiles:
        # Redă doar în modul "entire_maze" sau dacă tile-ul a fost explorat în "explored_view"
        if view_mode == 'entire_maze' or (view_mode == 'explored_view' and (x, y) in explored_tiles):
            pygame.draw.rect(
                screen,
                color_index,
                (
                    (x * scaled_tile_size) - scroll_x,
                    (y * scaled_tile_size) - scroll_y,
                    scaled_tile_size,
                    scaled_tile_size
                )
            )

            # Redă numerele de pe tile-uri (opțional)
            if 96 <= pixel_value <= 115:
                n_text = font.render(str(n_value), True, (0, 0, 0))
                text_rect = n_text.get_rect(center=((x * scaled_tile_size) - scroll_x + scaled_tile_size // 2,
                                                    (y * scaled_tile_size) - scroll_y + scaled_tile_size // 2))
                screen.blit(n_text, text_rect)

    # Redarea agenților și a traseelor lor
    if agents:
        for agent in agents:
            # Redă traseul parcurs cu o linie solidă
            if 'move_history' in agent and len(agent['move_history']) >= 1:
                for i in range(len(agent['move_history']) - 1):
                    start_y, start_x = agent['move_history'][i]
                    end_y, end_x = agent['move_history'][i + 1]
                    
                    # Check if the step is a portal (teleportation)
                    if abs(start_x - end_x) > 1 or abs(start_y - end_y) > 1:
                        # Skip drawing a line if it's a teleportation
                        continue

                    # Asigură-te că atât start-ul, cât și end-ul sunt tile-uri valide
                    if tile_map.get((start_x, start_y)) != (0, 0, 0) and tile_map.get((end_x, end_y)) != (0, 0, 0):
                        pygame.draw.line(
                            screen,
                            (0, 0, 255),  # Albastru pentru traseul parcurs
                            (
                                int((start_x * scaled_tile_size) - scroll_x + scaled_tile_size // 2),
                                int((start_y * scaled_tile_size) - scroll_y + scaled_tile_size // 2)
                            ),
                            (
                                int((end_x * scaled_tile_size) - scroll_x + scaled_tile_size // 2),
                                int((end_y * scaled_tile_size) - scroll_y + scaled_tile_size // 2)
                            ),
                            7  # Grosimea liniei
                        )
            
            
    if agents:
        for agent in agents:
            start_position = agent['position']
            planned_moves = agent['planned_moves']
            planned_positions = parse_planned_moves(start_position, planned_moves)

            for i in range(len(planned_positions) - 1):
                start = (
                    int((planned_positions[i][1] * scaled_tile_size) - scroll_x + scaled_tile_size // 2),
                    int((planned_positions[i][0] * scaled_tile_size) - scroll_y + scaled_tile_size // 2)
                )
                end = (
                    int((planned_positions[i + 1][1] * scaled_tile_size) - scroll_x + scaled_tile_size // 2),
                    int((planned_positions[i + 1][0] * scaled_tile_size) - scroll_y + scaled_tile_size // 2)
                )
                draw_dashed_line(screen, (0, 0, 0), start, end, dash_length=10, width=5)
            

    # Render the agents' circles last (to ensure they're on top)
    if agents:
        for agent in agents:
            agent_y, agent_x = agent['position']
            pygame.draw.circle(
                screen,
                (255, 0, 0),  # Red for the agent
                (
                    int((agent_x * scaled_tile_size) - scroll_x + scaled_tile_size // 2),
                    int((agent_y * scaled_tile_size) - scroll_y + scaled_tile_size // 2)
                ),
                max(3, scaled_tile_size // 4)  # Adjust marker size
            )

def main():
    global waiting_for_input
    pygame.init()
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    if screen is None:
        print("Failed to create a screen")
        pygame.quit()
        sys.exit()
        
    # print("waiting:",waiting_for_input)

    #maze_tiles, maze_width, maze_height = load_maze_from_image('../server/maze_100x100-seed=default.png')
    maze_tiles, maze_width, maze_height = load_maze_from_server()

    zoom_level = 1.0  # Start at unzoomed level
    zoom_step = 0.05  # Slower zooming speed
    tile_size = 20
    scroll_speed = 20  # Speed of scrolling

    # Calculate min_zoom_level to fit the entire maze on the screen
    min_zoom_x = screen_width / (maze_width * 20)
    min_zoom_y = screen_height / (maze_height * 20)
    min_zoom_level = min(min_zoom_x, min_zoom_y) 
    
    view_mode = 'entire_maze'  # Start with entire maze mode
    
    # Find the entrance tile
    entrance_tile = None
    for tile in maze_tiles:
        if tile[2] == color_mapping[64]:  # Entrance tile color
            entrance_tile = tile
            break

    if entrance_tile is None:
        print("Entrance tile not found in the maze.")
        sys.exit()
        
        
    # Calculate initial scroll position to center the entrance
    initial_scroll_x = entrance_tile[0] * tile_size - screen_width // 2
    initial_scroll_y = entrance_tile[1] * tile_size - screen_height // 2

    # Set initial scroll position
    scroll_x = initial_scroll_x
    scroll_y = initial_scroll_y

    # Track which keys are currently pressed
    keys = {
        'zoom_in': False,
        'zoom_out': False,
        'scroll_up': False,
        'scroll_down': False,
        'scroll_left': False,
        'scroll_right': False
    }
    
    # Track mouse dragging
    mouse_dragging = False
    mouse_start_x = 0
    mouse_start_y = 0

    global running
    global agents

    agent_thread = Thread(target=fetch_agents)
    agent_thread.daemon = True
    agent_thread.start()
    
    global legend_visible
    global controls_text
    legend_data = create_legend_items(color_mapping)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    if waiting_for_input:
                        url = "http://127.0.0.1:8000/toggle_input_mode"   
                        try:
                            response = requests.post(url)
                            if response.status_code == 200:
                                print("Continue signal sent.")
                            else:
                                print(f"Failed to send continue signal: {response.status_code} {response.text}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error connecting to the server: {e}") 
                            
                    waiting_for_input = False
                        
                elif event.key == K_a:
                    if waiting_for_input == False:
                        waiting_for_input = True  
                    else:
                        waiting_for_input = False
                    
                    url = "http://127.0.0.1:8000/toggle_input_mode"   
                    try:
                        response = requests.post(url)
                        if response.status_code == 200:
                            print("Toggle await input.")
                        else:
                            print(f"Failed to send await signal: {response.status_code} {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error connecting to the server: {e}")   
                elif event.key == K_f:
                    url = "http://127.0.0.1:8000/toggle_friendly_mode"   
                    try:
                        response = requests.post(url)
                        if response.status_code == 200:
                            print("Toggle friendly/unfriendly.")
                        else:
                            print(f"Failed to send friendly signal: {response.status_code} {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error connecting to the server: {e}")      
                elif event.key == K_c:
                    send_continue_signal()                    
                elif event.key == K_l:  # Toggle legend with the 'L' key
                    legend_visible = not legend_visible                     
                elif event.key == pygame.K_v:  # Use the 'v' key to switch modes
                        if view_mode == 'entire_maze':
                            view_mode = 'explored_view'
                        else:
                            view_mode = 'entire_maze'
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    keys['zoom_in'] = True
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    keys['zoom_out'] = True
                elif event.key == pygame.K_UP:
                    keys['scroll_up'] = True
                elif event.key == pygame.K_DOWN:
                    keys['scroll_down'] = True
                elif event.key == pygame.K_LEFT:
                    keys['scroll_left'] = True
                elif event.key == pygame.K_RIGHT:
                    keys['scroll_right'] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    keys['zoom_in'] = False
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    keys['zoom_out'] = False
                elif event.key == pygame.K_UP:
                    keys['scroll_up'] = False
                elif event.key == pygame.K_DOWN:
                    keys['scroll_down'] = False
                elif event.key == pygame.K_LEFT:
                    keys['scroll_left'] = False
                elif event.key == pygame.K_RIGHT:
                    keys['scroll_right'] = False

            # Mouse events for dragging
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = True
                    mouse_start_x, mouse_start_y = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    dx = event.pos[0] - mouse_start_x
                    dy = event.pos[1] - mouse_start_y
                    scroll_x -= dx
                    scroll_y -= dy
                    mouse_start_x, mouse_start_y = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up
                    scroll_y -= scroll_speed  # Scroll up
                elif event.y < 0:  # Scroll down
                    scroll_y += scroll_speed  # Scroll down

        # Apply continuous zooming or scrolling if keys are held down
        if keys['zoom_in']:
            prev_zoom = zoom_level
            zoom_level += zoom_step
            scroll_x = (scroll_x + screen_width / 2) * (zoom_level / prev_zoom) - screen_width / 2
            scroll_y = (scroll_y + screen_height / 2) * (zoom_level / prev_zoom) - screen_height / 2
        elif keys['zoom_out']:
            prev_zoom = zoom_level
            zoom_level = max(min_zoom_level, zoom_level - zoom_step)
            scroll_x = (scroll_x + screen_width / 2) * (zoom_level / prev_zoom) - screen_width / 2
            scroll_y = (scroll_y + screen_height / 2) * (zoom_level / prev_zoom) - screen_height / 2

        # Handle scrolling
        if keys['scroll_up']:
            scroll_y = scroll_y - scroll_speed
        if keys['scroll_down']:
            scroll_y = scroll_y + scroll_speed
        if keys['scroll_left']:
            scroll_x = scroll_x - scroll_speed
        if keys['scroll_right']:
            scroll_x = scroll_x + scroll_speed
            
        # Clear the screen and render the maze
        screen.fill((153, 204, 255))
        render_maze(screen, maze_tiles, zoom_level, scroll_x, scroll_y, agents, tile_size, view_mode)
        
        # Draw the legend
        if legend_visible:
            draw_legend(screen, legend_data, controls_text)
              
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main() 