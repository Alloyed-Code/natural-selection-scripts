import pygame
import random
import math

# --------- variables ---------
#grid square height and width
WIDTH = 5
HEIGHT = 5
MARGIN = 0
#grid size
grid_size_x = 128
grid_size_y = 128
#Colors
black = (0, 0, 0)
white = (255, 255, 255) #open space 0
brown = (205, 133, 63) #earth 1
blue = (0, 255, 255) #diamond! 2
red = (255, 0 ,0) #digger
#cell maximum value
cellMax = 2
#digger total
diggers = 5
#reproducing total
rep_diggers = 2
#smaller constant = more diamonds
diamond_constant = 8

round_limit = 500

class Digger():
    #position on the grid
    x = None
    y = None
    #diamonds collected
    diamonds = 0
    #tile weights
    open_weight = 1.0
    earth_weight = 0.5
    diamond_weight = 5.0
    #direction weights
    north_weight = 0.1
    east_weight = 0.5
    south_weight = 1.0
    west_weight = 0.5

    def behaviour(self):
        #sets up depth weight, decreases strength with depth applied to moving south
        depth_weight = (1.0 - (self.y / grid_size_y))
        #list of direction weights and spaces
        weight_list = []
        #North
        weight_list.append([self.tileWeight(checkSpace(self.x,self.y - 1), self.north_weight), self.x, self.y - 1])
        #East
        weight_list.append([self.tileWeight(checkSpace(self.x + 1,self.y), self.east_weight), self.x + 1, self.y])
        #South
        weight_list.append([self.tileWeight(checkSpace(self.x,self.y + 1), self.south_weight) * depth_weight, self.x, self.y + 1])
        #West
        weight_list.append([self.tileWeight(checkSpace(self.x - 1,self.y), self.west_weight), self.x - 1, self.y])

        weight_total = weight_list[0][0] + weight_list[1][0] + weight_list[2][0] + weight_list[3][0]
        roll = random.random() * weight_total
        #check where roll lands in weighted list
        if roll <= weight_list[0][0]: #North
            self.moveLocation(self.x,self.y - 1)
        elif roll <= weight_list[0][0] + weight_list[1][0]: #West
            self.moveLocation(self.x + 1,self.y)
        elif roll <= weight_list[0][0] + weight_list[1][0] + weight_list[2][0]: #South
            self.moveLocation(self.x,self.y + 1)
        elif roll <= weight_list[0][0] + weight_list[1][0] + weight_list[2][0] + weight_list[3][0]: #West
            self.moveLocation(self.x - 1,self.y)

    def tileWeight(self, tile_type, dir_weight):
        #figures out what tile type it is then applies a weight depending on type and direction
        if tile_type == 0: #open
            return 1 * self.open_weight * dir_weight
        elif tile_type == 1: #earth
            return 1 * self.earth_weight * dir_weight
        elif tile_type == 2: #diamond
            return 1 * self.diamond_weight * dir_weight
        else:
            return 0

    def moveLocation(self, loc_x, loc_y):
        to_tile = checkSpace(loc_x, loc_y)
        if to_tile == 0:#empty tile
            self.x = loc_x
            self.y = loc_y
        elif to_tile == 1:#earth tile
            grid[loc_y][loc_x] = 0
        elif to_tile == 2: #diamond tile
            grid[loc_y][loc_x] = 0
            self.diamonds += 1

    def randomMove(self):
        direction = random.randint(0,3)
        if direction == 0: #north
            self.moveLocation(self.x,self.y - 1)
        elif direction == 1: #east
            self.moveLocation(self.x + 1,self.y)
        elif direction == 2: #south
            self.moveLocation(self.x,self.y + 1)
        elif direction == 3: #west
            self.moveLocation(self.x - 1,self.y)



#array for the grid
grid = []
for row in range(grid_size_y): #range is grid height
    #adds column list for every row
    grid.append([])
    for column in range(grid_size_x): #range is grid width
        grid[row].append(1) #all cells start 1

#list of diggers
entities = []

#randomly disperses diamonds
def spreadDiamonds (grid):
    for row in range(grid_size_y):
        for column in range(grid_size_x):
            random_num = random.randint(0, grid_size_y)
            if random_num <= row // diamond_constant:
                grid[row][column] = 2
#blanks grid to earth
def blankGrid(grid):
    for row in range(grid_size_y):
            for column in range(grid_size_x):
                grid[row][column] = 1

def randomValue(coord):
    rand_coord = random.randint(0,coord - 1)
    return rand_coord

def checkSpace(x,y):
    if 0 <= x < grid_size_x and 0 <= y < grid_size_y: 
        return grid[y][x]
    else:
        return 99 #bedrock/arena border

#for sorting by diamond total
def takeDiamond(digger): 
    return digger.diamonds

#gene splicing function
def geneSwapping(parents):
    open_list = []
    earth_list = []
    north_list = []
    east_list = []
    south_list = []
    west_list = []

    children = []
    for parent in parents:#coallates all the gene weights into lists
        open_list.append(parent.open_weight)
        earth_list.append(parent.earth_weight)
        north_list.append(parent.north_weight)
        east_list.append(parent.east_weight)
        south_list.append(parent.south_weight)
        west_list.append(parent.west_weight)
    for n in range(diggers):
        children.append(Digger())
        children[n].open_weight = random.choice(open_list)
        children[n].open_weight = mutation(children[n].open_weight) #do a mutation roll
        children[n].earth_weight = random.choice(earth_list)
        children[n].earth_weight = mutation(children[n].earth_weight) #do a mutation roll
        children[n].north_weight = random.choice(north_list)
        children[n].north_weight = mutation(children[n].north_weight) #do a mutation roll
        children[n].east_weight = random.choice(east_list)
        children[n].east_weight = mutation(children[n].east_weight) #do a mutation roll
        children[n].south_weight = random.choice(south_list)
        children[n].south_weight = mutation(children[n].south_weight) #do a mutation roll
        children[n].west_weight = random.choice(west_list)
        children[n].west_weight = mutation(children[n].west_weight) #do a mutation roll
        ##places them in starting positions
        children[n].x = int((grid_size_x // diggers) * (n + 0.5))
        children[n].y = 0
    return children

def mutation(current):
    #1 in 20 chance of mutation
    if random.randint(1,20) == 20:
        print ("Mutation!")
        return random.random()
    else:
        return current
#initialize game
pygame.init()
#set size of screen
window_size = [grid_size_x * WIDTH, grid_size_y * HEIGHT]
screen = pygame.display.set_mode(window_size)
#Title
pygame.display.set_caption("The Mines")
#stop program button
done = False
#screen update speed
clock = pygame.time.Clock()

# Initialization functions
spreadDiamonds(grid)
for n in range(diggers):
    entities.append(Digger())
    #random position at the top
    #entities[n].x = randomValue(grid_size_x - 1)
    entities[n].x = int((grid_size_x // diggers) * (n + 0.5))
    entities[n].y = 0
    grid[entities[n].y][entities[n].x] = 0
    #random weights
    entities[n].open_weight = random.random()
    entities[n].earth_weight = random.random()
    entities[n].north_weight = random.random()
    entities[n].east_weight = random.random()
    entities[n].south_weight = random.random()
    entities[n].west_weight = random.random()

round_turns = 0
generation = 0
# -------- Main Loop -----------
while not done:
    if round_turns >= round_limit:
        ##reset grid
        #blankGrid(grid)
        #spreadDiamonds(grid)
        round_turns = 0
        generation += 1
        entities.sort(reverse = True, key=takeDiamond)
        #for entity in entities:
            #print (entity.diamonds)
        print ("Best diamond find:", entities[0].diamonds)
        reproducing = []
        for n in range(rep_diggers):
            reproducing.append(entities[n])
        entities = geneSwapping(reproducing)
        
    print ("Current Generaion:", generation)
    # -------- Round Loop -----------
    while not done and round_turns < round_limit:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH)
                row = pos[1] // (HEIGHT)
                # increases that location by one, wrap around
                grid[row][column] += 1
                if grid[row][column] > cellMax:
                    grid[row][column] = 0
                print("Click ", pos, "Grid coordinates: ", row, column)

        #set screen background
        screen.fill(black)

        #creature actions
        for entity in entities:
            #entity.randomMove()
            entity.behaviour()


        #draw the grid
        for row in range(grid_size_y):
            for column in range(grid_size_x): # 0 = empty space
                color = white
                if grid[row][column] == 1: # 1 = earth
                    color = brown
                elif grid[row][column] == 2: # 2 = diamond
                    color = blue
                pygame.draw.rect(screen, #Chooses the screen
                                 color, #chooses the color of square
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN,
                                  WIDTH,
                                  HEIGHT])

        #draw creatures
        for entity in entities:
            color = red
            pygame.draw.circle(screen,color,
                               [entity.x * WIDTH + WIDTH // 2,
                                entity.y * HEIGHT + HEIGHT // 2],
                               WIDTH // 2)
        round_turns += 1
        #limit 30 frames per second
        clock.tick(30)

        #update screen
        pygame.display.flip()

pygame.quit()
