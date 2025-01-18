###################################################
# Tech with Tim's tutorial was used to learn how  #
# to use pygame when it comes to a tetris game    #
###################################################


import random
import pygame


# creating the data structure for pieces
# setting up global vars

# functions to be used
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape 
# - setting up the main


# 
# 10 x 20 square grid
# shapes: S, Z, I, O, J, L, T
# in order by 0 - 6 respectively
# S = 0
# Z = 1
# I = 2
# O = 3
# J = 4
# L = 5
# T = 6


pygame.font.init()

# GLOBAL VARIABLES -----------------------------------------
screen_width = 800
screen_height = 700
play_width = 300    # 300 // 10  gives 30 width per block
play_height = 600   # 600 // 20 gives 30 height per block
block_size = 30


top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height


# SHAPE FORMATS IN BOTH OF THEIR POSSIBLE ROTATIONS -------
S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],   
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]


# Shapes stored to use their indexes (0 - 6)
shapes_list = [S, Z, I, O, J, L, T]

shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes_list.index(shape)]
        self.rotation = 0



# This function creates a grid, the dictionnary 'locked_positions' to store the positions of the pieces 
# that are locked in the grid. In other words, theres a block there
def create_grid(locked_positions = {}):

    # initializing each square to black originally (no block is there yet)
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    # We iterate through each square of the grid, and if it belongs to the dictionnary (theres a block there)
    # we change the color of the square to the color of the block
    for i in range(len(grid)):
        for j in range(len(grid[1])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    
    return grid

# Function that simply generates a shape and returns it
def get_shape(): 
    return Piece(5, 0,random.choice(shapes_list))

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



def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    
    return False



def convert_shape_format(shape):
    positions = []

    # if rotation is 0, we get the first iteration of the shape, and the more we rotate, the more we get the next iteration
    format = shape.shape[shape.rotation % len(shape.shape)]


    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
        
            # if there is a block there, we add the position to the list
            if column == '0':
                positions.append((shape.x + j, shape.y + i))


    for i, pos in enumerate(positions):
        # We offset the position so it displays correctly
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

def valid_space(shape, grid):
    # only a valid position if the position is blank
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]

    # This line changes from [[(0,1)], [(2,3)]] -> [(0,1), (2,3)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape) 

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    
    return True


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



def main(win):
    
    # We start with no locked positions
    locked_positions = {}
    
    # Create our grid
    grid = create_grid(locked_positions)

    # Variable that if true will switch the status of a block. It will stop it from falling
    change_piece = False

    # Generate the 
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.3
    level_time = 0
    score = 0


    run = True
    
    while run:

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1

                if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.x -= 1
                    
                if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.y -= 1
                    
                if event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.rotation -= 1
        
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]

            if y > -1:
                grid[y][x] = current_piece.color
            
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # 10 points per row cleared
            score += clear_rows(grid, locked_positions) * 10

        

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False



def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press any key to play', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                main(win)
    
    pygame.display.quit()
    

win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('TETRIS')
main_menu(win)