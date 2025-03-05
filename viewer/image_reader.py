import pygame
import sys
import random
import requests
from io import BytesIO

# Colors for the tiles
color_mapping = {
    0: (0, 0, 0),         # Wall - Black
    255: (255, 255, 255), # Path - White
    64: (0, 128, 0),      # Entrance - Dark Green
    182: (255, 0, 0),     # Exit - Red
    16: (0, 255, 255),    # X-RAY point increment - Cyan
    32: (128, 128, 128),  # Fog tile - Gray
    224: (255, 215, 0),   # Tower tile - Gold
}

trap_colors = {
    "movement": [(128 + 20 * (i - 96), 0, 128) for i in range(96, 101)],
    "rewind": [(0, 0, 139 + 20 * (i - 101)) for i in range(101, 106)],
    "pushforward": [(34, 139 + 20 * (i - 106), 34) for i in range(106, 111)],
    "pushback": [(255, 69 + 20 * (i - 111), 0) for i in range(111, 116)]
}

for i in range(96, 101):
    color_mapping[i] = trap_colors["movement"][i - 96]
for i in range(101, 106):
    color_mapping[i] = trap_colors["rewind"][i - 101]
for i in range(106, 111):
    color_mapping[i] = trap_colors["pushforward"][i - 106]
for i in range(111, 116):
    color_mapping[i] = trap_colors["pushback"][i - 111]

# Portal pairs
portal_colors = [
    (75, 0, 130), (238, 130, 238), (0, 255, 127), (255, 20, 147), (0, 191, 255),
    (124, 252, 0), (255, 165, 0), (0, 128, 128), (255, 105, 180), (30, 144, 255),
    (173, 255, 47), (255, 69, 0), (32, 178, 170), (128, 0, 128), (147, 112, 219),
    (152, 251, 152), (75, 0, 130), (219, 112, 147), (60, 179, 113), (255, 222, 173)
]
for i, color in zip(range(150, 170), portal_colors):
    color_mapping[i] = color


def load_maze_from_image(image_path):
    try:
        # Load the grayscale image
        maze_image = pygame.image.load(image_path).convert()
        width, height = maze_image.get_size()
        tiles = []
        

        # Parse each pixel
        for x in range(width):
            for y in range(height):
                # Get the pixel value
                pixel_value = maze_image.get_at((x, y))[0]  # Grayscale value is in the red channel
            
                if pixel_value in color_mapping.keys():
                    color = color_mapping[pixel_value]
                    if 96 <= pixel_value <= 100:
                        n_value = pixel_value - 95
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 101 <= pixel_value <= 105:
                        n_value = pixel_value - 100
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 106 <= pixel_value <= 110:
                        n_value = pixel_value - 105
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 111 <= pixel_value <= 115:
                        n_value = pixel_value - 110
                        tiles.append((x, y, color, pixel_value, n_value))
                    else:
                        tiles.append((x, y, color, pixel_value, 0))


        return tiles, width, height
    except Exception as e:
        print(f"Error loading maze image: {e}")
        sys.exit()

def load_maze_from_server():
    try:
        response = requests.get("http://localhost:8000/maze")
        image_file = BytesIO(response.content)
        maze_image = pygame.image.load(image_file).convert()
        width, height = maze_image.get_size()
        tiles = []
        
        # Parse each pixel
        for x in range(width):
            for y in range(height):
                # Get the pixel value
                pixel_value = maze_image.get_at((x, y))[0]  # Grayscale value is in the red channel
                
                if pixel_value in color_mapping.keys():
                    color = color_mapping[pixel_value]
                    if 96 <= pixel_value <= 100:
                        n_value = pixel_value - 95
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 101 <= pixel_value <= 105:
                        n_value = pixel_value - 100
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 106 <= pixel_value <= 110:
                        n_value = pixel_value - 105
                        tiles.append((x, y, color, pixel_value, n_value))
                    
                    elif 111 <= pixel_value <= 115:
                        n_value = pixel_value - 110
                        tiles.append((x, y, color, pixel_value, n_value))
                    else:
                        tiles.append((x, y, color, pixel_value, 0))
        
        for x in range(width):
                # Get the pixel value
                tiles.append((x, height, (0, 0, 0), 0, 0))
        
        for y in range(height + 1):
                # Get the pixel value
                tiles.append((width, y, (0, 0, 0), 0, 0))
                

        return tiles, width, height
    except Exception as e:
        print(f"Error loading maze image from server: {e}")
        sys.exit()