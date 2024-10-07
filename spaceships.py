import pygame
import random
import math
import copy

# --------- variables ---------
#grid square height and width
WIDTH = 4
HEIGHT = 4
MARGIN = 0
#grid size
grid_size_x = 128
grid_size_y = 128
#Colors
black = (50, 50, 50)
dark_grey = (85, 85, 85) #armor 1
light_grey = (170, 170, 170)
white = (255, 255, 255) #bridge 0
brown = (205, 133, 63) #thrusters 4
blue = (0, 255, 255) #sensor 2
red = (150, 0 ,0) #weapons 3
grey_brown = (150, 88, 67)
dark_blue = (0, 122, 122)
cellMax = 4


mutation_chance = 400

fuel_start = 100


class tile ():
    #just a tile
    color = black
    def __init__(self, x, y, ID):
        self.x = x
        self.y = y
        self.ID = ID
    def behavior(self):
        return

class block (tile):
    #part of ship
    def __init__(self, x, y, ID, kind):
        tile.__init__(self,x,y,ID)
        self.block_type = kind
        if self.block_type == 0: #bridge
              self.color = white
        elif self.block_type == 1: #armor
            self.color = dark_grey
        elif self.block_type == 2: #sensor
            self.color = blue
        elif self.block_type == 3: #weapons
            self.color = red
        elif self.block_type == 4: #thrusters
            self.color = brown

    def __deepcopy__(self, memodict={}):
        copy_object = block(self.x, self.y, self.block_type)
        return copy_object
                
class entity (tile):
    #everything that moves
    def __init__(self, x, y, Vx, Vy, ID):
        tile.__init__(self, x, y,ID)
        self.velocity = (Vy, Vx)
    def __deepcopy__(self, memodict={}):
        copy_object = entity(self.x,self.y,self.velocity[1],self.velocity[0],self.ID)
        #copy_object.age = self.age
        return copy_object

class spaceship (entity):
    #complex objects built by genetics(blueprint) that exert control based on neural net
    def __init__(self, x, y, Vx, Vy, ID, blueprint, net):
        entity.__init__(self, x, y, Vx, Vy, ID)
        self.blueprint = blueprint
        self.net = net
        self.blocks = []
        self.xrad = 2
        self.yrad = 2
        self.construct()
        self.fuel = fuel_start
    def construct(self):
        #first, all coordinates are relative to top left corner being 0,0
        self.blocks.append(block(self.blueprint[5][1],self.blueprint[5][0],self.ID,0,))
        self.spread_construct(self.blueprint[5][1]+0,self.blueprint[5][0]-1)
        self.spread_construct(self.blueprint[5][1]+1,self.blueprint[5][0]+0)
        self.spread_construct(self.blueprint[5][1]+0,self.blueprint[5][0]+1)
        self.spread_construct(self.blueprint[5][1]-1,self.blueprint[5][0]+0)
        #change to full grid coords
        for part in self.blocks:
            part.x = part.x + self.x - 2
            part.y = part.y + self.y - 2

    def spread_construct(self,x,y):
        if (x < 5 and x > -1):
            if ( y < 5 and y > -1):
                empty = True
                for part in self.blocks:
                    if (part.x == x and part.y == y):
                        empty = False
                if (empty == True):
                    if (self.blueprint[y][x] <= 4):
                        self.blocks.append(block(x,y,self.ID,self.blueprint[y][x]))
                        self.spread_construct(x+0,y-1)
                        self.spread_construct(x+1,y+0)
                        self.spread_construct(x+0,y+1)
                        self.spread_construct(x-1,y+0)

    def behavior(self):
        #check neural net to figure out what to do/adjust

        self.move()

    def move(self):
        safe = True
        for sbl in self.blocks:
            for ent in entities:
                if (ent.ID != self.ID):
                    for bl in ent.blocks:
                        if (wrapHandlerx(sbl.x + self.velocity[1]) == bl.x):
                            if (wrapHandlery(sbl.y + self.velocity[0]) == bl.y):
                                safe = False
        for bl in self.blocks:
            bl.x = wrapHandlerx(bl.x + self.velocity[1])
            bl.y = wrapHandlery(bl.y + self.velocity[0])
        

#========array for the grid==========#
##grid = []
##next_grid = []
##for row in range(grid_size_y): #range is grid height
##    #adds column list for every row
##    grid.append([])
##    next_grid.append([])
##    for column in range(grid_size_x): #range is grid width
##        grid[row].append(block(column,row,1)) #all cells start as air
##        next_grid[row].append(block(column,row,0))

#========array for entities==========#
entities = []


def initialGenes():
    genome = []
    for chromosome in range(5): #5x5 chromosome matrix per genome
        genome.append([])
        for gene in range(5): #random genes with 50% chance of a block
            genome[chromosome].append(random.randint(1,cellMax*2))
    genome.append([random.randint(0,4),random.randint(0,4)]) #special 6th chromosome for bridge location
    return genome



#blanks grid to earth
##def blankGrid(grid):
##    for row in range(grid_size_y):
##            for column in range(grid_size_x):
##                if not isinstance(grid[row][column], entity):
##                    grid[row][column] = block(column,row,1)
##def setAir(grid):
##    for row in range(grid_size_y): #sets air to everywhere level 32 and less
##                    for column in range(grid_size_x):
##                        if row > 32:
##                            break
##                        if not isinstance(grid[row][column], entity):
##                            grid[row][column] = block(column,row,0)


def randomValue(coord):
    rand_coord = random.randint(0,coord - 1)
    return rand_coord

def checkSpace(x,y):
    if 0 <= x and x < grid_size_x and 0 <= y and y < grid_size_y: 
        return next_grid[y][x]
    elif 0 <= y and y < grid_size_y:
        return next_grid[y][wrapHandler(x)]
    else:
        return 99 #bedrock/arena border

def wrapHandlerx(x):
    if x >= grid_size_x: #wrap right
        return x - grid_size_x
    elif x < 0: #wrap left
        return grid_size_x - x
    return x

def wrapHandlery(y):
    if y >= grid_size_y: #wrap down
        return y - grid_size_y
    elif y < 0: #wrap up
        return grid_size_y - y
    return y        

def mutation(current, gene_max):
    #1 in ? chance of mutation
    if random.randint(1,mutation_chance) == 1:
        #print ("Mutation!")
        return randomGene(gene_max)
    else:
        return current

def randomGene(gene_max):
    return random.randint(0,gene_max)

def passGenes(genes):
    for chromosome in range(16): #16 chromosomes per genome
        for gene in range(4): #4 different directions 0 up, 1 right, 2 down, 3 left
            for direction in range(cellMax+1):
                genes[chromosome][gene][direction] = mutation(genes[chromosome][gene][direction], 31)
    for gene in range(4): #direction
            genes[16][gene] = mutation(genes[16][gene], 15)
    return genes


    
#initialize game
pygame.init()
#set size of screen
window_size = [grid_size_x * WIDTH, grid_size_y * HEIGHT]
screen = pygame.display.set_mode(window_size)
#Title
pygame.display.set_caption("Space")
#stop program button
done = False
#screen update speed
clock = pygame.time.Clock()

# Initialization functions
entities.append(spaceship(64,64,1,2,0,initialGenes(),0))

# -------- Main Loop -----------
while not done:
    round_num = 0
    pause = False
    reset_terrain = False
    wait_round = False
    auto_restart = False
    # -------- Round Loop -----------
    while not done:
        alive = 0
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH)
                row = pos[1] // (HEIGHT)
                print("Click ", pos, "Grid coordinates: ", row, column)
                if type(grid[row][column]) is block:
                    if grid[row][column].block_type == cellMax:
                        grid[row][column] = block(row,column,0)
                    else:
                        grid[row][column] = block(row,column, 1 + grid[row][column].block_type)
                if isinstance(grid[row][column], entity):
                    if type(grid[row][column]) is source:
                        print("Energy: " + str(grid[row][column].energy))
                        print("Age: " + str(grid[row][column].age) + "/" + str(grid[row][column].age_limit))
                        print("Score: " + str(grid[row][column].score))
                    if type(grid[row][column]) is feeler:
                        print("State: " + str(grid[row][column].state))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if pause == True:
                        print("Unpaused")
                        pause = False
                    elif pause == False:
                        print("Paused")
                        pause = True
                if event.key == pygame.K_r:
                    print("Reseting terrain...")
                    reset_terrain = True
                if event.key == pygame.K_s:
                    print("Spawned 1 new")
                    random_x = random.randint(0, grid_size_x -1)
                    grid[32][random_x] = source(random_x,32,initialGenes(),starting_energy)
                if event.key == pygame.K_a:
                    if auto_restart == True:
                        print("Auto restart disabled")
                        auto_restart = False
                    elif auto_restart == False:
                        print("Auto restart enabled")
                        auto_restart = True

                if event.key == pygame.K_h:
                    print ("""+==========Help==========+
Key Inputs:

       h: Help Menu
Spacebar: Pause/Unpause
       r: Reset terrain
       s: Spawn a new random source
       a: Automatically restart simulation if all are dead""")

        if reset_terrain == True:
                reset_terrain = False
                blankGrid(grid)
                spreadOre(grid)
                #setAir(grid)

        #if pause == True:
            #screen.fill(black)
            #draw the grid
##            for row in range(grid_size_y):
##                for column in range(grid_size_x):
##                    color = grid[row][column].color
##                    pygame.draw.rect(screen, #Chooses the screen
##                                     color, #chooses the color of square
##                                     [(MARGIN + WIDTH) * column + MARGIN,
##                                      (MARGIN + HEIGHT) * row + MARGIN,
##                                      WIDTH,
##                                      HEIGHT])
        if pause == False:
            #activates behavior of all cells
##            next_grid = copy.deepcopy(grid)
##            for row in range(grid_size_y):
##                for column in range(grid_size_x):
##                    #if type(grid[row][column]) is not block:
##                    if type(grid[row][column]) == type(next_grid[row][column]):
##                        if type(grid[row][column]) is source or type(grid[row][column]) is seed or type(grid[row][column]) is feeler:
##                            alive += 1
##                        grid[row][column].behavior()
            """for s in sources:
                grid[s[0]-1][s[1]-1].behavior
                alive+=1
            for f in feelers:
                grid[f[0]][f[1]].behavior"""
            #grid = copy.deepcopy(next_grid)
            #set screen background
            screen.fill(black)

            #draw the grid
##            for row in range(grid_size_y):
##                for column in range(grid_size_x):
##                    color = grid[row][column].color
##                    pygame.draw.rect(screen, #Chooses the screen
##                                     color, #chooses the color of square
##                                     [(MARGIN + WIDTH) * column + MARGIN,
##                                      (MARGIN + HEIGHT) * row + MARGIN,
##                                      WIDTH,
##                                      HEIGHT])
            for entity in entities:
                entity.behavior()
                for bl in entity.blocks:
                    pygame.draw.rect(screen, #Chooses the screen
                                     bl.color, #chooses the color of square
                                     [(MARGIN + WIDTH) * bl.y + MARGIN,
                                      (MARGIN + HEIGHT) * bl.x + MARGIN,
                                      WIDTH,
                                      HEIGHT])

##            if wait_round == True:
##                if auto_restart == True:
##                    print("All dead, spawning new")
##                    wait_round = False
##                    blankGrid(grid)
##                    spreadOre(grid)
##                    #setAir(grid)
##                    round_num = 0
##                    for n in range(spawn_new_total):
##                        random_x = random.randint(0, grid_size_x -1)
##                        random_y = random.randint(0, grid_size_y -1)
##                        #spawn new
##                        alive += 1
                    
            print ("round: " + str(round_num))

            round_num += 1
        #limit 30 frames per second
        clock.tick(30)
        #update screen
        pygame.display.flip()

pygame.quit()
