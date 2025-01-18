import pygame
from game import *
from values import *

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('Tahoma', 30)
    label = font.render('Next Shape:', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))



def draw_text_middle_up(surface, text, size, color):
    font = pygame.font.SysFont('Tahoma', size, bold = True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2) - 250))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('Tahoma', size, bold = True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))



def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]

        # If (0,0,0) doesnt exist then the row is full of coloured cubes
        if (0, 0, 0) not in row:
            inc += 1
            ind = i

            # Go through each square in the row and delete them
            for j in range(len(row)):
                try: 
                    del locked[(j, i)]
                except:
                    continue
    

    # If there was a row deleted, then we move all the rows down
    if inc > 0:

        # We sort the list of locked keys, sorted by their y values
        for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
            x, y = key

            # If a square higher than a deleted row, then we need to move it down
            if y < ind:

                # Creates a new square, inc spots lower than it was before
                newKey = (x, y + inc)

                # This replaces the old square with the new one in the locked positions dictionary
                locked[newKey] = locked.pop(key)
    
    return inc


def draw_grid(surface, grid):
    # making the variables shorter and easier to write
    sx = top_left_x
    sy = top_left_y


    # Drawing each square of the grid
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i*block_size), (sx+play_width, sy + i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy), (sx + j*block_size, sy+play_height))





def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('Tahoma', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    # This draws the label we just created centered in the screen
    # The 30 at the end moves the label down 30 from the top 
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), 30))

    # current score
    font = pygame.font.SysFont('Tahoma', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 50, sy - 280))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # We draw the color (grid[i][j]) onto the surface, at the position we want
            # toplefty + i*block_size is the true 'y' position, same thing for 'x'
            # We then specify, the width and length of drawing, and the '0' means we fill the square (not a border)
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)
    
    
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)

    draw_grid(surface, grid)