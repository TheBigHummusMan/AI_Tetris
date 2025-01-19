###################################################
# Tech with Tim's tutorial was used to learn how  #
# to use pygame when it comes to a tetris game    #
###################################################
import multiprocessing
import random
import pygame
import numpy as np
import os

from gaze_tracking import eye_tracking

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




# GLOBAL VARIABLES -----------------------------------------
screen_width = 800
screen_height = 700
play_width = 300    # 300 // 10  gives 30 width per block
play_height = 600   # 600 // 20 gives 30 height per block
block_size = 30


top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

pygame.mixer.init()
if os.name == 'nt':
    warning_image_location = 'images\\warning_image.png'
    alarm_audio_location = 'audio\\alarm_audio.mp3'
else:
    warning_image_location = 'game/images/warning_image.png'
    alarm_audio_location = 'game/audio/alarm_audio.mp3'

warning_border_width = 20
warning_visible = False
user_inactive = False
user_ignored_warnings = False

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







pygame.font.init()



class Piece(object):
    # Initialize a new piece with its position and shape
    def __init__(self, x, y, shape):
        # Set the x and y coordinates of the piece
        self.x = x
        self.y = y
        self.index = shapes_list.index(shape)
        # Set the shape of the piece
        self.shape = shape
        # Set the color of the piece based on its shape
        self.color = shape_colors[self.index]
        # Initialize the rotation of the piece to 0
        self.rotation = 0
    def get_stats(self):
        print([self.x,self.y, self.index ,self.rotation])
        return [self.x,self.y, self.index ,self.rotation]

class TetrisGameTrain:
    def __init__(self,win,screen_width,screen_height,play_width,play_height):
        self.win = win
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.play_width = play_width
        self.play_height = play_height
        self.locked_positions = {}
        self.grid = self.create_grid(self.locked_positions)
        self.current_piece = self.get_shape().get_stats()
        self.next_piece = self.get_shape().get_stats()
        self.fall_time = 0
        self.fall_speed = 0.3
        self.level_time = 0
        self.score = 0
        self.running = True
        self.ai_control = False
        self.reward = 0
        self.run = None
        self.total_rows_cleared = 0
        self.current_piece_stat = None



    # This function creates a grid, the dictionnary 'locked_positions' to store the positions of the pieces 
    # that are locked in the grid. In other words, theres a block there
    def create_grid(self,locked_positions = {}):

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

    def get_number_of_holes(self):
        holes = 0  # Initialize the hole counter

        # Iterate through each column of the grid
        for col in range(len(self.grid[0])):
            found_filled_block = False  # Track if a filled block has been found in the column
            for row in range(len(self.grid)):
                if self.grid[row][col] != (0, 0, 0):  # If the cell is not empty
                    found_filled_block = True
                elif found_filled_block:  # If the cell is empty but there is a filled block above it
                    holes += 1

        return holes

    def get_total_height(self):
        """
        Calculates the total height of the grid based on locked positions.

        Returns:
            total_height (int): The sum of column heights.
        """
        heights = [0] * 10  # Initialize heights for each column (10 columns in the grid)

        # Calculate column heights
        for x in range(10):  # Iterate over columns
            for y in range(20):  # Iterate over rows from top to bottom
                if self.grid[y][x] != (0, 0, 0):  # If the cell is not empty
                    heights[x] = 20 - y  # Calculate height (20 - y because y=0 is the top)
                    break  # Stop after finding the first block in the column

        # Calculate total height
        total_height = sum(heights)
        return total_height

    def get_bumpiness(self):
        """
        Calculates the bumpiness of the grid based on locked positions.

        Returns:
            bumpiness (int): The sum of absolute differences in height between adjacent columns.
        """
        heights = [0] * 10  # Initialize heights for each column (10 columns in the grid)

        # Calculate column heights
        for x in range(10):  # Iterate over columns
            for y in range(20):  # Iterate over rows from top to bottom
                if self.grid[y][x] != (0, 0, 0):  # If the cell is not empty
                    heights[x] = 20 - y  # Calculate height (20 - y because y=0 is the top)
                    break  # Stop after finding the first block in the column

        # Calculate bumpiness
        bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))
        return bumpiness

    # Function that simply generates a shape and returns it
    def get_shape(self): 
        return Piece(5, 0,random.choice(shapes_list))

    def draw_next_shape(self,shape, surface):
        # Create a font object to render the 'Next Shape:' label
        font = pygame.font.SysFont('Tahoma', 30)
        # Render the 'Next Shape:' label with white color
        label = font.render('Next Shape:', 1, (255, 255, 255))

        # Calculate the x and y coordinates to draw the next shape
        sx = top_left_x + play_width + 50
        sy = top_left_y + play_height/2 - 100

        # Get the current shape format based on its rotation
        format = shape.shape[shape.rotation % len(shape.shape)]

        # Iterate over each line in the shape format
        for i, line in enumerate(format):
            # Convert the line to a list of characters
            row = list(line)
            # Iterate over each character in the line
            for j, column in enumerate(row):
                # If the character is '0', draw a rectangle at the corresponding position
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

        # Draw the 'Next Shape:' label at the calculated position
        surface.blit(label, (sx + 10, sy - 30))


    # Method to write text in the upper middle section of the window
    def draw_text_middle_up(self,surface, text, size, color):
        font = pygame.font.SysFont('Tahoma', size, bold = True)
        label = font.render(text, 1, color)

        surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2) - 250))


    #Method to write text in the middle of the window
    def draw_text_middle(self,surface, text, size, color):
        font = pygame.font.SysFont('Tahoma', size, bold = True)
        label = font.render(text, 1, color)

        surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))



    # Function to clear the rows after a row has been completed.
    def clear_rows(self,grid, locked):

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



    # We simply check if the blocked positions have reached the top of the grid
    def check_lost(self,positions):
        for pos in positions:
            x, y = pos
            if y < 1:
                return True
        
        return False



    def convert_shape_format(self,shape):
        # Initialize an empty list to store the positions of the shape
        positions = []

        # Get the current shape format based on its rotation
        format = shape.shape[shape.rotation % len(shape.shape)]

        # Iterate over each line in the shape format
        for i, line in enumerate(format):
            # Convert the line to a list of characters
            row = list(line)
            # Iterate over each character in the line
            for j, column in enumerate(row):
                # If the character is '0', it represents a block, so add its position to the list
                if column == '0':
                    # Calculate the position of the block based on the shape's x and y coordinates
                    positions.append((shape.x + j, shape.y + i))

        # Offset the positions so they display correctly
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        # Return the list of positions
        return positions

    def valid_space(self,shape, grid):
        # only a valid position if the position is blank
        accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]

        # This line changes from [[(0,1)], [(2,3)]] -> [(0,1), (2,3)]
        accepted_pos = [j for sub in accepted_pos for j in sub]

        formatted = self.convert_shape_format(shape) 

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        
        return True



    # Function to draw the grid, self explanatory
    def draw_grid(self,surface, grid):
        # making the variables shorter and easier to write
        sx = top_left_x
        sy = top_left_y


        # Drawing each square of the grid
        for i in range(len(grid)):
            pygame.draw.line(surface, (128, 128, 128), (sx, sy + i*block_size), (sx+play_width, sy + i*block_size))
            for j in range(len(grid[i])):
                pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy), (sx + j*block_size, sy+play_height))



    # Creating the whole window
    def draw_window(self,surface, grid, score=0):
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

        surface.blit(label, (sx + 0, sy - 280))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                # We draw the color (grid[i][j]) onto the surface, at the position we want
                # toplefty + i*block_size is the true 'y' position, same thing for 'x'
                # We then specify, the width and length of drawing, and the '0' means we fill the square (not a border)
                pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)
        
        
        pygame.draw.rect(surface, (255, 0, 0), (top_left_x,top_left_y, play_width, play_height), 4)

        self.draw_grid(surface, grid)



    # Method that displays the warning once the user leaves or looks away for too long
    def display_warning(self,surface, image_location):
        global warning_visible


        # If the warning hasnt been turned off, we display the images, as well as the red border and the message
        if warning_visible:    
            im = pygame.image.load(image_location)
            im = pygame.transform.scale(im, (100, 100))
            surface.blit(im, (screen_width - play_width + 60, screen_height - play_height))
            surface.blit(im, (screen_width - (2*play_width) - 60, screen_height - play_height))
            
            # Top Border
            pygame.draw.rect(surface, (255, 0, 0), (0, 0, screen_width, warning_border_width))
            # Bottom border
            pygame.draw.rect(surface, (255, 0, 0), (0, screen_height - warning_border_width, screen_width, warning_border_width))
            # Left border
            pygame.draw.rect(surface, (255, 0, 0), (0, 0, warning_border_width, screen_height))
            # Right border
            pygame.draw.rect(surface, (255, 0, 0), (screen_width - warning_border_width, 0, warning_border_width, screen_height))

            pygame.draw.rect(surface, (50, 50, 50), (0, (screen_height//2) + 25, 1000, 50))
            self.draw_text_middle(win, "WARNING, COME BACK TO GAME", 40, (255, 0, 0))

    # Function to stop the warning (remove red borders and images)
    def stop_warning(self):
        global warning_visible
        warning_visible = False
        self.stop_alarm()

    # Function that sounds the alarm
    def sound_alarm(self,audio_location):
        pygame.mixer.music.load(audio_location)
        pygame.mixer.music.play(-1)


    # Function that stops the alarm from ringing
    def stop_alarm(self):
        pygame.mixer.music.stop()
    
    def play_step(self,action):
        self.current_piece_stat = self.current_piece.get_stats()
        if self.ai_control:
            if np.array_equal(action, [1, 0, 0,0]):
                self.current_piece.x -= 1
                if not(self.valid_space(self.current_piece, self.grid)):
                    self.current_piece.x += 1
            if np.array_equal(action, [0, 1, 0,0]):
                self.current_piece.x += 1
                if not(self.valid_space(self.current_piece, self.grid)):
                    self.current_piece.x -= 1
            if np.array_equal(action, [0, 0, 1,0]):
                self.current_piece.rotation += 1
                if not(self.valid_space(self.current_piece, self.grid)):
                    self.current_piece.rotation -= 1
            if np.array_equal(action, [0, 0, 0,1]):
                pass
            


    # Main method. This is where the good stuff is
    def main(self,win):
        
        # We start with no locked positions
        locked_positions = {}
        
        # Create our grid
        grid = self.create_grid(locked_positions)

        # Variable that if true will switch the status of a block. It will stop it from falling
        change_piece = False

        # Generate the current and next piece.
        self.current_piece = self.get_shape()
        next_piece = self.get_shape()

        # We have these variables to keep track of the blocks' falling speed
        # and the player's cumulative score over the round
        clock = pygame.time.Clock()
        fall_time = 0
        fall_speed = 0.3
        level_time = 0
        score = 0



        # Event queue for communication between processes
        event_queue = multiprocessing.Queue()

        # Start the background process for eye tracking
        p1 = multiprocessing.Process(target=eye_tracking.run_head_tracking, args=(event_queue,))
        p1.start()

        run = True

        # Main game loop that keeps the game running as long as run = True
        while run:
            grid = self.create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()
            
            # Every five seconds the speed gets increased
            if level_time/1000 > 5:
                level_time = 0
                if fall_speed > 0.12:
                    fall_speed -= 0.005

            if fall_time/1000 > fall_speed:
                fall_time = 0
                self.current_piece.y += 1

                # If the piece hits the bottom of the grid or another piece, we lock it in place
                if not(self.valid_space(self.current_piece, grid)) and self.current_piece.y > 0:
                    self.current_piece.y -= 1
                    change_piece = True
                    ai_control = True

            if self.ai_control:
                print("ai controling")
            # We check for many events, keystrokes, and we have different things happening depending on input

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    p1.join()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        p1.join()
                        print("break")
                        
                if event.type == pygame.KEYDOWN:
                    self.ai_control = False
                #if self.ai_control:
                 #   self.play_step(self,agent.action)
                if(not self.ai_control and event.type == pygame.KEYDOWN):
                    if event.key == pygame.K_LEFT:
                        self.current_piece.x -= 1
                        if not(self.valid_space(self.current_piece, grid)):
                            self.current_piece.x += 1

                    if event.key == pygame.K_RIGHT:
                            self.current_piece.x += 1
                            if not(self.valid_space(self.current_piece, grid)):
                                self.current_piece.x -= 1
                        
                    if event.key == pygame.K_DOWN:
                            self.current_piece.y += 1
                            if not(self.valid_space(self.current_piece, grid)):
                                self.current_piece.y -= 1
                        
                    if event.key == pygame.K_UP:
                            self.current_piece.rotation += 1
                            if not(self.valid_space(self.current_piece, grid)):
                                self.current_piece.rotation -= 1
                    

                    # temporary keybindings to control and test the warning and alarm
                    if event.key == pygame.K_1:
                        global warning_visible
                        warning_visible = True
                        global user_inactive
                        user_inactive = True

                    if not event_queue.empty():
                        event = event_queue.get()
                        previous = "NOT_LOOKING_AWAY"
                        # if the user ignores the warnings, we sound the alarms
                        if event == (previous := "LOOKING_AWAY_5"):
                            self.display_warning(win, warning_image_location)
                        if event == (previous := "LOOKING_AWAY_10"):
                            self.sound_alarm(alarm_audio_location)
                        if event == "NOT_LOOKING_AWAY":
                            self.stop_warning()
                            self.stop_alarm()
                            previous = "NOT_LOOKING_AWAY"

                        


            # Convert the current piece's shape format to a list of positions
            shape_pos = self.convert_shape_format(self.current_piece)

            # Iterate over each position in the shape
            for i in range(len(shape_pos)):
                # Get the x and y coordinates of the position
                x, y = shape_pos[i]

                # If the y coordinate is greater than -1 (i.e., the piece is not above the grid)
                if y > -1:
                    # Set the color of the grid at the position to the color of the current piece
                    grid[y][x] = self.current_piece.color
                
            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = self.current_piece.color
                self.current_piece = next_piece
                next_piece = self.get_shape()
                change_piece = False

                # 100 ppr for one row
                # 300 ppr for two rows
                # 500 ppr for three rows
                # 800 ppr for four rows
                #score += clear_rows(grid, locked_positions) * 10

                rows_cleared = self.clear_rows(grid, locked_positions)
                self.total_rows_cleared += rows_cleared
                if rows_cleared > 3: 
                    self.reward+=10
                    score += rows_cleared * 800
                elif rows_cleared > 2:
                    self.reward+=7
                    score += rows_cleared * 500
                elif rows_cleared > 1:
                    self.reward+=4 
                    score += rows_cleared * 300
                else:
                    self.reward+=2
                    score += rows_cleared * 100
                

            
            self.draw_window(win, grid, score)
            self.draw_next_shape(next_piece, win)
                


            pygame.display.flip()

            # every iteration, we check if the user has lost the game
            # if he loses, we end the game and display GAME OVER
            if self.check_lost(locked_positions):
                self.draw_text_middle(win, "GAME OVER", 80, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(2000)
                self.reward -= 100
                run = False

        p1.join()

    def main_menu(self, win):
        run = True

        font = pygame.font.SysFont('Tahoma', 40, bold=True)
        # Define button dimensions for "PLAY"
        play_label = font.render("PLAY", 1, (255, 255, 255))
        play_x = top_left_x + play_width / 2 - (play_label.get_width() / 2)
        play_y = top_left_y + play_height / 2 - (play_label.get_height() / 2) - 100
        play_button = pygame.Rect(play_x - 20, play_y - 10, play_label.get_width() + 40, play_label.get_height() + 20)

        # Define button dimensions for "CHECK AI LOGS" (optional)
        ai_label = font.render("CHECK AI LOGS", 1, (255, 255, 255))
        ai_x = top_left_x + play_width / 2 - (ai_label.get_width() / 2)
        ai_y = top_left_y + play_height / 2 - (ai_label.get_height() / 2) - 25
        ai_button = pygame.Rect(ai_x - 20, ai_y - 10, ai_label.get_width() + 40, ai_label.get_height() + 20)

        # Main menu loop
        while run:
            win.fill((0, 0, 0))
            self.draw_text_middle_up(win, 'Welcome to TETRIS', 60, (255, 255, 255))

            # Draw buttons
            pygame.draw.rect(win, (50, 50, 50), play_button)  # Play button background
            win.blit(play_label, (play_x, play_y))  # Play button text

            pygame.draw.rect(win, (50, 50, 50), ai_button)  # AI Logs button background
            win.blit(ai_label, (ai_x, ai_y))  # AI Logs button text

            pygame.display.update()

            mouse_pos = pygame.mouse.get_pos()  # Get mouse position

            # Check if the mouse is over the "PLAY" button and change the cursor
            if play_button.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Hand cursor
            elif ai_button.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Hand cursor
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Default arrow cursor

            pygame.display.update()

            # listening for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click
                    mouse_pos = pygame.mouse.get_pos()  # Get mouse position
                    if play_button.collidepoint(mouse_pos):  # Check if "PLAY" button is clicked
                        self.main(win)  # Start the game
                    elif ai_button.collidepoint(mouse_pos):  # Check if "CHECK AI LOGS" button is clicked
                        print("AI Logs button clicked!")  # Placeholder for AI Logs functionality

        # If we make it here, it means player is done, we quit
        pygame.display.quit()




if __name__ == "__main__":
    # Initialize the window, the caption, and we START
    win = pygame.display.set_mode((screen_width, screen_height))
    game = TetrisGameTrain(win, screen_width, screen_height, play_height, play_height)
    pygame.display.set_caption('TETRIS')
    game.main_menu(win)